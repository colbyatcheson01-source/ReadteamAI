import React from 'react';

interface CyberCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'red' | 'green' | 'purple';
  glow?: boolean;
}

const variantClasses = {
  default: 'neon-border',
  red: 'neon-border-red',
  green: 'neon-border-green',
  purple: 'neon-border-purple',
};

export default function CyberCard({ children, className = '', variant = 'default', glow }: CyberCardProps) {
  return (
    <div
      className={`bg-[#0d1117] rounded-lg p-4 ${variantClasses[variant]} ${glow ? 'glow-cyan' : ''} ${className}`}
    >
      {children}
    </div>
  );
}
