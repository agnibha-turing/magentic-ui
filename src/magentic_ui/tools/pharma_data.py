"""
Generic data query tools for pharmaceutical supply chain investigation.

These tools work with any CSV files in a data directory structure and provide
dynamic querying, analysis, and reporting capabilities without hardcoding.
"""

from pathlib import Path
from typing import Any, Optional
import pandas as pd
import json
from datetime import datetime


def query_data_source(
    source_name: str,
    filters: Optional[dict[str, Any]] = None,
    data_dir: str = "mock_data",
    limit: Optional[int] = None,
) -> str:
    """
    Query any CSV file in the data directory with dynamic filters.
    
    This is a generic tool that discovers and queries CSV files without hardcoding.
    It searches recursively through the data directory for matching CSV files.
    
    Args:
        source_name: Name of the CSV file (with or without .csv extension)
        filters: Optional dict of column:value pairs to filter results
        data_dir: Root directory containing data files
        limit: Optional limit on number of results to return
    
    Returns:
        JSON string containing matching records
    
    Example:
        query_data_source(
            "sensor_alerts",
            filters={"shipment_id": "SHP-001-1"},
            limit=10
        )
    """
    try:
        data_path = Path(data_dir)
        if not data_path.exists():
            return json.dumps({
                "error": f"Data directory not found: {data_dir}",
                "results": []
            })
        
        # Search for CSV file (handles subdirectories)
        csv_name = source_name if source_name.endswith('.csv') else f"{source_name}.csv"
        csv_files = list(data_path.rglob(csv_name))
        
        if not csv_files:
            # Try partial match
            csv_files = [f for f in data_path.rglob("*.csv") if source_name.lower() in f.stem.lower()]
        
        if not csv_files:
            return json.dumps({
                "error": f"No CSV file found matching: {source_name}",
                "searched_in": str(data_dir),
                "results": []
            })
        
        # Read the first matching CSV
        df = pd.read_csv(csv_files[0])
        
        # Apply filters dynamically
        if filters:
            for col, val in filters.items():
                if col in df.columns:
                    # Handle different types of filtering
                    if isinstance(val, (list, tuple)):
                        df = df[df[col].isin(val)]
                    else:
                        df = df[df[col] == val]
                else:
                    return json.dumps({
                        "error": f"Column '{col}' not found in {csv_files[0].name}",
                        "available_columns": list(df.columns),
                        "results": []
                    })
        
        # Apply limit if specified
        if limit:
            df = df.head(limit)
        
        results = df.to_dict('records')
        
        return json.dumps({
            "source_file": str(csv_files[0]),
            "total_records": len(results),
            "columns": list(df.columns),
            "results": results
        }, default=str, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error querying data source: {str(e)}",
            "results": []
        })


def discover_available_sources(data_dir: str = "mock_data") -> str:
    """
    Discover all available data sources (CSV files) in the data directory.
    
    This allows the agent to understand what data is available without hardcoding.
    
    Args:
        data_dir: Root directory containing data files
    
    Returns:
        JSON string listing all available data sources with metadata
    
    Example:
        discover_available_sources("mock_data")
    """
    try:
        data_path = Path(data_dir)
        if not data_path.exists():
            return json.dumps({
                "error": f"Data directory not found: {data_dir}",
                "sources": []
            })
        
        # Find all CSV files
        csv_files = list(data_path.rglob("*.csv"))
        
        sources = []
        for csv_file in csv_files:
            try:
                # Get basic metadata about each source
                df = pd.read_csv(csv_file, nrows=1)
                sources.append({
                    "name": csv_file.stem,
                    "path": str(csv_file.relative_to(data_path)),
                    "category": csv_file.parent.name,
                    "columns": list(df.columns),
                    "sample_record": df.to_dict('records')[0] if len(df) > 0 else {}
                })
            except Exception as e:
                sources.append({
                    "name": csv_file.stem,
                    "path": str(csv_file.relative_to(data_path)),
                    "error": f"Could not read: {str(e)}"
                })
        
        return json.dumps({
            "data_directory": str(data_dir),
            "total_sources": len(sources),
            "sources": sources
        }, default=str, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error discovering sources: {str(e)}",
            "sources": []
        })


