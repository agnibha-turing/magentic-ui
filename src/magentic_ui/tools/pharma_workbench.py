"""
Workbench for pharmaceutical data query tools.

This provides a tool interface for the pharma investigation agent following
the MCP workbench pattern used in magentic-ui.
"""

from typing import Any, Literal, Mapping, Sequence
from autogen_core.tools import ToolSchema, Workbench, ToolResult, TextResultContent
from autogen_core import CancellationToken, Component
from pydantic import BaseModel

from .pharma_data import (
    analyze_shipment_timeline,
    compute_cost_analysis,
    discover_available_sources,
    generate_compliance_report,
    query_data_source,
)


class PharmaDataWorkbenchConfig(BaseModel):
    """Configuration for PharmaDataWorkbench."""
    data_dir: str = "mock_data"


class PharmaDataWorkbenchState(BaseModel):
    """State for PharmaDataWorkbench."""
    type: Literal["PharmaDataWorkbenchState"] = "PharmaDataWorkbenchState"


class PharmaDataWorkbench(Workbench, Component[PharmaDataWorkbenchConfig]):
    """
    Workbench providing pharmaceutical data query tools.
    
    This follows the workbench pattern used by MCP agents in magentic-ui,
    providing a standardized interface for tool registration and execution.
    """
    
    component_provider_override = "magentic_ui.tools.pharma_workbench.PharmaDataWorkbench"
    component_config_schema = PharmaDataWorkbenchConfig
    
    def __init__(self, data_dir: str = "mock_data"):
        """
        Initialize the pharma data workbench.
        
        Args:
            data_dir: Root directory containing pharmaceutical data CSV files
        """
        self.data_dir = data_dir
        self._config = PharmaDataWorkbenchConfig(data_dir=data_dir)
        
        # Define tool schemas
        self._tool_schemas = [
            ToolSchema(
                name="discover_available_sources",
                description=(
                    "Discover all available data sources (CSV files) in the pharma data directory. "
                    "Returns metadata about each source including columns and sample data. "
                    "Use this FIRST to understand what data is available for investigation."
                ),
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            ToolSchema(
                name="query_data_source",
                description=(
                    "Query any CSV data source with optional filters. "
                    "Use this to search for specific shipment data, alerts, quality logs, etc. "
                    "Returns matching records as JSON."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "source_name": {
                            "type": "string",
                            "description": "Name of the CSV file (e.g., 'sensor_alerts', 'logistics_shipments')"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional dict of column:value pairs to filter results",
                            "additionalProperties": True
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional limit on number of results to return"
                        }
                    },
                    "required": ["source_name"]
                }
            ),
            ToolSchema(
                name="analyze_shipment_timeline",
                description=(
                    "Build comprehensive timeline by querying multiple data sources and joining events. "
                    "Returns chronological event sequence with timestamps and responsible parties. "
                    "Use this to understand event causality and identify accountability."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "shipment_id": {
                            "type": "string",
                            "description": "Shipment identifier to investigate (e.g., 'SHP-001-1')"
                        }
                    },
                    "required": ["shipment_id"]
                }
            ),
            ToolSchema(
                name="compute_cost_analysis",
                description=(
                    "Compute cost-benefit analysis for different resolution options. "
                    "Returns cost scenarios (release vs reject) with expected values. "
                    "Use this to provide decision support data for approval requests."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "shipment_id": {
                            "type": "string",
                            "description": "Shipment identifier to analyze"
                        }
                    },
                    "required": ["shipment_id"]
                }
            ),
            ToolSchema(
                name="generate_compliance_report",
                description=(
                    "Generate GxP-compliant investigation report with all findings. "
                    "Returns structured report meeting regulatory requirements."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "shipment_id": {
                            "type": "string",
                            "description": "Shipment identifier"
                        },
                        "investigation_data": {
                            "type": "object",
                            "description": "Dict with timeline, root causes, recommendations, etc.",
                            "additionalProperties": True
                        }
                    },
                    "required": ["shipment_id", "investigation_data"]
                }
            )
        ]
    
    # Workbench lifecycle methods
    async def start(self) -> None:
        """Start the workbench (Workbench protocol)."""
        # No initialization needed for CSV-based tools
        pass
    
    async def stop(self) -> None:
        """Stop the workbench (Workbench protocol)."""
        # No cleanup needed for CSV-based tools
        pass
    
    async def reset(self) -> None:
        """Reset the workbench state (Workbench protocol)."""
        # Stateless workbench, nothing to reset
        pass
    
    async def save_state(self) -> Mapping[str, Any]:
        """Save the current state (Workbench protocol)."""
        return PharmaDataWorkbenchState().model_dump()
    
    # Workbench tool methods
    async def list_tools(self, cancellation_token: CancellationToken | None = None) -> Sequence[ToolSchema]:
        """List all available tools (Workbench protocol)."""
        return self._tool_schemas
    
    async def call_tool(
        self, 
        name: str, 
        arguments: Mapping[str, Any] | None = None, 
        cancellation_token: CancellationToken | None = None
    ) -> ToolResult:
        """
        Execute a tool function call (Workbench protocol).
        
        Args:
            name: Name of the tool to call
            arguments: Tool arguments (optional)
            cancellation_token: Optional cancellation token
            
        Returns:
            ToolResult with the function output
        """
        if arguments is None:
            arguments = {}
        
        try:
            # Route to appropriate tool function
            if name == "discover_available_sources":
                result = discover_available_sources(self.data_dir)
            
            elif name == "query_data_source":
                source_name = arguments.get("source_name")
                if not source_name:
                    error_content = TextResultContent(content='{"error": "source_name is required"}')
                    return ToolResult(name=name, result=[error_content], is_error=True)
                filters = arguments.get("filters")
                limit = arguments.get("limit")
                result = query_data_source(source_name, filters, self.data_dir, limit)
            
            elif name == "analyze_shipment_timeline":
                shipment_id = arguments["shipment_id"]
                result = analyze_shipment_timeline(shipment_id, self.data_dir)
            
            elif name == "compute_cost_analysis":
                shipment_id = arguments["shipment_id"]
                result = compute_cost_analysis(shipment_id, self.data_dir)
            
            elif name == "generate_compliance_report":
                shipment_id = arguments["shipment_id"]
                investigation_data = arguments["investigation_data"]
                result = generate_compliance_report(shipment_id, investigation_data, self.data_dir)
            
            else:
                error_content = TextResultContent(content=f'{{"error": "Unknown tool: {name}"}}')
                return ToolResult(name=name, result=[error_content], is_error=True)
            
            # Wrap result in TextResultContent and return as list
            result_content = TextResultContent(content=result)
            return ToolResult(name=name, result=[result_content])
            
        except Exception as e:
            error_content = TextResultContent(content=f'{{"error": "{str(e)}"}}')
            return ToolResult(name=name, result=[error_content], is_error=True)
    
    # Component protocol methods
    def dump_state(self) -> PharmaDataWorkbenchState:
        """Dump the current state (Component protocol)."""
        return PharmaDataWorkbenchState()
    
    def load_state(self, state: PharmaDataWorkbenchState) -> None:
        """Load state (Component protocol)."""
        pass  # Stateless workbench
    
    def _to_config(self) -> PharmaDataWorkbenchConfig:
        """Get configuration (Component protocol)."""
        return self._config
    
    @classmethod
    def _from_config(cls, config: PharmaDataWorkbenchConfig) -> "PharmaDataWorkbench":
        """Create from configuration (Component protocol)."""
        return cls(data_dir=config.data_dir)


__all__ = ["PharmaDataWorkbench"]

