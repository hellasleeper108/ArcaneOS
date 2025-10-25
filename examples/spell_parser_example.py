"""
Spell Parser Usage Examples

Demonstrates how to use the natural language spell parser.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.spell_parser import get_spell_parser, ParseError
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_basic_parsing():
    """Demonstrate basic spell parsing"""
    print_section("BASIC SPELL PARSING")

    parser = get_spell_parser()

    spells = [
        "summon claude",
        "invoke gemini to create a logo",
        "banish liquidmetal",
        "ask claude to analyze code",
        "show me all daemons"
    ]

    for spell in spells:
        parsed = parser.parse(spell)
        print(f"Spell: '{spell}'")
        print(f"  → Action: {parsed.action.value}")
        print(f"  → Daemon: {parsed.daemon}")
        print(f"  → Task: {parsed.task}")
        print(f"  → Confidence: {parsed.confidence:.2f}")
        print()


def example_parameter_extraction():
    """Demonstrate parameter extraction"""
    print_section("PARAMETER EXTRACTION")

    parser = get_spell_parser()

    spells = [
        "invoke claude to analyze code with depth=high",
        "ask gemini to create art with style=modern",
        "tell liquidmetal to process with timeout=30",
        "invoke claude to debug with verbose=true"
    ]

    for spell in spells:
        parsed = parser.parse(spell)
        print(f"Spell: '{spell}'")
        print(f"  → Task: {parsed.task}")
        print(f"  → Parameters: {json.dumps(parsed.parameters, indent=4)}")
        print()


def example_daemon_aliases():
    """Demonstrate daemon name normalization"""
    print_section("DAEMON NAME NORMALIZATION")

    parser = get_spell_parser()

    spells = [
        "summon Claude",  # Case insensitive
        "summon the logic keeper",  # Alias
        "invoke reasoner to analyze",  # Alias
        "summon creative",  # Gemini alias
        "call forth the transformer"  # LiquidMetal alias
    ]

    for spell in spells:
        parsed = parser.parse(spell)
        print(f"Spell: '{spell}'")
        print(f"  → Normalized daemon: {parsed.daemon}")
        print()


def example_flexible_syntax():
    """Demonstrate flexible spell syntax"""
    print_section("FLEXIBLE SPELL SYNTAX")

    parser = get_spell_parser()

    # Different ways to invoke
    invoke_variants = [
        "invoke claude to write code",
        "ask claude to write code",
        "tell claude to write code",
        "command claude: write code",
        "claude, write code",
        "invoke claude for writing code"
    ]

    print("Different ways to INVOKE:\n")
    for spell in invoke_variants:
        parsed = parser.parse(spell)
        print(f"✓ '{spell}'")
        print(f"  → daemon={parsed.daemon}, task={parsed.task}")
    print()

    # Different ways to summon
    summon_variants = [
        "summon claude",
        "call forth claude",
        "materialize claude",
        "awaken claude",
        "bring claude to life"
    ]

    print("Different ways to SUMMON:\n")
    for spell in summon_variants:
        parsed = parser.parse(spell)
        print(f"✓ '{spell}' → daemon={parsed.daemon}")
    print()


def example_error_handling():
    """Demonstrate error handling"""
    print_section("ERROR HANDLING")

    parser = get_spell_parser()

    invalid_spells = [
        "xyz random text",
        "do something",
        ""
    ]

    for spell in invalid_spells:
        try:
            parsed = parser.parse(spell)
            print(f"✓ '{spell}' → Unexpectedly parsed as {parsed.action.value}")
        except ParseError as e:
            print(f"✗ '{spell}' → ParseError (expected)")
            print(f"  Error: {str(e)[:60]}...")

            # Get suggestions
            suggestions = parser.suggest_correction(spell)
            print(f"  Suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"    {i}. {suggestion}")
        print()


def example_batch_parsing():
    """Demonstrate batch parsing"""
    print_section("BATCH PARSING")

    parser = get_spell_parser()

    spells = [
        "summon claude",
        "invoke gemini to create art",
        "this is invalid",  # Will be skipped
        "banish liquidmetal",
        "another invalid one",  # Will be skipped
        "status of claude"
    ]

    print(f"Parsing {len(spells)} spells in batch...\n")

    results = parser.parse_batch(spells)

    print(f"Successfully parsed {len(results)} out of {len(spells)} spells:\n")

    for parsed in results:
        print(f"✓ {parsed.action.value}: {parsed.daemon}")


def example_json_output():
    """Demonstrate JSON output"""
    print_section("JSON OUTPUT")

    parser = get_spell_parser()

    spell = "invoke claude to analyze security with depth=high"
    parsed = parser.parse(spell)

    print(f"Spell: '{spell}'\n")
    print("JSON Output:")
    print(json.dumps(parsed.to_dict(), indent=2))


def example_confidence_scores():
    """Demonstrate confidence scoring"""
    print_section("CONFIDENCE SCORES")

    parser = get_spell_parser()

    spells = [
        ("invoke claude to write code", "High priority pattern"),
        ("ask gemini to create", "Medium priority pattern"),
        ("summon claude", "Standard priority pattern"),
        ("bring claude to life", "Lower priority pattern")
    ]

    print("Spells sorted by confidence:\n")

    parsed_spells = [(parser.parse(spell), desc) for spell, desc in spells]
    parsed_spells.sort(key=lambda x: x[0].confidence, reverse=True)

    for parsed, description in parsed_spells:
        print(f"Confidence: {parsed.confidence:.2f} - {description}")
        print(f"  Spell: '{parsed.raw_input}'")
        print()


def example_practical_use_case():
    """Demonstrate practical integration"""
    print_section("PRACTICAL USE CASE: Chat Bot")

    parser = get_spell_parser()

    def process_chat_message(message: str) -> str:
        """Process user message as a spell"""
        try:
            parsed = parser.parse(message)

            if parsed.confidence < 0.7:
                return f"I'm not sure I understood that correctly (confidence: {parsed.confidence:.0%}). Can you rephrase?"

            if parsed.action.value == "invoke":
                if parsed.daemon and parsed.task:
                    return f"Invoking {parsed.daemon} to: {parsed.task}"
                else:
                    return "I need to know which daemon and what task to perform."

            elif parsed.action.value == "summon":
                if parsed.daemon:
                    return f"Summoning {parsed.daemon}..."
                else:
                    return "Which daemon would you like to summon?"

            elif parsed.action.value == "banish":
                if parsed.daemon:
                    return f"Banishing {parsed.daemon}..."
                else:
                    return "Which daemon should I banish?"

            elif parsed.action.value == "query":
                return "Checking daemon status..."

        except ParseError:
            return "I didn't understand that. Try: 'invoke <daemon> to <task>'"

    # Test the chat bot
    test_messages = [
        "invoke claude to write tests",
        "summon gemini",
        "random gibberish",
        "ask the creative daemon to design a logo"
    ]

    for message in test_messages:
        response = process_chat_message(message)
        print(f"User: {message}")
        print(f"Bot:  {response}")
        print()


def main():
    """Run all examples"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "SPELL PARSER EXAMPLES" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")

    examples = [
        example_basic_parsing,
        example_parameter_extraction,
        example_daemon_aliases,
        example_flexible_syntax,
        example_error_handling,
        example_batch_parsing,
        example_json_output,
        example_confidence_scores,
        example_practical_use_case
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("  All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
