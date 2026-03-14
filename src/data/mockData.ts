import type { WifiNetwork, Vulnerability, Exploit, Payload, Target, ScanResult, Report, PhoneDevice } from '../types';

export const mockNetworks: WifiNetwork[] = [
  { id: '1', ssid: 'CorpNet-HQ', bssid: 'AA:BB:CC:DD:EE:01', channel: 6, signal: -45, security: 'WPA2-Enterprise', encryption: 'CCMP', vendor: 'Cisco', firstSeen: '2026-03-09T08:00:00Z', lastSeen: '2026-03-09T11:40:00Z', lat: 37.7749, lng: -122.4194, clients: 47, frequency: '2.4GHz' },
  { id: '2', ssid: 'CorpNet-5G', bssid: 'AA:BB:CC:DD:EE:02', channel: 36, signal: -52, security: 'WPA3', encryption: 'GCMP', vendor: 'Cisco', firstSeen: '2026-03-09T08:00:00Z', lastSeen: '2026-03-09T11:40:00Z', lat: 37.7750, lng: -122.4192, clients: 23, frequency: '5GHz' },
  { id: '3', ssid: 'Guest-WiFi', bssid: 'AA:BB:CC:DD:EE:03', channel: 11, signal: -58, security: 'WPA2-PSK', encryption: 'TKIP', vendor: 'Ubiquiti', firstSeen: '2026-03-09T09:15:00Z', lastSeen: '2026-03-09T11:38:00Z', lat: 37.7748, lng: -122.4196, clients: 12, frequency: '2.4GHz' },
  { id: '4', ssid: 'IoT-Devices', bssid: 'AA:BB:CC:DD:EE:04', channel: 1, signal: -67, security: 'WPA2-PSK', encryption: 'CCMP', vendor: 'TP-Link', firstSeen: '2026-03-09T10:00:00Z', lastSeen: '2026-03-09T11:35:00Z', lat: 37.7751, lng: -122.4191, clients: 8, frequency: '2.4GHz' },
  { id: '5', ssid: 'OPEN-HOTSPOT', bssid: 'AA:BB:CC:DD:EE:05', channel: 6, signal: -72, security: 'OPEN', encryption: 'None', vendor: 'Unknown', firstSeen: '2026-03-09T11:00:00Z', lastSeen: '2026-03-09T11:42:00Z', lat: 37.7747, lng: -122.4198, clients: 3, frequency: '2.4GHz' },
  { id: '6', ssid: 'PrinterNet', bssid: 'AA:BB:CC:DD:EE:06', channel: 9, signal: -61, security: 'WEP', encryption: 'WEP', vendor: 'HP', firstSeen: '2026-03-09T07:30:00Z', lastSeen: '2026-03-09T11:30:00Z', lat: 37.7752, lng: -122.4190, clients: 2, frequency: '2.4GHz' },
];

export const mockVulnerabilities: Vulnerability[] = [
  { id: 'v1', cve: 'CVE-2021-44228', severity: 'CRITICAL', title: 'Log4Shell Remote Code Execution', description: 'Apache Log4j2 <=2.14.1 JNDI features do not protect against attacker controlled LDAP and other endpoints.', cvss: 10.0, service: 'HTTP', port: 8080, solution: 'Upgrade Log4j to 2.15.0 or later.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2021-44228'], exploitable: true },
  { id: 'v2', cve: 'CVE-2021-34527', severity: 'CRITICAL', title: 'PrintNightmare Windows Print Spooler RCE', description: 'Windows Print Spooler allows privileged file operations.', cvss: 8.8, service: 'SMB', port: 445, solution: 'Apply KB5004945 or disable Print Spooler.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2021-34527'], exploitable: true },
  { id: 'v3', cve: 'CVE-2022-30190', severity: 'HIGH', title: 'Follina MSDT RCE', description: 'Microsoft Support Diagnostic Tool vulnerability triggered via Office documents.', cvss: 7.8, service: 'HTTP', port: 80, solution: 'Disable MSDT URL protocol or apply patches.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2022-30190'], exploitable: true },
  { id: 'v4', cve: 'CVE-2023-23397', severity: 'CRITICAL', title: 'Outlook NTLM Hash Leak', description: 'Zero-click vulnerability in Microsoft Outlook that leaks NTLMv2 hashes.', cvss: 9.8, service: 'SMTP', port: 25, solution: 'Apply March 2023 Patch Tuesday updates.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2023-23397'], exploitable: true },
  { id: 'v5', cve: 'CVE-2024-21762', severity: 'CRITICAL', title: 'Fortinet SSL VPN RCE', description: 'Out-of-bounds write in Fortinet FortiOS allows unauthenticated RCE.', cvss: 9.6, service: 'HTTPS', port: 443, solution: 'Upgrade to FortiOS 7.4.3 or later.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2024-21762'], exploitable: true },
  { id: 'v6', cve: 'CVE-2023-4911', severity: 'HIGH', title: 'Glibc Buffer Overflow (Looney Tunables)', description: 'Buffer overflow in GNU C library dynamic loader.', cvss: 7.8, service: 'SSH', port: 22, solution: 'Update glibc package.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2023-4911'], exploitable: false },
  { id: 'v7', cve: 'CVE-2023-3519', severity: 'CRITICAL', title: 'Citrix NetScaler RCE', description: 'Unauthenticated RCE in Citrix ADC and Gateway.', cvss: 9.8, service: 'HTTPS', port: 443, solution: 'Apply CTX561482 patches.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2023-3519'], exploitable: true },
  { id: 'v8', cve: 'CVE-2024-3400', severity: 'CRITICAL', title: 'PAN-OS Command Injection', description: 'OS command injection in GlobalProtect feature of Palo Alto PAN-OS.', cvss: 10.0, service: 'HTTPS', port: 443, solution: 'Apply PAN-OS security updates.', references: ['https://nvd.nist.gov/vuln/detail/CVE-2024-3400'], exploitable: true },
];