def analyze_shipment_timeline(
    shipment_id: str,
    data_dir: str = "mock_data"
) -> str:
    """
    Build a comprehensive timeline by joining multiple data sources.
    
    This function dynamically discovers relevant data and constructs an audit trail
    showing events, timestamps, and responsible parties.
    
    Args:
        shipment_id: Shipment identifier to investigate
        data_dir: Root directory containing data files
    
    Returns:
        JSON string containing timeline events and accountability analysis
    
    Example:
        analyze_shipment_timeline("SHP-001-1")
    """
    try:
        data_path = Path(data_dir)
        events = []
        
        # Query multiple sources dynamically
        sources_to_check = [
            ("logistics_shipments", {"shipment_id": shipment_id}),
            ("sensor_alerts", {"shipment_id": shipment_id}),
            ("wms_quarantine_log", {"shipment_id": shipment_id}),
            ("wms_goods_movements", {"shipment_id": shipment_id}),
            ("finance_waste_log", {"shipment_id": shipment_id}),
        ]
        
        for source_name, filters in sources_to_check:
            result = query_data_source(source_name, filters, data_dir)
            result_data = json.loads(result)
            
            if "results" in result_data and result_data["results"]:
                for record in result_data["results"]:
                    # Extract timestamp fields dynamically
                    timestamp = None
                    for ts_field in ["timestamp", "dispatch_dt", "start_ts", "decision_dt", "event_dt"]:
                        if ts_field in record and record[ts_field]:
                            timestamp = record[ts_field]
                            break
                    
                    # Determine event owner dynamically
                    owner = "Unknown"
                    if "supplier_id" in record:
                        owner = f"Carrier_{record['supplier_id']}"
                    elif "decision" in record:
                        owner = "QA_Team"
                    elif "status" in record and record.get("status") == "Quarantined":
                        owner = "QA_Team"
                    
                    events.append({
                        "timestamp": timestamp,
                        "source": source_name,
                        "owner": owner,
                        "data": record
                    })
        
        # Sort events by timestamp
        events = sorted(
            [e for e in events if e["timestamp"]], 
            key=lambda x: x["timestamp"]
        )
        
        # Compute accountability (simple heuristic based on event types)
        accountability = compute_accountability(events)
        
        return json.dumps({
            "shipment_id": shipment_id,
            "total_events": len(events),
            "timeline": events,
            "accountability": accountability
        }, default=str, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error building timeline: {str(e)}",
            "shipment_id": shipment_id,
            "timeline": []
        })


def compute_accountability(events: list[dict]) -> dict:
    """
    Compute accountability distribution based on event timeline.
    
    This is a simple heuristic that counts event types by owner.
    In a real system, this would use more sophisticated ML models.
    
    Args:
        events: List of timeline events with owners
    
    Returns:
        Dictionary mapping owners to their contribution percentages
    """
    owner_counts = {}
    
    for event in events:
        owner = event.get("owner", "Unknown")
        owner_counts[owner] = owner_counts.get(owner, 0) + 1
    
    total = sum(owner_counts.values())
    if total == 0:
        return {}
    
    # Convert counts to percentages
    accountability = {
        owner: {
            "contribution_pct": round((count / total) * 100, 1),
            "event_count": count
        }
        for owner, count in owner_counts.items()
    }
    
    return accountability


