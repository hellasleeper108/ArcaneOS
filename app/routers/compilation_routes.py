"""
Compilation Routes for ArcaneOS VibeCompiler

These mystical endpoints allow you to compile and execute code with
fantasy-themed narration and ceremonial presentation.
"""

from fastapi import APIRouter, HTTPException
from app.models.compilation import (
    CompileRequest,
    CompileResponse,
    SupportedLanguagesResponse,
    LanguageInfo,
    NarrationEventResponse,
    CodeLanguage
)
from app.services.vibe_compiler import get_vibe_compiler, CompilationPhase
from app.services.arcane_event_bus import get_event_bus, SpellType
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/compile",
    tags=["Compilation"],
    responses={
        404: {"description": "The requested resource dwells not in this realm"},
        500: {"description": "Dark forces interfere with the compilation"}
    }
)


@router.post("/execute", response_model=CompileResponse)
async def compile_and_execute(request: CompileRequest):
    """
    🔥 COMPILE AND EXECUTE SPELL 🔥

    Transmutes your code into executable magic, narrating each step
    of the compilation and execution process with ceremonial flair.

    The VibeCompiler wraps real code execution in thematic presentation:
    - "Runes align..." during parsing
    - "Mana channels stabilizing..." during compilation
    - "The spell takes form..." during execution

    **Dry-Run Mode:**
    Set `dry_run: true` to validate without executing (safe for demos).

    **Supported Languages:**
    - Python (serpent magic)
    - JavaScript (lightning spells)
    - Bash (earth incantations)
    - Ruby (crystal rituals)
    - Go (steel conjurations)
    - Rust (iron ceremonies)

    **Safety Features:**
    - Timeouts to prevent infinite loops
    - Validation to catch dangerous patterns
    - Sandboxed execution environment

    Returns:
        Execution results with both literal output and styled narration
    """
    try:
        compiler = get_vibe_compiler()

        # Log compilation start
        logger.info(
            f"🔮 Compiling {request.language.value} code "
            f"({'dry-run' if request.dry_run else 'live execution'})"
        )

        # Compile and execute
        result = compiler.compile_and_execute(
            code=request.code,
            language=request.language,
            dry_run=request.dry_run,
            timeout=request.timeout
        )

        # Emit compilation event to event bus (if requested)
        if request.emit_events:
            event_bus = get_event_bus()
            asyncio.create_task(event_bus.emit_parse(
                spell_text=f"{request.language.value} code execution",
                success=result.success,
                parsed_action="compile_execute",
                daemon_name=None,
                description=(
                    f"✨ Code compilation {'succeeded' if result.success else 'failed'}! "
                    f"Language: {request.language.value}, "
                    f"Execution time: {result.execution_time:.3f}s "
                    f"{'[DRY RUN]' if request.dry_run else ''}"
                ),
                metadata={
                    "language": request.language.value,
                    "execution_time": result.execution_time,
                    "dry_run": request.dry_run,
                    "code_length": len(request.code),
                    "success": result.success
                }
            ))

        # Create fantasy-themed status message
        if result.success:
            if result.dry_run:
                message = (
                    f"✨ The {request.language.value} incantation is validated! "
                    "Safety protocols engaged - no actual execution performed. ✨"
                )
            else:
                message = (
                    f"✨ The spell manifests successfully! Your {request.language.value} code "
                    f"breathes life into the digital realm in {result.execution_time:.3f} seconds! ✨"
                )
        else:
            message = (
                f"✨ The {request.language.value} ritual falters! "
                "Dark energies disrupt the execution... ✨"
            )

        # Convert narration events to response models
        narration_responses = [
            NarrationEventResponse(
                phase=event.phase.value,
                message=event.message,
                timestamp=event.timestamp.isoformat(),
                details=event.details
            )
            for event in result.narration
        ]

        return CompileResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            narration=narration_responses,
            narration_text=result.get_narration_text(),
            language=result.language.value,
            dry_run=result.dry_run,
            message=message
        )

    except Exception as e:
        logger.error(f"Compilation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The compilation ritual has failed catastrophically: {str(e)}"
        )


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    📚 SUPPORTED LANGUAGES GRIMOIRE 📚

    Reveals all programming languages known to the VibeCompiler,
    each with its own elemental theme and mystical properties.

    Each language has:
    - A unique thematic element (serpent, lightning, earth, etc.)
    - Default timeout for safety
    - File extension for temporary artifacts

    Returns:
        List of all supported languages and their configurations
    """
    try:
        compiler = get_vibe_compiler()
        languages_data = compiler.get_supported_languages()

        languages = [
            LanguageInfo(**lang_data)
            for lang_data in languages_data
        ]

        return SupportedLanguagesResponse(
            status="success",
            message="✨ The grimoire reveals all known tongues of code... ✨",
            languages=languages,
            count=len(languages)
        )

    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve the grimoire: {str(e)}"
        )


@router.post("/dry-run", response_model=CompileResponse)
async def dry_run_compilation(request: CompileRequest):
    """
    🛡️ DRY-RUN COMPILATION 🛡️

    A safe way to test your code without actual execution.
    Perfect for demonstrations and validation.

    This endpoint forces dry-run mode regardless of the request setting,
    ensuring no code is actually executed. The compiler will:
    - Validate syntax and safety
    - Generate full narration
    - Return mock success output
    - Never execute the code

    Use this to:
    - Test the narration system
    - Validate code safety
    - Demo the VibeCompiler without risk
    - Preview the ceremonial experience

    Returns:
        Validation results with narration (no actual execution)
    """
    # Force dry-run mode
    request.dry_run = True

    # Use the same execute endpoint logic
    return await compile_and_execute(request)


@router.get("/example/{language}")
async def get_example_code(language: CodeLanguage):
    """
    📖 EXAMPLE SPELLS 📖

    Provides example code snippets for each supported language.
    Use these as templates for your own mystical compilations!

    Args:
        language: The programming language for the example

    Returns:
        Example code snippet with description
    """
    examples = {
        CodeLanguage.PYTHON: {
            "code": "# Python serpent magic\nfor i in range(3):\n    print(f'✨ Spell iteration {i+1} complete!')\n\nprint('The Python ritual concludes!')",
            "description": "A simple loop demonstrating Python's serpentine flow"
        },
        CodeLanguage.JAVASCRIPT: {
            "code": "// JavaScript lightning spell\nfor (let i = 0; i < 3; i++) {\n    console.log(`⚡ Lightning strike ${i+1}!`);\n}\nconsole.log('The storm subsides...');",
            "description": "A loop that channels JavaScript's electric energy"
        },
        CodeLanguage.BASH: {
            "code": "#!/bin/bash\n# Bash earth incantation\necho \"🌍 The earth trembles...\"\nfor i in 1 2 3; do\n    echo \"Tremor $i detected!\"\ndone\necho \"The earth settles.\"",
            "description": "A shell script invoking the power of earth"
        },
        CodeLanguage.RUBY: {
            "code": "# Ruby crystal ritual\n3.times do |i|\n  puts \"💎 Crystal #{i+1} resonates!\"\nend\nputs \"The crystals harmonize...\"",
            "description": "A Ruby loop showcasing crystalline elegance"
        },
        CodeLanguage.GO: {
            "code": "package main\nimport \"fmt\"\n\nfunc main() {\n    fmt.Println(\"⚙️ Steel gears engage...\")\n    for i := 0; i < 3; i++ {\n        fmt.Printf(\"Gear %d turning!\\n\", i+1)\n    }\n    fmt.Println(\"Machinery complete.\")\n}",
            "description": "A Go program demonstrating steel-forged efficiency"
        },
        CodeLanguage.RUST: {
            "code": "fn main() {\n    println!(\"🔨 Iron forges kindle...\");\n    for i in 0..3 {\n        println!(\"Forge {} blazing!\", i+1);\n    }\n    println!(\"The iron is tempered.\");\n}",
            "description": "A Rust program showing iron-clad memory safety"
        }
    }

    example = examples.get(language)
    if not example:
        raise HTTPException(
            status_code=404,
            detail=f"No example available for {language.value}"
        )

    return {
        "status": "success",
        "language": language.value,
        "message": f"✨ Behold, an example of {language.value} magic! ✨",
        "example": example
    }
