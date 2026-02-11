# Authentication and BFF Integration Plan

## Goals

- Add authentication with Better Auth using email/password only.
- Introduce a Backend-for-Frontend (BFF) using Hono on Bun.
- Serve the React Router frontend and BFF API from the same container/process.
- Keep FastAPI private/internal and reachable only by the BFF.
- Enforce basic security controls for browser sessions and API proxying.

## Final Decisions (Locked)

- BFF framework/runtime: Hono + Bun.
- Auth mechanism: Better Auth.
- Login methods: email/password only.
- Signup: enabled (self-signup).
- Email verification: not required in v1.
- Deployment shape: frontend + BFF in the same container; Hono serves React app.
- FastAPI exposure: internal-only (not publicly exposed).

## High-Level Architecture

1. Browser calls a single public origin hosted by Hono.
2. Hono handles:
   - Better Auth endpoints (`/api/auth/*`)
   - Session/bootstrap endpoint (`/api/session`)
   - Authenticated proxy to FastAPI (`/api/*`)
   - Static frontend files and SPA fallback for React Router
3. FastAPI remains on internal Docker network and serves investigation data only.

## Route Map

- `GET/POST /api/auth/*` -> Better Auth handler.
- `GET /api/session` -> returns current session/user (or null/401 behavior by design).
- `ALL /api/investigations/*` -> authenticated proxy to FastAPI `/api/investigations/*`.
- `ALL /api/schema` -> authenticated proxy to FastAPI `/api/schema`.
- `ALL /api/enrich/*` -> authenticated proxy to FastAPI `/api/enrich/*`.
- `GET /*` (non-API) -> serve frontend static files; fallback to `index.html` for React Router.

## Repository Changes

### New `bff/` service

Planned files:

- `bff/package.json`
- `bff/tsconfig.json`
- `bff/src/index.ts`
- `bff/src/auth.ts`
- `bff/.env.example`
- `bff/Dockerfile`

Responsibilities:

- Build and run Hono server on Bun.
- Initialize Better Auth with Postgres.
- Validate session on protected routes.
- Enforce CSRF header on mutating requests.
- Proxy selected API paths to internal FastAPI.
- Serve built frontend assets and SPA fallback.

### Frontend updates

Planned file updates:

- `frontend/src/api/client.ts`
- `frontend/src/App.tsx` and/or route files for guard/auth pages
- `frontend/src/auth/client.ts` (new helper for Better Auth client)

Required behavior changes:

- Include `credentials: "include"` on frontend fetch calls.
- Add `x-csrf: 1` on mutating requests (`POST/PUT/PATCH/DELETE`, upload).
- Add sign-up/sign-in/sign-out flow.
- Add route guard to redirect unauthenticated users to sign-in.

### Infrastructure updates

Planned file updates:

- `docker-compose.yml`
- `README.md`

Compose changes:

- Add BFF service and expose it publicly.
- Keep FastAPI internal-only (remove public port mapping).
- Configure BFF to reach FastAPI through internal network (`http://backend:8000`).

## Security Baseline (v1)

- Browser only talks to BFF; no direct browser access to FastAPI.
- Better Auth session cookies are HTTP-only.
- Secure cookie attributes enabled in production mode.
- CSRF defense: require custom header (`x-csrf: 1`) for mutating API calls.
- Proxy path allowlist (only required FastAPI routes forwarded).
- Upstream timeout and controlled error mapping (e.g., 502/504).
- Minimal forwarded headers from BFF to FastAPI.

## Environment Variables

### BFF

- `BETTER_AUTH_SECRET`
- `BETTER_AUTH_URL`
- `DATABASE_URL`
- `FASTAPI_INTERNAL_URL` (expected: `http://backend:8000`)
- `TRUSTED_ORIGINS`
- `NODE_ENV`

### Frontend (dev-only patterns)

- If running Vite separately in development, proxy API to BFF.
- In production single-container mode, frontend is served by Hono and does not need direct backend URL.

## Better Auth Scope for v1

Enabled:

- Email/password sign-up and sign-in.
- Session management via Better Auth cookies.

Deferred:

- Email verification flow.
- Password reset emails.
- Social login providers.
- MFA/2FA.

## Migration and Setup

1. Configure Better Auth in `bff/src/auth.ts` with Postgres.
2. Run Better Auth CLI migration for schema creation.
3. Start services and validate auth/session/proxy flow.

Expected auth tables include user/session/account/verification and plugin-related additions if used later.

## Functional Acceptance Criteria

- Unauthenticated request to protected API route returns `401`.
- User can sign up and then sign in using email/password.
- Session cookie is issued and used automatically by browser.
- Authenticated requests from frontend succeed through BFF proxy.
- Mutating requests without `x-csrf` fail.
- FastAPI is not reachable from public network.
- React Router deep links resolve correctly via SPA fallback.

## Testing Checklist

- Sign-up happy path.
- Sign-in happy path.
- Sign-out invalidates active session.
- Protected route access when signed out.
- Protected route access when signed in.
- CSRF header enforcement on `POST/PUT/PATCH/DELETE`.
- Proxy behavior when FastAPI is unavailable (timeout/error handling).
- Browser refresh/deep-link handling for routes like `/investigation/:id`.

## Rollout Strategy

1. Implement BFF and auth in feature branch.
2. Integrate frontend auth client and route guards.
3. Switch Docker networking/exposure model.
4. Validate end-to-end locally.
5. Deploy with FastAPI private-only ingress.
6. Monitor logs and session/auth errors.

## Post-v1 Enhancements

- Add email verification and password reset with SMTP provider.
- Add user ownership/authorization mapping for investigations if required.
- Add stronger service-to-service trust between BFF and FastAPI (service JWT or mTLS).
- Add rate limiting and request tracing at BFF.
- Add integration/e2e auth test suite in CI.
