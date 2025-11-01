# Repository Guidelines

## Project Structure & Module Organization
The repo is split into `backend`, `frontend`, and `data`. The FastAPI service lives in `backend/app/main.py` alongside the SQLModel definitions and upload seed data; add new routers under `backend/app/` and wire them in `main.py`. Batch import helpers sit in `backend/app/import_excel.py`. React source code is in `frontend/src` (entry `main.tsx`, root component `App.tsx`, shared API client `api.ts`), with global styles in `src/index.css` and Tailwind config in `tailwind.config.js`. Persisted uploads and the seed workbook are kept in `data/`.

## Build, Test, and Development Commands
Run `docker-compose up --build` from the repo root to launch FastAPI on `:8000` and Vite on `:5173` with matching environment variables. For backend-only iteration, create a virtualenv, `pip install -r backend/requirements.txt`, then `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` inside `backend/app`. Frontend development uses `npm install` followed by `npm run dev -- --host` in `frontend/`. Build production assets with `npm run build` and preview them via `npm run preview -- --host`.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, descriptive snake_case function names, and PascalCase SQLModel classes. Keep response models typed and validate inputs with Pydantic. In TypeScript, stick to functional components, PascalCase component files (`App.tsx`), and camelCase hooks/utilities. Co-locate component-specific styles and prefer Tailwind utility classes over ad-hoc CSS.

## Testing Guidelines
Automated tests are not yet in place; new features should bring coverage. Back-end tests go under `backend/tests/` using `pytest`; name files `test_<feature>.py` and seed temporary SQLite databases via fixtures. Front-end tests should live in `frontend/src/__tests__/` using Vite’s `vitest` runner (`npm install -D vitest @testing-library/react @testing-library/jest-dom`) with files named `<Component>.test.tsx`. Document manual QA steps in the PR description when automated coverage is not feasible.

## Commit & Pull Request Guidelines
Use present-tense, imperative commit subjects under 72 characters (e.g., `Add certificate import endpoint`). Each PR should explain intent, list backend/frontend impacts, include test commands, and mention any new env vars or migrations. Attach screenshots or GIFs for UI changes and sample JSON payloads for API work. Request review from both backend and frontend maintainers when touching shared contracts.

## Security & Configuration Tips
Never commit real credentials or internal spreadsheets; rely on `.env` files mounted via Docker and keep example values in a committed `env.example`. Update `docker-compose.yml` notes when ports or volumes change and call out any migrations that require clearing `data/uploads`. Validate file uploads and sanitize filenames before writing to disk.
