const STEPS = [
  { label: 'Validating input', key: 'validate' },
  { label: 'Checking reference ranges', key: 'reference' },
  { label: 'Classifying results', key: 'classify' },
  { label: 'Routing by severity', key: 'route' },
  { label: 'Generating AI explanations', key: 'explain' },
];

export default function LoadingState({ activeStep = 4 }) {
  return (
    <div className="loading-state">
      <div className="loading-spinner"></div>
      <h3>Analyzing laboratory results...</h3>
      <ul className="loading-steps">
        {STEPS.map((step, i) => (
          <li key={step.key} className={i <= activeStep ? 'done' : i === activeStep + 1 ? 'active' : ''}>
            {i < activeStep ? '✓' : i === activeStep ? '⟳' : '○'} {step.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
