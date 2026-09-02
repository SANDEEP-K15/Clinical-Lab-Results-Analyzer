import { useState } from 'react';
import SeverityBadge from './SeverityBadge';
import ExplanationCard from './ExplanationCard';

export default function ResultsDisplay({ results }) {
  const [filter, setFilter] = useState('ALL');

  if (!results || results.length === 0) return null;

  const filtered = filter === 'ALL'
    ? results
    : results.filter((r) => r.severity === filter);

  return (
    <div className="results-display">
      <div className="filter-bar">
        {['ALL', 'CRITICAL', 'WARNING', 'NORMAL', 'UNKNOWN'].map((f) => (
          <button
            key={f}
            type="button"
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'ALL' ? 'All' : f.charAt(0) + f.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {filtered.map((result, i) => (
        <div key={i} className={`result-card severity-${result.severity?.toLowerCase()}`}>
          <div className="result-header">
            <h3>{result.test_name}</h3>
            <p className="result-value">{result.value} {result.unit}</p>
            <SeverityBadge severity={result.severity} />
          </div>

          <div className="reference-range">
            <h4>Reference Range</h4>
            {result.reference_range ? (
              <p>{result.reference_range.low} – {result.reference_range.high} {result.reference_range.unit}</p>
            ) : (
              <p className="unavailable">Reference range unavailable</p>
            )}
          </div>

          <p className="result-summary">{result.explanation?.summary}</p>

          <ExplanationCard explanation={result.explanation} severity={result.severity} />
        </div>
      ))}
    </div>
  );
}
