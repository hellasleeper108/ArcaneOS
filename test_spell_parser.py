"""
Tests for the Spell Parser

Validates natural language parsing functionality.
"""

import sys
from app.services.spell_parser import SpellParser, ParseError, SpellAction


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_summon_spells():
    """Test summon spell parsing"""
    print_section("TESTING SUMMON SPELLS")

    parser = SpellParser()

    test_cases = [
        "summon claude",
        "summon the gemini daemon",
        "call forth liquidmetal",
        "materialize claude",
        "awaken gemini",
        "bring claude to life",
        "summon the logic keeper"
    ]

    for spell in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.action == SpellAction.SUMMON
            assert parsed.daemon is not None
            print(f"✓ '{spell}'")
            print(f"  → daemon: {parsed.daemon}, confidence: {parsed.confidence:.2f}")
        except AssertionError:
            print(f"✗ '{spell}' - Wrong action: {parsed.action}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All summon spell tests passed!")
    return True


def test_invoke_spells():
    """Test invoke spell parsing"""
    print_section("TESTING INVOKE SPELLS")

    parser = SpellParser()

    test_cases = [
        ("invoke claude to write code", "claude", "write code"),
        ("ask gemini to create a logo", "gemini", "create a logo"),
        ("tell liquidmetal to transform data", "liquidmetal", "transform data"),
        ("command claude: analyze security", "claude", "analyze security"),
        ("invoke gemini for brainstorming", "gemini", "brainstorming"),
        ("claude, explain quantum physics", "claude", "explain quantum physics"),
    ]

    for spell, expected_daemon, expected_task_substring in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.action == SpellAction.INVOKE
            assert parsed.daemon == expected_daemon
            assert parsed.task is not None
            assert expected_task_substring in parsed.task.lower()

            print(f"✓ '{spell}'")
            print(f"  → daemon: {parsed.daemon}, task: {parsed.task}")
        except AssertionError as e:
            print(f"✗ '{spell}'")
            print(f"  Expected: daemon={expected_daemon}, task containing '{expected_task_substring}'")
            print(f"  Got: daemon={parsed.daemon if 'parsed' in locals() else 'FAILED'}, task={parsed.task if 'parsed' in locals() else 'FAILED'}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All invoke spell tests passed!")
    return True


def test_banish_spells():
    """Test banish spell parsing"""
    print_section("TESTING BANISH SPELLS")

    parser = SpellParser()

    test_cases = [
        "banish claude",
        "banish the gemini daemon",
        "dismiss liquidmetal",
        "send claude back",
        "release gemini"
    ]

    for spell in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.action == SpellAction.BANISH
            assert parsed.daemon is not None
            print(f"✓ '{spell}'")
            print(f"  → daemon: {parsed.daemon}")
        except AssertionError:
            print(f"✗ '{spell}' - Wrong action: {parsed.action if 'parsed' in locals() else 'FAILED'}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All banish spell tests passed!")
    return True


def test_query_spells():
    """Test query spell parsing"""
    print_section("TESTING QUERY SPELLS")

    parser = SpellParser()

    test_cases = [
        "show me all daemons",
        "list daemons",
        "what daemons are active",
        "status of claude",
        "check on gemini"
    ]

    for spell in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.action == SpellAction.QUERY
            print(f"✓ '{spell}'")
            if parsed.daemon:
                print(f"  → daemon: {parsed.daemon}")
        except AssertionError:
            print(f"✗ '{spell}' - Wrong action: {parsed.action if 'parsed' in locals() else 'FAILED'}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All query spell tests passed!")
    return True


def test_parameters_extraction():
    """Test parameter extraction from spells"""
    print_section("TESTING PARAMETER EXTRACTION")

    parser = SpellParser()

    test_cases = [
        ("invoke claude to analyze code with depth=high", {"depth": "high"}),
        ("ask gemini to create art with style=modern", {"style": "modern"}),
        ("invoke claude to process data with timeout=30", {"timeout": 30}),
        ("tell liquidmetal to convert with format=json", {"format": "json"}),
    ]

    for spell, expected_params in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.parameters is not None
            for key, value in expected_params.items():
                assert key in parsed.parameters
                assert parsed.parameters[key] == value

            print(f"✓ '{spell}'")
            print(f"  → parameters: {parsed.parameters}")
        except AssertionError as e:
            print(f"✗ '{spell}'")
            print(f"  Expected: {expected_params}")
            print(f"  Got: {parsed.parameters if 'parsed' in locals() else 'FAILED'}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All parameter extraction tests passed!")
    return True


