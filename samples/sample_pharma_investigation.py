"""
Sample script demonstrating the Pharmaceutical Investigation Agent.

This shows how to use the PharmaInvestigationAgent to perform root cause analysis
and CAPA investigations for supply chain events with human-in-the-loop approval.

The agent dynamically discovers data sources, queries them, builds timelines,
and provides evidence-based recommendations - all without hardcoding scenarios.

Usage:
    python sample_pharma_investigation.py

Prerequisites:
    - Data files in mock_data/ directory
    - OpenAI API key set (OPENAI_API_KEY environment variable)
"""

import asyncio
from pathlib import Path

from magentic_ui import MagenticUIConfig
from magentic_ui.task_team import get_task_team
from magentic_ui.types import RunPaths


async def investigate_shipment(shipment_id: str):
    """
    Run a pharma investigation for a specific shipment.
    
    Args:
        shipment_id: The shipment ID to investigate (e.g., "SHP-001-1")
    """
    
    # Configure magentic-ui with pharma agent enabled
    config = MagenticUIConfig(
        pharma_agent_enabled=True,
        pharma_data_dir="mock_data",
        cooperative_planning=False,  # Disable for simpler testing
        autonomous_execution=True,  # Let agent work autonomously
        approval_policy="never",  # No approval needed for testing
        max_turns=10,
        user_proxy_type="dummy",  # For testing without real user input
        run_without_docker=True,  # Simpler for testing
    )
    
    # Setup paths
    current_dir = Path.cwd()
    paths = RunPaths(
        internal_root_dir=current_dir,
        external_root_dir=current_dir,
        internal_run_dir=current_dir / "test_run",
        external_run_dir=current_dir / "test_run",
    )
    paths.internal_run_dir.mkdir(exist_ok=True)
    
    # Create team with pharma agent
    print("🔬 Initializing pharmaceutical investigation team...")
    team = await get_task_team(config, paths=paths)
    
    # Run investigation
    investigation_prompt = f"""
    Please investigate the following pharma supply chain scenario:
    
    Shipment {shipment_id} was flagged for a temperature excursion during transit.
    
    Please provide:
    1. What happened? (summarize the event)
    2. Who is accountable? (carrier, QA team, supplier, etc.)
    3. What are the resolution options? (release, reject, reship)
    4. What is your recommendation with rationale?
    5. What preventive actions should be taken?
    
    Think step-by-step and provide a structured analysis.
    """
    
    print(f"\n📦 Starting investigation for shipment: {shipment_id}")
    print("=" * 70)
    
    # Start investigation
    result = await team.run(task=investigation_prompt)
    
    print("\n" + "=" * 70)
    print("✅ Investigation complete!")
    print(f"📊 Messages exchanged: {len(result.messages)}")
    
    # Print summary
    print("\n📝 Investigation Summary:")
    if result.messages:
        for i, msg in enumerate(result.messages[-3:], 1):  # Show last 3 messages
            print(f"\n--- Message {i} (from {msg.source}) ---")
            print(msg.content[:500] + "..." if len(msg.content) > 500 else msg.content)
    
    return result


async def demo_dynamic_investigation():
    """
    Demo showing how the agent works without hardcoded scenarios.
    """
    print("\n" + "=" * 70)
    print("🧪 DEMO: Dynamic Pharma Investigation Agent")
    print("=" * 70)
    print("\nThis agent demonstrates:")
    print("✓ No hardcoded scenarios - discovers data dynamically")
    print("✓ Queries multiple CSV sources to build complete picture")
    print("✓ Performs root cause analysis from evidence")
    print("✓ Provides human-in-the-loop decision support")
    print("✓ Generates GxP-compliant documentation")
    print("=" * 70 + "\n")
    
    # Example investigations
    shipments_to_investigate = [
        "SHP-001-1",  # From sample.json - temperature excursion case
        # Add more shipment IDs to test with different scenarios
    ]
    
    for shipment_id in shipments_to_investigate:
        try:
            await investigate_shipment(shipment_id)
        except Exception as e:
            print(f"\n❌ Error investigating {shipment_id}: {e}")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """
    Main entry point for the demo.
    """
    # Check if data directory exists
    data_dir = Path("mock_data")
    if not data_dir.exists():
        print("❌ Error: mock_data directory not found!")
        print("Please ensure mock_data/ directory exists in the current directory.")
        return
    
    print("✓ Found mock_data directory")
    print(f"✓ Data sources available: {len(list(data_dir.rglob('*.csv')))} CSV files")
    
    # Run the demo
    asyncio.run(demo_dynamic_investigation())


if __name__ == "__main__":
    main()

