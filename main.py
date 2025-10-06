from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI(title="SentinelOneX Backend")

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

class TelemetryData(BaseModel):
    timestamp: float
    agent_id: str
    system_info: Dict[str, Any]
    processes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    network_intelligence: Dict[str, Any]

@app.post("/ingest")
async def receive_telemetry(data: TelemetryData):
    """Receive and store telemetry data from agents"""
    try:
        # Create agent directory if it doesn't exist
        agent_dir = DATA_DIR / data.agent_id
        agent_dir.mkdir(exist_ok=True)

        # Format timestamp for filename
        timestamp = datetime.fromtimestamp(data.timestamp).strftime("%Y%m%d_%H%M%S")
        filename = f"telemetry_{timestamp}.json"
        
        # Save telemetry data
        with open(agent_dir / filename, "w") as f:
            json.dump(data.dict(), f, indent=2)

        # Save latest state
        with open(agent_dir / "latest_state.json", "w") as f:
            json.dump(data.dict(), f, indent=2)

        return {
            "status": "success",
            "message": f"Telemetry received from {data.agent_id}",
            "timestamp": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all agents that have sent telemetry"""
    try:
        agents = []
        for agent_dir in DATA_DIR.iterdir():
            if agent_dir.is_dir():
                latest_state = agent_dir / "latest_state.json"
                if latest_state.exists():
                    with open(latest_state) as f:
                        state = json.load(f)
                        agents.append({
                            "agent_id": state["agent_id"],
                            "last_seen": datetime.fromtimestamp(state["timestamp"]).isoformat(),
                            "os_platform": state["system_info"]["os_platform"],
                            "hostname": state["system_info"]["hostname"]
                        })
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/latest")
async def get_agent_state(agent_id: str):
    """Get the latest state of a specific agent"""
    try:
        latest_state = DATA_DIR / agent_id / "latest_state.json"
        if not latest_state.exists():
            raise HTTPException(status_code=404, detail="Agent not found")
        
        with open(latest_state) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting SentinelOneX Backend Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
