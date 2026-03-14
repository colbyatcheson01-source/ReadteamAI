import React from 'react';

interface RevealStats {
  value: string | number;
  label: string;
  icon?: React.ReactNode;
}

interface CyberCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'red' | 'green' | 'purple';
  glow?: boolean;
  onClick?: () => void;
  // Reveal options
  revealable?: boolean;
  revealContent?: React.ReactNode;
  revealStats?: RevealStats[];
  revealDescription?: string;
  // Reveal mode
  revealMode?: 'slide' | 'expand' | 'glass' | 'matrix';
  // Animation options
  enableParticles?: boolean;
  enableScan?: boolean;
  enableProgress?: boolean;
  // Icon that rotates on hover
  rotateIcon?: React.ReactNode;
}

const variantClasses = {
  default: 'neon-border',
  red: 'neon-border-red',
  green: 'neon-border-green',
  purple: 'neon-border-purple',
};

const variantColors = {
  default: '#06b6d4',
  red: '#ef4444',
  green: '#10b981',
  purple: '#8b5cf6',
};

export default function CyberCard({
  children,
  className = '',
  variant = 'default',
  glow,
  revealable = false,
  revealContent,
  revealStats,
  revealDescription,
  revealMode = 'slide',
  enableParticles = false,
  enableScan = false,
  enableProgress = false,
  rotateIcon,
}: CyberCardProps) {
  const color = variantColors[variant];
  
  // Build reveal class names
  const getRevealClasses = () => {
    const classes = ['reveal-card'];
    
    if (revealable) {
      classes.push('reveal-content');
    }
    
    if (revealMode === 'glass') {
      classes.push('reveal-glass');
    }
    
    if (enableParticles) {
      classes.push('reveal-particles');
    }
    
    if (enableScan) {
      classes.push('reveal-scan');
    }
    
    if (enableProgress) {
      classes.push('reveal-progress');
    }
    
    return classes.join(' ');
  };

  // Render stats if provided
  const renderStats = () => {
    if (!revealStats || revealStats.length === 0) return null;
    
    return (
      <div className="reveal-stats">
        {revealStats.map((stat, index) => (
          <div 
            key={index} 
            className="reveal-stat"
            style={{ 
              borderColor: `${color}33`,
              background: `${color}15` 
            }}
          >
            {stat.icon && (
              <span className="reveal-icon" style={{ color }}>
                {stat.icon}
              </span>
            )}
            <span 
              className="reveal-stat-value" 
              style={{ color }}
            >
              {stat.value}
            </span>
            <span className="reveal-stat-label">{stat.label}</span>
          </div>
        ))}
      </div>
    );
  };

  // Render particles if enabled
  const renderParticles = () => {
    if (!enableParticles) return null;
    
    return (
      <div className="re">
        <span className="particle" style={{ background: color }}></span>
        <span className="particle" style={{ background: color }}></span>
        <span className="particle" style={{ background: color }}></span>
        <span className="particle" style={{ background: color }}></span>
        <span className="particle" style={{ background: color }}></span>
      </div>
    );
  };

  // Main container classes
  const containerClasses = [
    'bg-[#0d1117] rounded-lg p-4',
    variantClasses[variant],
    glow ? 'glow-cyan' : '',
    className,
  ].filter(Boolean).join(' ');

  // If not revealable, return simple card
  if (!revealable) {
    return (
      <div className={containerClasses}>
        {rotateIcon && <span className="reveal-icon">{rotateIcon}</span>}
        {children}
      </div>
    );
  }

  // Render revealable card
  return (
    <div className={`${containerClasses} ${getRevealClasses()}`} style={{ '--cyber-cyan': color } as React.CSSProperties}>
      {/* Floating particles */}
      {renderParticles()}
      
      {/* Main content */}
      <div className="relative z-10">
        {rotateIcon && (
          <span className="reveal-icon mb-2 inline-block" style={{ color }}>
            {rotateIcon}
          </span>
        )}
        {children}
      </div>
      
      {/* Reveal overlay */}
      {revealMode === 'expand' ? (
        <div className="reveal-expand">
          <div className="pt-4" style={{ borderTop: `1px solid ${color}33` }}>
            {revealContent}
            {revealDescription && (
              <p className="text-gray-400 text-sm mt-2 reveal-slide reveal-delay-2">
                {revealDescription}
              </p>
            )}
            {renderStats()}
          </div>
        </div>
      ) : (
        <div className="reveal-content" style={{
          background: revealMode === 'glass' 
            ? `rgba(13, 17, 23, 0.9)`
            : `linear-gradient(to top, rgba(13, 17, 23, 0.98) 0%, rgba(13, 17, 23, 0.9) 40%, rgba(13, 17, 23, 0.4) 70%, transparent 100%)`
        }}>
          {revealContent && (
            <div className="reveal-slide reveal-delay-1">
              {revealContent}
            </div>
          )}
          {revealDescription && (
            <p className="text-gray-400 text-sm mt-2 reveal-slide reveal-delay-2">
              {revealDescription}
            </p>
          )}
          {renderStats()}
        </div>
      )}
    </div>
  );
}

