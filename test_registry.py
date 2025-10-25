"""
Quick validation test for the Enhanced Daemon Registry

Run this to verify core functionality works correctly.
"""

import sys
from app.services.daemon_registry import daemon_registry
from app.models.daemon import DaemonType


def test_registration():
    """Test daemon registration"""
    print("Testing daemon registration...")

    daemon = daemon_registry.register_daemon(
        name=DaemonType.CLAUDE,
        model="claude-3-5-sonnet-20241022",
        role="Test Role",
        capabilities=["test"]
    )

    assert daemon.name == DaemonType.CLAUDE
    assert daemon.metadata["model"] == "claude-3-5-sonnet-20241022"

    state = daemon_registry.get_daemon_state(DaemonType.CLAUDE)
    assert state.mcp_registered == True

    print("✓ Registration test passed")


def test_summon():
    """Test daemon summoning"""
    print("Testing daemon summoning...")

    # Ensure not summoned
    daemon = daemon_registry.get_daemon(DaemonType.GEMINI)
    if daemon.is_summoned:
        daemon_registry.banish_daemon(DaemonType.GEMINI)

    # Summon
    daemon = daemon_registry.summon(DaemonType.GEMINI)

    assert daemon.is_summoned == True
    assert daemon.invocation_count == 0

    state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
    assert state.summoned_at is not None
    assert state.mcp_registered == True

    print("✓ Summon test passed")


def test_invoke():
    """Test daemon invocation"""
    print("Testing daemon invocation...")

    result = daemon_registry.invoke_daemon(
        name=DaemonType.GEMINI,
        task="Test task",
        parameters={"test": "param"}
    )

    assert result["success"] == True
    assert result["daemon"].invocation_count == 1
    assert "result" in result
    assert "execution_time" in result

    state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
    assert len(state.invocation_history) == 1
    assert state.last_invoked_at is not None

    print("✓ Invoke test passed")


def test_state_tracking():
    """Test state tracking"""
    print("Testing state tracking...")

    # Multiple invocations
    for i in range(3):
        daemon_registry.invoke_daemon(
            DaemonType.GEMINI,
            f"Task {i}"
        )

    state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
    stats = state.get_statistics()

    assert stats["total_invocations"] == 4  # 1 from previous test + 3 new
    assert stats["is_active"] == True
    assert stats["average_execution_time"] > 0

    print("✓ State tracking test passed")


def test_banish():
    """Test daemon banishment"""
    print("Testing daemon banishment...")

    result = daemon_registry.banish_daemon(DaemonType.GEMINI)

    assert result["daemon"].is_summoned == False
    assert "statistics" in result
    assert result["statistics"]["total_invocations"] == 4

    state = daemon_registry.get_daemon_state(DaemonType.GEMINI)
    assert state.mcp_registered == False

    print("✓ Banish test passed")


def test_multiple_daemons():
    """Test multiple daemon management"""
    print("Testing multiple daemons...")

    # Summon all
    daemon_registry.summon(DaemonType.CLAUDE)
    daemon_registry.summon(DaemonType.GEMINI)
    daemon_registry.summon(DaemonType.LIQUIDMETAL)

    # Check active
    active = daemon_registry.get_active_daemons()
    assert len(active) == 3

    # Get statistics
    stats = daemon_registry.get_registry_statistics()
    assert stats["active_daemons"] == 3
    assert stats["total_daemons"] == 3

    # Cleanup
    daemon_registry.banish_daemon(DaemonType.CLAUDE)
    daemon_registry.banish_daemon(DaemonType.GEMINI)
    daemon_registry.banish_daemon(DaemonType.LIQUIDMETAL)

    print("✓ Multiple daemons test passed")


def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")

    # Try to invoke unsummoned daemon
    try:
        daemon_registry.invoke_daemon(DaemonType.CLAUDE, "Should fail")
        assert False, "Should have raised exception"
    except Exception as e:
        assert "slumbers in the void" in str(e) or "400" in str(e)

    # Try to summon twice
    daemon_registry.summon(DaemonType.CLAUDE)
    try:
        daemon_registry.summon(DaemonType.CLAUDE)
        assert False, "Should have raised exception"
    except Exception as e:
        assert "already walks" in str(e) or "400" in str(e)

    # Cleanup
    daemon_registry.banish_daemon(DaemonType.CLAUDE)

    print("✓ Error handling test passed")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  ARCANEOS DAEMON REGISTRY - VALIDATION TESTS")
    print("=" * 70 + "\n")

    try:
        test_registration()
        test_summon()
        test_invoke()
        test_state_tracking()
        test_banish()
        test_multiple_daemons()
        test_error_handling()

        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 70 + "\n")

        print("The Enhanced Daemon Registry is working correctly.")
        print("You can now start the server with: python -m app.main\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
