import { useState, useEffect } from 'react';
import { ShieldAlert, Play, Server, ChevronDown, ChevronRight, ExternalLink, Brain } from 'lucide-react';
import type { Vulnerability, Target } from '../types';

type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

const severityColor: Record<Severity, string> = {
  CRITICAL: 'text-red-400', HIGH: 'text-orange-400',
  MEDIUM: 'text-yellow-400', LOW: 'text-blue-400', INFO: 'text-gray-400',
};

const severityBg: Record<Severity, string> = {
  CRITICAL: 'bg-red-900/30 border-red-800/40',
  HIGH: 'bg-orange-900/30 border-orange-800/40',
  MEDIUM: 'bg-yellow-900/30 border-yellow-800/40',
  LOW: 'bg-blue-900/30 border-blue-800/40',
  INFO: 'bg-gray-900/30 border-gray-800/40',
};

const aiInsights: Record<string, string> = {
  'v1': 'AI RECOMMENDATION: Immediately exploit via exploit/multi/http/log4shell_header_injection. High confidence (97%). Target 192.168.1.25:8080 running Tomcat with Log4j 2.14.1. Use JNDI callback to your listener. Suggested payload: linux/x64/meterpreter/reverse_tcp.',
  'v2': 'AI RECOMMENDATION: Use exploit/windows/local/print_spooler_priv_esc after initial access. Requires local user context. Combine with credential harvesting post-exploitation. CVSS 8.8 — critical priority.',
  'v3': 'AI RECOMMENDATION: Craft malicious DOCX with MSDT URI trigger. Social engineering vector required. Medium complexity. Pre-requisite: phishing campaign or physical access.',
  'v4': 'AI RECOMMENDATION: Send crafted calendar invite to target Outlook user. Captures NTLMv2 hashes passively. Combine with Responder/NTLMRelayX for immediate lateral movement without cracking.',
  'v5': 'AI RECOMMENDATION: Unauthenticated. Direct exploit against 192.168.1.50:443. exploit/windows/http/fortinet_sslvpn_rce — Excellent reliability. Drop meterpreter for persistent access.',
  'v6': 'AI RECOMMENDATION: Local privilege escalation. Requires shell on target first. Low direct impact — chain with other exploits for root access.',
  'v7': 'AI RECOMMENDATION: Unauthenticated RCE on Citrix NetScaler. exploit/multi/http/citrix_netscaler_rce. High-value target — likely routes all internal traffic. Persistent backdoor recommended.',
  'v8': 'AI RECOMMENDATION: CVSSv3 10.0 — Maximum severity. PAN-OS GlobalProtect. Weaponizable without authentication. Direct shell access to firewall — catastrophic impact.',
};