// Convenience component for common card patterns
interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'red' | 'green' | 'purple';
  stats?: RevealStats[];
  description?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
  stats,
  description,
  className = '',
}: StatCardProps) {
  return (
    <CyberCard
      variant={variant}
      revealable={!!(stats || description)}
      revealStats={stats}
      revealDescription={description}
      revealMode="glass"
      enableParticles
      rotateIcon={icon}
      className={className}
    >
      <div className="flex flex-col">
        <span className="text-gray-500 text-xs uppercase tracking-wider">{title}</span>
        <span className="text-2xl font-bold text-white mt-1">{value}</span>
        {subtitle && (
          <span className="text-gray-600 text-sm mt-1">{subtitle}</span>
        )}
      </div>
    </CyberCard>
  );
}

// Info card with expandable details
interface InfoCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  details?: string;
  stats?: RevealStats[];
  variant?: 'default' | 'red' | 'green' | 'purple';
  className?: string;
}

export function InfoCard({
  title,
  description,
  icon,
  details,
  stats,
  variant = 'default',
  className = '',
}: InfoCardProps) {
  return (
    <CyberCard
      variant={variant}
      revealable={!!(details || stats)}
      revealContent={details && <span className="text-cyan-400 text-sm font-mono">{details}</span>}
      revealStats={stats}
      revealDescription={details}
      revealMode="slide"
      enableParticles
      enableProgress
      rotateIcon={icon}
      className={className}
    >
      <div>
        <h3 className="text-lg font-bold text-white">{title}</h3>
        <p className="text-gray-500 text-sm mt-1">{description}</p>
      </div>
    </CyberCard>
  );
}

// Selection card for lists
interface SelectionCardProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  selected?: boolean;
  onClick?: () => void;
  variant?: 'default' | 'red' | 'green' | 'purple';
  className?: string;
}

export function SelectionCard({
  title,
  subtitle,
  icon,
  selected = false,
  onClick,
  variant = 'default',
  className = '',
}: SelectionCardProps) {
  return (
    <CyberCard
      variant={variant}
      className={`cursor-pointer transition-all ${selected ? 'ring-2 ring-cyan-400' : ''} ${className}`}
      onClick={onClick}
      enableScan={selected}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <span className={`reveal-icon ${selected ? 'text-cyan-400' : 'text-gray-500'}`}>
            {icon}
          </span>
        )}
        <div>
          <h3 className={`font-bold ${selected ? 'text-cyan-400' : 'text-white'}`}>{title}</h3>
          {subtitle && <p className="text-gray-500 text-sm">{subtitle}</p>}
        </div>
      </div>
    </CyberCard>
  );
}
