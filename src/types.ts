export interface WifiNetwork {
  id: string;
  ssid: string;
  bssid: string;
  channel: number;
  signal: number;
  security: string;
  encryption: string;
  vendor: string;
  firstSeen: string;
  lastSeen: string;
  lat?: number;
  lng?: number;
  clients: number;
  frequency: string;
}

export interface Vulnerability {
  id: string;
  cve: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  title: string;
  description: string;
  cvss: number;
  service: string;
  port: number;
  solution: string;
  references: string[];
  exploitable: boolean;
}

export interface Exploit {
  id: string;
  name: string;
  type: string;
  platform: string;
  arch: string;
  reliability: string;
  description: string;
  cve: string;
  rank: 'Excellent' | 'Great' | 'Good' | 'Normal' | 'Average' | 'Low';
  payload_options: string[];
}

export interface Payload {
  id: string;
  name: string;
  type: 'reverse_shell' | 'bind_shell' | 'meterpreter' | 'shellcode' | 'staged';
  platform: string;
  arch: string;
  size: number;
  description: string;
  options: Record<string, string>;
}

export interface Target {
  ip: string;
  hostname: string;
  os: string;
  openPorts: number[];
  services: Array<{ port: number; service: string; version: string }>;
  vulnerabilities: Vulnerability[];
}

export interface ScanResult {
  id: string;
  timestamp: string;
  target: string;
  status: 'running' | 'completed' | 'failed';
  vulnerabilities: Vulnerability[];
  hosts: Target[];
  duration: number;
}

export interface Report {
  id: string;
  title: string;
  timestamp: string;
  operator: string;
  scope: string;
  networks: WifiNetwork[];
  targets: Target[];
  findings: Vulnerability[];
  exploits_used: string[];
  status: 'draft' | 'final';
  risk_score: number;
  executive_summary: string;
}

export interface PhoneDevice {
  id: string;
  name: string;
  connected: boolean;
  batteryLevel: number;
  location?: { lat: number; lng: number };
  wardrivingActive: boolean;
  networksFound: number;
  lastSync: string;
}

export interface Tool {
  id: string;
  name: string;
  category: 'exploitation' | 'enumeration' | 'credential' | 'network' | 'persistence';
  description: string;
  available: boolean;
  icon: string;
  platforms: string[];
}
