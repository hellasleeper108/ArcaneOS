# VibeJam Project Overview

This document provides a comprehensive overview of the VibeJam project, intended as a guide for Gemini AI interactions.

## Project Overview

VibeJam is a fantasy-themed backend service named ArcaneOS. It is built with Python and FastAPI, and it manages mystical AI "daemon" entities. The project also includes a TypeScript-based frontend and utilizes the Raindrop MCP SDK for daemon management.

The core functionality revolves around "spells," which are API endpoints for summoning, invoking, and banishing AI daemons. Each daemon (Claude, Gemini, LiquidMetal) has unique characteristics and roles.

### Key Technologies

*   **Backend:** Python, FastAPI, Pydantic, Uvicorn
*   **Frontend:** TypeScript, Tailwind CSS, Vitest
*   **Testing:** Pytest, Coverage.py
*   **SDKs:** @liquidmetal-ai/raindrop-framework, @modelcontextprotocol/sdk

### Architecture

The project follows a clean, modular architecture:

*   `app/`: The main FastAPI application, containing models, API routes, and services.
*   `core/`: Core components with minimal dependencies, such as the `VibeCompiler` for safe code execution and the `ArcaneEventBus` for WebSocket communication.
*   `ArcaneOS/ui/`: The frontend application.
*   `tests/`: Pytest tests for the backend.
*   `docs/`: Detailed documentation for various components.

## Building and Running

### Backend (Python/FastAPI)

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

### Frontend (TypeScript)

The frontend is located in the `ArcaneOS/ui` directory.

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Build the frontend:**
    ```bash
    npm run build
    ```

## Testing

### Backend

*   **Run all tests:**
    ```bash
    pytest -v
    ```

*   **Run tests with coverage:**
    ```bash
    pytest --cov=core --cov=app -v
    ```

### Frontend

*   **Run tests:**
    ```bash
    npm test
    ```

## Development Conventions

*   **Coding Style:** The project uses `prettier` for code formatting and `eslint` for linting in the frontend. The Python code appears to follow standard PEP 8 guidelines.
*   **Testing:** The project has a comprehensive test suite using `pytest` for the backend and `vitest` for the frontend.
*   **API Documentation:** The API is documented using OpenAPI, with Swagger UI available at `/grimoire` and ReDoc at `/arcane-docs` when the server is running.