export const mockExploits: Exploit[] = [
  { id: 'e1', name: 'exploit/multi/handler', type: 'Handler', platform: 'Multi', arch: 'x86/x64', reliability: 'Excellent', description: 'Generic payload handler — use with staged payloads.', cve: 'N/A', rank: 'Excellent', payload_options: ['windows/meterpreter/reverse_tcp', 'linux/x64/meterpreter/reverse_tcp'] },
  { id: 'e2', name: 'exploit/windows/smb/ms17_010_eternalblue', type: 'Remote', platform: 'Windows', arch: 'x64', reliability: 'Excellent', description: 'EternalBlue SMB exploit targeting MS17-010.', cve: 'CVE-2017-0144', rank: 'Excellent', payload_options: ['windows/x64/meterpreter/reverse_tcp', 'windows/x64/shell/reverse_tcp'] },
  { id: 'e3', name: 'exploit/multi/http/log4shell_header_injection', type: 'Remote', platform: 'Multi', arch: 'x86/x64', reliability: 'Excellent', description: 'Log4Shell JNDI injection via HTTP headers.', cve: 'CVE-2021-44228', rank: 'Excellent', payload_options: ['linux/x64/meterpreter/reverse_tcp', 'java/meterpreter/reverse_tcp'] },
  { id: 'e4', name: 'exploit/windows/http/fortinet_sslvpn_rce', type: 'Remote', platform: 'Windows', arch: 'x64', reliability: 'Great', description: 'Fortinet SSL VPN unauthenticated heap overflow.', cve: 'CVE-2024-21762', rank: 'Great', payload_options: ['windows/meterpreter/reverse_https', 'windows/shell/reverse_https'] },
  { id: 'e5', name: 'exploit/windows/local/print_spooler_priv_esc', type: 'Local', platform: 'Windows', arch: 'x64', reliability: 'Great', description: 'PrintNightmare privilege escalation via print spooler.', cve: 'CVE-2021-34527', rank: 'Great', payload_options: ['windows/x64/meterpreter/reverse_tcp'] },
  { id: 'e6', name: 'exploit/multi/http/citrix_netscaler_rce', type: 'Remote', platform: 'Multi', arch: 'x64', reliability: 'Excellent', description: 'Unauthenticated RCE in Citrix NetScaler ADC.', cve: 'CVE-2023-3519', rank: 'Excellent', payload_options: ['linux/x64/meterpreter/reverse_tcp', 'cmd/unix/reverse_bash'] },
];

