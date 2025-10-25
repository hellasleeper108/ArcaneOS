# VibeCompiler Documentation

## Overview

The **VibeCompiler** is a safe Python code execution engine with timeout enforcement and ceremonial logging. It allows you to run Python snippets in an isolated subprocess with comprehensive safety measures.

## Features

- **Safe Execution**: Runs code in subprocess isolation (no shell, no network access)
- **Timeout Enforcement**: Configurable execution timeout (default: 3 seconds)
- **Ceremonial Logging**: Fantasy-themed execution messages
- **Output Capture**: Captures both stdout and stderr
- **Duration Tracking**: Records execution time in seconds
- **Built-in Modules Only**: No external dependencies required

## Installation

The VibeCompiler is part of the core ArcaneOS modules:

```python
from core.vibecompiler import VibeCompiler
```

## Basic Usage

### Simple Execution

```python
from core.vibecompiler import VibeCompiler

compiler = VibeCompiler()

# Execute a simple snippet
result = compiler.run_snippet("print('Hello, world!')")

print(result)
# Output:
# {
#   "stdout": "Hello, world!\n",
#   "stderr": "",
#   "duration": 0.005
# }
```

### With Custom Timeout

```python
# Execute with 5-second timeout
result = compiler.run_snippet("""
import time
time.sleep(2)
print('Done!')
""", timeout=5)

print(f"Execution took {result['duration']:.3f}s")
# Output: Execution took 2.005s
```

### Handling Errors

```python
# Code with errors will capture stderr
result = compiler.run_snippet("""
import sys
print('Starting...')
sys.stderr.write('Warning: Something happened\\n')
print('Finished!')
""")

print(f"stdout: {result['stdout']}")
# Output: stdout: Starting...
#                 Finished!

print(f"stderr: {result['stderr']}")
# Output: stderr: Warning: Something happened
```

## API Reference

### Class: VibeCompiler

#### `__init__()`

Initialize the VibeCompiler.

**Parameters:** None

**Example:**
```python
compiler = VibeCompiler()
```

#### `run_snippet(code: str, timeout: int = 3) -> Dict[str, any]`

Execute a Python code snippet safely with timeout enforcement.

**Parameters:**
- `code` (str): The Python code to execute
- `timeout` (int, optional): Maximum execution time in seconds (default: 3)

**Returns:**
Dictionary with keys:
- `stdout` (str): Captured standard output
- `stderr` (str): Captured standard error
- `duration` (float): Execution time in seconds

**Raises:**
- `TimeoutError`: If execution exceeds timeout

**Example:**
```python
result = compiler.run_snippet("print('test')", timeout=5)
```

#### `dry_run_demo() -> Dict[str, any]`

Run a demo snippet to demonstrate VibeCompiler functionality.

**Returns:**
Dictionary with stdout, stderr, and duration

**Example:**
```python
result = compiler.dry_run_demo()
print(result['stdout'])
# Output: VibeCompiler demo: The arcane energies flow!
```

## Ceremonial Logging

The VibeCompiler logs ceremonial messages during execution:

```
✨ Runes align...
✨ Mana stabilizing...
✨ The spell takes form...
✨ Spell execution complete in 0.005s
```

These messages are logged using Python's logging system and can be viewed in `arcane_log.txt` or the console.

## Security Features

### Subprocess Isolation

