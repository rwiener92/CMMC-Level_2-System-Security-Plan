# CMMC Level 2 System Security Plan

## Overview
This repository contains a small full-stack application for managing a Cybersecurity Maturity Model Certification (CMMC) Level 2 System Security Plan. The FastAPI backend stores CMMC control metadata, assessment notes, and supporting evidence, while the React frontend provides filtering, dashboards, and detailed editing for each requirement. The goal is to streamline tracking C3PAO findings, self-reported implementation statuses, and documentation artifacts during certification preparation.

## Features
- Interactive dashboard summarizing C3PAO assessment findings and self-reported implementation progress.
- Searchable, filterable table of controls with per-domain filtering and quick status edits.
- Detail view for each requirement with provider/solution narratives and activity history.
- Evidence upload management that organizes files per control in `data/uploads/`.
- Optional Excel import utility to enrich assessment objectives and methods from a workbook.
  
<img width="1258" height="634" alt="Dashboard" src="https://github.com/user-attachments/assets/14cebd40-07b2-47c8-a44b-14176b9b185d" />

<img width="1250" height="1164" alt="Controls" src="https://github.com/user-attachments/assets/31f2004f-5cc7-4078-99b1-5ace1325e987" />

## Tech Stack
- **Backend:** FastAPI, SQLModel/SQLite, Pydantic, Uvicorn.
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Axios.
- **Tooling:** Docker Compose for local orchestration, pandas for batch imports.

## Repository Layout
- `backend/` – FastAPI service (`app/main.py`), SQLModel definitions, and the Excel import helper.
- `frontend/` – React/Vite single-page application (`src/App.tsx`, `src/api.ts`).
- `data/` – Persisted uploads and the expected location of the seed Excel workbook.
- `docker-compose.yml` – Combined development environment exposing FastAPI on `:8000` and Vite on `:5173`.

## Quick Start (Docker Compose)
1. Install Docker Desktop and Docker Compose.
2. From the repo root run `docker-compose up --build`.
3. Visit http://localhost:5173 for the UI; the API is available at http://localhost:8000/docs.
4. Uploaded evidence is written to `data/uploads/`, mounted into the backend container.

Use `Ctrl+C` to stop both services, or add `-d` to run detached. Re-run with `--build` when dependencies change.

## Backend Development Without Docker
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies: `pip install -r backend/requirements.txt` (run inside `backend/`).
3. Export optional env vars as needed (see Environment section below).
4. Start the API: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` from `backend/app`.

By default the service uses `sqlite:///./app.db` inside the working directory and stores uploads under `/data/uploads`. Ensure `data/uploads` exists or override `UPLOAD_DIR`.

## Frontend Development Without Docker
1. Install Node.js 18+ and pnpm/npm (examples use npm).
2. In `frontend/`, install dependencies: `npm install`.
3. Start the dev server: `npm run dev -- --host` and open the printed URL (typically http://localhost:5173).
4. Build static assets with `npm run build` and preview them via `npm run preview -- --host`.

The frontend expects `VITE_API_BASE` to point at the FastAPI server (defaults to `http://localhost:8000`).

## Environment Configuration
| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLModel database connection string. |
| `UPLOAD_DIR` | `/data/uploads` | Filesystem path for evidence storage. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed browser origins. |
| `VITE_API_BASE` | `http://localhost:8000` | Frontend API base URL (configure in `.env` or Docker). |

Create `.env` or `.env.local` files as needed; do not commit real credentials.

## Data Imports
The optional importer (`backend/app/import_excel.py`) can sync assessment objectives and methods from `data/{your xlsx}`:
```bash
python -m app.import_excel
```
Run the command from `backend/app/` with the virtual environment active. Columns `requirement_id`, `assessment_objectives`, and `assessment_methods` are required.


## Security Notes
- Evidence filenames are sanitized with timestamps, but ensure uploads are scanned before distribution.
- Keep sensitive spreadsheets out of version control; rely on example env values and local `.env` files.
- When changing Docker ports or volumes, update `docker-compose.yml` and call out data migrations that might affect `data/uploads`.


