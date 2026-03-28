---
name: dev-server
description: Start/stop development servers for frontend, backend, or PFD generator
---

# Dev Server Management

Start the requested development server(s). If the user doesn't specify which, ask.

## Available servers

| Name | Command | Port | Dir |
|------|---------|------|-----|
| backend | `uvicorn main:app --reload --port 8000` | 8000 | `backend/` |
| frontend | `npm run dev` | 5173 | `frontend/` |
| pfd | `npm run dev` | 5180 | `pfd-generator/` |

## Notes
- Frontend proxies `/api` to backend on port 8000 — start backend first if both are needed
- Run `npm install` or `pip install -r requirements.txt` if node_modules or venv is missing
- Use `preview_start` for browser verification after starting
