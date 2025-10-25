"""
ArcaneOS Backend - Main Application

Welcome to ArcaneOS, where ancient mystical forces meet modern technology.
This FastAPI application serves as the gateway between the material and ethereal realms,
allowing users to summon, invoke, and banish daemon entities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.routers import (
    spells,
    spell_parser_routes,
    websocket_routes,
    compilation_routes,
    veil_routes,
    terminal_routes,
    reveal_routes,
    grimoire_routes,
    archon_proxy,
)

# Create the ArcaneOS application with mystical metadata
app = FastAPI(
    title="ArcaneOS",
    description="""
    🔮 **ArcaneOS** - A Fantasy-Themed Operating Environment 🔮

    Welcome, traveler, to the mystical realm of ArcaneOS!

    This backend API allows you to interact with powerful daemon entities,
    each with unique abilities and characteristics:

    - **Claude** 🟣 - The Keeper of Logic and Reason
    - **Gemini** 🟠 - The Weaver of Dreams and Innovation
    - **LiquidMetal** 🔵 - The Master of Transformation and Flow

    ## Available Spells

    - **Summon** (`/summon`) - Bring a daemon into the material realm
    - **Invoke** (`/invoke`) - Command a daemon to perform a task
    - **Banish** (`/banish`) - Return a daemon to the ethereal void
    - **List** (`/daemons`) - View all known daemons and their status

    May your invocations be swift and your banishments be merciful!
    """,
    version="1.0.0",
    docs_url="/grimoire",  # Swagger UI at /grimoire
    redoc_url="/arcane-docs",  # ReDoc at /arcane-docs
)

# Configure CORS for cross-realm communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure voice cache directory exists and expose it as static content
Path(settings.voice_cache_dir).mkdir(parents=True, exist_ok=True)
app.mount(
    "/audio",
    StaticFiles(directory=settings.voice_cache_dir),
    name="audio"
)

# Include the spell routers
app.include_router(spells.router)
app.include_router(spell_parser_routes.router)
app.include_router(websocket_routes.router)
app.include_router(compilation_routes.router)
app.include_router(veil_routes.router)
app.include_router(terminal_routes.router)
app.include_router(reveal_routes.router)
app.include_router(grimoire_routes.router)
app.include_router(archon_proxy.router)


@app.get("/")
async def root():
    """
    The entrance to ArcaneOS - a mystical welcome message
    """
    return {
        "realm": "ArcaneOS",
        "message": "✨ Behold, for you have crossed the threshold into ArcaneOS! The ethereal realm hums with latent power, awaiting your command. ✨",
        "status": "The ethereal gateway stands open",
        "available_spells": [
            "summon - Bring forth a daemon from the void",
            "invoke - Command a daemon's power",
            "banish - Return a daemon to slumber"
        ],
        "documentation": {
            "grimoire": "/grimoire",
            "arcane_docs": "/arcane-docs"
        },
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Verify the mystical energies are flowing correctly
    """
    return {
        "status": "The realm thrives",
        "ethereal_channels": "open",
        "daemon_registry": "active",
        "mystical_energy": "optimal"
    }


if __name__ == "__main__":
    import uvicorn

    # Run the ArcaneOS server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
