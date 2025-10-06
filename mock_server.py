from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/ingest', methods=['POST'])
def receive_telemetry():
    """Endpoint to receive telemetry data from the agent"""
    data = request.json
    
    # Print received data with timestamp
    print(f"\n[{datetime.now()}] Received telemetry from agent: {data.get('agent_id')}")
    print("System Info:", json.dumps(data.get('system_info'), indent=2))
    print(f"Number of processes: {len(data.get('processes', []))}")
    print(f"Number of network connections: {len(data.get('connections', []))}")
    print("Network Intelligence:", json.dumps(data.get('network_intelligence'), indent=2))
    
    return jsonify({"status": "success", "message": "Telemetry received"})

if __name__ == '__main__':
    print("Mock SentinelOneX Platform Server starting...")
    print("Listening for telemetry data on http://127.0.0.1:8000/ingest")
    app.run(host='127.0.0.1', port=8000)
