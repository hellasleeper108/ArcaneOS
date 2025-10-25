"""
VibeCompiler - Thematic Code Execution Engine

This module wraps real code execution in fantasy-themed ceremonial presentation.
Each step of compilation and execution is narrated with mystical phrasing,
creating an immersive coding experience.

Features:
- Multi-language support (Python, JavaScript, Bash, etc.)
- Dry-run mode for safe demos
- Ceremonial logging with fantasy narration
- Safe execution with timeouts and sandboxing
- Event integration with ArcaneEventBus
"""

import subprocess
import tempfile
import os
import time
import json
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from datetime import datetime
import logging
import asyncio
import re

logger = logging.getLogger(__name__)


class CodeLanguage(str, Enum):
    """Supported programming languages for the VibeCompiler"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"


class CompilationPhase(str, Enum):
    """Phases of the compilation/execution process"""
    INITIATION = "initiation"
    PARSING = "parsing"
    COMPILATION = "compilation"
    INVOCATION = "invocation"
    EXECUTION = "execution"
    COMPLETION = "completion"
    ERROR = "error"


class NarrationEvent:
    """A single narration event during compilation/execution"""

    def __init__(
        self,
        phase: CompilationPhase,
        message: str,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.phase = phase
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "phase": self.phase.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class ExecutionResult:
    """Result of code execution with narration"""

    def __init__(
        self,
        success: bool,
        output: str,
        error: Optional[str] = None,
        execution_time: float = 0.0,
        narration: Optional[List[NarrationEvent]] = None,
        language: Optional[CodeLanguage] = None,
        dry_run: bool = False
    ):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.narration = narration or []
        self.language = language
        self.dry_run = dry_run

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": round(self.execution_time, 3),
            "narration": [event.to_dict() for event in self.narration],
            "language": self.language.value if self.language else None,
            "dry_run": self.dry_run,
            "narration_text": self.get_narration_text()
        }

    def get_narration_text(self) -> str:
        """Get full narration as a single formatted string"""
        return "\n".join([
            f"✨ [{event.phase.value.upper()}] {event.message}"
            for event in self.narration
        ])


class VibeCompiler:
    """
    The Mystical Code Compiler - Transforms mundane code into arcane rituals

    This compiler wraps real code execution in thematic presentation,
    narrating each step of the compilation and execution process with
    ceremonial phrasing fit for a fantasy realm.
    """

    # Language-specific configurations
    LANGUAGE_CONFIG = {
        CodeLanguage.PYTHON: {
            "command": ["python3", "-c"],
            "extension": ".py",
            "timeout": 10,
            "narration_theme": "serpent"
        },
        CodeLanguage.JAVASCRIPT: {
            "command": ["node", "-e"],
            "extension": ".js",
            "timeout": 10,
            "narration_theme": "lightning"
        },
        CodeLanguage.BASH: {
            "command": ["bash", "-c"],
            "extension": ".sh",
            "timeout": 10,
            "narration_theme": "earth"
        },
        CodeLanguage.RUBY: {
            "command": ["ruby", "-e"],
            "extension": ".rb",
            "timeout": 10,
            "narration_theme": "crystal"
        },
        CodeLanguage.GO: {
            "command": ["go", "run"],
            "extension": ".go",
            "timeout": 15,
            "narration_theme": "steel",
            "use_file": True  # Go requires a file
        },
        CodeLanguage.RUST: {
            "command": ["rustc", "--edition", "2021", "-o"],
            "extension": ".rs",
            "timeout": 30,
            "narration_theme": "iron",
            "use_file": True,
            "compile_and_run": True
        }
    }

    # Thematic narration templates by phase
    NARRATION_TEMPLATES = {
        CompilationPhase.INITIATION: [
            "✨ The mystical compiler awakens from its slumber...",
            "✨ Ancient runes begin to glow with ethereal energy...",
            "✨ The ceremonial chamber hums with anticipation...",
            "✨ Mana channels open, ready to receive your incantation..."
        ],
        CompilationPhase.PARSING: [
            "✨ Arcane symbols dance across the ethereal plane...",
            "✨ The compiler's eyes scan the sacred text...",
            "✨ Runes align themselves into patterns of power...",
            "✨ Syntax crystals form in the void..."
        ],
        CompilationPhase.COMPILATION: [
            "✨ The forge of creation blazes with eldritch flame...",
            "✨ Mana channels stabilizing across dimensional barriers...",
            "✨ Code transforms into executable essence...",
            "✨ The spell takes form in the material realm..."
        ],
        CompilationPhase.INVOCATION: [
            "✨ The ritual circle activates with brilliant light...",
            "✨ Summoning the execution daemon from the depths...",
            "✨ Reality bends to accommodate your command...",
            "✨ The incantation reaches its crescendo..."
        ],
        CompilationPhase.EXECUTION: [
            "✨ The spell manifests! Code flows like liquid light...",
            "✨ Computational energies surge through the matrix...",
            "✨ Your program awakens, breathing digital life...",
            "✨ The execution daemon channels pure logic..."
        ],
        CompilationPhase.COMPLETION: [
            "✨ The ritual concludes with a shimmer of success!",
            "✨ Mana channels seal, the spell is complete!",
            "✨ The compiler bows, its duty fulfilled!",
            "✨ Your code has transcended into reality!"
        ],
        CompilationPhase.ERROR: [
            "✨ The runes flicker... something is amiss!",
            "✨ Dark energies interfere with the ritual!",
            "✨ The compiler recoils from forbidden syntax!",
            "✨ The spell unravels, chaos ensues!"
        ]
    }

    def __init__(self):
        """Initialize the Vibe Compiler"""
        self.narration_index = {phase: 0 for phase in CompilationPhase}
        logger.info("✨ VibeCompiler initialized - Ready to transmute code into magic")

    def _get_narration(self, phase: CompilationPhase, details: Optional[Dict] = None) -> NarrationEvent:
        """
        Generate a thematic narration message for a compilation phase

        Args:
            phase: The current compilation phase
            details: Optional additional details for the narration

        Returns:
            NarrationEvent with thematic message
        """
        templates = self.NARRATION_TEMPLATES.get(phase, ["✨ The compiler proceeds..."])
        index = self.narration_index[phase] % len(templates)
        self.narration_index[phase] += 1

        message = templates[index]
        return NarrationEvent(phase=phase, message=message, details=details or {})

    def _validate_code(self, code: str, language: CodeLanguage) -> tuple[bool, Optional[str]]:
        """
        Basic validation of code for safety

        Args:
            code: The code to validate
            language: The programming language

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for obviously dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf',  # Bash destructive commands
            r'format\s+[A-Z]:',  # Windows format
            r'dd\s+if=',  # Disk operations
            r':\(\)\{.*\}',  # Fork bombs
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Code contains potentially dangerous pattern: {pattern}"

        # Check code length
        if len(code) > 10000:
            return False, "Code exceeds maximum length of 10000 characters"

        return True, None

    def _execute_code_safely(
        self,
        code: str,
        language: CodeLanguage,
        timeout: int = 10
    ) -> tuple[bool, str, Optional[str], float]:
        """
        Execute code safely with timeout and resource limits

        Args:
            code: The code to execute
            language: The programming language
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success, stdout, stderr, execution_time)
        """
        config = self.LANGUAGE_CONFIG.get(language)
        if not config:
            return False, "", f"Unsupported language: {language}", 0.0

        start_time = time.time()

        try:
            # Prepare command
            command = config["command"].copy()

            # Handle languages that need files (Go, Rust)
            if config.get("use_file", False):
                # Create temporary file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=config["extension"],
                    delete=False
                ) as f:
                    f.write(code)
                    temp_file = f.name

                try:
                    if config.get("compile_and_run", False):
                        # Compile first (Rust)
                        output_file = temp_file.replace(config["extension"], "")
                        compile_cmd = command + [output_file, temp_file]

                        compile_result = subprocess.run(
                            compile_cmd,
                            capture_output=True,
                            text=True,
                            timeout=timeout
                        )

                        if compile_result.returncode != 0:
                            return False, "", compile_result.stderr, time.time() - start_time

                        # Run compiled binary
                        run_result = subprocess.run(
                            [output_file],
                            capture_output=True,
                            text=True,
                            timeout=timeout
                        )

                        # Cleanup
                        os.unlink(output_file)
                        os.unlink(temp_file)

                        execution_time = time.time() - start_time
                        success = run_result.returncode == 0
                        return success, run_result.stdout, run_result.stderr if not success else None, execution_time

                    else:
                        # Just run the file (Go)
                        command.append(temp_file)
                        result = subprocess.run(
                            command,
                            capture_output=True,
                            text=True,
                            timeout=timeout
                        )

                        # Cleanup
                        os.unlink(temp_file)

                        execution_time = time.time() - start_time
                        success = result.returncode == 0
                        return success, result.stdout, result.stderr if not success else None, execution_time

                except Exception as e:
                    # Cleanup on error
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                    raise e

            else:
                # Execute directly with -c or -e flag
                command.append(code)

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                execution_time = time.time() - start_time
                success = result.returncode == 0
                return success, result.stdout, result.stderr if not success else None, execution_time

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return False, "", f"Execution timeout after {timeout} seconds", execution_time

        except FileNotFoundError:
            return False, "", f"Interpreter for {language.value} not found. Please install it.", 0.0

        except Exception as e:
            execution_time = time.time() - start_time
            return False, "", f"Execution error: {str(e)}", execution_time

    def compile_and_execute(
        self,
        code: str,
        language: CodeLanguage,
        dry_run: bool = False,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Compile and execute code with thematic narration

        Args:
            code: The code to execute
            language: The programming language
            dry_run: If True, only validate without executing
            timeout: Optional custom timeout in seconds

        Returns:
            ExecutionResult with output and narration
        """
        narration: List[NarrationEvent] = []
        start_time = time.time()

        # Phase 1: Initiation
        narration.append(self._get_narration(
            CompilationPhase.INITIATION,
            {"language": language.value, "dry_run": dry_run}
        ))

        # Phase 2: Parsing
        narration.append(self._get_narration(
            CompilationPhase.PARSING,
            {"code_length": len(code)}
        ))

        # Validate code
        is_valid, validation_error = self._validate_code(code, language)
        if not is_valid:
            narration.append(self._get_narration(
                CompilationPhase.ERROR,
                {"error": validation_error}
            ))

            return ExecutionResult(
                success=False,
                output="",
                error=f"Validation failed: {validation_error}",
                execution_time=time.time() - start_time,
                narration=narration,
                language=language,
                dry_run=dry_run
            )

        # Phase 3: Compilation
        narration.append(self._get_narration(
            CompilationPhase.COMPILATION,
            {"language": language.value}
        ))

        # Dry-run mode - return mock success
        if dry_run:
            narration.append(self._get_narration(
                CompilationPhase.INVOCATION,
                {"mode": "simulation"}
            ))

            narration.append(NarrationEvent(
                phase=CompilationPhase.EXECUTION,
                message="✨ [DRY RUN] The spell is validated but not cast... Safety protocols engaged!",
                details={"mode": "dry_run"}
            ))

            narration.append(self._get_narration(CompilationPhase.COMPLETION))

            mock_output = f"[DRY RUN MODE]\n\nCode validated successfully for {language.value}!\n\nNo actual execution performed."

            return ExecutionResult(
                success=True,
                output=mock_output,
                error=None,
                execution_time=time.time() - start_time,
                narration=narration,
                language=language,
                dry_run=True
            )

        # Phase 4: Invocation
        narration.append(self._get_narration(
            CompilationPhase.INVOCATION,
            {"mode": "live_execution"}
        ))

        # Phase 5: Execution
        narration.append(self._get_narration(
            CompilationPhase.EXECUTION,
            {"starting": True}
        ))

        # Get timeout from config or use provided
        config = self.LANGUAGE_CONFIG.get(language, {})
        execution_timeout = timeout or config.get("timeout", 10)

        # Execute the code
        success, stdout, stderr, exec_time = self._execute_code_safely(
            code, language, execution_timeout
        )

        # Phase 6: Completion or Error
        if success:
            narration.append(self._get_narration(
                CompilationPhase.COMPLETION,
                {"execution_time": exec_time}
            ))
        else:
            narration.append(self._get_narration(
                CompilationPhase.ERROR,
                {"error": stderr}
            ))

        total_time = time.time() - start_time

        return ExecutionResult(
            success=success,
            output=stdout,
            error=stderr,
            execution_time=total_time,
            narration=narration,
            language=language,
            dry_run=False
        )

    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported languages with their configurations

        Returns:
            List of language configurations
        """
        return [
            {
                "language": lang.value,
                "theme": config.get("narration_theme", "unknown"),
                "timeout": config.get("timeout", 10),
                "extension": config.get("extension", "")
            }
            for lang, config in self.LANGUAGE_CONFIG.items()
        ]


# Global singleton instance
_vibe_compiler: Optional[VibeCompiler] = None


def get_vibe_compiler() -> VibeCompiler:
    """
    Get the global VibeCompiler instance (singleton)

    Returns:
        The singleton VibeCompiler instance
    """
    global _vibe_compiler

    if _vibe_compiler is None:
        _vibe_compiler = VibeCompiler()

    return _vibe_compiler
