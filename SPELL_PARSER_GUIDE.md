## 🔮 Natural Language Spell Parser Guide

### Overview

The ArcaneOS Spell Parser translates natural language commands into structured JSON, allowing users to interact with daemon entities using intuitive,

 mystical incantations.

### Features

- **Natural Language Processing**: Parse human-readable commands
- **Flexible Patterns**: Supports multiple ways to express the same action
- **Parameter Extraction**: Automatically extract parameters from task descriptions
- **Daemon Name Normalization**: Handle aliases and variations
- **Confidence Scoring**: Indicates parsing reliability
- **Error Suggestions**: Helpful hints when parsing fails

### Supported Actions

| Action | Description | Example |
|--------|-------------|---------|
| **summon** | Bring a daemon into existence | "summon claude" |
| **invoke** | Command a daemon to perform a task | "invoke gemini to create art" |
| **banish** | Send a daemon back to the void | "banish liquidmetal" |
| **query** | Check daemon status | "show me all daemons" |

### API Endpoints

#### POST `/spell/parse`

Parse a natural language spell into structured JSON.

**Request:**
```json
{
  "spell": "invoke claude to write code"
}
```

**Response:**
```json
{
  "success": true,
  "action": "invoke",
  "daemon": "claude",
  "task": "write code",
  "parameters": null,
  "confidence": 1.0,
  "raw_input": "invoke claude to write code",
  "error": null,
  "suggestions": null
}
```

#### POST `/spell/cast`

Parse AND execute a spell in one step.

**Request:**
```json
{
  "spell": "invoke claude to explain recursion"
}
```

**Response:**
```json
{
  "success": true,
  "parsed": {
    "action": "invoke",
    "daemon": "claude",
    "task": "explain recursion",
    "confidence": 1.0
  },
  "execution": {
    "action": "invoked",
    "daemon": {...},
    "result": {...},
    "execution_time": 0.023
  }
}
```

#### GET `/spell/examples`

Get example spells for learning.

**Response:**
```json
{
  "summon_examples": [...],
  "invoke_examples": [...],
  "banish_examples": [...],
  "query_examples": [...]
}
```

### Spell Syntax

#### Summon Spells

Bring a daemon into existence:

```
✓ summon claude
✓ summon the gemini daemon
✓ call forth liquidmetal
✓ materialize claude
✓ awaken gemini
✓ bring claude to life
```

#### Invoke Spells

Command a daemon to perform tasks:

```
✓ invoke claude to analyze code
✓ ask gemini to create a logo
✓ tell liquidmetal to transform data
✓ command claude: explain quantum physics
✓ claude, write a poem
✓ invoke gemini for brainstorming
```

**With Parameters:**
```
✓ invoke claude to analyze code with depth=high
✓ ask gemini to create art with style=modern
✓ tell claude to process data with timeout=30
```

#### Banish Spells

Send daemons back to the void:

```
✓ banish claude
✓ banish the gemini daemon
✓ dismiss liquidmetal
✓ send claude back
✓ release gemini
```

#### Query Spells

Check daemon status:

```
✓ show me all daemons
✓ list daemons
✓ what daemons are active
✓ status of claude
✓ check on gemini
```

### Daemon Names & Aliases

The parser recognizes multiple names for each daemon:

| Canonical | Aliases |
|-----------|---------|
| **claude** | claude, logic keeper, reasoner, analyzer |
| **gemini** | gemini, creative, innovator, dreamer |
| **liquidmetal** | liquidmetal, liquid metal, transformer, shapeshifter |

### Parameter Extraction

Parameters can be embedded in task descriptions using `with key=value` syntax:

**Examples:**
```
"invoke claude to analyze with depth=high"
  → task: "analyze"
  → parameters: {"depth": "high"}

"ask gemini to create with style=modern"
  → task: "create"
  → parameters: {"style": "modern"}

"process data with timeout=30"
  → task: "process data"
  → parameters: {"timeout": 30}  # Auto-converted to number
```

