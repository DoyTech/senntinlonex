# SentinelOneX Agent
# A cross-platform telemetry collector for the SentinelOneX platform.
# Collects endpoint data and performs network intelligence scans.
import requests
import psutil
import json
import time
import socket
import platform

# --- Configuration ---
PLATFORM_URL = "http://127.0.0.1:8000/ingest"  # Backend server URL
COLLECTION_INTERVAL_SECONDS = 15  # Interval for sending telemetry
AGENT_ID = None # Will be set to the machine's hostname

def get_system_info():
    """Gathers basic static information about the host system."""
    hostname = socket.gethostname()
    os_platform = platform.system()
    os_version = platform.version()
    return {
        'hostname': hostname,
        'os_platform': os_platform,
        'os_version': os_version
    }

def get_process_telemetry():
    """Collects information about all running processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
        try:
            info = proc.info
            processes.append({
                'pid': info.get('pid'),
                'name': info.get('name'),
                'username': info.get('username'),
                'cmdline': ' '.join(info.get('cmdline', []))
            })
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return processes

def get_network_telemetry():
    """Collects information about active network connections."""
    connections = []
    for conn in psutil.net_connections():
        local_address = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
        remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
        connections.append({
            'local_address': local_address,
            'remote_address': remote_address,
            'status': conn.status,
            'pid': conn.pid
        })
    return connections

# For this function, you may need to guide Copilot or install a library first: pip install netifaces
def discover_gateway_ip():
    """Discovers the default gateway IP address. Should be cross-platform."""
    try:
        import netifaces
    except ImportError:
        print("netifaces not installed. Please run: pip install netifaces")
        return None
    gateways = netifaces.gateways()
    default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
    if default_gateway:
        return default_gateway[0]
    return None

def scan_router_ports(router_ip):
    """Performs a simple TCP port scan on the router."""
    ports = [22, 23, 80, 443, 8080]
    results = {}
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((router_ip, port))
            results[port] = 'open' if result == 0 else 'closed'
        except Exception:
            results[port] = 'closed'
        finally:
            sock.close()
    return results

def check_router_config(router_ip):
    """Simulates checking for common router misconfigurations for the demo."""
    findings = []
    try:
        response = requests.get(f"http://{router_ip}", timeout=2)
        if response.status_code == 200:
            findings.append({'check': 'default_http_admin', 'status': 'detected'})
        else:
            findings.append({'check': 'default_http_admin', 'status': 'not_detected'})
    except Exception:
        findings.append({'check': 'default_http_admin', 'status': 'not_detected'})
    return findings

def get_network_intelligence_data():
    """Orchestrates the network intelligence gathering."""
    gateway_ip = discover_gateway_ip()
    if not gateway_ip:
        return {}
    router_ports = scan_router_ports(gateway_ip)
    router_findings = check_router_config(gateway_ip)
    return {
        'gateway_ip': gateway_ip,
        'router_assessment': {
            'ports': router_ports,
            'findings': router_findings
        }
    }

def package_all_telemetry(system_info):
    """Packages all endpoint and network telemetry into a single payload."""
    payload = {
        "timestamp": time.time(),
        "agent_id": system_info.get('hostname'),
        "system_info": system_info,
        "processes": get_process_telemetry(),
        "connections": get_network_telemetry(),
        "network_intelligence": get_network_intelligence_data() # Add the new data
    }
    return payload

def send_telemetry_to_platform(payload):
    """Sends the final telemetry payload to the platform backend."""
    try:
        response = requests.post(PLATFORM_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print("Telemetry sent successfully.")
        else:
            print(f"Failed to send telemetry. Status code: {response.status_code}")
    except requests.ConnectionError:
        print("Connection error: Unable to reach the platform backend.")
    except Exception as e:
        print(f"Error sending telemetry: {e}")

if __name__ == "__main__":
    # Get the static system info once at the start.
    system_info = get_system_info()
    AGENT_ID = system_info['hostname']
    print(f"SentinelOneX Agent started on host: {AGENT_ID}")

    # Start the main infinite loop.
    while True:
        # Use a main try-except block to ensure the agent is resilient and never crashes.
        try:
            print(f"[{time.ctime()}] Collecting telemetry...")
            payload = package_all_telemetry(system_info)
            send_telemetry_to_platform(payload)
            print(f"[{time.ctime()}] Telemetry sent successfully. Waiting for next interval...")
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")

        # Wait for the configured interval before the next collection.
        time.sleep(COLLECTION_INTERVAL_SECONDS)
