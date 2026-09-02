import { useState } from 'react';
import LabInput from './components/LabInput';
import CsvUpload from './components/CsvUpload';
import ResultsDisplay from './components/ResultsDisplay';
import SummaryCards from './components/SummaryCards';
import LoadingState from './components/LoadingState';
import { analyzeLabs } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('manual');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisData, setAnalysisData] = useState(null);

  const handleAnalyze = async (labs) => {
    setLoading(true);
    setError('');
    setAnalysisData(null);
    try {
      const data = await analyzeLabs(labs);
      setAnalysisData(data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Unable to analyze the laboratory results. Please check the backend connection and try again.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Clinical Lab AI Analyzer</h1>
        <p className="subtitle">Explainable AI for Laboratory Results</p>
        <p className="ref-disclaimer">
          Reference ranges shown are demo configuration values. Actual ranges may vary by laboratory, age, sex, methodology, and clinical context.
        </p>
      </header>

      <main className="app-main">
        <div className="tabs">
          <button
            type="button"
            className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
            onClick={() => setActiveTab('manual')}
          >
            Manual Input
          </button>
          <button
            type="button"
            className={`tab ${activeTab === 'csv' ? 'active' : ''}`}
            onClick={() => setActiveTab('csv')}
          >
            CSV Upload
          </button>
        </div>

        <div className="input-panel">
          {activeTab === 'manual' ? (
            <LabInput onAnalyze={handleAnalyze} loading={loading} />
          ) : (
            <CsvUpload onAnalyze={handleAnalyze} loading={loading} />
          )}
        </div>

        {loading && <LoadingState />}

        {error && <div className="error-banner">{error}</div>}

        {!loading && !analysisData && !error && (
          <div className="empty-state">
            <p>No laboratory results yet.</p>
            <p>Enter results manually or upload a CSV file to begin.</p>
          </div>
        )}

        {analysisData && !loading && (
          <div className="results-panel">
            <SummaryCards summary={analysisData.summary} total={analysisData.total_results} />
            <ResultsDisplay results={analysisData.results} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>This is an educational/demo clinical decision-support application. It does not diagnose patients or replace professional medical advice.</p>
      </footer>
    </div>
  );
}
