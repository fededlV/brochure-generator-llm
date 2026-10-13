# Task Checklist: AI Company Brochure Generator

## Phase 0 & Phase 1: Specifications (Completed)
- [x] Task 1: Create Phase 0 Capability Map
  - Acceptance: Capability map defining modules, boundaries, and build order is documented.
  - Verify: Reviewed in `CAPABILITY-MAP.md`.
  - Files: `CAPABILITY-MAP.md`
- [x] Task 2: Create Phase 1 Full Specification
  - Acceptance: Spec document covering Objective, Tech Stack, Commands, Structure, Style, Testing, Boundaries, and Success Criteria.
  - Verify: Reviewed in `SPEC.md`.
  - Files: `SPEC.md`
- [x] Task 3: Create Phase 2 Implementation Plan
  - Acceptance: Step-by-step phased plan with sequence diagrams and risk mitigation.
  - Verify: Reviewed in `tasks/plan.md`.
  - Files: `tasks/plan.md`

---

## Phase A: Core Crawler (`core-crawler`)
- [x] Task 4: Setup Backend Dependencies & Project Structure
  - Acceptance: `backend/requirements.txt` created with fastapi, uvicorn, google-genai, httpx, beautifulsoup4, lxml, pydantic, pydantic-settings, pytest, pytest-asyncio.
  - Verify: `pip install -r backend/requirements.txt` succeeds in python environment.
  - Files: `backend/requirements.txt`, `backend/__init__.py`
- [x] Task 5: Implement Core Web Crawler & Link Extractor
  - Acceptance: `backend/services/crawler.py` safely fetches HTML asynchronously, strips noise, parses page text, resolves relative URLs to absolute, filters out anchor/external fragments, and respects character limits.
  - Verify: Unit test passing with `pytest tests/test_crawler.py`.
  - Files: `backend/services/crawler.py`, `tests/test_crawler.py`

---

## Phase B: AI Engine with Gemini (`ai-engine`)
- [x] Task 6: Implement Environment Configuration & Validation
  - Acceptance: `backend/config.py` loads `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), validates key shape, and handles fallback gracefully.
  - Verify: Script imports and asserts valid settings without crashing.
  - Files: `backend/config.py`, `.env.example`
- [x] Task 7: Implement Prompt Templates & AI Service
  - Acceptance: `backend/services/prompts.py` and `backend/services/ai_engine.py` implement link relevance selection (JSON schema) and streaming brochure synthesis with audience/tone parameters.
  - Verify: Unit test with mocked Gemini response in `tests/test_ai_engine.py`.
  - Files: `backend/services/prompts.py`, `backend/services/ai_engine.py`, `tests/test_ai_engine.py`

---

## Phase C: Backend API & SSE Streaming (`backend-api`)
- [x] Task 8: Implement Request/Response Models and Router
  - Acceptance: `backend/models/request.py`, `backend/models/response.py`, and `backend/routers/generate.py` define models and the SSE streaming generator pipeline.
  - Verify: `curl -N http://localhost:8000/api/generate/stream` outputs SSE events.
  - Files: `backend/models/request.py`, `backend/models/response.py`, `backend/routers/generate.py`, `backend/main.py`
- [x] Task 9: Implement Health Check & API Tests
  - Acceptance: `GET /api/health` returns status; integration tests verify validation errors and event flow.
  - Verify: `pytest tests/test_api.py`.
  - Files: `tests/test_api.py`, `backend/routers/generate.py`

---

## Phase D: Frontend Application (`frontend-ui`)
- [x] Task 10: Initialize Vite + React + Tailwind Frontend
  - Acceptance: Vite React TypeScript app initialized with Tailwind CSS configured and compiling without errors.
  - Verify: `npm run build` succeeds in `frontend/`.
  - Files: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.js`, `frontend/src/*`
- [x] Task 11: Implement Frontend Components & State Management
  - Acceptance: `GeneratorForm`, `StreamProgress`, `BrochureViewer`, and `ExportActions` render cleanly with responsive layout and real-time SSE stream consumption.
  - Verify: Tested in browser / build succeeds with no TypeScript errors.
  - Files: `frontend/src/components/*`, `frontend/src/services/api.ts`, `frontend/src/App.tsx`

---

## Phase E: Documentation & Final Verification (`docs-devops`)
- [x] Task 12: Comprehensive Documentation & README
  - Acceptance: Complete project documentation in `README.md` and `docs/architecture.md`, detailing architecture, setup instructions, comparison with the original notebook, and API specifications.
  - Verify: Documentation links and markdown render properly.
  - Files: `README.md`, `docs/architecture.md`, `docs/api.md`
