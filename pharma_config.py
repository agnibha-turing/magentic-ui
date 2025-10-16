"""
Configuration to enable the Pharma Investigation Agent.

Use this when starting magentic-ui to enable pharma investigations.
"""

from magentic_ui import MagenticUIConfig

# Configuration with pharma agent enabled
pharma_config = MagenticUIConfig(
    # Enable pharma agent
    pharma_agent_enabled=True,
    pharma_data_dir="mock_data",
    
    # Standard magentic-ui settings
    cooperative_planning=True,
    autonomous_execution=False,
    approval_policy="auto-conservative",
    max_turns=30,
    
    # For local testing
    run_without_docker=False,  # Set to True if docker not available
)

