export default function SummaryCards({ summary, total }) {
  if (!summary) return null;

  return (
    <div className="summary-cards">
      <div className="summary-card total">
        <span className="summary-label">Total Tests</span>
        <span className="summary-value">{total}</span>
      </div>
      <div className="summary-card critical">
        <span className="summary-label">🔴 Critical</span>
        <span className="summary-value">{summary.critical}</span>
      </div>
      <div className="summary-card warning">
        <span className="summary-label">⚠️ Warning</span>
        <span className="summary-value">{summary.warning}</span>
      </div>
      <div className="summary-card normal">
        <span className="summary-label">✓ Normal</span>
        <span className="summary-value">{summary.normal}</span>
      </div>
      {summary.unknown > 0 && (
        <div className="summary-card unknown">
          <span className="summary-label">? Unknown</span>
          <span className="summary-value">{summary.unknown}</span>
        </div>
      )}
    </div>
  );
}