def test_daemon_normalization():
    """Test daemon name normalization"""
    print_section("TESTING DAEMON NAME NORMALIZATION")

    parser = SpellParser()

    test_cases = [
        ("summon Claude", "claude"),  # Case insensitive
        ("summon the logic keeper", "claude"),  # Alias
        ("invoke reasoner to analyze", "claude"),  # Alias
        ("summon gemini", "gemini"),
        ("summon the creative", "gemini"),  # Alias
        ("summon liquidmetal", "liquidmetal"),
        ("summon liquid metal", "liquidmetal"),  # Alias
    ]

    for spell, expected_daemon in test_cases:
        try:
            parsed = parser.parse(spell)
            assert parsed.daemon == expected_daemon
            print(f"✓ '{spell}' → normalized to '{expected_daemon}'")
        except AssertionError:
            print(f"✗ '{spell}'")
            print(f"  Expected: {expected_daemon}")
            print(f"  Got: {parsed.daemon if 'parsed' in locals() else 'FAILED'}")
            return False
        except Exception as e:
            print(f"✗ '{spell}' - Error: {e}")
            return False

    print("\n✓ All daemon normalization tests passed!")
    return True


def test_error_handling():
    """Test error handling for invalid spells"""
    print_section("TESTING ERROR HANDLING")

    parser = SpellParser()

    invalid_spells = [
        "",  # Empty
        "gibberish nonsense words",  # No recognizable pattern
        "xyzabc",  # Random text
    ]

    for spell in invalid_spells:
        try:
            parsed = parser.parse(spell)
            print(f"✗ '{spell}' - Should have raised ParseError but got: {parsed}")
            return False
        except ParseError as e:
            print(f"✓ '{spell}' → Correctly raised ParseError")
            suggestions = parser.suggest_correction(spell)
            print(f"  Suggestions: {len(suggestions)} provided")
        except Exception as e:
            print(f"✗ '{spell}' - Unexpected error: {e}")
            return False

    print("\n✓ All error handling tests passed!")
    return True


def test_batch_parsing():
    """Test batch spell parsing"""
    print_section("TESTING BATCH PARSING")

    parser = SpellParser()

    spells = [
        "summon claude",
        "invoke gemini to create art",
        "banish liquidmetal",
        "invalid spell here",  # This should be skipped
        "status of claude"
    ]

    results = parser.parse_batch(spells)

    # Should have 4 successful results (skipping the invalid one)
    if len(results) != 4:
        print(f"✗ Expected 4 results, got {len(results)}")
        return False

    print(f"✓ Batch parsed {len(results)} valid spells out of {len(spells)} total")

    for parsed in results:
        print(f"  → {parsed.action.value}: {parsed.daemon}")

    print("\n✓ Batch parsing test passed!")
    return True


def test_confidence_scores():
    """Test confidence scoring"""
    print_section("TESTING CONFIDENCE SCORES")

    parser = SpellParser()

    # High-priority patterns should have higher confidence
    high_priority = "invoke claude to write code"
    parsed_high = parser.parse(high_priority)

    print(f"✓ '{high_priority}'")
    print(f"  → Confidence: {parsed_high.confidence:.2f}")

    # All valid parses should have confidence > 0
    assert parsed_high.confidence > 0
    assert parsed_high.confidence <= 1.0

    print("\n✓ Confidence scoring test passed!")
    return True


def test_json_output():
    """Test JSON output format"""
    print_section("TESTING JSON OUTPUT")

    parser = SpellParser()

    spell = "invoke claude to analyze security with depth=high"
    parsed = parser.parse(spell)

    json_output = parsed.to_dict()

    # Verify required fields
    assert "action" in json_output
    assert "daemon" in json_output
    assert "confidence" in json_output
    assert "raw_input" in json_output

    print(f"✓ Parsed: '{spell}'")
    print(f"  → JSON output:")
    import json
    print(json.dumps(json_output, indent=2))

    print("\n✓ JSON output test passed!")
    return True


def main():
    """Run all tests"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "SPELL PARSER TESTS" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")

    tests = [
        test_summon_spells,
        test_invoke_spells,
        test_banish_spells,
        test_query_spells,
        test_parameters_extraction,
        test_daemon_normalization,
        test_error_handling,
        test_batch_parsing,
        test_confidence_scores,
        test_json_output
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")

    if failed == 0:
        print("✅ All spell parser tests passed! The mystical arts are strong.\n")
        return 0
    else:
        print("❌ Some tests failed. The incantations need refinement.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
