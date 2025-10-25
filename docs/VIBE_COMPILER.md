# VibeCompiler Documentation

## Overview

The **VibeCompiler** is a thematic code execution engine that wraps real code compilation and execution in fantasy-themed ceremonial presentation. Each step of the compilation process is narrated with mystical phrasing, creating an immersive coding experience.

## Concept

Instead of boring compiler output, the VibeCompiler transforms code execution into a magical ritual:

```
Standard Compiler:
> python script.py
Hello World!

VibeCompiler:
✨ [INITIATION] The mystical compiler awakens from its slumber...
✨ [PARSING] Arcane symbols dance across the ethereal plane...
✨ [COMPILATION] The forge of creation blazes with eldritch flame...
✨ [INVOCATION] The ritual circle activates with brilliant light...
✨ [EXECUTION] The spell manifests! Code flows like liquid light...
✨ [COMPLETION] The ritual concludes with a shimmer of success!

Output: Hello World!
```

## Features

- **Multi-Language Support**: Python, JavaScript, Bash, Ruby, Go, Rust
- **Ceremonial Narration**: Fantasy-themed progress messages
- **Dry-Run Mode**: Validate without executing (safe for demos)
- **Safe Execution**: Timeouts, validation, sandboxing
- **Event Integration**: Real-time updates via ArcaneEventBus
- **Dual Output**: Both literal output and styled narration

## Supported Languages

| Language | Theme | Timeout | Extension | Notes |
|----------|-------|---------|-----------|-------|
| Python | Serpent | 10s | .py | Direct execution |
| JavaScript | Lightning | 10s | .js | Node.js required |
| Bash | Earth | 10s | .sh | Shell scripts |
| Ruby | Crystal | 10s | .rb | Direct execution |
| Go | Steel | 15s | .go | Requires file compilation |
| Rust | Iron | 30s | .rs | Compile then run |

## API Endpoints

### 1. Compile and Execute

```http
POST /compile/execute
```

Executes code with full ceremonial narration.

**Request Body:**
```json
{
  "code": "print('Hello from the mystical realm!')",
  "language": "python",
  "dry_run": false,
  "timeout": 10,
  "emit_events": true
}
```

**Response:**
```json
{
  "success": true,
  "output": "Hello from the mystical realm!\n",
  "error": null,
  "execution_time": 0.123,
  "narration": [
    {
      "phase": "initiation",
      "message": "✨ The mystical compiler awakens...",
      "timestamp": "2025-10-24T12:34:56.789000",
      "details": {"language": "python", "dry_run": false}
    },
    {
      "phase": "parsing",
      "message": "✨ Arcane symbols dance across the ethereal plane...",
      "timestamp": "2025-10-24T12:34:56.790000",
      "details": {"code_length": 42}
    }
  ],
  "narration_text": "✨ [INITIATION] The mystical compiler awakens...\n✨ [PARSING] Arcane symbols dance...",
  "language": "python",
  "dry_run": false,
  "message": "✨ The spell manifests successfully! Your python code breathes life into the digital realm in 0.123 seconds! ✨"
}
```

### 2. Dry-Run Execution

```http
POST /compile/dry-run
```

Validates code without executing (always safe).

**Request Body:**
```json
{
  "code": "print('This will not run!')",
  "language": "python"
}
```

**Response:**
```json
{
  "success": true,
  "output": "[DRY RUN MODE]\n\nCode validated successfully for python!\n\nNo actual execution performed.",
  "error": null,
  "execution_time": 0.001,
  "narration": [...],
  "narration_text": "...",
  "language": "python",
  "dry_run": true,
  "message": "✨ The python incantation is validated! Safety protocols engaged... ✨"
}
```

### 3. Get Supported Languages

```http
GET /compile/languages
```

Lists all supported languages.

**Response:**
```json
{
  "status": "success",
  "message": "✨ The grimoire reveals all known tongues of code... ✨",
  "languages": [
    {
      "language": "python",
      "theme": "serpent",
      "timeout": 10,
      "extension": ".py"
    }
  ],
  "count": 6
}
```

### 4. Get Example Code

```http
GET /compile/example/{language}
```

Returns example code for a language.

**Response:**
```json
{
  "status": "success",
  "language": "python",
  "message": "✨ Behold, an example of python magic! ✨",
  "example": {
    "code": "for i in range(3):\n    print(f'✨ Spell iteration {i+1} complete!')",
    "description": "A simple loop demonstrating Python's serpentine flow"
  }
}
```

## Compilation Phases

The VibeCompiler narrates six phases:

### 1. INITIATION
The compiler awakens and prepares for the ritual.

**Narration Examples:**
- "✨ The mystical compiler awakens from its slumber..."
- "✨ Ancient runes begin to glow with ethereal energy..."
- "✨ The ceremonial chamber hums with anticipation..."

### 2. PARSING
Code is analyzed and validated.

