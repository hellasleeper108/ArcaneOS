"""
Tests for VibeCompiler

Validates safe Python snippet execution with timeout enforcement.
"""

import pytest
import sys
import os

# Add parent directory to path to import core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.vibecompiler import VibeCompiler


def test_vibecompiler_runs():
    """
    Test that VibeCompiler can execute a simple snippet and capture output.

    Validates:
    - Simple print statement executes successfully
    - stdout contains expected output
    - Result contains required keys
    """
    compiler = VibeCompiler()

    # Execute simple print statement
    result = compiler.run_snippet("print('ok')")

    # Validate result structure
    assert "stdout" in result, "Result should contain 'stdout' key"
    assert "stderr" in result, "Result should contain 'stderr' key"
    assert "duration" in result, "Result should contain 'duration' key"

    # Validate output
    assert "ok" in result["stdout"], "stdout should contain 'ok'"
    assert result["stdout"].strip() == "ok", "stdout should be exactly 'ok'"

    # Validate duration is reasonable
    assert isinstance(result["duration"], float), "duration should be a float"
    assert result["duration"] > 0, "duration should be positive"
    assert result["duration"] < 2, "simple print should complete quickly"

    print("✓ VibeCompiler runs test passed")


def test_vibecompiler_timeout():
    """
    Test that VibeCompiler enforces timeout correctly.

    Validates:
    - Code exceeding timeout raises TimeoutError
    - Timeout is enforced within reasonable bounds
    """
    compiler = VibeCompiler()

    # Code that sleeps longer than timeout
    slow_code = """
import time
time.sleep(5)
print('should not reach here')
"""

    # Should raise TimeoutError
    with pytest.raises(TimeoutError) as exc_info:
        compiler.run_snippet(slow_code, timeout=1)

    # Validate error message
    assert "timeout" in str(exc_info.value).lower(), \
        "Error message should mention timeout"

    print("✓ VibeCompiler timeout test passed")


def test_vibecompiler_captures_stderr():
    """
    Test that VibeCompiler captures stderr output.

    Validates:
    - stderr is captured correctly
    - errors are handled gracefully
    """
    compiler = VibeCompiler()

    # Code that writes to stderr
    code = """
import sys
sys.stderr.write('error message')
"""

    result = compiler.run_snippet(code)

    assert "error message" in result["stderr"], \
        "stderr should contain error message"

    print("✓ VibeCompiler stderr capture test passed")


def test_vibecompiler_returns_both_outputs():
    """
    Test that VibeCompiler captures both stdout and stderr.

    Validates:
    - Both output streams are captured simultaneously
    """
    compiler = VibeCompiler()

    # Code that writes to both streams
    code = """
import sys
print('standard output')
sys.stderr.write('error output')
"""

    result = compiler.run_snippet(code)

    assert "standard output" in result["stdout"], \
        "stdout should contain standard output"
    assert "error output" in result["stderr"], \
        "stderr should contain error output"

    print("✓ VibeCompiler dual output test passed")


def test_vibecompiler_dry_run_demo():
    """
    Test the dry_run_demo method.

    Validates:
    - Demo runs successfully
    - Returns expected structure
    """
    compiler = VibeCompiler()

    result = compiler.dry_run_demo()

    assert "stdout" in result
    assert "stderr" in result
    assert "duration" in result
    assert "VibeCompiler demo" in result["stdout"]

    print("✓ VibeCompiler dry_run_demo test passed")


if __name__ == "__main__":
    # Run tests directly
    print("\n" + "=" * 70)
    print("  VIBECOMPILER - VALIDATION TESTS")
    print("=" * 70 + "\n")

    try:
        test_vibecompiler_runs()
        test_vibecompiler_timeout()
        test_vibecompiler_captures_stderr()
        test_vibecompiler_returns_both_outputs()
        test_vibecompiler_dry_run_demo()

        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
