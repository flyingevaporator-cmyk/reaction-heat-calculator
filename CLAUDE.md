# Project: Chemistry Calculation Platform

Multi-component chemistry calculation toolkit (reaction heat, transition states, PFD generation).

## Project Structure

| Directory | Stack | Purpose |
|-----------|-------|---------|
| `backend/` | Python FastAPI + RDKit + xTB | Reaction enthalpy REST API |
| `frontend/` | React 19 + TypeScript + Vite + Ketcher | Molecular editor web UI |
| `ts_calculator/` | Python PyQt6 + PySCF/xTB (DDD) | Transition state desktop GUI |
| `pfd-generator/` | React 19 + Mermaid + jsPDF + Vite | Process flow diagram generator |

## Build & Run Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (dev server proxies /api to localhost:8000)
cd frontend && npm install && npm run dev

# PFD Generator (port 5180)
cd pfd-generator && npm install && npm run dev

# Desktop app
cd ts_calculator && pip install -e .
ts-calculator

# Lint
cd frontend && npm run lint
cd pfd-generator && npm run lint
```

## Testing & Verification

Every change MUST be verified before commit/PR. Follow this checklist:

### ts_calculator (Python)
```bash
cd ts_calculator && python -m pytest tests/unit/ -v
```
- Run unit tests after any change to domain/, adapters/, or app/ layers
- If adding new functionality, add corresponding test in tests/unit/

### Frontend / PFD Generator (TypeScript)
```bash
cd frontend && npm run lint
cd pfd-generator && npm run lint
```
- No test suite yet — verify via lint + dev server browser check
- For UI changes: start dev server, verify visually, check browser console for errors
- A PostToolUse hook auto-runs ESLint after every TS/TSX file edit

### Backend (Python)
- No test suite yet — verify via manual API call or curl
- For API changes: start uvicorn, test with `curl http://localhost:8000/api/...`

## Code Conventions

- Frontend/PFD: TypeScript strict mode, React functional components, ESLint flat config
- Backend: Python 3.11+, FastAPI async patterns, type hints
- ts_calculator: Domain-Driven Design (domain/adapters/app/gui layers), PyQt6

## Architecture Notes

- Frontend communicates with backend via SSE streaming (`/api/calculate`) and sync endpoint (`/api/calculate-sync`)
- Backend uses in-memory enthalpy caching (no DB)
- ts_calculator wraps multiple chemistry backends: xTB, PySCF, Psi4
- Ketcher molecular editor is embedded in both frontend and ts_calculator

## Available Skills & Agents

### Skills (invoke with natural language)
- **dev-server** — Start/stop dev servers (backend, frontend, pfd)
- **verify-all** — Run all linters and tests across the project, report summary table
- **add-component** — Scaffold a new React component following project conventions

### Custom Agents (use via "use the X agent")
- **code-reviewer** (Sonnet) — Review code for bugs, security, and style. Read-only, outputs severity-tagged issues
- **test-writer** (Sonnet) — Generate pytest unit tests for ts_calculator modules

## Session Management

- Use `/clear` between unrelated tasks to keep context clean
- Use `/compact` when context grows large during a single task
- Delegate investigation to subagents to avoid polluting main context
- After 2 failed corrections, `/clear` and rewrite the prompt instead of continuing
- Use `code-reviewer` agent after implementation before committing

## IMPORTANT

- ALWAYS run lint before suggesting a PR or commit
- When editing React components, preserve existing component boundaries — do not merge components without discussion
- Backend CORS is configured for localhost:5173 only — update if ports change
- `index.html` and `bom-cost.html` in root are generated artifacts — do NOT edit directly