**Supported Types:**
- String: `name=value`
- Number: `count=42` or `ratio=3.14`
- Boolean: `enabled=true` or `debug=false`

### Confidence Scores

Each parsed spell includes a confidence score (0-1):

- **1.0**: High-priority pattern match (e.g., "invoke X to Y")
- **0.95**: Medium-priority match (e.g., "ask X to Y")
- **0.80**: Standard pattern match (e.g., "summon X")
- **0.70**: Lower-priority match

Higher scores indicate more specific pattern matches.

### Error Handling

When parsing fails, the response includes helpful suggestions:

**Failed Parse:**
```json
{
  "success": false,
  "error": "Unable to parse spell: 'xyz'...",
  "suggestions": [
    "Try starting with an action: summon, invoke, or banish",
    "Include a daemon name: claude, gemini, liquidmetal",
    "Example: 'invoke claude to analyze code'"
  ]
}
```

### Python Usage

#### Basic Parsing

```python
from app.services.spell_parser import get_spell_parser

parser = get_spell_parser()

# Parse a spell
parsed = parser.parse("invoke claude to write code")

print(f"Action: {parsed.action.value}")
print(f"Daemon: {parsed.daemon}")
print(f"Task: {parsed.task}")
print(f"Confidence: {parsed.confidence}")

# Convert to JSON
json_output = parsed.to_dict()
```

#### Batch Parsing

```python
spells = [
    "summon claude",
    "invoke gemini to create art",
    "banish liquidmetal"
]

results = parser.parse_batch(spells)

for parsed in results:
    print(f"{parsed.action.value}: {parsed.daemon}")
```

#### Error Handling

```python
from app.services.spell_parser import ParseError

try:
    parsed = parser.parse("invalid spell")
except ParseError as e:
    print(f"Error: {e}")
    suggestions = parser.suggest_correction("invalid spell")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
```

### HTTP Examples

#### Using cURL

```bash
# Parse a spell
curl -X POST http://localhost:8000/spell/parse \
  -H "Content-Type: application/json" \
  -d '{"spell": "invoke claude to write tests"}'

# Cast a spell (parse + execute)
curl -X POST http://localhost:8000/spell/cast \
  -H "Content-Type: application/json" \
  -d '{"spell": "summon gemini"}'

# Get examples
curl http://localhost:8000/spell/examples
```

#### Using Python Requests

```python
import requests

# Parse a spell
response = requests.post(
    "http://localhost:8000/spell/parse",
    json={"spell": "invoke claude to analyze security"}
)

result = response.json()
print(f"Action: {result['action']}")
print(f"Daemon: {result['daemon']}")
print(f"Task: {result['task']}")

# Cast a spell
response = requests.post(
    "http://localhost:8000/spell/cast",
    json={"spell": "invoke gemini to create logo"}
)

execution = response.json()
if execution['success']:
    print(f"Execution time: {execution['execution']['execution_time']}s")
    print(f"Result: {execution['execution']['result']}")
```

### Advanced Features

#### Custom Patterns

You can extend the parser with custom patterns:

```python
from app.services.spell_parser import SpellParser, SpellPattern, SpellAction

parser = SpellParser()

# Add custom pattern
custom_pattern = SpellPattern(
    pattern=r"cast\s+(\w+)\s+spell",
    action=SpellAction.INVOKE,
    groups={"daemon": 1},
    priority=85
)

parser.patterns.append(custom_pattern)
parser.patterns.sort(key=lambda p: p.priority, reverse=True)

# Now can parse: "cast claude spell"
parsed = parser.parse("cast claude spell")
```

#### Daemon Normalization

```python
# The parser normalizes daemon names
parsed1 = parser.parse("summon Claude")  # → daemon: "claude"
parsed2 = parser.parse("summon logic keeper")  # → daemon: "claude"
parsed3 = parser.parse("summon reasoner")  # → daemon: "claude"

# All resolve to canonical name "claude"
```

