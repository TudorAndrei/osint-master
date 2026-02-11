# Frontend Agents

## Frontend Implementation Agent

### Scope
- Entire `frontend/` folder.
- React routes, UI components, graph canvas interactions, and API integration.

### Software Stack
- **Runtime/Package Manager**: Bun
- **Build Tool**: Vite
- **Language/UI**: TypeScript + React 18
- **Routing**: React Router
- **Server State**: TanStack Query
- **Styling**: Tailwind CSS (+ shadcn/ui component patterns)
- **Graph Visualization**: Cytoscape.js + `cytoscape-fcose`
- **Linting**: ESLint v9 flat config (`frontend/eslint.config.js`)
- **Containerization**: `frontend/Dockerfile` with `oven/bun:1.2`

### Rules
- Use `src/api/client.ts` methods instead of ad-hoc network calls.
- Keep API typings in sync with backend models (`src/api/types.ts`).
- Preserve responsive behavior across desktop and mobile.
- Keep Cytoscape interactions stable (select, expand, zoom, layout).
- Maintain lint/build health for every change.

### Validate Before Finishing
- `bun run lint`
- `bun run build`

### Success Criteria
- Views remain functional (`home`, `investigation`) against backend.
- Lint/build pass with no TypeScript errors.
