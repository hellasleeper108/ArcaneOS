"""
HTTP API Usage Examples for ArcaneOS

This script demonstrates how to interact with the ArcaneOS API
via HTTP requests using the requests library.
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_response(response: requests.Response):
    """Pretty print an HTTP response"""
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def example_basic_flow():
    """Demonstrate basic API flow"""

    print_section("BASIC API FLOW")

    # 1. Check server health
    print("1. Checking server health...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

    # 2. List all daemons
    print("\n2. Listing all daemons...")
    response = requests.get(f"{BASE_URL}/daemons")
    print_response(response)

    # 3. Summon Claude
    print("\n3. Summoning Claude daemon...")
    response = requests.post(
        f"{BASE_URL}/summon",
        json={"daemon_name": "claude"}
    )
    print_response(response)

    # 4. Invoke Claude
    print("\n4. Invoking Claude with task...")
    response = requests.post(
        f"{BASE_URL}/invoke",
        json={
            "daemon_name": "claude",
            "task": "Analyze the performance characteristics of binary search trees",
            "parameters": {
                "depth": "comprehensive",
                "include_examples": True
            }
        }
    )
    print_response(response)

    # 5. Get daemon state
    print("\n5. Getting Claude's state...")
    response = requests.get(f"{BASE_URL}/daemon/claude/state")
    print_response(response)

    # 6. Banish Claude
    print("\n6. Banishing Claude...")
    response = requests.post(
        f"{BASE_URL}/banish",
        json={"daemon_name": "claude"}
    )
    print_response(response)


def example_multiple_daemons():
    """Work with multiple daemons"""

    print_section("MULTIPLE DAEMONS")

    daemons = ["claude", "gemini", "liquidmetal"]

    # Summon all
    print("1. Summoning all daemons...\n")
    for daemon in daemons:
        response = requests.post(
            f"{BASE_URL}/summon",
            json={"daemon_name": daemon}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {daemon}: {data['status']}")

    # Check active daemons
    print("\n2. Listing active daemons...")
    response = requests.get(f"{BASE_URL}/daemons/active")
    print_response(response)

    # Invoke each with specialized tasks
    print("\n3. Invoking daemons with specialized tasks...\n")

    tasks = {
        "claude": "Explain the CAP theorem in distributed systems",
        "gemini": "Create a color palette for a nature-themed app",
        "liquidmetal": "Transform XML data to JSON format"
    }

    for daemon, task in tasks.items():
        response = requests.post(
            f"{BASE_URL}/invoke",
            json={"daemon_name": daemon, "task": task}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {daemon}: invoked successfully")

    # Get statistics
    print("\n4. Getting registry statistics...")
    response = requests.get(f"{BASE_URL}/statistics")
    print_response(response)

    # Banish all
    print("\n5. Banishing all daemons...\n")
    for daemon in daemons:
        response = requests.post(
            f"{BASE_URL}/banish",
            json={"daemon_name": daemon}
        )
        if response.status_code == 200:
            print(f"   ✓ {daemon}: banished")


def example_performance_tracking():
    """Track performance across multiple invocations"""

    print_section("PERFORMANCE TRACKING")

    # Summon daemon
    print("1. Summoning Gemini for performance testing...")
    requests.post(f"{BASE_URL}/summon", json={"daemon_name": "gemini"})

    # Multiple invocations
    print("\n2. Performing 5 invocations...\n")
    execution_times = []

    for i in range(1, 6):
        response = requests.post(
            f"{BASE_URL}/invoke",
            json={
                "daemon_name": "gemini",
                "task": f"Generate creative idea #{i}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            # Extract execution time from message or daemon state
            print(f"   ✓ Invocation {i} completed")

        time.sleep(0.5)  # Small delay between requests

    # Get final statistics
    print("\n3. Final statistics...")
    response = requests.get(f"{BASE_URL}/daemon/gemini/state")
    if response.status_code == 200:
        data = response.json()
        stats = data['daemon_state']['statistics']
        print(f"\n   Total invocations: {stats['total_invocations']}")
        print(f"   Total execution time: {stats['total_execution_time']:.3f}s")
        print(f"   Average execution time: {stats['average_execution_time']:.3f}s")

    # Cleanup
    requests.post(f"{BASE_URL}/banish", json={"daemon_name": "gemini"})


def example_error_handling():
    """Demonstrate error handling"""

    print_section("ERROR HANDLING")

    # Try to invoke without summoning
    print("1. Attempting to invoke unsummoned daemon...")
    response = requests.post(
        f"{BASE_URL}/invoke",
        json={
            "daemon_name": "claude",
            "task": "This should fail"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ✓ Expected error: {response.json()['detail']}")

    # Try to summon twice
    print("\n2. Attempting to summon daemon twice...")
    requests.post(f"{BASE_URL}/summon", json={"daemon_name": "claude"})
    response = requests.post(
        f"{BASE_URL}/summon",
        json={"daemon_name": "claude"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ✓ Expected error: {response.json()['detail']}")

    # Cleanup
    requests.post(f"{BASE_URL}/banish", json={"daemon_name": "claude"})


def example_comprehensive_workflow():
    """Complete workflow with all features"""

    print_section("COMPREHENSIVE WORKFLOW")

    print("1. Initial setup - checking server...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   ✓ Server status: {response.json()['status']}\n")

    print("2. Daemon lifecycle: Gemini")
    print("   a) Summoning...")
    requests.post(f"{BASE_URL}/summon", json={"daemon_name": "gemini"})

    print("   b) Multiple invocations with different parameters...")
    for i in range(3):
        requests.post(
            f"{BASE_URL}/invoke",
            json={
                "daemon_name": "gemini",
                "task": f"Creative task iteration {i+1}",
                "parameters": {"iteration": i+1, "creativity_level": "high"}
            }
        )

    print("   c) Checking state...")
    response = requests.get(f"{BASE_URL}/daemon/gemini/state")
    state_data = response.json()
    print(f"   ✓ Invocations: {state_data['daemon_state']['statistics']['total_invocations']}")

    print("   d) Banishing with statistics...")
    response = requests.post(f"{BASE_URL}/banish", json={"daemon_name": "gemini"})
    print(f"   ✓ Banished: {response.json()['status']}\n")

    print("3. Final registry state...")
    response = requests.get(f"{BASE_URL}/statistics")
    stats = response.json()['statistics']
    print(f"   ✓ Total daemons: {stats['total_daemons']}")
    print(f"   ✓ Active daemons: {stats['active_daemons']}")
    print(f"   ✓ Total invocations: {stats['total_invocations']}")


def main():
    """Run all examples"""

    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "ARCANEOS HTTP API EXAMPLES" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")

    print(f"\nBase URL: {BASE_URL}")
    print("Make sure the ArcaneOS server is running!\n")

    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Server not responding correctly!")
            return

    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server!")
        print("   Please start the server with: python -m app.main")
        return

    # Run examples
    try:
        example_basic_flow()
        example_multiple_daemons()
        example_performance_tracking()
        example_error_handling()
        example_comprehensive_workflow()

        print_section("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("The mystical HTTP demonstrations have concluded.\n")

    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