### Pattern Priority

Patterns are evaluated in priority order (highest first):

| Priority | Pattern Type | Example |
|----------|--------------|---------|
| 100 | Specific invoke | "invoke X to Y" |
| 95 | Action synonyms | "ask X to Y", "tell X to Y" |
| 95 | Query (specific) | "show me all daemons" |
| 90 | Command syntax | "command X: Y" |
| 85 | Invoke variants | "invoke X for Y" |
| 80 | Basic actions | "summon X", "banish X" |

### Best Practices

1. **Be Specific**: More specific commands get higher confidence scores
   - ✓ "invoke claude to analyze code"
   - ✗ "claude do something"

2. **Use Canonical Names**: While aliases work, canonical names are clearer
   - ✓ "summon claude"
   - ✓ "summon logic keeper" (works, but less clear)

3. **Include Action Words**: Always start with an action
   - ✓ "invoke gemini to create"
   - ✗ "gemini create" (might not parse)

4. **Extract Parameters**: Use `with key=value` for parameters
   - ✓ "analyze with depth=high"
   - ✗ "analyze deeply" (not extracted as parameter)

5. **Handle Errors**: Always check success status
   ```python
   result = response.json()
   if result['success']:
       # Process result
   else:
       print(f"Error: {result['error']}")
       for suggestion in result['suggestions']:
           print(f"Try: {suggestion}")
   ```

### Testing

Run the comprehensive test suite:

```bash
python test_spell_parser.py
```

Tests cover:
- Summon spell parsing
- Invoke spell parsing
- Banish spell parsing
- Query spell parsing
- Parameter extraction
- Daemon name normalization
- Error handling
- Batch parsing
- Confidence scoring
- JSON output

### Troubleshooting

**Problem**: Spell not parsing

**Solution**: Check the examples endpoint for valid syntax
```bash
curl http://localhost:8000/spell/examples
```

**Problem**: Daemon not recognized

**Solution**: Use canonical names (claude, gemini, liquidmetal)

**Problem**: Parameters not extracted

**Solution**: Use `with key=value` syntax:
```
"invoke claude to process with format=json"
```

**Problem**: Low confidence score

**Solution**: Use more specific pattern:
- Instead of: "claude, do X"
- Use: "invoke claude to do X"

### Integration Examples

#### Chat Bot Integration

```python
def handle_user_message(message: str):
    """Handle user chat message as spell"""
    parser = get_spell_parser()

    try:
        parsed = parser.parse(message)

        if parsed.action.value == "invoke" and parsed.daemon and parsed.task:
            # Execute the invocation
            result = daemon_registry.invoke_daemon(
                name=DaemonType(parsed.daemon),
                task=parsed.task,
                parameters=parsed.parameters
            )
            return result["result"]["output"]
        else:
            return "I understood your spell, but need more details to execute it."

    except ParseError:
        return "I couldn't understand that spell. Try: 'invoke claude to [task]'"
```

#### Voice Command Integration

```python
def process_voice_command(transcription: str):
    """Process voice-transcribed spell"""
    parser = get_spell_parser()

    # Parse the transcribed text
    parsed = parser.parse(transcription)

    # Execute based on confidence
    if parsed.confidence >= 0.8:
        # High confidence, execute directly
        return execute_spell(parsed)
    else:
        # Low confidence, ask for confirmation
        return {
            "action": "confirm",
            "parsed": parsed.to_dict(),
            "message": f"Did you mean: {parsed.action.value} {parsed.daemon}?"
        }
```

### Future Enhancements

Planned features:
- Support for composite commands ("summon claude and invoke it to...")
- Context-aware parsing (remember last daemon)
- Multi-language support
- Custom action types
- Advanced parameter syntax

### Support

- Documentation: See README.md and REGISTRY_GUIDE.md
- Tests: Run `python test_spell_parser.py`
- API Docs: Visit http://localhost:8000/grimoire

---

May your spells be clear and your parsing be swift! 🔮✨
