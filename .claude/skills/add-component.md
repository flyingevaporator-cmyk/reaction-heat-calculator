---
name: add-component
description: Scaffold a new React component in frontend or pfd-generator following project conventions
---

# Add React Component

Create a new React component following existing project patterns.

## Inputs needed
- **Component name** (PascalCase)
- **Target app**: `frontend` or `pfd-generator`
- **Purpose**: brief description of what the component does

## Steps

1. Read an existing component in the target app's `src/components/` to understand the pattern
2. Create the new component file at `src/components/{ComponentName}.tsx`
3. Follow these conventions:
   - Functional component with explicit props type
   - Named export (not default)
   - TypeScript strict — no `any` types
   - Shared types go in `src/types.ts`
4. Add the import to the parent component that will use it
5. Run lint to verify: `npm run lint`

## Do NOT
- Create a separate CSS module unless the component has complex styling
- Add tests (no test framework configured yet)
- Create barrel/index files
