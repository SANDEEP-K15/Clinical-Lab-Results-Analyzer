import { useState } from 'react';
import { parseCSV, validateFileSize } from '../utils/csvParser';

export default function CsvUpload({ onAnalyze, loading }) {
  const [fileName, setFileName] = useState('');
  const [validRows, setValidRows] = useState([]);
  const [invalidRows, setInvalidRows] = useState([]);
  const [error, setError] = useState('');

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const sizeCheck = validateFileSize(file);
    if (!sizeCheck.valid) {
      setError(sizeCheck.error);
      return;
    }

    const reader = new FileReader();
    reader.onload = (ev) => {
      const result = parseCSV(ev.target.result);
      if (!result.valid) {
        setError(result.error);
        setValidRows([]);
        setInvalidRows([]);
        setFileName('');
        return;
      }
      setError('');
      setFileName(file.name);
      setValidRows(result.validRows);
      setInvalidRows(result.invalidRows);
    };
    reader.readAsText(file);
  };

  const handleAnalyze = () => {
    if (validRows.length > 0) onAnalyze(validRows);
  };

  return (
    <div className="csv-upload">
      <input type="file" accept=".csv" onChange={handleFile} className="file-input" />

      {error && <div className="error-message">{error}</div>}

      {fileName && (
        <div className="csv-preview">
          <p className="csv-file-info">File: <strong>{fileName}</strong></p>
          <p className="csv-count">{validRows.length} laboratory result{validRows.length !== 1 ? 's' : ''} detected</p>
          <div className="csv-divider">{'─'.repeat(48)}</div>

          {validRows.length > 0 && (
            <table className="csv-table">
              <thead>
                <tr><th>Test Name</th><th>Value</th><th>Unit</th></tr>
              </thead>
              <tbody>
                {validRows.map((row, i) => (
                  <tr key={i}>
                    <td>{row.test_name}</td>
                    <td>{row.value}</td>
                    <td>{row.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {invalidRows.length > 0 && (
            <div className="invalid-rows">
              {invalidRows.map((row) => (
                <div key={row.row} className="invalid-row">
                  <strong>Row {row.row}:</strong> {row.errors.join(', ')}
                </div>
              ))}
            </div>
          )}

          <div className="csv-divider">{'─'.repeat(48)}</div>
          <button
            type="button"
            className="btn-primary"
            onClick={handleAnalyze}
            disabled={validRows.length === 0 || loading}
          >
            Analyze CSV
          </button>
        </div>
      )}
    </div>
  );
}
