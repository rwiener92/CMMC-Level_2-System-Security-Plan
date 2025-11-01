# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CMMC (Cybersecurity Maturity Model Certification) Level 2 compliance management application. It helps organizations track security control requirements, implementation status, C3PAO assessment findings, and supporting evidence. The application is split into a FastAPI backend and React/Vite frontend, both containerized with Docker.

## Development Commands

### Full Stack (Docker)
```bash
# Start both services with hot reload
docker-compose up --build

# Backend runs on http://localhost:8000
# Frontend runs on http://localhost:5173
```

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Only
```bash
cd frontend
npm install
npm run dev -- --host      # Development server
npm run build              # Production build
npm run preview -- --host  # Preview production build
```

### Data Import
```bash
# Import assessment data from Excel (run from backend/app directory)
python -m import_excel
```

## Architecture

### Backend (FastAPI + SQLModel)

**Entry Point:** `backend/app/main.py` (~1970 lines)
- All SQLModel table definitions (Control, TextLog, Evidence)
- All API routes defined inline (no separate router files)
- Embedded seed data (SEED array contains ~110 CMMC L2 controls)
- Database: SQLite with path from `DATABASE_URL` env var
- File uploads stored in path from `UPLOAD_DIR` env var

**Key Models:**
- `Control`: Core CMMC requirements with fields for requirement_id, domain, title, statement, assessment details, c3pao_finding, self_impl_status
- `TextLog`: Timestamped notes for "provider" and "solution" documentation
- `Evidence`: File attachments linked to requirements

**API Endpoints:**
- `GET /health` - Health check
- `GET /controls` - List controls (supports ?q=search&domain=filter)
- `GET /controls/{control_id}` - Get single control
- `PATCH /controls/{control_id}` - Update c3pao_finding or self_impl_status
- `GET /dashboard` - Aggregate stats for filter badges
- `POST /controls/{requirement_id}/textlog` - Add provider/solution note
- `GET /controls/{requirement_id}/textlog` - List notes (filter by ?kind=)
- `DELETE /textlog/{log_id}` - Delete note
- `POST /controls/{requirement_id}/evidence` - Upload files (multipart/form-data)
- `GET /controls/{requirement_id}/evidence` - List evidence
- `DELETE /evidence/{evidence_id}` - Delete evidence file

**Import Utility:** `backend/app/import_excel.py`
- Reads `/data/CMMC L2 SSP.xlsx`
- Updates assessment_objectives and assessment_methods fields
- Expected columns: requirement_id, assessment_objectives, assessment_methods

### Frontend (React + TypeScript + Vite)

**Structure:**
- `src/main.tsx` - Entry point
- `src/App.tsx` - Single-file React component (~350 lines)
- `src/api.ts` - Axios client and TypeScript API functions
- `src/index.css` - Global styles
- `tailwind.config.js` - Tailwind configuration

**Component Architecture:**
The entire UI is in `App.tsx` with two main views:
1. **List View**: Table of all controls with search, domain dropdown, and two sets of filter badges (C3PAO findings and Implementation status). Inline dropdowns for quick status updates.
2. **Detail View**: Drill-down showing full requirement text, discussion, assessment info, plus sections for logging Control Provider notes, Solution descriptions, and uploading Evidence files.

**State Management:**
- Local React state (no Redux/Context)
- Debounced search (250ms timeout)
- Filter state for C3PAO findings (MET, NOT_MET, NA, UNASSIGNED) and Implementation status (Implemented, Partially Implemented, etc.)

**API Client (`src/api.ts`):**
- Base URL from `VITE_API_BASE` environment variable
- All endpoints wrapped in TypeScript functions
- Control type definition matches backend SQLModel

### Data Flow

1. Backend seeds database from hardcoded SEED array on startup if tables are empty
2. Frontend fetches controls via `/controls` endpoint with optional search/domain filters
3. Client-side filtering applied for C3PAO/Implementation status badges
4. Status changes immediately PATCH to backend and refetch to update dashboard counts
5. Detail view uses separate endpoints for textlog and evidence CRUD operations
6. All file uploads stored in Docker volume `./data:/data` mounted to both services

## Coding Conventions

**Backend:**
- PEP 8 with 4-space indentation
- SQLModel classes in PascalCase (Control, TextLog, Evidence)
- Snake_case for function names and variables
- Dependency injection with `Depends(get_session)` pattern
- All routes currently in main.py (add new routers there if needed)

**Frontend:**
- Functional React components
- PascalCase for component files (App.tsx)
- camelCase for functions, variables, hooks
- Tailwind utility classes preferred over custom CSS
- TypeScript strict mode
- Co-locate component-specific logic within component functions

## Environment Variables

**Backend:**
- `DATABASE_URL` - SQLite path (default: `sqlite:///./app.db`)
- `UPLOAD_DIR` - File storage path (default: `/data/uploads`)
- `CORS_ORIGINS` - Comma-separated origins (default: `http://localhost:5173`)

**Frontend:**
- `VITE_API_BASE` - Backend URL (default: `http://localhost:8000`)

## Testing

No automated tests currently exist. When adding tests:
- Backend: Use pytest in `backend/tests/`, name files `test_<feature>.py`
- Frontend: Use vitest in `frontend/src/__tests__/`, name files `<Component>.test.tsx`
  - Install with: `npm install -D vitest @testing-library/react @testing-library/jest-dom`

## Data Persistence

- SQLite database persisted in Docker volume `backend_db:/app`
- Uploaded evidence files in `./data/uploads` (bind mount)
- Seed Excel workbook expected at `./data/CMMC L2 SSP.xlsx`

## Important Notes

- All 110+ CMMC L2 controls are hardcoded in the SEED array in main.py
- The backend creates tables and seeds data automatically on startup
- File uploads are validated and sanitized before writing to disk
- Frontend uses debounced search to reduce API calls
- Dashboard endpoint computes counts on-demand (not cached)
