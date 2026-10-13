# Specification: AI Company Brochure Generator

## 1. Objective
Transform the educational prototype from `week1/day5.ipynb` into a fullstack web application that automatically crawls a company's website, selectively fetches relevant secondary pages using Google Gemini AI, and generates polished, multi-audience marketing brochures (for customers/prospects, investors, and potential job applicants).

### Target Users
- **Marketers & Founders**: Rapidly draft sales one-pagers and market positioning profiles from any corporate domain.
- **Investors & Analysts**: Extract core value propositions, product offerings, leadership highlights, and market focus in seconds.
- **Recruiters & Candidates**: Generate tailored summaries emphasizing company mission, culture, and career opportunities.

---

## 2. Tech Stack & Dependencies

### Backend
- **Language**: Python 3.12+
- **Web Framework**: FastAPI (high performance, async support, auto OpenAPI docs)
- **ASGI Server**: Uvicorn
- **AI SDK**: `google-genai` (official Google GenAI SDK for Gemini 2.5 Flash / 1.5 Flash)
- **Web Scraping & Parsing**: `httpx` (async HTTP requests), `BeautifulSoup4` + `lxml`
- **Data Validation & Settings**: `pydantic` & `pydantic-settings`
- **Testing**: `pytest`, `pytest-asyncio`, `respx`

### Frontend
- **Framework**: React 18 / 19 with Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Lucide Icons
- **Markdown & Preview**: `react-markdown`, `remark-gfm`
- **Streaming**: Native browser EventSource / `fetch` SSE reader

---

## 3. Commands

### Backend Commands
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Run Development Server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run Tests
pytest tests/ -v --cov=backend

# Run Lint & Formatting
ruff check backend tests
```

### Frontend Commands
```bash
# Install dependencies
cd frontend && npm install

# Run Development Server
npm run dev

# Build for Production
npm run build

# Run Lint
npm run lint
```

---

## 4. Project Structure

```
brochure-generator-llm/
├── CAPABILITY-MAP.md              # Phase 0 Architecture map
├── SPEC.md                        # Phase 1 Formal specification
├── tasks/
│   ├── plan.md                    # Phase 2 Implementation plan
│   └── todo.md                    # Phase 3 Task checklist
├── docs/
│   ├── architecture.md            # Architecture & flow diagrams
│   └── api.md                     # API endpoints & SSE event spec
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entrypoint & router mount
│   ├── config.py                  # Environment config & validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py             # BrochureRequest schema
│   │   └── response.py            # Event & status schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py             # Async web crawler & link extractor
│   │   ├── ai_engine.py           # Gemini relevance filtering & generation
│   │   └── prompts.py             # System & user prompt templates
│   ├── routers/
│   │   ├── __init__.py
│   │   └── generate.py            # SSE streaming endpoint & health check
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── GeneratorForm.tsx
│   │   │   ├── StreamProgress.tsx
│   │   │   ├── BrochureViewer.tsx
│   │   │   └── ExportActions.tsx
│   │   ├── services/
│   │   │   └── api.ts             # SSE connection & event dispatcher
│   │   └── types/
│   │       └── index.ts
├── tests/
│   ├── test_crawler.py
│   ├── test_ai_engine.py
│   └── test_api.py
├── .env.example
├── README.md
└── .gitignore
```

---

## 5. Code Style & Conventions

- **Python**: PEP 8 standards, typed function signatures (`def crawl(url: str) -> CrawlResult:`), Pydantic schemas for all payloads, async-first for network I/O (`httpx.AsyncClient`).
- **TypeScript**: Strict mode enabled, functional components with hooks, typed interfaces for all props and backend events.
- **Error Handling**: Graceful degradation (e.g. if a sub-page fails to scrape, continue with landing page data and inform the client through an event).
- **Naming**: `snake_case` for Python functions/variables, `PascalCase` for React components and classes, `camelCase` for TypeScript variables/functions.

---

## 6. API & Event Streaming Contract

### `POST /api/generate/stream`
Request Payload:
```json
{
  "url": "https://example.com",
  "audience": "prospects", // "prospects" | "investors" | "candidates" | "general"
  "tone": "professional",   // "professional" | "energetic" | "minimalist"
  "max_subpages": 3
}
```

Server-Sent Events (`text/event-stream`):
1. `event: status` -> `{"step": "crawling_landing", "message": "Scraping landing page...", "progress": 15}`
2. `event: status` -> `{"step": "analyzing_links", "message": "Analyzing candidate links with Gemini...", "progress": 35}`
3. `event: links_selected` -> `{"links": ["https://example.com/about", "https://example.com/pricing"]}`
4. `event: status` -> `{"step": "crawling_subpages", "message": "Fetching selected subpages...", "progress": 60}`
5. `event: status` -> `{"step": "generating_brochure", "message": "Synthesizing brochure...", "progress": 80}`
6. `event: token` -> `{"chunk": "### Welcome to ExampleCorp..."}` (streamed text tokens)
7. `event: complete` -> `{"status": "completed", "total_pages": 3, "company_name": "ExampleCorp"}`
8. `event: error` -> `{"message": "Failed to scrape target domain."}`

---

## 7. Testing Strategy

- **Unit Tests**:
  - `test_crawler.py`: Test URL resolution (relative to absolute), HTML text cleaning, script/style removal, truncation limits.
  - `test_ai_engine.py`: Test prompt formatting, link relevance JSON parser, fallback handling when JSON is malformed.
- **Integration Tests**:
  - `test_api.py`: Test FastAPI endpoints, SSE event structure, validation errors for invalid URLs.
- **Mocking**: Use `respx` to mock external website responses and mock Gemini client calls in automated CI tests so tests do not consume Gemini API quota.

---

## 8. Boundaries

### Always Do
- Validate and normalize incoming URLs (ensure valid scheme `http`/`https` and prevent SSRF attacks against private networks like `localhost` or `127.0.0.1` / `169.254.x.x`).
- Enforce sensible text truncation and timeout limits on web scraping to avoid hanging requests or token context overflow.
- Handle Gemini API rate limits with retry/backoff or clean user-facing error messages.
- Provide comprehensive test coverage for core scraping and parsing logic.

### Ask First
- Changing core framework decisions (e.g. switching away from FastAPI or React).
- Adding heavy third-party dependencies.

### Never Do
- Never hardcode API keys in source code or commit `.env`.
- Never execute arbitrary user scripts from scraped website contents.
- Never crash the entire generation pipeline if an optional subpage returns a 404 or times out.

---

## 9. Success Criteria
1. Backend correctly scrapes the provided homepage and resolves all internal sub-links.
2. Gemini evaluates the links, returns the most relevant ones (e.g. About, Careers, Products/Pricing), and backend scrapes their contents.
3. Brochure is synthesized according to selected audience and tone, and streamed live via SSE into the React frontend.
4. User can read, copy, and export the resulting brochure as Markdown or PDF.
5. All automated unit and API tests pass.
