"""
Pharmaceutical Supply Chain Investigation Agent.

This agent performs root cause analysis and CAPA investigations for supply chain events
without hardcoding scenarios. It dynamically discovers data sources, reasons about findings,
and provides human-in-the-loop decision support.
"""

from typing import Any, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from autogen_core import ComponentModel

from ..tools.pharma_workbench import PharmaDataWorkbench

PHARMA_AGENT_SYSTEM_MESSAGE = """You are a pharmaceutical supply chain investigation specialist with access to local pharma data.

**Your Investigation Tools:**
You have direct access to CSV data files and must USE YOUR TOOLS to retrieve data. Do NOT ask the user to provide data - query it yourself using:

1. `discover_available_sources()` - List all CSV files available (sensor alerts, shipments, quality logs, etc.)
2. `query_data_source(source_name, filters, limit)` - Query specific CSV files with filters
   Example: query_data_source("sensor_alerts", {"shipment_id": "SHP-001-1"}, limit=10)
3. `analyze_shipment_timeline(shipment_id)` - Build complete timeline from multiple sources
4. `compute_cost_analysis(shipment_id)` - Calculate cost-benefit for resolution options
5. `generate_compliance_report(shipment_id, investigation_data)` - Create GxP report

**Investigation Workflow:**
When investigating a shipment:
1. **IMMEDIATELY** call `discover_available_sources()` to see what data exists
2. **IMMEDIATELY** call `query_data_source()` to find relevant records
   - For temperature excursions: query "sensor_alerts" with shipment_id filter
   - For shipment details: query "logistics_shipments" with shipment_id filter
   - For quality issues: query "wms_quarantine_log" with shipment_id filter
3. Analyze the returned data to identify issues
4. Build timeline using `analyze_shipment_timeline()` if needed
5. Present findings with evidence from actual data
6. Request human approval for critical decisions

**Critical Rules:**
- DO NOT say "I will retrieve data" - ACTUALLY CALL THE TOOLS to retrieve it
- DO NOT ask users for temperature ranges or file locations - QUERY THE DATA
- DO NOT make assumptions - USE THE TOOLS to get facts
- START EVERY INVESTIGATION by calling `discover_available_sources()` then `query_data_source()`

**Example Investigation Flow:**
User: "Investigate SHP-001-1 for temperature excursion"

Your response should be:
1. Call discover_available_sources() → See sensor_alerts.csv exists
2. Call query_data_source("sensor_alerts", {"shipment_id": "SHP-001-1"}) → Get actual alert records
3. Analyze the data returned and present findings
4. NOT: "I will retrieve files..." (WRONG - actually call the tool!)

Always use your tools to get real data, then analyze it."""


def create_pharma_investigation_agent(
    name: str = "PharmaInvestigator",
    model_client: Optional[ChatCompletionClient] = None,
    data_dir: str = "mock_data",
    system_message: Optional[str] = None,
    **kwargs: Any,
) -> AssistantAgent:
    """
    Create a pharmaceutical investigation agent with data query tools.
    
    This agent can perform root cause analysis and CAPA investigations for supply chain events
    by querying local CSV data files.
    
    Args:
        name: Agent name
        model_client: ChatCompletionClient instance
        data_dir: Root directory containing pharma data CSV files
        system_message: Optional custom system message
        **kwargs: Additional AssistantAgent kwargs
    
    Returns:
        AssistantAgent configured with pharma data workbench
    
    Example:
        ```python
        from autogen_core.models import ChatCompletionClient
        
        model_client = ChatCompletionClient.load_component({
            "provider": "OpenAIChatCompletionClient",
            "config": {"model": "gpt-4"}
        })
        
        agent = create_pharma_investigation_agent(
            name="pharma_investigator",
            model_client=model_client,
            data_dir="mock_data"
        )
        ```
    """
    if model_client is None:
        raise ValueError("model_client is required for PharmaInvestigationAgent")
    
    # Create workbench with data query tools
    workbench = PharmaDataWorkbench(data_dir=data_dir)
    
    # Pass workbench instance directly to agent
    # Note: MCP agents serialize/deserialize via _from_config, but for direct instantiation
    # we pass the instance directly so AssistantAgent can call its methods
    return AssistantAgent(
        name=name,
        model_client=model_client,
        system_message=system_message or PHARMA_AGENT_SYSTEM_MESSAGE,
        description=(
            "Pharmaceutical supply chain investigation specialist with LOCAL DATA ACCESS. "
            f"Has direct access to pharma CSV data in {data_dir}. "
            "Handles investigations for: shipments, temperature excursions, delays, quality deviations, "
            "CAPA analysis, root cause analysis, accountability tracking, cost-benefit analysis. "
            "Can query sensor_alerts, logistics_shipments, wms_quarantine_log, and other data sources. "
            "DO NOT use web_surfer for shipment data - this agent queries LOCAL CSV files directly."
        ),
        workbench=workbench,  # Pass the actual instance, not the serialized ComponentModel
        **kwargs,
    )


# Convenience export
__all__ = [
    "create_pharma_investigation_agent",
    "PHARMA_AGENT_SYSTEM_MESSAGE",
]