**Narration Examples:**
- "✨ Arcane symbols dance across the ethereal plane..."
- "✨ The compiler's eyes scan the sacred text..."
- "✨ Runes align themselves into patterns of power..."

### 3. COMPILATION
Code is transformed into executable form.

**Narration Examples:**
- "✨ The forge of creation blazes with eldritch flame..."
- "✨ Mana channels stabilizing across dimensional barriers..."
- "✨ Code transforms into executable essence..."

### 4. INVOCATION
The execution environment is prepared.

**Narration Examples:**
- "✨ The ritual circle activates with brilliant light..."
- "✨ Summoning the execution daemon from the depths..."
- "✨ Reality bends to accommodate your command..."

### 5. EXECUTION
Code runs and produces output.

**Narration Examples:**
- "✨ The spell manifests! Code flows like liquid light..."
- "✨ Computational energies surge through the matrix..."
- "✨ Your program awakens, breathing digital life..."

### 6. COMPLETION (or ERROR)
The execution finishes successfully or fails.

**Success:**
- "✨ The ritual concludes with a shimmer of success!"
- "✨ Mana channels seal, the spell is complete!"

**Error:**
- "✨ The runes flicker... something is amiss!"
- "✨ Dark energies interfere with the ritual!"

## Safety Features

### 1. Code Validation

Before execution, code is checked for:
- Dangerous patterns (rm -rf, format, fork bombs)
- Excessive length (max 10,000 characters)
- Empty or whitespace-only input

### 2. Execution Timeouts

Each language has a default timeout:
- Python, JS, Bash, Ruby: 10 seconds
- Go: 15 seconds
- Rust: 30 seconds (compilation is slower)

Custom timeouts can be specified (max 60 seconds).

### 3. Sandboxed Execution

Code runs in subprocess with:
- Limited privileges
- Captured stdout/stderr
- Timeout enforcement
- Resource limits

### 4. Dry-Run Mode

Perfect for demos and testing:
- Validates syntax
- Generates full narration
- Returns mock output
- **Never executes code**

## Usage Examples

### Python Example

```bash
curl -X POST http://localhost:8000/compile/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in range(3):\n    print(f\"Iteration {i+1}\")",
    "language": "python"
  }'
```

### JavaScript Example

```bash
curl -X POST http://localhost:8000/compile/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for (let i = 0; i < 3; i++) { console.log(`Count: ${i}`); }",
    "language": "javascript"
  }'
```

### Dry-Run Example

```bash
curl -X POST http://localhost:8000/compile/dry-run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"This is safe!\")",
    "language": "python"
  }'
```

## Integration with ArcaneEventBus

The VibeCompiler emits events to the event bus for real-time monitoring:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.spell_name === 'parse') {
    // Compilation event!
    console.log(`Language: ${data.metadata.language}`);
    console.log(`Success: ${data.success}`);
    console.log(`Time: ${data.metadata.execution_time}s`);
  }
};

// Then execute code
fetch('http://localhost:8000/compile/execute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    code: 'print("Hello!")',
    language: 'python',
    emit_events: true
  })
});
```

## Frontend Integration

### Display Narration Step-by-Step

```javascript
async function compileWithAnimation(code, language) {
  const response = await fetch('/compile/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code, language})
  });

  const result = await response.json();

  // Animate narration
  for (const event of result.narration) {
    await showNarrationEvent(event);
    await delay(500); // 500ms between phases
  }

  // Show output
  showOutput(result.output);
}

function showNarrationEvent(event) {
  const phaseColors = {
    'initiation': '#8B5CF6',
    'parsing': '#F59E0B',
    'compilation': '#EF4444',
    'invocation': '#10B981',
    'execution': '#3B82F6',
    'completion': '#22C55E',
    'error': '#DC2626'
  };

  const color = phaseColors[event.phase] || '#6B7280';

  // Display with themed styling
  addMessage(event.message, color);
}
```

### Real-Time Progress with WebSocket

```javascript
// Listen for compilation events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.spell_name === 'parse' && data.metadata.language) {
    showCompilationNotification(
      `${data.metadata.language} compilation ${data.success ? 'succeeded' : 'failed'}!`
    );
  }
};
```

## Error Handling

### Validation Errors

```json
{
  "success": false,
  "output": "",
  "error": "Validation failed: Code contains potentially dangerous pattern: rm\\s+-rf",
  "execution_time": 0.001,
  "narration": [
    {
      "phase": "initiation",
      "message": "✨ The mystical compiler awakens..."
    },
    {
      "phase": "parsing",
      "message": "✨ Arcane symbols dance..."
    },
    {
      "phase": "error",
      "message": "✨ The runes flicker... something is amiss!"
    }
  ]
}
```

### Execution Errors

```json
{
  "success": false,
  "output": "",
  "error": "NameError: name 'undefined_variable' is not defined",
  "execution_time": 0.045,
  "narration": [...],
  "message": "✨ The python ritual falters! Dark energies disrupt the execution... ✨"
}
```

### Timeout Errors

```json
{
  "success": false,
  "output": "",
  "error": "Execution timeout after 10 seconds",
  "execution_time": 10.001,
  "narration": [...]
}
```

## Best Practices

### 1. Use Dry-Run for Demos

```javascript
// Always dry-run for public demos
const result = await compileDryRun(userCode, language);
// Shows full experience without risk
```

### 2. Set Appropriate Timeouts

```javascript
// Quick scripts: 5-10 seconds
{code: "print('Hi')", language: "python", timeout: 5}

