import { useState } from 'react';
import { FileText, Download, Share2, Printer, Calendar, ShieldAlert, Wifi, Target, AlertTriangle, ChevronRight, Check } from 'lucide-react';
import { mockReport, mockNetworks, mockVulnerabilities, mockTargets } from '../data/mockData';

const severityScore: Record<string, number> = { CRITICAL: 10, HIGH: 7, MEDIUM: 4, LOW: 2, INFO: 1 };

export default function Reports() {
  const [report] = useState(mockReport);
  const [view, setView] = useState<'summary' | 'networks' | 'vulns' | 'exploits'>('summary');
  const [exportFormat, setExportFormat] = useState<'pdf' | 'html' | 'json'>('html');

  const vulnBySev = mockVulnerabilities.reduce((acc, v) => {
    acc[v.severity] = (acc[v.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const avgCvss = (mockVulnerabilities.reduce((sum, v) => sum + v.cvss, 0) / mockVulnerabilities.length).toFixed(1);
  const riskScore = (Object.entries(vulnBySev).reduce((sum, [sev, count]) => sum + severityScore[sev] * count, 0) / 10).toFixed(1);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-wider flex items-center gap-3">
            <FileText size={24} />
            REPORTS
          </h1>
          <p className="text-gray-600 text-sm font-mono mt-1">Assessment findings & penetration test documentation</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={exportFormat}
            onChange={e => setExportFormat(e.target.value as any)}
            className="bg-[#0d1117] border border-cyan-900/50 rounded px-3 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-cyan-600"
          >
            <option value="html">HTML</option>
            <option value="pdf">PDF</option>
            <option value="json">JSON</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-cyan-900/30 text-cyan-400 border border-cyan-700 rounded hover:bg-cyan-800/50 transition-all font-mono text-xs">
            <Download size={14} />
            EXPORT
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#0d1117] text-gray-400 border border-gray-700 rounded hover:bg-gray-800/50 transition-all font-mono text-xs">
            <Share2 size={14} />
            SHARE
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#0d1117] text-gray-400 border border-gray-700 rounded hover:bg-gray-800/50 transition-all font-mono text-xs">
            <Printer size={14} />
            PRINT
          </button>
        </div>
      </div>

      {/* Report meta */}
      <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold text-white font-mono">{report.title}</h2>
            <div className="flex items-center gap-4 mt-2 text-xs font-mono text-gray-600">
              <span className="flex items-center gap-1"><Calendar size={12} /> {new Date(report.timestamp).toLocaleDateString()}</span>
              <span>Operator: <span className="text-cyan-500">{report.operator}</span></span>
              <span>Scope: <span className="text-gray-400">{report.scope}</span></span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-600 font-mono mb-1">RISK SCORE</div>
            <div className={`text-3xl font-bold font-mono ${Number(riskScore) > 8 ? 'text-red-400' : Number(riskScore) > 5 ? 'text-orange-400' : 'text-yellow-400'}`}>
              {riskScore}<span className="text-lg text-gray-600">/10</span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: 'Hosts', value: mockTargets.length, icon: Target, color: 'text-cyan-400 border-cyan-900/30' },
          { label: 'Networks', value: mockNetworks.length, icon: Wifi, color: 'text-cyan-400 border-cyan-900/30' },
          { label: 'Vulnerabilities', value: mockVulnerabilities.length, icon: ShieldAlert, color: 'text-red-400 border-red-900/30' },
          { label: 'Avg CVSS', value: avgCvss, icon: AlertTriangle, color: 'text-orange-400 border-orange-900/30' },
          { label: 'Exploits Used', value: report.exploits_used.length, icon: AlertTriangle, color: 'text-purple-400 border-purple-900/30' },
        ].map(stat => (
          <div key={stat.label} className={`bg-[#0d1117] border rounded-lg p-3 text-center ${stat.color}`}>
            <div className="text-xl font-bold font-mono">{stat.value}</div>
            <div className="text-xs text-gray-600 font-mono mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* View tabs */}
      <div className="flex gap-2 border-b border-gray-800/50 pb-3">
        {(['summary', 'networks', 'vulns', 'exploits'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setView(tab)}
            className={`flex items-center gap-2 px-4 py-2 rounded font-mono text-xs transition-all ${
              view === tab
                ? 'border border-cyan-700 text-cyan-400 bg-cyan-900/20'
                : 'border border-gray-700 text-gray-600 hover:text-gray-400'
            }`}
          >
            {tab === 'summary' && 'Executive Summary'}
            {tab === 'networks' && 'Network Findings'}
            {tab === 'vulns' && 'Vulnerabilities'}
            {tab === 'exploits' && 'Exploit Details'}
          </button>
        ))}
      </div>

      {/* Content */}
      {view === 'summary' && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-6 space-y-6">
          <div>
            <h3 className="text-sm font-bold text-cyan-400 font-mono tracking-wider mb-3">EXECUTIVE SUMMARY</h3>
            <p className="text-sm text-gray-300 font-mono leading-relaxed">{report.executive_summary}</p>
          </div>

          <div>
            <h3 className="text-sm font-bold text-cyan-400 font-mono tracking-wider mb-3">KEY FINDINGS BY SEVERITY</h3>
            <div className="space-y-2">
              {Object.entries(vulnBySev).map(([sev, count]) => (
                <div key={sev} className="flex items-center gap-3">
                  <span className={`text-xs font-mono font-bold w-20 ${
                    sev === 'CRITICAL' ? 'text-red-400' : sev === 'HIGH' ? 'text-orange-400' : sev === 'MEDIUM' ? 'text-yellow-400' : 'text-blue-400'
                  }`}>{sev}</span>
                  <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        sev === 'CRITICAL' ? 'bg-red-500' : sev === 'HIGH' ? 'bg-orange-500' : sev === 'MEDIUM' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${(count / mockVulnerabilities.length) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 font-mono w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-cyan-400 font-mono tracking-wider mb-3">RECOMMENDATIONS</h3>
            <ul className="space-y-2 text-xs font-mono text-gray-400">
              <li className="flex items-start gap-2"><ChevronRight size={14} className="text-red-400 mt-0.5 flex-shrink-0" /> Immediately patch all CRITICAL vulnerabilities (Log4Shell, PrintNightmare, Fortinet SSL-VPN)</li>
              <li className="flex items-start gap-2"><ChevronRight size={14} className="text-orange-400 mt-0.5 flex-shrink-0" /> Disable unnecessary services and close exposed ports on perimeter devices</li>
              <li className="flex items-start gap-2"><ChevronRight size={14} className="text-yellow-400 mt-0.5 flex-shrink-0" /> Implement network segmentation to limit lateral movement</li>
              <li className="flex items-start gap-2"><ChevronRight size={14} className="text-cyan-400 mt-0.5 flex-shrink-0" /> Conduct regular vulnerability assessments and penetration tests</li>
              <li className="flex items-start gap-2"><ChevronRight size={14} className="text-green-400 mt-0.5 flex-shrink-0" /> Deploy EDR/XDR solutions with behavioral detection capabilities</li>
            </ul>
          </div>
        </div>
      )}

      {view === 'networks' && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg overflow-hidden">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-gray-600 border-b border-gray-800 bg-black/30">
                {['SSID', 'BSSID', 'CHANNEL', 'SIGNAL', 'SECURITY', 'ENCRYPTION', 'VENDOR', 'RISK'].map(h => (
                  <th key={h} className="text-left py-3 px-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockNetworks.map(n => (
                <tr key={n.id} className="border-b border-gray-800/30 hover:bg-cyan-900/10">
                  <td className="py-2.5 px-4 text-white">{n.ssid}</td>
                  <td className="py-2.5 px-4 text-gray-500">{n.bssid}</td>
                  <td className="py-2.5 px-4 text-cyan-600">{n.channel}</td>
                  <td className="py-2.5 px-4 text-gray-400">{n.signal} dBm</td className="py-2.5>
                  <td px-4">
                    <span className={`text-xs px-2 py-0.5 rounded border ${
                      n.security === 'OPEN' ? 'bg-red-900/30 text-red-400 border-red-800' :
                      n.security === 'WEP' ? 'bg-orange-900/30 text-orange-400 border-orange-800' :
                      'bg-green-900/30 text-green-400 border-green-800'
                    }`}>{n.security}</span>
                  </td>
                  <td className="py-2.5 px-4 text-gray-500">{n.encryption}</td>
                  <td className="py-2.5 px-4 text-gray-500">{n.vendor}</td>
                  <td className="py-2.5 px-4">
                    {(n.security === 'OPEN' || n.security === 'WEP') ? (
                      <span className="flex items-center gap-1 text-red-400"><AlertTriangle size={12} /> HIGH</span>
                    ) : (
                      <span className="flex items-center gap-1 text-green-400"><Check size={12} /> LOW</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {view === 'vulns' && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg overflow-hidden">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-gray-600 border-b border-gray-800 bg-black/30">
                {['CVE', 'SEVERITY', 'CVSS', 'SERVICE', 'PORT', 'TITLE', 'EXPLOITABLE'].map(h => (
                  <th key={h} className="text-left py-3 px-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockVulnerabilities.map(v => (
                <tr key={v.id} className="border-b border-gray-800/30 hover:bg-cyan-900/10">
                  <td className="py-2.5 px-4 text-cyan-600">{v.cve}</td>
                  <td className="py-2.5 px-4">
                    <span className={`text-xs px-2 py-0.5 rounded border ${
                      v.severity === 'CRITICAL' ? 'bg-red-900/30 text-red-400 border-red-800' :
                      v.severity === 'HIGH' ? 'bg-orange-900/30 text-orange-400 border-orange-800' :
                      v.severity === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' :
                      'bg-blue-900/30 text-blue-400 border-blue-800'
                    }`}>{v.severity}</span>
                  </td>
                  <td className="py-2.5 px-4 text-orange-400 font-bold">{v.cvss}</td>
                  <td className="py-2.5 px-4 text-gray-500">{v.service}</td>
                  <td className="py-2.5 px-4 text-gray-400">{v.port}</td>
                  <td className="py-2.5 px-4 text-white max-w-xs truncate">{v.title}</td>
                  <td className="py-2.5 px-4">
                    {v.exploitable ? (
                      <span className="flex items-center gap-1 text-red-400"><AlertTriangle size={12} /> YES</span>
                    ) : (
                      <span className="text-gray-600">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {view === 'exploits' && (
        <div className="bg-[#0d1117] border border-cyan-900/30 rounded-lg p-4 space-y-4">
          <div className="text-sm font-bold text-cyan-400 font-mono tracking-wider">EXPLOITS USED IN ASSESSMENT</div>
          {report.exploits_used.map((e, i) => (
            <div key={i} className="bg-black/30 border border-gray-800/50 rounded p-3">
              <div className="text-xs text-purple-400 font-mono">{e}</div>
              <div className="text-xs text-gray-600 mt-1">Successfully executed against target infrastructure</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
