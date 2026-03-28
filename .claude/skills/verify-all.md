---
name: verify-all
description: Run all available linters and tests across the entire project
---

# Full Project Verification

Run all verification steps in order. Report results as a summary table.

## Steps

1. **Frontend lint**
   ```bash
   cd frontend && npm run lint
   ```

2. **PFD Generator lint**
   ```bash
   cd pfd-generator && npm run lint
   ```

3. **ts_calculator unit tests**
   ```bash
   cd ts_calculator && python -m pytest tests/unit/ -v
   ```

4. **Frontend build check** (catches TypeScript errors beyond lint)
   ```bash
   cd frontend && npm run build
   ```

5. **PFD Generator build check**
   ```bash
   cd pfd-generator && npm run build
   ```

## Output format

| Check | Status | Details |
|-------|--------|---------|
| Frontend lint | PASS/FAIL | error count or "clean" |
| PFD lint | PASS/FAIL | error count or "clean" |
| ts_calculator tests | PASS/FAIL | passed/failed count |
| Frontend build | PASS/FAIL | error summary |
| PFD build | PASS/FAIL | error summary |

If any step fails, list the specific errors and suggest fixes.
