# Frontend

The frontend is a Vite + React TypeScript application in `frontend/`.

## Runtime and scripts

- Install dependencies: `bun install`
- Start development server: `bun run dev`
- Build production bundle: `bun run build`
- Lint: `bun run lint`

## Route structure

- `/` - authenticated shell with home dashboard
- `/investigation/:id` - investigation workspace

All routes are wrapped in `RequireAuth`, and API auth context is bridged through Clerk configuration.

## Key UI modules

- `src/components/investigation/NotebookCanvas.tsx` - notebook workflow canvas
- `src/components/investigation/EntityMap.tsx` - geospatial exploration view
- `src/components/investigation/nodes/EntityNode.tsx` - graph node rendering
- `src/components/investigation/nodes/NoteNode.tsx` - note node rendering
- `src/components/layout/ThemeProvider.tsx` - theme state and persistence

## API integration

- API client code lives in `src/api/client.ts`.
- Shared API types live in `src/api/types.ts`.
- Backend base URL comes from `VITE_API_URL` and `VITE_DEV_PROXY_TARGET`.
