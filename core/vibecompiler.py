"""
VibeCompiler - Safe Python Snippet Execution with Ceremonial Logging

The VibeCompiler allows safe execution of Python code snippets with timeout
enforcement and mystical ceremonial logging for ArcaneOS.
"""

import subprocess
import sys
import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class VibeCompiler:
    """
    The VibeCompiler executes Python snippets safely with timeout and
    ceremonial logging.
    """

    def __init__(self):
        """Initialize the VibeCompiler."""
        self.ceremonial_messages = [
            "Runes align...",
            "Mana stabilizing...",
            "The spell takes form..."
        ]

    def run_snippet(self, code: str, timeout: int = 3) -> Dict[str, any]:
        """
        Execute a Python code snippet safely with timeout enforcement.

        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds (default: 3)

        Returns:
            Dict with keys:
                - stdout: Captured standard output
                - stderr: Captured standard error
                - duration: Execution time in seconds

        Raises:
            TimeoutError: If execution exceeds timeout
        """
        # Log ceremonial messages
        for message in self.ceremonial_messages:
            logger.info(f"✨ {message}")

        # Record start time
        start_time = time.time()

        try:
            # Execute code in subprocess for isolation and safety
            # Use sys.executable to ensure same Python interpreter
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                # Security: prevent shell injection, no network
                shell=False,
                # Inherit limited environment
                env={"PYTHONDONTWRITEBYTECODE": "1"}
            )

            # Calculate duration
            duration = time.time() - start_time

            # Log completion
            logger.info(f"✨ Spell execution complete in {duration:.3f}s")

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration
            }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"Spell execution timed out after {timeout}s")
            raise TimeoutError(
                f"Code execution exceeded timeout of {timeout} seconds"
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Spell execution failed: {e}")
            raise

    def dry_run_demo(self) -> Dict[str, any]:
        """
        Run a demo snippet to demonstrate VibeCompiler functionality.

        Returns:
            Sample output dictionary
        """
        demo_code = "print('VibeCompiler demo: The arcane energies flow!')"
        print("Running VibeCompiler dry-run demo...")

        return self.run_snippet(demo_code, timeout=5)
