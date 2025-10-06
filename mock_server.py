from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({"status": "running", "message": "SentinelOneX Mock Server"})

@app.route('/ingest', methods=['POST'])
def receive_telemetry():
    """Endpoint to receive telemetry data from the agent"""
    data = request.json
    
    # Print received data with timestamp
    print(f"\n[{datetime.now()}] Received telemetry from agent: {data.get('agent_id')}")
    
    # System Information
    sys_info = data.get('system_info', {})
    print("\nSystem Information:")
    print(f"OS: {sys_info.get('os_platform')} {sys_info.get('os_version')}")
    
    # CPU Information
    cpu_info = sys_info.get('cpu', {})
    print("\nCPU Status:")
    print(f"Usage: {cpu_info.get('cpu_percent')}%")
    print(f"Cores: {cpu_info.get('cpu_count')}")
    
    # Memory Information
    mem_info = sys_info.get('memory', {})
    print("\nMemory Status:")
    print(f"Total: {mem_info.get('total', 0) / (1024**3):.2f} GB")
    print(f"Used: {mem_info.get('percent')}%")
    
    # Disk Information
    print("\nDisk Status:")
    for mount, disk in sys_info.get('disks', {}).items():
        print(f"\nMount: {mount}")
        print(f"Total: {disk.get('total', 0) / (1024**3):.2f} GB")
        print(f"Used: {disk.get('percent')}%")
    
    # Process and Network Information
    print(f"\nProcesses: {len(data.get('processes', []))}")
    print(f"Network Connections: {len(data.get('connections', []))}")
    
    # Network Intelligence
    net_intel = data.get('network_intelligence', {})
    print("\nNetwork Intelligence:")
    print(f"Gateway IP: {net_intel.get('gateway_ip')}")
    if 'router_assessment' in net_intel:
        print("Open Ports:", [port for port, status in net_intel['router_assessment'].get('ports', {}).items() if status == 'open'])
    
    return jsonify({"status": "success", "message": "Telemetry received"})

if __name__ == '__main__':
    print("Mock SentinelOneX Platform Server starting...")
    print("Listening for telemetry data on http://127.0.0.1:8000/ingest")
    app.run(host='127.0.0.1', port=8000)