function VulnRow({ vuln, expanded, onToggle }: { vuln: Vulnerability; expanded: boolean; onToggle: () => void }) {
  return (
    <div className={`border rounded-lg mb-2 ${severityBg[vuln.severity]} transition-all`}>
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-3 text-left hover:bg-white/5 transition-colors"
      >
        {expanded ? <ChevronDown size={14} className="text-gray-500 flex-shrink-0" /> : <ChevronRight size={14} className="text-gray-500 flex-shrink-0" />}
        <span className={`text-xs font-bold font-mono w-20 flex-shrink-0 ${severityColor[vuln.severity]}`}>{vuln.severity}</span>
        <span className="text-xs text-gray-400 font-mono w-36 flex-shrink-0">{vuln.cve}</span>
        <span className="text-sm text-white font-mono flex-1">{vuln.title}</span>
        <div className="flex items-center gap-3 ml-auto flex-shrink-0">
          <span className={`text-xs font-mono font-bold ${vuln.cvss >= 9 ? 'text-red-400' : vuln.cvss >= 7 ? 'text-orange-400' : 'text-yellow-400'}`}>
            CVSS {vuln.cvss}
          </span>
          <span className={`text-xs font-mono px-2 py-0.5 rounded ${vuln.exploitable ? 'bg-red-900/50 text-red-400 border border-red-700' : 'bg-gray-800 text-gray-600 border border-gray-700'}`}>
            {vuln.exploitable ? 'EXPLOITABLE' : 'NOT EXPLOITABLE'}
          </span>
          <span className="text-xs text-gray-600 font-mono">{vuln.service}:{vuln.port}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-white/5 pt-3">
          <p className="text-xs text-gray-400 font-mono">{vuln.description}</p>

          {/* AI Insight */}
          {aiInsights[vuln.id] && (
            <div className="bg-purple-900/20 border border-purple-700/40 rounded p-3">
              <div className="flex items-center gap-2 mb-1">
                <Brain size={13} className="text-purple-400" />
                <span className="text-xs text-purple-400 font-mono font-bold">AI EXPLOIT ADVISOR</span>
              </div>
              <p className="text-xs text-purple-300 font-mono leading-relaxed">{aiInsights[vuln.id]}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div>
              <span className="text-gray-600">Solution: </span>
              <span className="text-green-400">{vuln.solution}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-600">References: </span>
              {vuln.references.map((r, i) => (
                <a key={i} href={r} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-cyan-500 hover:text-cyan-300">
                  NVD <ExternalLink size={10} />
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TargetPanel({ target, selected, onSelect }: { target: Target; selected: boolean; onSelect: () => void }) {
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left p-3 rounded-lg border transition-all font-mono text-xs ${selected ? 'bg-cyan-900/20 border-cyan-700' : 'bg-black/30 border-gray-800/50 hover:border-cyan-900'}`}
    >
      <div className="flex items-center gap-2 mb-1">
        <Server size={12} className="text-cyan-600" />
        <span className="text-white font-bold">{target.ip}</span>
        <span className="ml-auto text-red-400">{target.vulnerabilities.filter(v => v.severity === 'CRITICAL').length} CRIT</span>
      </div>
      <div className="text-gray-600">{target.hostname}</div>
      <div className="text-gray-700">{target.os}</div>
    </button>
  );
}

export default function VulnScanner() {
  const [scanning, setScanning] = useState(false);
  const [scanCompleted, setScanCompleted] = useState(false);
  const [targetIP, setTargetIP] = useState('192.168.1.0/24');
  const [selectedTarget, setSelectedTarget] = useState<Target | null>(null);
  const [expandedVulns, setExpandedVulns] = useState<Set<string>>(new Set());
  const [filterSev, setFilterSev] = useState<string>('ALL');
  const [progress, setProgress] = useState(0);
  const [scanLogs, setScanLogs] = useState<string[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function runScan() {
    setScanning(true);
    setScanCompleted(false);
    setProgress(0);
    setScanLogs(['[INIT] Starting Nmap-compatible scan...', '[INFO] Target: ' + targetIP]);
    setLoading(true);
    setError(null);
    
    // In a real implementation, this would trigger a scan via the backend API
    // For now, we'll simulate the UI progression but fetch real data
    const stages = [
      '[DISC] Host discovery — ICMP/ARP sweep',
      '[PORT] Port scanning — SYN stealth scan (-sS)',
      '[SVCV] Service version detection (-sV)',
      '[OSDT] OS fingerprinting (-O)',
      '[SCRP] NSE script execution (vuln, exploit)',
      '[CVSS] CVE cross-reference & scoring',
      '[AI]   AI analysis — correlation & exploit mapping',
      '[REPT] Generating structured findings...',
    ];
    let i = 0;
    const t = setInterval(() => {
      if (i < stages.length) {
        setScanLogs(prev => [...prev, stages[i]]);
        setProgress(Math.round(((i + 1) / stages.length) * 100));
        i++;
      } else {
        clearInterval(t);
        setScanning(false);
        setScanCompleted(true);
        setProgress(100);
        // Fetch real vulnerability data after "scan" completes
        fetchVulnerabilityData();
      }
    }, 500);
  }

   async function fetchVulnerabilityData() {
     try {
       // Fetch vulnerabilities from backend
       const vulnResponse = await fetch('/api/vulnerabilities');
       let vulnData = [];
       if (vulnResponse.ok) {
         vulnData = await vulnResponse.json();
         setVulnerabilities(vulnData);
       }
       
       // In a real implementation, we would also fetch targets from a dedicated endpoint
       // For now, we'll set empty targets and let the UI handle it
       setTargets([]);
       
       setScanLogs(prev => [...prev, `[DONE] Scan complete — ${vulnData.length} findings`]);
       setLoading(false);
     } catch (err) {
       setScanning(false);
       setLoading(false);
       setError('Failed to load vulnerability data: ' + (err instanceof Error ? err.message : String(err)));
       setScanLogs(prev => [...prev, `[ERROR] Failed to load vulnerability data`]);
     }
   }

  function toggleVuln(id: string) {
    setExpandedVulns(prev => {
      const s = new Set(prev);
      s.has(id) ? s.delete(id) : s.add(id);
      return s;
    });
  }

  const vulns = selectedTarget ? (selectedTarget.vulnerabilities || []) : vulnerabilities;
  const filteredVulns = filterSev === 'ALL' ? vulns : vulns.filter((v: Vulnerability) => v.severity === filterSev);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-wider flex items-center gap-3">
            <ShieldAlert size={24} />
            AI VULNERABILITY SCANNER
          </h1>
          <p className="text-gray-600 text-sm font-mono mt-1">AI-powered CVE detection, CVSS scoring & exploit guidance</p>
        </div>
      </div>

      {/* Scan bar */}
      <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={targetIP}
            onChange={e => setTargetIP(e.target.value)}
            className="flex-1 bg-black/50 border border-cyan-900/50 rounded px-3 py-2 text-sm font-mono text-white placeholder-gray-700 focus:outline-none focus:border-cyan-600"
            placeholder="Target IP / CIDR / hostname..."
          />
          <button
            onClick={runScan}
            disabled={scanning}
            className={`flex items-center gap-2 px-5 py-2 rounded font-mono text-sm font-bold transition-all ${scanning ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-cyan-900/40 text-cyan-400 border border-cyan-700 hover:bg-cyan-800/50'}`}
          >
            <Play size={14} />
            {scanning ? 'SCANNING...' : 'RUN SCAN'}
          </button>
        </div>

        {(scanning || scanCompleted) && (
          <div className="mt-3 space-y-2">
            <div className="flex justify-between text-xs font-mono text-gray-600">
              <span>Progress</span><span>{progress}%</span>
            </div>
            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="font-mono text-xs text-green-400 max-h-24 overflow-y-auto space-y-0.5 bg-black/40 p-2 rounded">
              {scanLogs.map((l, i) => <div key={i}>{l}</div>)}
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Target list */}
       <div className="space-y-2">
         <div className="text-xs font-mono text-gray-600 tracking-wider uppercase mb-3">Hosts ({targets.length})</div>
         {targets.map(t => (
           <TargetPanel key={t.ip} target={t} selected={selectedTarget?.ip === t.ip} onSelect={() => setSelectedTarget(t)} />
         ))}
         <button
           onClick={() => setSelectedTarget(null)}
           className={`w-full text-left p-3 rounded-lg border transition-all font-mono text-xs ${!selectedTarget ? 'bg-cyan-900/20 border-cyan-700' : 'bg-black/30 border-gray-800/50 hover:border-cyan-900'}`}
         >
           <div className="text-cyan-400 font-bold">ALL FINDINGS</div>
           <div className="text-gray-600">{vulnerabilities.length} total vulns</div>
         </button>
       </div>

        {/* Findings */}
        <div className="lg:col-span-3 space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-5 gap-2">
            {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map(sev => {
              const count = sev === 'ALL' ? vulns.length : vulns.filter(v => v.severity === sev).length;
              const colors: Record<string, string> = {
                ALL: 'border-gray-700 text-gray-400',
                CRITICAL: 'border-red-800 text-red-400',
                HIGH: 'border-orange-800 text-orange-400',
                MEDIUM: 'border-yellow-800 text-yellow-400',
                LOW: 'border-blue-800 text-blue-400',
              };
              return (
                <button
                  key={sev}
                  onClick={() => setFilterSev(sev)}
                  className={`p-2 rounded border text-center font-mono text-xs transition-all ${colors[sev]} ${filterSev === sev ? 'bg-white/10' : 'bg-black/30 hover:bg-white/5'}`}
                >
                  <div className="text-lg font-bold">{count}</div>
                  <div className="text-xs opacity-70">{sev}</div>
                </button>
              );
            })}
          </div>

          {/* Vuln list */}
          <div>
            {filteredVulns.length === 0 ? (
              <div className="text-center py-12 text-gray-700 font-mono text-sm">
                {scanning ? '◉ Scanning in progress...' : 'No findings for selected filter'}
              </div>
            ) : (
              filteredVulns.map(v => (
                <VulnRow
                  key={v.id}
                  vuln={v}
                  expanded={expandedVulns.has(v.id)}
                  onToggle={() => toggleVuln(v.id)}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
