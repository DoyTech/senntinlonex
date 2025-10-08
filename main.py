import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import requests

# --- Core Dependencies ---
import uvicorn
import gradio as gr
import aiofiles
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- Application Setup ---
app = FastAPI(
    title="SentinelOneX Backend",
    description="An API for ingesting agent telemetry with a Gradio UI.",
    version="1.1.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost:1420", # The default port for Tauri dev server
    "tauri://localhost"      # The protocol for the Tauri app itself
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
BASE_URL = "http://127.0.0.1:8000" # Base URL for API calls from Gradio

# --- Pydantic Models (Data Contracts) ---
class TelemetryData(BaseModel):
    timestamp: float
    agent_id: str
    system_info: Dict[str, Any]
    processes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    network_intelligence: Dict[str, Any]

ALL_ALERTS: List[Dict] = [] # In-memory store for alerts

# ==============================================================================
# FASTAPI - API ENDPOINTS
# ==============================================================================

def run_detection_engine(telemetry: TelemetryData) -> List[Dict]:
    alerts = []
    # --- RULE 1: Network Router Scan ---
    if telemetry.network_intelligence and \
       telemetry.network_intelligence.get("router_assessment") and \
       telemetry.network_intelligence["router_assessment"].get("ports"):
        if "23" in telemetry.network_intelligence["router_assessment"]["ports"] and \
           telemetry.network_intelligence["router_assessment"]["ports"]["23"] == "open":
            alerts.append({
                "title": "Telnet Port Open on Router",
                "description": "Router has Telnet (port 23) open, indicating a potential vulnerability.",
                "severity": "high",
                "evidence": {
                    "agent_id": telemetry.agent_id,
                    "gateway_ip": telemetry.network_intelligence.get("gateway_ip"),
                    "open_port": 23
                }
            })
    
    # --- RULE 2: PowerShell Download Cradle ---
    for process in telemetry.processes:
        if process.get("name", "").lower() == "powershell.exe" and \
           "downloadstring" in process.get("cmdline", "").lower() and \
           "iex" in process.get("cmdline", "").lower():
            alerts.append({
                "title": "PowerShell Download Cradle Detected",
                "description": "Malicious PowerShell download cradle detected in process command line.",
                "severity": "critical",
                "evidence": {
                    "agent_id": telemetry.agent_id,
                    "pid": process.get("pid"),
                    "cmdline": process.get("cmdline")
                }
            })
            
    return alerts

@app.post("/ingest", summary="Ingest Telemetry Data")
async def receive_telemetry(data: TelemetryData):
    """Receive and store telemetry data from agents"""
    try:
        agent_dir = DATA_DIR / data.agent_id
        agent_dir.mkdir(exist_ok=True)

        # Format timestamp for filename
        ts_obj = datetime.fromtimestamp(data.timestamp)
        filename = f"telemetry_{ts_obj.strftime('%Y%m%d_%H%M%S_%f')}.json"
        
        # Asynchronously save telemetry data and the latest state
        data_json = data.model_dump()
        
        async with aiofiles.open(agent_dir / filename, "w") as f:
            await f.write(json.dumps(data_json, indent=2))
        
        async with aiofiles.open(agent_dir / "latest_state.json", "w") as f:
            await f.write(json.dumps(data_json, indent=2))

        # Run detection engine
        alerts = run_detection_engine(data)
        if alerts:
            print("[*] Detected Alerts:")
            for alert in alerts:
                # Get AI analysis for the alert
                ai_analysis = get_ai_analysis(alert["title"])
                alert["ai_analysis"] = ai_analysis
                ALL_ALERTS.append(alert) # Save enriched alert to in-memory store
                print(json.dumps(alert, indent=2))

        return {
            "status": "success",
            "message": f"Telemetry received from {data.agent_id}",
            "timestamp": ts_obj.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/agents", summary="List All Agents")
async def list_agents():
    """
    List all agents that have sent telemetry by reading their 'latest_state.json'.
    """
    agents = []
    if not DATA_DIR.exists():
        return {"agents": []}
        
    for agent_dir in DATA_DIR.iterdir():
        if agent_dir.is_dir():
            latest_state_path = agent_dir / "latest_state.json"
            if latest_state_path.exists():
                try:
                    async with aiofiles.open(latest_state_path, "r") as f:
                        state = json.loads(await f.read())
                        agents.append({
                            "agent_id": state.get("agent_id", "N/A"),
                            "last_seen": datetime.fromtimestamp(state.get("timestamp", 0)).isoformat(),
                            "os_platform": state.get("system_info", {}).get("os_platform", "N/A"),
                            "hostname": state.get("system_info", {}).get("hostname", "N/A"),
                        })
                except (json.JSONDecodeError, KeyError) as e:
                    # Log this error or handle it as needed
                    print(f"Warning: Could not process state for {agent_dir.name}: {e}")
    return {"agents": sorted(agents, key=lambda x: x["last_seen"], reverse=True)}


@app.get("/agents/{agent_id}/latest", summary="Get Agent's Latest State")
async def get_agent_state(agent_id: str):
    """
    Get the latest state of a specific agent.
    """
    latest_state_path = DATA_DIR / agent_id / "latest_state.json"
    if not latest_state_path.exists():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        async with aiofiles.open(latest_state_path) as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts", summary="List All Alerts")
async def list_all_alerts():
    """List all detected alerts."""
    return {"alerts": ALL_ALERTS}

@app.post("/agents/{agent_id}/contain", summary="Contain Agent Host")
async def contain_agent(agent_id: str):
    """Simulates issuing a containment command for a specific agent."""
    print(f"!!! CONTAINMENT COMMAND ISSUED FOR AGENT: {agent_id} !!!")
    subject = f"CRITICAL: Containment Action for Agent {agent_id}"
    body = f"A containment action was initiated for agent {agent_id} due to detected threats."
    send_email_alert(subject, body)
    send_sms_alert(f"CRITICAL: Agent {agent_id} contained.")
    return {"status": "containment command issued", "agent_id": agent_id}

# ==============================================================================
# GRADIO - UI LOGIC
# ==============================================================================

async def refresh_agent_list():
    """Gradio function to call the /agents API and format the output."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/agents")
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            
            agents = data.get("agents", [])
            if not agents:
                return [], gr.Dropdown(choices=[], value=None)
                
            # Update DataFrame and Dropdown choices
            agent_ids = [agent['agent_id'] for agent in agents]
            return agents, gr.Dropdown(choices=agent_ids, value=agent_ids[0] if agent_ids else None)
    except httpx.RequestError as e:
        print(f"UI Error fetching agents: {e}")
        return [], gr.Dropdown(choices=[], value=None)

async def get_agent_details(agent_id: str):
    """Gradio function to get details for a selected agent."""
    if not agent_id:
        return "{}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/agents/{agent_id}/latest")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        return {"error": f"Could not fetch details for {agent_id}: {e}"}

def generate_fake_telemetry(agent_id: str):
    """Generates a sample telemetry payload."""
    return {
        "timestamp": datetime.now().timestamp(),
        "agent_id": agent_id or "test-agent-01",
        "system_info": {
            "hostname": "dev-machine",
            "os_platform": "Windows 11",
            "ip_address": "192.168.1.101"
        },
        "processes": [{"pid": 1234, "name": "powershell.exe", "cmdline": "powershell -enc ..."}],
        "connections": [{"local_port": 49152, "remote_ip": "8.8.8.8", "remote_port": 53}],
        "network_intelligence": {"dns_queries": ["malicious-domain.com"]}
    }

async def send_sample_telemetry(agent_id: str):
    """Gradio function to generate and send a sample telemetry payload."""
    if not agent_id:
        return "Error: Agent ID cannot be empty."
    
    payload = generate_fake_telemetry(agent_id)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/ingest", json=payload)
            response.raise_for_status()
            return f"Success! Response: {response.json()['message']}"
    except httpx.RequestError as e:
        return f"Error sending telemetry: {e}"

def get_ai_analysis(alert_title: str) -> Dict:
    """Calls the Ollama API to get an AI-driven analysis of an alert."""
    ollama_url = "http://127.0.0.1:11434/api/generate"
    prompt = (
        f"You are 'The Virtual Security Analyst'. Your analysis must be concise, accurate, and actionable. "
        f"Analyze the alert titled '{alert_title}'. "
        f"Provide your response in a structured JSON format with the following keys: "
        f"'summary' (a 1-sentence summary), "
        f"'mitre_id' (the most likely MITRE ATT&CK technique ID, e.g., T1059.001), and "
        f"'remediation_plan' (a 2-step remediation plan as a list of strings)."
    )
    
    payload = {
        "model": "llama3", # Or another suitable model you have running
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        
        full_response = response.json()
        ai_response_text = full_response.get("response", "{}")
        
        try:
            ai_analysis = json.loads(ai_response_text)
        except json.JSONDecodeError:
            print(f"Warning: AI response was not valid JSON: {ai_response_text}")
            ai_analysis = {"summary": ai_response_text, "mitre_id": "N/A", "remediation_plan": ["Could not parse AI response."]}
            
        return ai_analysis
    except requests.exceptions.ConnectionError as e:
        print(f"Error connecting to Ollama: {e}. Make sure Ollama is running.")
        return {"summary": "AI analysis unavailable: Ollama not running.", "mitre_id": "N/A", "remediation_plan": ["Ensure Ollama is running and accessible."]}
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama API request: {e}")
        return {"summary": f"AI analysis failed: {e}", "mitre_id": "N/A", "remediation_plan": ["Check Ollama API status."]}

async def refresh_alerts():
    """Gradio function to call the /alerts API and format the output for the DataFrame."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/alerts")
            response.raise_for_status()
            data = response.json()
            
            alerts = data.get("alerts", [])
            
            # Store full alerts in a hidden state for later retrieval
            # For the DataFrame, we only show a subset of fields
            formatted_alerts_for_df = []
            for alert in alerts:
                mitre_id = alert.get("ai_analysis", {}).get("mitre_id", "N/A")
                remediation_summary = " ".join(alert.get("ai_analysis", {}).get("remediation_plan", ["N/A"]))
                formatted_alerts_for_df.append([
                    alert.get("title", "N/A"),
                    alert.get("severity", "N/A"),
                    mitre_id,
                    remediation_summary,
                    alert.get("evidence", {}).get("agent_id", "N/A") # Hidden agent_id for selection
                ])
            return formatted_alerts_for_df, alerts # Return both for DataFrame and full objects
    except httpx.RequestError as e:
        print(f"UI Error fetching alerts: {e}")
        return [], []

async def show_selected_alert_details(selected_data: gr.SelectData, all_alerts: List[Dict]):
    """Gradio function to display full details of a selected alert and update agent_id state."""
    if not selected_data.index or not all_alerts:
        return {}, ""
    
    selected_alert_index = selected_data.index[0] # Assuming single row selection
    if selected_alert_index < 0 or selected_alert_index >= len(all_alerts):
        return {}, ""

    selected_alert = all_alerts[selected_alert_index]
    agent_id_for_containment = selected_alert.get("evidence", {}).get("agent_id", "")
    
    return selected_alert, agent_id_for_containment

# ==============================================================================
# GRADIO - UI DEFINITION
# ==============================================================================

with gr.Blocks(theme=gr.themes.Soft(), title="SentinelOneX") as gradio_interface:
    gr.Markdown("# SentinelOneX Agent Dashboard")

    with gr.Tabs():
        with gr.TabItem("Agent Overview"):
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Agent List", variant="primary")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Agents")
                    agent_df = gr.DataFrame(
                        headers=["agent_id", "last_seen", "os_platform", "hostname"],
                        datatype=["str", "str", "str", "str"],
                        row_count=(0, "dynamic"),
                        interactive=False,
                    )
                    
                with gr.Column(scale=2):
                    gr.Markdown("### Latest Agent State")
                    agent_dropdown = gr.Dropdown(label="Select Agent ID", interactive=True)
                    agent_details_json = gr.JSON(label="Full Telemetry Data")
        
        with gr.TabItem("Testing & Ingestion"):
            gr.Markdown("## Send Sample Telemetry")
            gr.Markdown("Use this section to simulate an agent sending data to the `/ingest` endpoint.")
            
            test_agent_id = gr.Textbox(label="Agent ID to Simulate", value="test-agent-01")
            send_telemetry_btn = gr.Button("Send Sample Telemetry", variant="primary")
            ingest_response_output = gr.Textbox(label="API Response", interactive=False)
            
            send_telemetry_btn.click(
                fn=send_sample_telemetry,
                inputs=[test_agent_id],
                outputs=[ingest_response_output]
            )

        with gr.TabItem("Threat Center"):
            gr.Markdown("## Live Alerts & Virtual Analyst Reports")
            with gr.Row():
                refresh_alerts_btn = gr.Button("🔄 Refresh Alerts", variant="primary")
            
            all_alerts_state = gr.State([]) # Hidden state to store full alert objects
            selected_agent_id_state = gr.State("") # Hidden state for selected agent_id for containment

            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Detected Alerts")
                    alerts_table = gr.DataFrame(
                        headers=["Title", "Severity", "MITRE ATT&CK", "Remediation Summary", "Agent ID (Hidden)"],
                        datatype=["str", "str", "str", "str", "str"],
                        row_count=(5, "dynamic"),
                        interactive=False,
                        visible=True # Make sure it's visible
                    )
                    alerts_table.change(
                        fn=show_selected_alert_details,
                        inputs=[alerts_table, all_alerts_state],
                        outputs=[gr.JSON(label="Selected Alert Details"), selected_agent_id_state]
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### Alert Details & Response")
                    alert_details_json = gr.JSON(label="Full Alert Data")
                    contain_host_btn = gr.Button("🚨 Contain Host", variant="stop")
                    containment_status_output = gr.Textbox(label="Containment Status", interactive=False)
                    
                    contain_host_btn.click(
                        fn=contain_agent,
                        inputs=[selected_agent_id_state],
                        outputs=[containment_status_output]
                    )

    # --- UI Event Wiring ---
    refresh_btn.click(
        fn=refresh_agent_list,
        inputs=[],
        outputs=[agent_df, agent_dropdown]
    )

    agent_dropdown.change(
        fn=get_agent_details,
        inputs=[agent_dropdown],
        outputs=[agent_details_json]
    )
    
    # Load initial agent list when the UI starts
    gradio_interface.load(
        fn=refresh_agent_list,
        inputs=[],
        outputs=[agent_df, agent_dropdown]
    )

    # Threat Center events
    refresh_alerts_btn.click(
        fn=refresh_alerts,
        inputs=[],
        outputs=[alerts_table, all_alerts_state]
    )
    gradio_interface.load(
        fn=refresh_alerts,
        inputs=[],
        outputs=[alerts_table, all_alerts_state]
    )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

# Mount the Gradio app onto the FastAPI app
app = gr.mount_gradio_app(app, gradio_interface, path="/")

if __name__ == "__main__":
    # --- Run with Uvicorn ---
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def send_email_alert(subject: str, body: str):
    """Simulates sending an email alert."""
    print(f"[EMAIL ALERT] Subject: {subject}, Body: {body}")

def send_sms_alert(message: str):
    """Simulates sending an SMS alert."""
    print(f"[SMS ALERT] Message: {message}")