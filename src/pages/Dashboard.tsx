import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert, Wifi, Bug, Package, Activity, AlertTriangle,
  TrendingUp, Server, Cpu, Database, Eye
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { mockVulnerabilities, mockNetworks, mockTargets } from '../data/mockData';

const activityData = [
  { time: '00:00', scans: 2, exploits: 0, alerts: 1 },
  { time: '02:00', scans: 1, exploits: 0, alerts: 0 },
  { time: '04:00', scans: 0, exploits: 0, alerts: 0 },
  { time: '06:00', scans: 3, exploits: 1, alerts: 2 },
  { time: '08:00', scans: 8, exploits: 2, alerts: 5 },
  { time: '10:00', scans: 12, exploits: 4, alerts: 7 },
  { time: '12:00', scans: 15, exploits: 6, alerts: 9 },
];

const severityData = [
  { name: 'CRITICAL', value: 4, color: '#ef4444' },
  { name: 'HIGH', value: 2, color: '#f97316' },
  { name: 'MEDIUM', value: 1, color: '#eab308' },
  { name: 'LOW', value: 1, color: '#3b82f6' },
];

const networkSecurityData = [
  { name: 'WPA3', count: 1, fill: '#10b981' },
  { name: 'WPA2-Ent', count: 1, fill: '#06b6d4' },
  { name: 'WPA2-PSK', count: 2, fill: '#eab308' },
  { name: 'WEP', count: 1, fill: '#f97316' },
  { name: 'OPEN', count: 1, fill: '#ef4444' },
];

