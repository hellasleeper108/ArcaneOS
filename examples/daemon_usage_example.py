"""
Example Usage of ArcaneOS Daemon Registry

This script demonstrates how to interact with the enhanced DaemonRegistry,
including registration, invocation through Raindrop MCP, and banishment.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.daemon_registry import daemon_registry
from app.models.daemon import DaemonType


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_basic_workflow():
    """Demonstrate basic daemon workflow: summon -> invoke -> banish"""

    print_section("BASIC DAEMON WORKFLOW")

    # 1. Summon Claude
    print("1. Summoning Claude daemon...")
    claude = daemon_registry.summon(DaemonType.CLAUDE)
    print(f"   ✓ Daemon summoned: {claude.name.value}")
    print(f"   ✓ Role: {claude.role}")
    print(f"   ✓ Color: {claude.color_code}")
    print(f"   ✓ Is summoned: {claude.is_summoned}")

    # 2. Invoke Claude with a task
    print("\n2. Invoking Claude with a task...")
    result = daemon_registry.invoke_daemon(
        name=DaemonType.CLAUDE,
        task="Analyze the security implications of this authentication system",
        parameters={"complexity": "high", "depth": "comprehensive"}
    )
    print(f"   ✓ Invocation successful!")
    print(f"   ✓ Execution time: {result['execution_time']:.3f}s")
    print(f"   ✓ Model output: {result['result']['output'][:100]}...")

    # 3. Invoke again
    print("\n3. Second invocation...")
    result2 = daemon_registry.invoke_daemon(
        name=DaemonType.CLAUDE,
        task="Generate unit tests for a REST API endpoint"
    )
    print(f"   ✓ Invocation #{result2['invocation_number']} completed")
    print(f"   ✓ Execution time: {result2['execution_time']:.3f}s")

    # 4. Banish Claude
    print("\n4. Banishing Claude daemon...")
    banish_result = daemon_registry.banish_daemon(DaemonType.CLAUDE)
    print(f"   ✓ Daemon banished: {banish_result['message']}")
    print(f"   ✓ Total invocations: {banish_result['statistics']['total_invocations']}")
    print(f"   ✓ Total execution time: {banish_result['statistics']['total_execution_time']:.3f}s")


def example_multiple_daemons():
    """Demonstrate working with multiple daemons simultaneously"""

    print_section("MULTIPLE DAEMONS WORKFLOW")

    # Summon all three daemons
    print("1. Summoning all three daemons...\n")

    claude = daemon_registry.summon(DaemonType.CLAUDE)
    print(f"   ✓ {claude.name.value} summoned - {claude.role}")

    gemini = daemon_registry.summon(DaemonType.GEMINI)
    print(f"   ✓ {gemini.name.value} summoned - {gemini.role}")

    liquidmetal = daemon_registry.summon(DaemonType.LIQUIDMETAL)
    print(f"   ✓ {liquidmetal.name.value} summoned - {liquidmetal.role}")

    # Check active daemons
    print("\n2. Checking active daemons...")
    active = daemon_registry.get_active_daemons()
    print(f"   ✓ {len(active)} daemons currently active")

    # Invoke each daemon with different tasks
    print("\n3. Invoking daemons with specialized tasks...\n")

    # Claude for analysis
    r1 = daemon_registry.invoke_daemon(
        DaemonType.CLAUDE,
        "Analyze algorithm complexity"
    )
    print(f"   ✓ Claude: {r1['execution_time']:.3f}s")

    # Gemini for creativity
    r2 = daemon_registry.invoke_daemon(
        DaemonType.GEMINI,
        "Design innovative UI component"
    )
    print(f"   ✓ Gemini: {r2['execution_time']:.3f}s")

    # LiquidMetal for transformation
    r3 = daemon_registry.invoke_daemon(
        DaemonType.LIQUIDMETAL,
        "Transform data format"
    )
    print(f"   ✓ LiquidMetal: {r3['execution_time']:.3f}s")

    # Get statistics
    print("\n4. Registry statistics...")
    stats = daemon_registry.get_registry_statistics()
    print(f"   ✓ Active daemons: {stats['active_daemons']}")
    print(f"   ✓ Total invocations: {stats['total_invocations']}")
    print(f"   ✓ MCP registered: {stats['mcp_registered_daemons']}")

    # Banish all
    print("\n5. Banishing all daemons...\n")
    for daemon_type in [DaemonType.CLAUDE, DaemonType.GEMINI, DaemonType.LIQUIDMETAL]:
        result = daemon_registry.banish_daemon(daemon_type)
        stats = result['statistics']
        print(f"   ✓ {daemon_type.value}: {stats['total_invocations']} invocations, "
              f"{stats['total_execution_time']:.3f}s total time")


def example_custom_registration():
    """Demonstrate custom daemon registration with specific models"""

    print_section("CUSTOM DAEMON REGISTRATION")

    print("1. Registering Claude with custom model configuration...")

    # Register with specific model
    daemon = daemon_registry.register_daemon(
        name=DaemonType.CLAUDE,
        model="claude-3-opus-20240229",  # Custom model
        role="Master of Deep Analysis",
        capabilities=["deep_reasoning", "complex_analysis", "research"]
    )

    print(f"   ✓ Registered: {daemon.name.value}")
    print(f"   ✓ Model: {daemon.metadata.get('model')}")
    print(f"   ✓ Role: {daemon.role}")

    # Check registration status
    state = daemon_registry.get_daemon_state(DaemonType.CLAUDE)
    print(f"   ✓ MCP Registered: {state.mcp_registered}")


def example_state_tracking():
    """Demonstrate comprehensive state tracking"""

    print_section("STATE TRACKING & STATISTICS")

    # Summon and use a daemon multiple times
    print("1. Summoning Gemini and performing multiple invocations...\n")

    daemon = daemon_registry.summon(DaemonType.GEMINI)

    tasks = [
        "Create a creative landing page design",
        "Generate innovative product ideas",
        "Design a unique logo concept",
        "Brainstorm marketing campaign themes"
    ]

    for i, task in enumerate(tasks, 1):
        result = daemon_registry.invoke_daemon(DaemonType.GEMINI, task)
        print(f"   ✓ Invocation {i}: {result['execution_time']:.3f}s")

    # Get detailed state
    print("\n2. Daemon state inspection...")
    state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
    stats = state.get_statistics()

    print(f"   ✓ Daemon: {stats['daemon_name']}")
    print(f"   ✓ Active: {stats['is_active']}")
    print(f"   ✓ Total invocations: {stats['total_invocations']}")
    print(f"   ✓ Total execution time: {stats['total_execution_time']:.3f}s")
    print(f"   ✓ Average execution time: {stats['average_execution_time']:.3f}s")
    print(f"   ✓ Summoned at: {stats['summoned_at']}")

    # Show invocation history
    print("\n3. Recent invocation history:")
    for i, inv in enumerate(state.invocation_history[-3:], 1):
        print(f"   {i}. Task: {inv['task'][:40]}...")
        print(f"      Time: {inv['execution_time']:.3f}s | Success: {inv['success']}")

    # Cleanup
    daemon_registry.banish_daemon(DaemonType.GEMINI)


def example_error_handling():
    """Demonstrate error handling scenarios"""

    print_section("ERROR HANDLING")

    print("1. Attempting to invoke unsummoned daemon...")
    try:
        daemon_registry.invoke_daemon(DaemonType.CLAUDE, "Test task")
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}")
        print(f"   ✓ Message: {str(e)[:60]}...")

    print("\n2. Attempting to summon already summoned daemon...")
    daemon_registry.summon(DaemonType.CLAUDE)
    try:
        daemon_registry.summon(DaemonType.CLAUDE)
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}")

    print("\n3. Attempting to banish unsummoned daemon...")
    daemon_registry.banish_daemon(DaemonType.CLAUDE)
    try:
        daemon_registry.banish_daemon(DaemonType.CLAUDE)
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}")


def main():
    """Run all examples"""

    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ARCANEOS DAEMON REGISTRY EXAMPLES" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run each example
    try:
        example_basic_workflow()
        example_multiple_daemons()
        example_custom_registration()
        example_state_tracking()
        example_error_handling()

        print_section("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("The mystical demonstrations have concluded.\n")

    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
