import { useState, useEffect, useRef } from 'react';
import { Radio, Wifi, WifiOff, Smartphone, MapPin, Battery, RefreshCw, Signal, Lock, Unlock, AlertTriangle } from 'lucide-react';
import { mockNetworks, mockPhoneDevice } from '../data/mockData';
import type { WifiNetwork, PhoneDevice } from '../types';

const QR_LINK = 'https://redteam-mobile.local/pair?token=RT-ALPHA-001';

function SignalBar({ signal }: { signal: number }) {
  const strength = signal > -50 ? 4 : signal > -65 ? 3 : signal > -75 ? 2 : 1;
  return (
    <div className="flex items-end gap-0.5 h-4">
      {[1, 2, 3, 4].map(i => (
        <div
          key={i}
          style={{ height: `${i * 25}%` }}
          className={`w-1 rounded-sm ${i <= strength ? 'bg-cyan-400' : 'bg-gray-700'}`}
        />
      ))}
    </div>
  );
}

function SecurityIcon({ security }: { security: string }) {
  if (security === 'OPEN') return <Unlock size={14} className="text-red-400" />;
  if (security === 'WEP') return <Lock size={14} className="text-orange-400" />;
  return <Lock size={14} className="text-green-400" />;
}

function SecurityBadge({ security }: { security: string }) {
  const colors: Record<string, string> = {
    'OPEN': 'bg-red-900/50 text-red-400 border-red-700',
    'WEP': 'bg-orange-900/50 text-orange-400 border-orange-700',
    'WPA2-PSK': 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
    'WPA2-Enterprise': 'bg-blue-900/50 text-blue-400 border-blue-700',
    'WPA3': 'bg-green-900/50 text-green-400 border-green-700',
  };
  const cls = colors[security] || 'bg-gray-800/50 text-gray-400 border-gray-700';
  return (
    <span className={`text-xs font-mono px-2 py-0.5 rounded border ${cls}`}>{security}</span>
  );
}