// Complex compilations: 20-30 seconds
{code: rustCode, language: "rust", timeout: 30}
```

### 3. Stream Narration in Real-Time

```javascript
// Show narration as it happens
for (const event of result.narration) {
  displayEvent(event);
  await sleep(300); // Dramatic pause
}
```

### 4. Handle Errors Gracefully

```javascript
if (!result.success) {
  showError(result.error);
  // Still show the narration for immersion
  displayNarration(result.narration);
}
```

## Advanced Usage

### Custom Narration Themes

While the current themes are built-in, you can style the narration based on language:

```javascript
const themeStyles = {
  'python': {color: '#3776ab', icon: '🐍'},
  'javascript': {color: '#f7df1e', icon: '⚡'},
  'bash': {color: '#4eaa25', icon: '🌍'},
  'ruby': {color: '#cc342d', icon: '💎'},
  'go': {color: '#00add8', icon: '⚙️'},
  'rust': {color: '#dea584', icon: '🔨'}
};

function styleNarration(event, language) {
  const theme = themeStyles[language];
  return `${theme.icon} ${event.message}`;
}
```

### Progress Bars

```javascript
function updateProgress(phase) {
  const phases = ['initiation', 'parsing', 'compilation',
                  'invocation', 'execution', 'completion'];
  const progress = (phases.indexOf(phase) + 1) / phases.length * 100;
  progressBar.style.width = `${progress}%`;
}
```

## Testing

### Manual Testing

```bash
# Start server
uvicorn app.main:app --reload

# Test Python
curl -X POST http://localhost:8000/compile/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello!\")", "language": "python"}'

# Test dry-run
curl -X POST http://localhost:8000/compile/dry-run \
  -H "Content-Type: application/json" \
  -d '{"code": "dangerous_code()", "language": "python"}'

# Get languages
curl http://localhost:8000/compile/languages

# Get example
curl http://localhost:8000/compile/example/python
```

### Automated Testing

```python
import pytest
from app.services.vibe_compiler import get_vibe_compiler, CodeLanguage

def test_python_execution():
    compiler = get_vibe_compiler()
    result = compiler.compile_and_execute(
        code='print("Hello")',
        language=CodeLanguage.PYTHON
    )

    assert result.success
    assert "Hello" in result.output
    assert len(result.narration) >= 6
    assert result.narration[0].phase.value == "initiation"

def test_dry_run():
    compiler = get_vibe_compiler()
    result = compiler.compile_and_execute(
        code='print("Should not execute")',
        language=CodeLanguage.PYTHON,
        dry_run=True
    )

    assert result.success
    assert result.dry_run
    assert "[DRY RUN" in result.output

def test_validation():
    compiler = get_vibe_compiler()
    result = compiler.compile_and_execute(
        code='rm -rf /',
        language=CodeLanguage.BASH
    )

    assert not result.success
    assert "dangerous pattern" in result.error.lower()
```

## Troubleshooting

### Language Not Found

**Problem:** "Interpreter for python not found"

**Solution:** Install the required language:
```bash
# Python
sudo apt install python3

# Node.js (JavaScript)
sudo apt install nodejs

# Ruby
sudo apt install ruby

# Go
sudo apt install golang

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Timeout Issues

**Problem:** Code times out

**Solution:**
1. Increase timeout: `{"timeout": 30}`
2. Optimize code
3. Use dry-run for validation only

### Validation False Positives

**Problem:** Safe code flagged as dangerous

**Solution:** The validation patterns are conservative. If needed, adjust patterns in `vibe_compiler.py:_validate_code()`

## Future Enhancements

- [ ] More languages (PHP, Java, C++, TypeScript)
- [ ] Custom narration templates
- [ ] Persistent compilation history
- [ ] Multi-file project support
- [ ] Package/dependency management
- [ ] Code highlighting in narration
- [ ] Animated ASCII art for phases
- [ ] Sound effects for ceremonial atmosphere

## Related Documentation

- [ArcaneEventBus](./ARCANE_EVENT_BUS.md) - Real-time event streaming
- [API Documentation](http://localhost:8000/grimoire) - Interactive API docs
- [Main README](../README.md) - Project overview