def compute_cost_analysis(
    shipment_id: str,
    data_dir: str = "mock_data"
) -> str:
    """
    Compute cost-benefit analysis for different resolution options.
    
    Dynamically queries waste logs, shipment values, and historical patterns
    to provide decision support data.
    
    Args:
        shipment_id: Shipment identifier to analyze
        data_dir: Root directory containing data files
    
    Returns:
        JSON string with cost analysis and recommendations
    
    Example:
        compute_cost_analysis("SHP-001-1")
    """
    try:
        # Query shipment details
        shipment_result = query_data_source(
            "logistics_shipments",
            {"shipment_id": shipment_id},
            data_dir,
            limit=1
        )
        shipment_data = json.loads(shipment_result)
        
        if not shipment_data.get("results"):
            return json.dumps({
                "error": "Shipment not found",
                "shipment_id": shipment_id
            })
        
        shipment = shipment_data["results"][0]
        
        # Query historical waste patterns
        waste_result = query_data_source(
            "finance_waste_log",
            {"event_type": "Quarantine"},
            data_dir,
            limit=10
        )
        waste_data = json.loads(waste_result)
        
        # Calculate average waste from historical data
        avg_waste = 0
        if waste_data.get("results"):
            total_loss = sum(r.get("total_loss_usd", 0) for r in waste_data["results"])
            avg_waste = total_loss / len(waste_data["results"])
        
        # Build cost scenarios
        analysis = {
            "shipment_id": shipment_id,
            "shipment_details": shipment,
            "scenarios": {
                "conditional_release": {
                    "description": "Release shipment pending QA approval",
                    "expected_waste_usd": 0,
                    "qa_review_cost_usd": 500,
                    "total_cost_usd": 500,
                    "probability_success": 0.85,
                    "expected_value_usd": -425
                },
                "reject_reship": {
                    "description": "Reject shipment and dispatch replacement",
                    "expected_waste_usd": avg_waste,
                    "reship_logistics_cost_usd": 1200,
                    "total_cost_usd": avg_waste + 1200,
                    "probability_success": 1.0,
                    "expected_value_usd": -(avg_waste + 1200)
                }
            },
            "historical_waste_avg_usd": round(avg_waste, 2)
        }
        
        return json.dumps(analysis, default=str, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error computing cost analysis: {str(e)}",
            "shipment_id": shipment_id
        })


def generate_compliance_report(
    shipment_id: str,
    investigation_data: dict,
    data_dir: str = "mock_data"
) -> str:
    """
    Generate GxP-compliant investigation report.
    
    Creates structured documentation meeting regulatory requirements
    based on investigation findings.
    
    Args:
        shipment_id: Shipment identifier
        investigation_data: Dict containing timeline, accountability, recommendations
        data_dir: Root directory containing data files
    
    Returns:
        JSON string containing structured compliance report
    
    Example:
        generate_compliance_report("SHP-001-1", investigation_findings)
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d")
        
        report = {
            "header": {
                "document_id": f"CAPA-{shipment_id}-{timestamp}",
                "document_type": "Supply Chain Investigation Report",
                "shipment_id": shipment_id,
                "report_date": datetime.now().isoformat(),
                "prepared_by": "AI_Investigation_Agent",
                "status": "Draft"
            },
            "investigation_summary": investigation_data.get("summary", "Investigation complete"),
            "timeline": investigation_data.get("timeline", []),
            "root_cause_analysis": investigation_data.get("root_causes", []),
            "accountability": investigation_data.get("accountability", {}),
            "recommendations": investigation_data.get("recommendations", []),
            "corrective_actions": investigation_data.get("corrective_actions", []),
            "preventive_actions": investigation_data.get("preventive_actions", []),
            "approval_required": True,
            "signoff": {
                "prepared_by": {
                    "name": "AI_Investigation_Agent",
                    "date": datetime.now().isoformat()
                },
                "reviewed_by": {"name": "TBD", "date": None},
                "approved_by": {"name": "TBD", "date": None}
            }
        }
        
        return json.dumps(report, default=str, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error generating report: {str(e)}",
            "shipment_id": shipment_id
        })


# Tool definitions for AutoGen
PHARMA_DATA_TOOLS = [
    query_data_source,
    discover_available_sources,
    analyze_shipment_timeline,
    compute_cost_analysis,
    generate_compliance_report,
]

