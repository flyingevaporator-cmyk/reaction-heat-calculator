"""WorkflowOrchestrator: executes steps in sequence and wires data between them."""
from __future__ import annotations
from pathlib import Path
from typing import Callable, Optional

from adapters import get_registry
from adapters.base import CalcParams
from domain.models import CalcType, CalculationResult, CalcStatus
from domain.validators.ts_validator import TSValidator
from infrastructure.workspace_manager import WorkspaceManager
from infrastructure.process_runner import ProcessRunner
from infrastructure.session_serializer import SessionSerializer
from .workflow_session import WorkflowSession, WorkflowStep, StepStatus


class WorkflowOrchestrator:
    """
    Runs all enabled steps of a WorkflowSession in order.
    Designed to be called from a background thread (CalculationWorker).
    """

    def __init__(
        self,
        session: WorkflowSession,
        on_step_start: Optional[Callable[[WorkflowStep], None]] = None,
        on_step_done: Optional[Callable[[WorkflowStep], None]] = None,
        on_log_line: Optional[Callable[[str, str], None]] = None,   # (step_name, line)
        on_cancelled: Optional[Callable[[], None]] = None,
    ) -> None:
        self.session = session
        self.on_step_start = on_step_start or (lambda _: None)
        self.on_step_done = on_step_done or (lambda _: None)
        self.on_log_line = on_log_line or (lambda s, l: None)
        self.on_cancelled = on_cancelled or (lambda: None)
        self._cancel_requested = False
        self._current_runner: Optional[ProcessRunner] = None

    def run(self) -> None:
        registry = get_registry()
        workspace = WorkspaceManager()
        session_dir = Path(self.session.session_dir)
        validator = TSValidator()

        for step in self.session.steps:
            if self._cancel_requested:
                self.on_cancelled()
                return
            if not step.enabled:
                step.status = StepStatus.SKIPPED
                continue
            if step.status == StepStatus.SUCCESS:
                continue  # already done (resumed session)

            adapter = registry.get(step.engine)
            if adapter is None or not adapter.check_installation():
                step.status = StepStatus.FAILED
                step.result = CalculationResult(
                    calc_type=step.calc_type,
                    status=CalcStatus.FAILED,
                    engine=step.engine,
                    work_dir="",
                    error_message=f"Engine '{step.engine}' is not installed",
                )
                self.on_step_done(step)
                return

            step.status = StepStatus.RUNNING
            self.on_step_start(step)

            work_dir = workspace.create_step_dir(session_dir, step.name)
            step.work_dir = str(work_dir)

            # Resolve input molecule from previous step output
            molecule = self.session.last_successful_molecule()
            params = CalcParams(
                calc_type=step.calc_type,
                method=step.params.get("method", "gfn2"),
                basis=step.params.get("basis", ""),
                n_cores=step.params.get("n_cores", 1),
                memory_gb=step.params.get("memory_gb", 4.0),
                extra=step.params.get("extra", {}),
            )

            # NEB needs the product molecule as aux
            aux = None
            if step.calc_type == CalcType.NEB:
                aux = list(self.session.reaction_system.products)

            try:
                bundle = adapter.prepare_input(molecule, params, work_dir, aux_molecules=aux)
            except Exception as e:
                step.status = StepStatus.FAILED
                step.result = CalculationResult(
                    calc_type=step.calc_type, status=CalcStatus.FAILED,
                    engine=step.engine, work_dir=str(work_dir),
                    error_message=str(e),
                )
                self.on_step_done(step)
                return

            def _on_line(line: str, _step_name: str = step.name) -> None:
                self.on_log_line(_step_name, line)

            runner = ProcessRunner(
                command=bundle.command,
                cwd=bundle.work_dir,
                on_line=_on_line,
            )
            self._current_runner = runner
            runner.start()
            runner.wait()
            self._current_runner = None

            result = CalculationResult(
                calc_type=step.calc_type,
                status=CalcStatus.RUNNING,
                engine=step.engine,
                work_dir=str(work_dir),
                wall_time_seconds=runner.wall_time,
            )

            if self._cancel_requested:
                result.status = CalcStatus.CANCELLED
                step.status = StepStatus.FAILED
                step.result = result
                self.on_step_done(step)
                self.on_cancelled()
                return

            if runner.returncode != 0:
                result.status = CalcStatus.FAILED
                result.error_message = f"Process exited with code {runner.returncode}"
                step.status = StepStatus.FAILED
                step.result = result
                self.on_step_done(step)
                return

            result = adapter.parse_output(result)
            step.result = result

            # Validate TS steps
            if step.calc_type == CalcType.FREQUENCY and result.frequency_data:
                warnings = validator.check_frequency(result.frequency_data)
                if warnings:
                    result.extra["warnings"] = warnings

            step.status = StepStatus.SUCCESS if result.status == CalcStatus.SUCCESS else StepStatus.FAILED
            self.on_step_done(step)

            # Auto-save after each step
            save_path = session_dir / "session.json"
            SessionSerializer.save(self.session, save_path)

            if step.status == StepStatus.FAILED:
                return  # abort workflow on failure

        self.session.completed = True
        save_path = session_dir / "session.json"
        SessionSerializer.save(self.session, save_path)

    def cancel(self) -> None:
        self._cancel_requested = True
        if self._current_runner:
            self._current_runner.cancel()
