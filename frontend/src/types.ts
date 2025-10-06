export interface SystemInfo {
  hostname: string;
  os: string;
  platform: string;
  release: string;
  uptime: number;
  cpu_percent: number;
  memory_total: number;
  memory_used: number;
  memory_percent: number;
}

export interface NetworkInterface {
  name: string;
  ip: string;
  netmask: string;
  mac: string;
}

export interface Process {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status: string;
}

export interface Agent {
  id: string;
  hostname: string;
  lastSeen: string;
  systemInfo: SystemInfo;
  networkInterfaces: NetworkInterface[];
  processes: Process[];
}
