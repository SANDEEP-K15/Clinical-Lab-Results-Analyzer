export default function ExplanationCard({ explanation, severity }) {
  if (!explanation) return null;

  const isFallback = explanation.summary?.includes('temporarily unavailable');
  const sev = severity?.toUpperCase();

  const whyHeading = {
    NORMAL: 'WHY IS THIS NORMAL?',
    WARNING: 'WHY WAS THIS FLAGGED?',
    CRITICAL: 'WHY WAS THIS FLAGGED?',
    UNKNOWN: 'WHY IS THE STATUS UNKNOWN?',
  }[sev] || 'CLASSIFICATION REASON';

  return (
    <div className="explanation-card">
      {isFallback && (
        <div className="llm-fallback-notice">
          AI explanation temporarily unavailable. The deterministic classification is still shown.
        </div>
      )}

      <div className="explanation-section">
        <h4>{whyHeading}</h4>
        <p>{explanation.why_flagged}</p>
      </div>

      <div className="explanation-section">
        <h4>WHAT DOES THIS MEAN?</h4>
        <p>{explanation.clinical_significance}</p>
      </div>

      <div className="explanation-section">
        <h4>SUGGESTED NEXT STEP</h4>
        <p>{explanation.next_step}</p>
      </div>

      <p className="ai-label">AI-generated explanation</p>
      <p className="disclaimer">{explanation.disclaimer}</p>
    </div>
  );
}
