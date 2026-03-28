# Core data models (no PyQt6 dependency)
from .workflow_session import WorkflowSession, WorkflowStep, StepStatus

# GUI-dependent classes — import directly where needed:
#   from app.workflow_orchestrator import WorkflowOrchestrator
#   from app.job_manager import JobManager
#   from app.calculation_worker import CalculationWorker
