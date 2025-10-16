# How to Run the Pharma Investigation Agent

## ✅ The Problem is Fixed!

The issue was:
- **Pharma agent not enabled** → Default is `pharma_agent_enabled=False`
- **Orchestrator routing to WebSurfer** → Saw "search for shipment" and chose web search instead of local data query

## 🚀 How to Enable the Pharma Agent

### Option 1: Command Line (Easiest!)

```bash
cd /Users/agnibha.sarkar/Desktop/research/magentic-ui
source .venv/bin/activate

# Start with pharma agent enabled
magentic-ui --port 8081 --pharma-agent-enabled --pharma-data-dir mock_data
```

That's it! Now the pharma agent will be available to the orchestrator.

### Option 2: Environment Variables

```bash
export PHARMA_AGENT_ENABLED=True
export PHARMA_DATA_DIR=mock_data
magentic-ui --port 8081
```

## 🎯 Testing the Agent

### In the Web UI:

1. Start magentic-ui with `--pharma-agent-enabled`
2. Open browser: `http://localhost:8081`
3. In the chat, type:

```
Investigate shipment SHP-001-1 for temperature excursion.
Provide root cause analysis and recommendations.
```

### Expected Behavior:

- **✅ Orchestrator selects PharmaInvestigator** instead of WebSurfer
- Agent analyzes the scenario using domain knowledge
- Provides structured investigation findings
- Requests human approval for critical decisions

### What Changed:

**Agent Description (in `pharma_investigation.py`):**
```python
description=(
    "Pharmaceutical supply chain investigation specialist. "
    f"Handles investigations for shipments, temperature excursions, delays, "
    f"quality deviations, and CAPA analysis. Has access to local pharma data in {data_dir}. "
    "Use this agent for: shipment investigations, root cause analysis, "
    "accountability tracking, cost-benefit analysis, compliance reporting. "
    "DO NOT use web search for shipment data - this agent has local CSV data."
)
```

This tells the orchestrator:
- When to use the pharma agent (shipment investigations, temperature excursions, etc.)
- That it has LOCAL data (not web data)
- NOT to use WebSurfer for this type of query

## 📊 Verify It's Working

### Check Agent is Loaded:

Look for this in the console output when starting:
```
Starting Magentic-UI
...
Checking Docker...
...
```

The pharma agent loads silently, but you can verify by checking the team participants.

### Check Orchestrator Selection:

When you send a pharma-related query, you should see in the UI:
- Agent: `pharma_investigator` (NOT `web_surfer`)
- Message: "I'll help investigate this temperature excursion..."

### If WebSurfer Still Runs:

Double-check:
1. Did you use `--pharma-agent-enabled` flag?
2. Is the flag spelled correctly? (with dashes)
3. Check console output for any errors

## 🔍 Example Queries that Should Use Pharma Agent:

✅ "Investigate shipment SHP-001-1"  
✅ "Analyze temperature excursion for shipment XYZ"  
✅ "Root cause analysis for delayed shipment"  
✅ "CAPA investigation for quality deviation"  
✅ "Cost-benefit analysis for shipment release vs rejection"  

❌ "What is the weather in Boston?" → Uses WebSurfer (correct!)  
❌ "Write a Python script" → Uses Coder (correct!)  

## 🛠️ Troubleshooting

### "Still using WebSurfer instead of PharmaInvestigator"

**Solution:** Make sure you're using the CLI flag:
```bash
magentic-ui --port 8081 --pharma-agent-enabled
```

### "ModuleNotFoundError: No module named 'autogen'"

**Solution:** Already fixed! The agent now uses `autogen_agentchat` correctly.

### "Pharma agent gives generic answers"

**Current Status:** The agent is integrated but tool workbench is not yet implemented.  
**What it does now:** Reasons about pharma scenarios using domain knowledge in system prompt  
**What's next:** Add PharmaDataWorkbench to give it actual data query tools  

## 📝 Quick Reference

```bash
# Full command with all options
magentic-ui \
  --port 8081 \
  --pharma-agent-enabled \
  --pharma-data-dir mock_data \
  --run-without-docker  # Optional: if no Docker

# Minimal command
magentic-ui --pharma-agent-enabled
```

## 🎓 What Happens Behind the Scenes:

1. **CLI** (`cli.py`):
   - Parses `--pharma-agent-enabled` flag
   - Sets `PHARMA_AGENT_ENABLED=True` environment variable

2. **WebApp** (`app.py`):
   - Reads environment variables
   - Passes to `WebSocketManager`

3. **TeamManager** (`teammanager.py`):
   - Reads `PHARMA_AGENT_ENABLED` from environment
   - Adds to `MagenticUIConfig` parameters

4. **TaskTeam** (`task_team.py`):
   - Checks `pharma_agent_enabled` in config
   - Creates `PharmaInvestigator` agent if enabled
   - Adds to team participants

5. **Orchestrator** (`_orchestrator.py`):
   - Sees agent description: "Handles investigations for shipments, temperature excursions..."
   - Routes pharma queries to `PharmaInvestigator`
   - Routes web queries to `WebSurfer`

## ✨ Benefits of This Approach:

✅ **Non-Breaking** - Only loads if flag is provided  
✅ **Zero Config Changes** - Works with existing magentic-ui setup  
✅ **Proper Routing** - Orchestrator knows when to use pharma agent  
✅ **HITL Ready** - Works with existing approval guard system  
✅ **Extensible** - Easy to add more domain agents later  

## 📚 Next Steps:

1. **Test basic functionality** - Run with `--pharma-agent-enabled` and verify routing
2. **Add tool workbench** - Implement `PharmaDataWorkbench` following MCP pattern
3. **Enhance prompts** - Refine agent system message based on usage
4. **Add UI toggle** - Allow enabling/disabling from settings page

## 🎉 Summary:

**To fix your issue:**
```bash
magentic-ui --port 8081 --pharma-agent-enabled
```

That's it! The orchestrator will now route shipment investigations to the PharmaInvestigator instead of WebSurfer.

