# Repository Guidelines

## Project Structure & Module Organization
- **ArcaneOS/core** – FastAPI backend modules (`archon_router.py`, `event_bus.py`, `audio_bus.py`, `safety.py`, `schemas.py`, `veil.py`, `grimoire.py`).  
- **ArcaneOS/daemons** – Executors for Claude, Gemini, and LiquidMetal (`*_exec.py`).  
- **ArcaneOS/ui** – React client (`src/` for components/lib, `public/` for static assets, `package.json`).  
- **ArcaneOS/tests** – Pytest suites (`test_archon.py`, `test_api.py`, etc.).  
- Root-level legacy shims under `app/` forward to the new `ArcaneOS.core` modules while FastAPI routing is migrated.

## Build, Test, and Development Commands
- **Backend**  
  - `pip install -r requirements.txt` – install FastAPI, pytest, coverage.  
  - `pytest ArcaneOS/tests --asyncio-mode=strict` – run backend unit/integration suites.  
  - `coverage run -m pytest ArcaneOS/tests && coverage report` – enforce ≥85 % coverage.  
- **Frontend**  
  - `cd ArcaneOS/ui && npm install` – install React/Tailwind deps.  
  - `npm run build` – production bundle with sensory sync assets.  
  - `npm test` – CRA test runner (Jest/RTL).

## Coding Style & Naming Conventions
- **Python**: Pydantic + FastAPI, 4-space indent, snake_case modules. Shared code lives in `ArcaneOS/core`.  
- **TypeScript/React**: Function components in PascalCase (`ArchonSigil.tsx`), hooks in camelCase (`useArchonSocket`). Keep shared utilities under `src/lib`.  
- Run `ruff` or `black` if introduced; otherwise follow existing formatting.

## Testing Guidelines
- Pytest is the primary framework; new tests belong under `ArcaneOS/tests`. Name files `test_*.py`.  
- Mock remote model calls (GPT-OSS, Claude, LiquidMetal) to keep tests deterministic.  
- Assert fantasy vs developer outputs explicitly (golden strings).  
- Log sanitizer checks (`REJECTED_PAYLOAD`) should be covered when adding safety rules.

## Commit & Pull Request Guidelines
- Commits: imperative mood, scoped prefixes when possible (e.g., `core:`, `ui:`). Group related changes; avoid multi-feature commits.  
- Pull Requests: include summary, test evidence (`pytest`, `npm run build`), linked issue, and screenshots/gifs for UI adjustments.  
- Ensure `/reveal` and veil toggles are exercised before merge; note any new feature flags or settings in the PR description.

## Security & Configuration Tips
- Keep `allow_shell` and `allow_net` false by default; update Archon safety if expanding capabilities.  
- ElevenLabs keys live in `.env`; never commit secrets.  
- Run `/reveal/restore` after developer debugging to re-enable fantasy presentation for demo environments.