export default function WarDrive() {
  const [phone, setPhone] = useState<PhoneDevice>({ ...mockPhoneDevice });
  const [scanning, setScanning] = useState(false);
  const [networks, setNetworks] = useState<WifiNetwork[]>([]);
  const [selected, setSelected] = useState<WifiNetwork | null>(null);
  const [filter, setFilter] = useState('');
  const [showQR, setShowQR] = useState(false);
  const [log, setLog] = useState<string[]>(['[SYS] War drive module initialized', '[SYS] Waiting for scan or mobile connection...']);
  const scanTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => { if (scanTimer.current) clearInterval(scanTimer.current); };
  }, []);

  function addLog(msg: string) {
    const ts = new Date().toLocaleTimeString();
    setLog(prev => [`[${ts}] ${msg}`, ...prev].slice(0, 50));
  }

  function startScan() {
    setScanning(true);
    setNetworks([]);
    addLog('[INFO] Initiating 802.11 passive scan on all channels...');
    let i = 0;
    scanTimer.current = setInterval(() => {
      if (i < mockNetworks.length) {
        const net = mockNetworks[i];
        setNetworks(prev => [...prev, net]);
        addLog(`[FOUND] SSID: ${net.ssid} | BSSID: ${net.bssid} | CH: ${net.channel} | ${net.signal} dBm | ${net.security}`);
        if (net.security === 'OPEN') addLog(`[WARN] OPEN network detected: ${net.ssid}`);
        if (net.security === 'WEP') addLog(`[WARN] Weak encryption (WEP): ${net.ssid}`);
        i++;
      } else {
        clearInterval(scanTimer.current!);
        setScanning(false);
        addLog(`[DONE] Scan complete — ${mockNetworks.length} networks discovered`);
        if (phone.connected) {
          addLog('[SYNC] Results synchronized to mobile device');
        }
      }
    }, 600);
  }

  function stopScan() {
    if (scanTimer.current) clearInterval(scanTimer.current);
    setScanning(false);
    addLog('[INFO] Scan manually stopped');
  }

  function connectPhone() {
    setShowQR(false);
    setPhone(prev => ({ ...prev, connected: true, networksFound: networks.length, wardrivingActive: scanning }));
    addLog('[PHONE] RedTeam Phone Alpha connected via secure pairing');
    addLog('[PHONE] Remote war drive control enabled');
  }

  function disconnectPhone() {
    setPhone(prev => ({ ...prev, connected: false }));
    addLog('[PHONE] Device disconnected');
  }

  const filtered = networks.filter(n =>
    n.ssid.toLowerCase().includes(filter.toLowerCase()) ||
    n.bssid.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-wider flex items-center gap-3">
            <Radio size={24} className={scanning ? 'text-red-400 animate-pulse' : ''} />
            WAR DRIVE MODULE
          </h1>
          <p className="text-gray-600 text-sm font-mono mt-1">802.11 passive reconnaissance & network mapping</p>
        </div>
        <div className="flex gap-3">
          {!scanning ? (
            <button
              onClick={startScan}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-900/30 text-cyan-400 border border-cyan-700 rounded hover:bg-cyan-900/50 transition-all font-mono text-sm"
            >
              <Radio size={16} />START SCAN
            </button>
          ) : (
            <button
              onClick={stopScan}
              className="flex items-center gap-2 px-4 py-2 bg-red-900/30 text-red-400 border border-red-700 rounded hover:bg-red-900/50 transition-all font-mono text-sm animate-pulse"
            >
              <RefreshCw size={16} className="animate-spin" />SCANNING...
            </button>
          )}
        </div>
      </div>

      {/* Phone device panel + QR */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Phone status */}
        <div className={`bg-[#0d1117] rounded-lg p-4 border ${phone.connected ? 'border-green-700/50 shadow-[0_0_15px_rgba(16,185,129,0.15)]' : 'border-cyan-900/30'}`}>
          <div className="flex items-center gap-2 mb-4">
            <Smartphone size={16} className={phone.connected ? 'text-green-400' : 'text-gray-600'} />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Mobile Integration</h2>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 font-mono">Device Name</span>
              <span className="text-xs text-white font-mono">{phone.name}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 font-mono">Status</span>
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${phone.connected ? 'bg-green-500 animate-pulse' : 'bg-gray-700'}`}></span>
                <span className={`text-xs font-mono font-bold ${phone.connected ? 'text-green-400' : 'text-gray-600'}`}>
                  {phone.connected ? 'CONNECTED' : 'DISCONNECTED'}
                </span>
              </div>
            </div>
            {phone.connected && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600 font-mono">Battery</span>
                  <div className="flex items-center gap-1">
                    <Battery size={12} className="text-green-400" />
                    <span className="text-xs text-green-400 font-mono">{phone.batteryLevel}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600 font-mono">Networks Found</span>
                  <span className="text-xs text-cyan-400 font-mono font-bold">{networks.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600 font-mono">GPS</span>
                  <div className="flex items-center gap-1">
                    <MapPin size={12} className="text-cyan-400" />
                    <span className="text-xs text-cyan-400 font-mono">
                      {phone.location?.lat.toFixed(4)}, {phone.location?.lng.toFixed(4)}
                    </span>
                  </div>
                </div>
              </>
            )}

            <div className="pt-2 space-y-2">
              {!phone.connected ? (
                <>
                  <button
                    onClick={() => setShowQR(true)}
                    className="w-full text-xs font-mono py-2 rounded border border-cyan-700 text-cyan-400 hover:bg-cyan-900/30 transition-all"
                  >
                    📱 PAIR MOBILE DEVICE
                  </button>
                  {showQR && (
                    <div className="space-y-2">
                      <div className="bg-white/5 rounded p-3 text-center border border-cyan-900/30">
                        <div className="text-xs text-gray-500 font-mono mb-2">Scan QR or enter link:</div>
                        {/* QR placeholder */}
                        <div className="inline-block bg-white p-2 rounded">
                          <div className="w-20 h-20 grid grid-cols-5 gap-0.5">
                            {Array.from({ length: 25 }).map((_, i) => (
                              <div key={i} className={`${Math.random() > 0.5 ? 'bg-black' : 'bg-white'} aspect-square`} />
                            ))}
                          </div>
                        </div>
                        <div className="text-xs text-cyan-700 font-mono mt-2 break-all">{QR_LINK}</div>
                      </div>
                      <button
                        onClick={connectPhone}
                        className="w-full text-xs font-mono py-2 rounded border border-green-700 text-green-400 hover:bg-green-900/30 transition-all"
                      >
                        ✓ SIMULATE CONNECTION
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="bg-green-900/20 rounded p-2 text-center border border-green-800/30">
                    <span className="text-xs text-green-400 font-mono">Remote war drive active</span>
                  </div>
                  <button
                    onClick={disconnectPhone}
                    className="w-full text-xs font-mono py-2 rounded border border-red-800 text-red-400 hover:bg-red-900/30 transition-all"
                  >
                    DISCONNECT DEVICE
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-[#0d1117] rounded-lg p-3 border border-cyan-900/30 text-center">
            <div className="text-2xl font-bold text-cyan-400 font-mono">{networks.length}</div>
            <div className="text-xs text-gray-600 font-mono mt-1">Detected</div>
          </div>
          <div className="bg-[#0d1117] rounded-lg p-3 border border-red-900/30 text-center">
            <div className="text-2xl font-bold text-red-400 font-mono">{networks.filter(n => n.security === 'OPEN').length}</div>
            <div className="text-xs text-gray-600 font-mono mt-1">Open</div>
          </div>
          <div className="bg-[#0d1117] rounded-lg p-3 border border-orange-900/30 text-center">
            <div className="text-2xl font-bold text-orange-400 font-mono">{networks.filter(n => n.security === 'WEP').length}</div>
            <div className="text-xs text-gray-600 font-mono mt-1">WEP (Weak)</div>
          </div>
          <div className="bg-[#0d1117] rounded-lg p-3 border border-green-900/30 text-center">
            <div className="text-2xl font-bold text-green-400 font-mono">{networks.filter(n => n.clients > 10).length}</div>
            <div className="text-xs text-gray-600 font-mono mt-1">High Traffic</div>
          </div>

          {/* Radar / sweep visualizer */}
          <div className="col-span-2 sm:col-span-4 bg-[#0d1117] rounded-lg p-4 border border-cyan-900/30 flex items-center gap-6">
            {/* Radar circle */}
            <div className="relative w-24 h-24 flex-shrink-0">
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <circle cx="50" cy="50" r="48" fill="none" stroke="#06b6d420" strokeWidth="1" />
                <circle cx="50" cy="50" r="32" fill="none" stroke="#06b6d420" strokeWidth="1" />
                <circle cx="50" cy="50" r="16" fill="none" stroke="#06b6d430" strokeWidth="1" />
                <line x1="50" y1="2" x2="50" y2="98" stroke="#06b6d415" strokeWidth="1" />
                <line x1="2" y1="50" x2="98" y2="50" stroke="#06b6d415" strokeWidth="1" />
                {scanning && (
                  <line
                    x1="50" y1="50" x2="50" y2="2"
                    stroke="#06b6d4"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    className="radar-line"
                    style={{ transformOrigin: '50px 50px' }}
                  />
                )}
                {networks.map((n, i) => {
                  const angle = (i / 6) * Math.PI * 2;
                  const r = 20 + (i % 3) * 10;
                  return (
                    <circle
                      key={n.id}
                      cx={50 + r * Math.cos(angle)}
                      cy={50 + r * Math.sin(angle)}
                      r="2.5"
                      fill={n.security === 'OPEN' ? '#ef4444' : n.security === 'WEP' ? '#f97316' : '#06b6d4'}
                      opacity="0.9"
                    />
                  );
                })}
              </svg>
            </div>
            <div className="flex-1 space-y-1">
              <div className="text-xs text-cyan-400 font-mono font-bold">RF SWEEP — 2.4GHz / 5GHz</div>
              <div className="text-xs text-gray-600 font-mono">Channels scanned: 1-14, 36-165</div>
              <div className="flex gap-3 text-xs font-mono mt-2">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span>Open</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500"></span>WEP</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-400"></span>Encrypted</span>
              </div>
              {scanning && <div className="text-xs text-red-400 font-mono animate-pulse mt-1">● SCANNING...</div>}
              {!scanning && networks.length > 0 && (
                <div className="text-xs text-green-400 font-mono mt-1">✓ {networks.length} networks mapped</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Network list */}
      <div className="bg-[#0d1117] rounded-lg border border-cyan-900/30">
        <div className="flex items-center gap-4 p-4 border-b border-cyan-900/30">
          <Wifi size={16} className="text-cyan-400" />
          <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Detected Networks</h2>
          <div className="ml-auto flex items-center gap-2">
            <input
              type="text"
              value={filter}
              onChange={e => setFilter(e.target.value)}
              placeholder="Filter SSID / BSSID..."
              className="bg-black/50 border border-cyan-900/50 rounded px-3 py-1.5 text-xs font-mono text-white placeholder-gray-700 focus:outline-none focus:border-cyan-600 w-48"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-gray-600 border-b border-gray-800/50">
                {['SSID', 'BSSID', 'CH', 'SIGNAL', 'SECURITY', 'VENDOR', 'CLIENTS', 'FREQ', ''].map(h => (
                  <th key={h} className="px-4 py-2 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-8 text-center text-gray-700 font-mono">
                    {scanning ? '◉ Scanning, please wait...' : 'No networks detected. Start a scan.'}
                  </td>
                </tr>
              ) : filtered.map(n => (
                <tr
                  key={n.id}
                  className={`border-b border-gray-800/30 cursor-pointer transition-colors hover:bg-cyan-900/10 ${selected?.id === n.id ? 'bg-cyan-900/20' : ''}`}
                  onClick={() => setSelected(selected?.id === n.id ? null : n)}
                >
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <SecurityIcon security={n.security} />
                      <span className="text-white">{n.ssid}</span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-gray-500">{n.bssid}</td>
                  <td className="px-4 py-2.5 text-cyan-600">{n.channel}</td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <SignalBar signal={n.signal} />
                      <span className="text-gray-500">{n.signal} dBm</span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5"><SecurityBadge security={n.security} /></td>
                  <td className="px-4 py-2.5 text-gray-500">{n.vendor}</td>
                  <td className="px-4 py-2.5 text-cyan-600">{n.clients}</td>
                  <td className="px-4 py-2.5 text-gray-500">{n.frequency}</td>
                  <td className="px-4 py-2.5">
                    {(n.security === 'OPEN' || n.security === 'WEP') && (
                      <AlertTriangle size={12} className="text-orange-400" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected network detail */}
      {selected && (
        <div className="bg-[#0d1117] rounded-lg p-4 border border-cyan-700/50 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
          <div className="flex items-center gap-2 mb-4">
            <Signal size={16} className="text-cyan-400" />
            <h2 className="text-xs font-mono text-cyan-400 tracking-widest uppercase">Network Detail — {selected.ssid}</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
            {[
              ['SSID', selected.ssid], ['BSSID', selected.bssid],
              ['Channel', String(selected.channel)], ['Frequency', selected.frequency],
              ['Signal', `${selected.signal} dBm`], ['Security', selected.security],
              ['Encryption', selected.encryption], ['Vendor', selected.vendor],
              ['Active Clients', String(selected.clients)], ['First Seen', new Date(selected.firstSeen).toLocaleTimeString()],
              ['Last Seen', new Date(selected.lastSeen).toLocaleTimeString()],
              ['GPS', selected.lat ? `${selected.lat.toFixed(4)}, ${selected.lng?.toFixed(4)}` : 'N/A'],
            ].map(([k, v]) => (
              <div key={k}>
                <div className="text-gray-600">{k}</div>
                <div className="text-white mt-0.5">{v}</div>
              </div>
            ))}
          </div>
          {(selected.security === 'OPEN' || selected.security === 'WEP') && (
            <div className="mt-4 p-3 rounded bg-orange-900/20 border border-orange-800/40">
              <div className="flex items-center gap-2 text-xs text-orange-400 font-mono">
                <AlertTriangle size={14} />
                <span>Vulnerable network — {selected.security === 'OPEN' ? 'No authentication required' : 'WEP can be cracked in minutes with aircrack-ng'}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Log window */}
      <div className="bg-black/60 rounded-lg p-4 border border-gray-800/50 font-mono text-xs max-h-48 overflow-y-auto">
        {log.map((l, i) => (
          <div key={i} className={`${l.includes('[WARN]') || l.includes('[CRIT]') ? 'text-orange-400' : l.includes('[DONE]') || l.includes('[SUCC]') ? 'text-green-400' : l.includes('[FOUND]') ? 'text-cyan-400' : l.includes('[PHONE]') ? 'text-purple-400' : 'text-gray-600'} py-0.5`}>
            {l}
          </div>
        ))}
        <div className="text-green-400">▸<span className="blink">_</span></div>
      </div>
    </div>
  );
}