Code runs in a completely isolated subprocess:
- No access to parent process memory
- No access to file system (beyond Python's normal permissions)
- No network access
- No shell execution (`shell=False`)

### Timeout Protection

Every execution is protected by a timeout:
- Prevents infinite loops
- Prevents long-running operations
- Raises `TimeoutError` if exceeded

```python
try:
    result = compiler.run_snippet("""
import time
time.sleep(10)  # Will timeout after 3 seconds
""", timeout=3)
except TimeoutError as e:
    print(f"Execution timed out: {e}")
```

### Limited Environment

The subprocess runs with minimal environment variables:
- `PYTHONDONTWRITEBYTECODE=1` - Prevents .pyc file creation
- No custom PATH or other environment variables

## Examples

### Example 1: Mathematical Computation

```python
code = """
import math

# Calculate fibonacci numbers
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

for i in range(10):
    print(f"fib({i}) = {fib(i)}")
"""

result = compiler.run_snippet(code, timeout=5)
print(result['stdout'])
# Output:
# fib(0) = 0
# fib(1) = 1
# fib(2) = 1
# fib(3) = 2
# ...
```

### Example 2: Data Processing

```python
code = """
import json

data = {
    'users': [
        {'name': 'Alice', 'score': 95},
        {'name': 'Bob', 'score': 87},
        {'name': 'Charlie', 'score': 92}
    ]
}

# Calculate average score
total = sum(user['score'] for user in data['users'])
average = total / len(data['users'])

print(f"Average score: {average:.2f}")
"""

result = compiler.run_snippet(code)
print(result['stdout'])
# Output: Average score: 91.33
```

### Example 3: Error Handling

```python
code = """
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
"""

result = compiler.run_snippet(code)
print(result['stdout'])
# Output: Cannot divide by zero!
```

### Example 4: Timeout Handling

```python
import logging

logging.basicConfig(level=logging.INFO)

code = """
import time
for i in range(10):
    print(f"Iteration {i}")
    time.sleep(1)
"""

try:
    result = compiler.run_snippet(code, timeout=3)
except TimeoutError:
    print("Code execution exceeded 3 second timeout")
```

## Testing

The VibeCompiler includes comprehensive tests:

```bash
# Run all VibeCompiler tests
pytest tests/test_vibecompiler.py -v

# Run specific tests
pytest tests/test_vibecompiler.py::test_vibecompiler_runs -v
pytest tests/test_vibecompiler.py::test_vibecompiler_timeout -v
```

### Test Coverage

1. **test_vibecompiler_runs** - Basic execution and output capture
2. **test_vibecompiler_timeout** - Timeout enforcement
3. **test_vibecompiler_captures_stderr** - Error stream capture
4. **test_vibecompiler_returns_both_outputs** - Dual stream capture
5. **test_vibecompiler_dry_run_demo** - Demo functionality

## Best Practices

### 1. Always Set Appropriate Timeouts

```python
# Bad - might hang forever
result = compiler.run_snippet(unknown_code)

# Good - has timeout protection
result = compiler.run_snippet(unknown_code, timeout=5)
```

### 2. Handle TimeoutError

```python
try:
    result = compiler.run_snippet(code, timeout=3)
except TimeoutError:
    print("Code took too long to execute")
    # Handle timeout gracefully
```

### 3. Check Both stdout and stderr

```python
result = compiler.run_snippet(code)

if result['stderr']:
    print(f"Warnings/Errors: {result['stderr']}")

if result['stdout']:
    print(f"Output: {result['stdout']}")
```

### 4. Validate Code Before Execution (if possible)

```python
import ast

def is_valid_python(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

if is_valid_python(user_code):
    result = compiler.run_snippet(user_code)
else:
    print("Invalid Python syntax")
```

## Limitations

### 1. Python Only

Currently only supports Python code execution. Other languages require subprocess configuration.

### 2. Standard Library Only

Code must use Python's standard library. External packages are not available in the subprocess.

### 3. No Persistent State

Each execution is isolated - no state persists between runs:

```python
# These are independent executions
compiler.run_snippet("x = 10")
result = compiler.run_snippet("print(x)")  # NameError: x not defined
```

### 4. No Interactive Input

Code cannot use `input()` or other interactive features:

```python
# This will fail
compiler.run_snippet("name = input('Enter name: ')")
```

## Integration with ArcaneOS

The VibeCompiler integrates with other ArcaneOS components:

### With Grimoire

```python
from core.vibecompiler import VibeCompiler
from app.services.grimoire import get_grimoire

compiler = VibeCompiler()
grimoire = get_grimoire()

# Execute code
result = compiler.run_snippet("print('test')")

# Record in grimoire
grimoire.record_spell(
    spell_name="vibecompile_execution",
    command={"code": "print('test')"},
    result=result,
    spell_type="compile",
    success=result['stderr'] == '',
    execution_time=result['duration']
)
```

### With Event Bus

```python
from core.vibecompiler import VibeCompiler
from core.event_bus import get_event_bus

compiler = VibeCompiler()
bus = get_event_bus()

# Execute and broadcast result
result = compiler.run_snippet("print('test')")

await bus.emit("compile", {
    "event": "execution_complete",
    "duration": result['duration'],
    "success": result['stderr'] == ''
})
```

## Troubleshooting

### Issue: TimeoutError on Valid Code

**Problem:** Code times out even though it should complete quickly.

**Solution:** Increase timeout value:
```python
result = compiler.run_snippet(code, timeout=10)
```

### Issue: Missing Output

**Problem:** Expected output not in stdout.

**Solution:** Check stderr for errors:
```python
if result['stderr']:
    print(f"Errors: {result['stderr']}")
```

### Issue: Import Errors

**Problem:** Cannot import external packages.

**Solution:** VibeCompiler only supports standard library. Use built-in modules only:
```python
# Works
code = "import json; print(json.dumps({'a': 1}))"

# Doesn't work
code = "import requests; print(requests.get(...))"
```

## Advanced Usage

### Custom Error Handling

```python
def safe_execute(code, timeout=3):
    """Execute code with comprehensive error handling"""
    compiler = VibeCompiler()

    try:
        result = compiler.run_snippet(code, timeout=timeout)

        # Check for errors
        if result['stderr']:
            return {
                'success': False,
                'error': result['stderr'],
                'output': result['stdout']
            }

        return {
            'success': True,
            'output': result['stdout'],
            'duration': result['duration']
        }

    except TimeoutError:
        return {
            'success': False,
            'error': f'Execution exceeded {timeout}s timeout',
            'output': ''
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'output': ''
        }
```

### Batch Execution

```python
def execute_batch(code_snippets, timeout=3):
    """Execute multiple code snippets"""
    compiler = VibeCompiler()
    results = []

    for i, code in enumerate(code_snippets):
        try:
            result = compiler.run_snippet(code, timeout=timeout)
            results.append({
                'index': i,
                'success': True,
                'result': result
            })
        except Exception as e:
            results.append({
                'index': i,
                'success': False,
                'error': str(e)
            })

    return results
```

## See Also

- [ArcaneOS README](../README.md) - Main project documentation
- [The Grimoire](GRIMOIRE.md) - Spell history documentation
- [Event Bus](EVENT_BUS.md) - WebSocket event broadcasting
- [Reality Veil](REALITY_VEIL.md) - Fantasy/developer mode toggle

---

**Note:** The VibeCompiler is designed for safe, sandboxed execution of untrusted code. Always validate and sanitize user input before execution.