function StatCard({ label, value, sub, icon: Icon, color, onClick }: {
  label: string; value: string | number; sub?: string;
  icon: React.ElementType; color: string; onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`bg-[#0d1117] rounded-lg p-5 border ${color} cursor-pointer hover:bg-[#111827] transition-all duration-200 group`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 font-mono tracking-wider uppercase">{label}</p>
          <p className="text-3xl font-bold mt-1 font-mono text-white">{value}</p>
          {sub && <p className="text-xs text-gray-600 mt-1 font-mono">{sub}</p>}
        </div>
        <Icon size={24} className={`opacity-60 group-hover:opacity-100 transition-opacity`} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setTick(x => x + 1), 2000);
    return () => clearInterval(t);
  }, []);

  const criticalCount = mockVulnerabilities.filter(v => v.severity === 'CRITICAL').length;
  const exploitableCount = mockVulnerabilities.filter(v => v.exploitable).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-wider">OPERATIONS DASHBOARD</h1>
          <p className="text-gray-600 text-sm font-mono mt-1">Real-time threat intelligence & campaign control</p>
        </div>
        <div className="flex items-center gap-3 bg-[#0d1117] px-4 py-2 rounded border border-yellow-800/50">
          <AlertTriangle size={16} className="text-yellow-500" />
          <span className="text-yellow-400 text-xs font-mono font-bold">ACTIVE ENGAGEMENT</span>
          <span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Networks Detected" value={mockNetworks.length}
          sub={`${mockNetworks.filter(n => n.security === 'OPEN').length} open networks`}
          icon={Wifi} color="border-cyan-800/50 shadow-[0_0_10px_rgba(6,182,212,0.1)]"
          onClick={() => navigate('/wardrive')}
        />
        <StatCard
          label="Critical Vulns" value={criticalCount}
          sub={`${exploitableCount} exploitable`}
          icon={ShieldAlert} color="border-red-800/50 shadow-[0_0_10px_rgba(239,68,68,0.1)]"
          onClick={() => navigate('/scanner')}
        />
        <StatCard
          label="Targets Profiled" value={mockTargets.length}
          sub="Awaiting exploitation"
          icon={Server} color="border-orange-800/50 shadow-[0_0_10px_rgba(249,115,22,0.1)]"
          onClick={() => navigate('/exploits')}
        />
        <StatCard
          label="Payloads Staged" value={3}
          sub="Ready to deliver"
          icon={Package} color="border-purple-800/50 shadow-[0_0_10px_rgba(139,92,246,0.1)]"
          onClick={() => navigate('/payload')}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Activity chart */}
        <div className="lg:col-span-2 bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} className="text-cyan-400" />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Operation Activity — UTC Today</h2>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="exploitGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="time" tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }} />
              <Tooltip
                contentStyle={{ background: '#0d1117', border: '1px solid #06b6d4', borderRadius: 4, fontFamily: 'monospace', fontSize: 11 }}
                labelStyle={{ color: '#06b6d4' }}
              />
              <Area type="monotone" dataKey="scans" stroke="#06b6d4" fill="url(#scanGrad)" strokeWidth={2} name="Scans" />
              <Area type="monotone" dataKey="exploits" stroke="#ef4444" fill="url(#exploitGrad)" strokeWidth={2} name="Exploits" />
              <Area type="monotone" dataKey="alerts" stroke="#f97316" fill="none" strokeWidth={1} strokeDasharray="4 2" name="Alerts" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Severity pie */}
        <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-cyan-400" />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Vuln Severity</h2>
          </div>
          <ResponsiveContainer width="100%" height={140}>
            <PieChart>
              <Pie data={severityData} cx="50%" cy="50%" innerRadius={40} outerRadius={65} dataKey="value" strokeWidth={0}>
                {severityData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} opacity={0.85} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#0d1117', border: '1px solid #374151', fontFamily: 'monospace', fontSize: 11 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1 mt-2">
            {severityData.map(d => (
              <div key={d.name} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color }}></span>
                  <span className="text-gray-500">{d.name}</span>
                </div>
                <span className="text-white font-bold">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Network security + Targets row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Network security bar chart */}
        <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30">
          <div className="flex items-center gap-2 mb-4">
            <Wifi size={16} className="text-cyan-400" />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">WiFi Security Distribution</h2>
          </div>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={networkSecurityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }} />
              <Tooltip contentStyle={{ background: '#0d1117', border: '1px solid #374151', fontFamily: 'monospace', fontSize: 11 }} />
              <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                {networkSecurityData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Target summary */}
        <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30">
          <div className="flex items-center gap-2 mb-4">
            <Eye size={16} className="text-cyan-400" />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Target Roster</h2>
          </div>
          <div className="space-y-2">
            {mockTargets.map(t => (
              <div key={t.ip} className="flex items-center justify-between p-2 rounded bg-black/30 border border-gray-800/50 hover:border-cyan-800/50 transition-colors cursor-pointer" onClick={() => navigate('/scanner')}>
                <div className="flex items-center gap-3">
                  <Server size={14} className="text-cyan-600" />
                  <div>
                    <p className="text-xs font-mono text-white">{t.hostname}</p>
                    <p className="text-xs font-mono text-gray-600">{t.ip} — {t.os}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-red-400">
                    {t.vulnerabilities.filter(v => v.severity === 'CRITICAL').length} CRIT
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Terminal log */}
      <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30 scan-effect">
        <div className="flex items-center gap-2 mb-3">
          <Cpu size={16} className="text-green-400" />
          <h2 className="text-xs font-mono text-green-400 tracking-widest uppercase">System Log</h2>
          <span className="ml-auto text-xs font-mono text-gray-700">LIVE</span>
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
        </div>
        <div className="space-y-1 font-mono text-xs">
          {[
            { time: '11:42:07', level: 'INFO', msg: 'War drive session active — 6 networks detected' },
            { time: '11:40:22', level: 'WARN', msg: 'Open network detected: OPEN-HOTSPOT (AA:BB:CC:DD:EE:05)' },
            { time: '11:38:55', level: 'CRIT', msg: 'CVE-2021-44228 confirmed on 192.168.1.25:8080' },
            { time: '11:35:10', level: 'INFO', msg: 'AI recommends: exploit/multi/http/log4shell_header_injection' },
            { time: '11:30:02', level: 'INFO', msg: 'Payload staged: windows/x64/meterpreter/reverse_tcp' },
            { time: '11:22:44', level: 'SUCC', msg: 'Meterpreter session 1 opened (10.0.0.1:4444 → 192.168.1.25:49234)' },
          ].map((log, i) => (
            <div key={i} className="flex gap-3">
              <span className="text-gray-700">[{log.time}]</span>
              <span className={`w-10 ${log.level === 'CRIT' ? 'text-red-400' : log.level === 'WARN' ? 'text-yellow-400' : log.level === 'SUCC' ? 'text-green-400' : 'text-cyan-700'}`}>
                {log.level}
              </span>
              <span className="text-gray-400">{log.msg}</span>
            </div>
          ))}
          <div className="flex gap-3 mt-2">
            <span className="text-gray-700">[{new Date().toLocaleTimeString()}]</span>
            <span className="text-green-400">SYS </span>
            <span className="text-white">▸<span className="blink">_</span></span>
          </div>
        </div>
      </div>
    </div>
  );
}