export const mockPayloads: Payload[] = [
  { id: 'p1', name: 'windows/x64/meterpreter/reverse_tcp', type: 'meterpreter', platform: 'Windows', arch: 'x64', size: 308, description: 'Staged Meterpreter reverse TCP payload for Windows x64.', options: { LHOST: '10.0.0.1', LPORT: '4444', ExitFunc: 'thread' } },
  { id: 'p2', name: 'windows/x64/meterpreter/reverse_https', type: 'meterpreter', platform: 'Windows', arch: 'x64', size: 552, description: 'Staged Meterpreter reverse HTTPS — encrypted comms.', options: { LHOST: '10.0.0.1', LPORT: '443', HandlerSSLCert: '', StagerVerifySSLCert: 'true' } },
  { id: 'p3', name: 'linux/x64/meterpreter/reverse_tcp', type: 'meterpreter', platform: 'Linux', arch: 'x64', size: 130, description: 'Staged Meterpreter reverse TCP for Linux x64.', options: { LHOST: '10.0.0.1', LPORT: '4444' } },
  { id: 'p4', name: 'cmd/unix/reverse_bash', type: 'reverse_shell', platform: 'Unix', arch: 'cmd', size: 92, description: 'Bash reverse shell one-liner.', options: { LHOST: '10.0.0.1', LPORT: '4444' } },
  { id: 'p5', name: 'java/meterpreter/reverse_tcp', type: 'meterpreter', platform: 'Java', arch: 'java', size: 6144, description: 'Java Meterpreter for cross-platform targets.', options: { LHOST: '10.0.0.1', LPORT: '4444' } },
  { id: 'p6', name: 'windows/x64/shell/reverse_tcp', type: 'reverse_shell', platform: 'Windows', arch: 'x64', size: 259, description: 'Staged Windows shell reverse TCP.', options: { LHOST: '10.0.0.1', LPORT: '4444' } },
];

export const mockTargets: Target[] = [
  {
    ip: '192.168.1.10', hostname: 'WIN-CORP-DC01', os: 'Windows Server 2019', openPorts: [22, 80, 443, 445, 3389],
    services: [
      { port: 80, service: 'HTTP', version: 'Apache 2.4.50' },
      { port: 443, service: 'HTTPS', version: 'Apache 2.4.50' },
      { port: 445, service: 'SMB', version: 'Windows SMB 3.1.1' },
      { port: 3389, service: 'RDP', version: 'Microsoft RDP 10.0' },
    ],
    vulnerabilities: [mockVulnerabilities[1], mockVulnerabilities[2]],
  },
  {
    ip: '192.168.1.25', hostname: 'LINUX-WEB-01', os: 'Ubuntu 20.04 LTS', openPorts: [22, 80, 8080, 9200],
    services: [
      { port: 22, service: 'SSH', version: 'OpenSSH 8.2p1' },
      { port: 80, service: 'HTTP', version: 'nginx 1.18' },
      { port: 8080, service: 'HTTP', version: 'Apache Tomcat 9.0 (Log4j 2.14.1)' },
      { port: 9200, service: 'Elasticsearch', version: '7.10.1' },
    ],
    vulnerabilities: [mockVulnerabilities[0], mockVulnerabilities[5]],
  },
  {
    ip: '192.168.1.50', hostname: 'FORTINET-FW', os: 'FortiOS 7.2.0', openPorts: [22, 443, 8443],
    services: [
      { port: 443, service: 'HTTPS', version: 'FortiGate SSL-VPN 7.2.0' },
      { port: 8443, service: 'HTTPS', version: 'FortiGate Admin 7.2.0' },
    ],
    vulnerabilities: [mockVulnerabilities[4]],
  },
];

export const mockScanResult: ScanResult = {
  id: 'scan-001',
  timestamp: '2026-03-09T10:00:00Z',
  target: '192.168.1.0/24',
  status: 'completed',
  vulnerabilities: mockVulnerabilities,
  hosts: mockTargets,
  duration: 284,
};

export const mockReport: Report = {
  id: 'rpt-001',
  title: 'Internal Network Penetration Test — Q1 2026',
  timestamp: '2026-03-09T11:00:00Z',
  operator: 'Operator Alpha',
  scope: '192.168.1.0/24, WiFi SSID: CorpNet-*',
  networks: mockNetworks,
  targets: mockTargets,
  findings: mockVulnerabilities,
  exploits_used: ['exploit/multi/http/log4shell_header_injection', 'exploit/windows/smb/ms17_010_eternalblue'],
  status: 'draft',
  risk_score: 9.4,
  executive_summary: 'Critical vulnerabilities including Log4Shell and EternalBlue were identified and successfully exploited on internal systems. Immediate remediation is required for all CRITICAL findings.',
};

export const mockPhoneDevice: PhoneDevice = {
  id: 'phone-001',
  name: 'RedTeam Phone Alpha',
  connected: false,
  batteryLevel: 78,
  location: { lat: 37.7749, lng: -122.4194 },
  wardrivingActive: false,
  networksFound: 0,
  lastSync: '2026-03-09T10:55:00Z',
};
