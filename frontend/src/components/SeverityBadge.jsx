const SEVERITY_CONFIG = {
  CRITICAL: { label: 'CRITICAL', icon: '🔴', className: 'badge-critical' },
  WARNING: { label: 'WARNING', icon: '⚠️', className: 'badge-warning' },
  NORMAL: { label: 'NORMAL', icon: '✓', className: 'badge-normal' },
  UNKNOWN: { label: 'UNKNOWN', icon: '?', className: 'badge-unknown' },
};

export default function SeverityBadge({ severity }) {
  const config = SEVERITY_CONFIG[severity?.toUpperCase()] || SEVERITY_CONFIG.UNKNOWN;
  return (
    <span className={`severity-badge ${config.className}`}>
      {config.icon} {config.label}
    </span>
  );
}
