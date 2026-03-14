interface SeverityBadgeProps {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
}

const config = {
  CRITICAL: 'bg-red-900/50 text-red-400 border border-red-500',
  HIGH: 'bg-orange-900/50 text-orange-400 border border-orange-500',
  MEDIUM: 'bg-yellow-900/50 text-yellow-400 border border-yellow-500',
  LOW: 'bg-blue-900/50 text-blue-400 border border-blue-500',
  INFO: 'bg-gray-800/50 text-gray-400 border border-gray-600',
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  return (
    <span className={`px-2 py-0.5 text-xs font-bold rounded font-mono ${config[severity]}`}>
      {severity}
    </span>
  );
}
