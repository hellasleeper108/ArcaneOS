#!/usr/bin/env python3
"""
VibeCompiler Example Client

This example demonstrates how to use the VibeCompiler to execute code
with fantasy-themed ceremonial narration.

Usage:
    python examples/vibe_compiler_example.py
"""

import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_banner(text: str):
    """Print a styled banner"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_narration(narration_events: list):
    """Print narration events with styling"""
    phase_icons = {
        "initiation": "🔮",
        "parsing": "📖",
        "compilation": "🔥",
        "invocation": "⚡",
        "execution": "✨",
        "completion": "🌟",
        "error": "❌"
    }

    print("\n" + "-" * 80)
    print("CEREMONIAL NARRATION:")
    print("-" * 80)

    for event in narration_events:
        icon = phase_icons.get(event["phase"], "✨")
        phase = event["phase"].upper()
        message = event["message"]
        print(f"{icon} [{phase:12}] {message}")

    print("-" * 80 + "\n")


def execute_code(code: str, language: str, dry_run: bool = False):
    """
    Execute code with the VibeCompiler

    Args:
        code: The code to execute
        language: Programming language
        dry_run: If True, validate without executing
    """
    endpoint = f"{BASE_URL}/compile/{'dry-run' if dry_run else 'execute'}"

    print(f"🎯 Compiling {language} code...")
    print(f"   Mode: {'DRY RUN (safe)' if dry_run else 'LIVE EXECUTION'}")
    print(f"\n📝 Code:\n{code}\n")

    try:
        response = requests.post(
            endpoint,
            json={
                "code": code,
                "language": language,
                "dry_run": dry_run,
                "emit_events": True
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        # Print narration
        print_narration(result["narration"])

        # Print status message
        print(f"📬 {result['message']}\n")

        # Print execution results
        if result["success"]:
            print("✅ SUCCESS!")
            print(f"⏱️  Execution Time: {result['execution_time']:.3f}s")
            print(f"\n📤 Output:")
            print("-" * 80)
            print(result["output"])
            print("-" * 80)
        else:
            print("❌ EXECUTION FAILED!")
            print(f"\n🔥 Error:")
            print("-" * 80)
            print(result["error"])
            print("-" * 80)

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def get_supported_languages():
    """Get list of supported languages"""
    try:
        response = requests.get(f"{BASE_URL}/compile/languages")
        response.raise_for_status()
        result = response.json()

        print(f"📚 {result['message']}\n")
        print(f"Supported Languages ({result['count']}):")
        print("-" * 80)

        for lang in result["languages"]:
            print(f"  • {lang['language']:12} - Theme: {lang['theme']:10} "
                  f"Timeout: {lang['timeout']:2}s  Extension: {lang['extension']}")

        print("-" * 80 + "\n")

        return result["languages"]

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get languages: {e}")
        return None


def get_example(language: str):
    """Get example code for a language"""
    try:
        response = requests.get(f"{BASE_URL}/compile/example/{language}")
        response.raise_for_status()
        result = response.json()

        print(f"📖 {result['message']}\n")
        print(f"Description: {result['example']['description']}\n")
        print("Code:")
        print("-" * 80)
        print(result["example"]["code"])
        print("-" * 80 + "\n")

        return result["example"]["code"]

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get example: {e}")
        return None


def demo_python():
    """Demo Python execution"""
    print_banner("🐍 PYTHON SERPENT MAGIC")

    code = """
# Python ceremonial spell
import random

spells = ["Fireball", "Lightning Bolt", "Ice Storm"]

print("🔮 Casting mystical spells...")
for spell in spells:
    power = random.randint(50, 100)
    print(f"  ⚡ {spell}: {power} damage!")

print("✨ All spells cast successfully!")
"""

    execute_code(code.strip(), "python")


def demo_javascript():
    """Demo JavaScript execution"""
    print_banner("⚡ JAVASCRIPT LIGHTNING SPELL")

    code = """
// JavaScript electrical incantation
const elements = ['Fire', 'Water', 'Earth', 'Air'];

console.log('⚡ Channeling elemental energies...');
elements.forEach((elem, i) => {
    console.log(`  🌟 Element ${i + 1}: ${elem}`);
});

console.log('✨ Elemental harmony achieved!');
"""

    execute_code(code.strip(), "javascript")


def demo_bash():
    """Demo Bash execution"""
    print_banner("🌍 BASH EARTH INCANTATION")

    code = """
#!/bin/bash
echo "🌍 The earth trembles with ancient power..."

for i in {1..3}; do
    echo "  🗿 Stone guardian $i awakens!"
    sleep 0.1
done

echo "✨ The earth spirits are appeased!"
"""

    execute_code(code.strip(), "bash")


def demo_dry_run():
    """Demo dry-run mode"""
    print_banner("🛡️ DRY-RUN MODE (SAFE DEMO)")

    code = """
# This code will NOT execute
import os
os.system("echo 'This is safe in dry-run mode'")
print("This line won't run either")
"""

    execute_code(code.strip(), "python", dry_run=True)


def main():
    """Main demo function"""
    print("\n" + "🔮" * 40)
    print(" " * 10 + "ARCANE OS - VIBE COMPILER DEMO")
    print("🔮" * 40 + "\n")

    print("Welcome to the VibeCompiler demonstration!")
    print("This script showcases code execution with fantasy-themed narration.\n")

    # Check server
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ ArcaneOS server is running\n")
    except:
        print("❌ ERROR: ArcaneOS server is not running!")
        print("   Please start it with: uvicorn app.main:app --reload\n")
        return

    # Get supported languages
    print_banner("📚 SUPPORTED LANGUAGES")
    languages = get_supported_languages()

    if not languages:
        return

    time.sleep(2)

    # Demo each language
    demos = [
        demo_python,
        demo_javascript,
        demo_bash,
        demo_dry_run
    ]

    for demo_func in demos:
        demo_func()
        time.sleep(2)

    # Final message
    print_banner("🌟 DEMONSTRATION COMPLETE")
    print("The VibeCompiler has demonstrated its mystical powers!")
    print("All code has been executed with ceremonial flair.\n")
    print("Try it yourself:")
    print("  POST /compile/execute - Execute code with narration")
    print("  POST /compile/dry-run - Validate without executing")
    print("  GET  /compile/languages - List supported languages")
    print("  GET  /compile/example/{lang} - Get example code\n")
    print("May your code compile swiftly and your bugs be few! ✨\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✨ Demonstration interrupted. Farewell! ✨\n")
