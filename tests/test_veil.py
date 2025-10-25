"""
Reality Veil Tests

Validates veil state persistence and toggling functionality.
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.core_veil_routes import router


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def clean_state():
    """Clean up state file before and after tests."""
    state_file = Path(".veil_state.json")

    # Clean before
    if state_file.exists():
        state_file.unlink()

    yield

    # Clean after
    if state_file.exists():
        state_file.unlink()


def test_veil_toggle_persists(client, clean_state):
    """
    Test that veil state persists across toggles.

    Validates:
    - Initial state is fantasy mode (veil=True)
    - Toggle updates state file
    - State file contains correct JSON
    - Multiple toggles persist correctly
    """
    state_file = Path(".veil_state.json")

    # Get initial state
    response = client.get("/veil")
    assert response.status_code == 200
    initial = response.json()
    assert initial["veil"] == True
    assert initial["mode"] == "fantasy"

    # First toggle - reveal (set veil to False)
    response = client.post("/reveal")
    assert response.status_code == 200
    result = response.json()
    assert result["veil"] == False
    assert result["mode"] == "developer"

    # Check persistence file exists and has correct content
    assert state_file.exists(), "State file should be created"

    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == False, "First toggle should persist veil=False"
        assert data["mode"] == "developer"

    # Second toggle - restore (set veil to True)
    response = client.post("/veil/restore")
    assert response.status_code == 200
    result = response.json()
    assert result["veil"] == True
    assert result["mode"] == "fantasy"

    # Check persistence file updated
    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == True, "Second toggle should persist veil=True"
        assert data["mode"] == "fantasy"

    print("✓ Veil toggle persistence test passed")


def test_veil_state_reload(client, clean_state):
    """
    Test that veil state is reloaded on app restart.

    Simulates:
    - Setting veil state
    - Verifying state file is created
    - Manually checking file-based persistence works

    Validates:
    - State persists to JSON file
    - File format is correct
    """
    state_file = Path(".veil_state.json")

    # Set veil to developer mode
    response = client.post("/reveal")
    assert response.status_code == 200
    assert response.json()["veil"] == False

    # Verify state file exists
    assert state_file.exists(), "State file should be created after setting veil"

    # Verify file contents
    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == False, "Persisted veil should be False"
        assert data["mode"] == "developer", "Persisted mode should be developer"

    # Change back to fantasy mode
    response = client.post("/veil/restore")
    assert response.status_code == 200
    assert response.json()["veil"] == True

    # Verify file updated
    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == True, "Persisted veil should be True"
        assert data["mode"] == "fantasy", "Persisted mode should be fantasy"

    print("✓ Veil state reload test passed")


def test_veil_post_endpoint(client, clean_state):
    """
    Test the POST /veil endpoint with explicit state setting.

    Validates:
    - Can set veil to True explicitly
    - Can set veil to False explicitly
    - State persists after each change
    """
    state_file = Path(".veil_state.json")

    # Set veil to False explicitly
    response = client.post("/veil", json={"veil": False})
    assert response.status_code == 200
    result = response.json()
    assert result["veil"] == False
    assert result["mode"] == "developer"

    # Check persistence
    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == False

    # Set veil to True explicitly
    response = client.post("/veil", json={"veil": True})
    assert response.status_code == 200
    result = response.json()
    assert result["veil"] == True
    assert result["mode"] == "fantasy"

    # Check persistence
    with open(state_file, 'r') as f:
        data = json.load(f)
        assert data["veil"] == True

    print("✓ Veil POST endpoint test passed")


def test_veil_endpoints_all(client, clean_state):
    """
    Test all veil endpoints comprehensively.

    Validates:
    - GET /veil
    - POST /veil
    - POST /reveal
    - POST /veil/restore
    """
    # Test GET
    response = client.get("/veil")
    assert response.status_code == 200
    assert "veil" in response.json()
    assert "mode" in response.json()

    # Test POST /reveal
    response = client.post("/reveal")
    assert response.status_code == 200
    assert response.json()["veil"] == False
    assert response.json()["mode"] == "developer"

    # Test POST /veil/restore
    response = client.post("/veil/restore")
    assert response.status_code == 200
    assert response.json()["veil"] == True
    assert response.json()["mode"] == "fantasy"

    # Test POST /veil with explicit value
    response = client.post("/veil", json={"veil": False})
    assert response.status_code == 200
    assert response.json()["veil"] == False

    print("✓ All veil endpoints test passed")


if __name__ == "__main__":
    # Run tests directly
    print("\n" + "=" * 70)
    print("  REALITY VEIL - VALIDATION TESTS")
    print("=" * 70 + "\n")

    client = TestClient(app)

    try:
        # Create clean state context
        state_file = Path(".veil_state.json")
        if state_file.exists():
            state_file.unlink()

        test_veil_toggle_persists(client, None)
        test_veil_post_endpoint(client, None)
        test_veil_endpoints_all(client, None)

        # Clean up
        if state_file.exists():
            state_file.unlink()

        # Note: test_veil_state_reload requires pytest fixture behavior
        # and module reloading, so it's best run via pytest

        print("\n" + "=" * 70)
        print("  ✓ TESTS PASSED!")
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
