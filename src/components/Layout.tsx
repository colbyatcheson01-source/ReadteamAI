import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard, Wifi, ShieldAlert, Bug, Package, FileText,
  Menu, X, Terminal, Radio, Zap
} from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { to: '/wardrive', label: 'War Drive', icon: Radio },
  { to: '/scanner', label: 'Vuln Scanner', icon: ShieldAlert },
  { to: '/exploits', label: 'Exploit Chooser', icon: Bug },
  { to: '/payload', label: 'Payload Delivery', icon: Package },
  { to: '/reports', label: 'Reports', icon: FileText },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [time, setTime] = useState(new Date());

  // Update clock
  useState(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  });

  return (
    <div className="flex h-screen bg-[#030712] cyber-grid overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-16'} flex-shrink-0 bg-[#0a0e1a] border-r border-cyan-900/50 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 p-4 border-b border-cyan-900/50">
          <div className="w-8 h-8 flex-shrink-0 relative">
            <div className="absolute inset-0 bg-cyan-500/20 rounded border border-cyan-500 flex items-center justify-center">
              <Zap size={16} className="text-cyan-400" />
            </div>
          </div>
          {sidebarOpen && (
            <div>
              <div className="text-cyan-400 font-bold text-sm tracking-widest">REDTEAM</div>
              <div className="text-cyan-600 text-xs tracking-wider">AI PLATFORM</div>
            </div>
          )}
        </div>

        {/* Nav Items */}
        <nav className="flex-1 py-4 space-y-1 px-2">
          {navItems.map(({ to, label, icon: Icon, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded text-sm transition-all duration-200 font-mono
                ${isActive
                  ? 'bg-cyan-900/30 text-cyan-400 border border-cyan-700/50 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                }`
              }
            >
              <Icon size={18} className="flex-shrink-0" />
              {sidebarOpen && <span className="tracking-wide">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Status bar */}
        {sidebarOpen && (
          <div className="p-4 border-t border-cyan-900/50 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs text-green-400 font-mono">SYSTEM ONLINE</span>
            </div>
            <div className="text-xs text-gray-600 font-mono">
              {time.toUTCString().slice(17, 25)} UTC
            </div>
            <div className="text-xs text-cyan-700 font-mono text-center border border-cyan-900/30 rounded py-1">
              AUTH: LEVEL 5 OPERATOR
            </div>
          </div>
        )}
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="flex-shrink-0 h-12 bg-[#0a0e1a] border-b border-cyan-900/50 flex items-center px-4 gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-500 hover:text-cyan-400 transition-colors"
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          <div className="flex items-center gap-2 text-xs font-mono text-gray-600">
            <Terminal size={12} />
            <span className="text-cyan-700">root@redteam-ai</span>
            <span className="text-gray-700">~</span>
          </div>

          <div className="ml-auto flex items-center gap-6 text-xs font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-green-500">VPN ACTIVE</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
              <span className="text-cyan-600">ENCRYPTED</span>
            </div>
            <div className="text-gray-600">
              {time.toLocaleDateString()} {time.toLocaleTimeString()}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
