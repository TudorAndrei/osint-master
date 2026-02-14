# API Explorer

Use this page to browse and test backend endpoints through Swagger UI.

## Live API schema

When your backend is running locally, use the embedded explorer below.

<swagger-ui src="http://localhost:8000/openapi.json"/>

## Notes

- Start backend first: `uv run uvicorn app.main:app --reload` from `backend/`
- Auth-protected routes require a valid session token in requests.
- You can replace the `src` URL with a hosted OpenAPI document later.
