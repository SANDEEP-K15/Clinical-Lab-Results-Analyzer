import { useState } from 'react';

const EMPTY_ROW = { test_name: '', value: '', unit: '' };

export default function LabInput({ onAnalyze, loading }) {
  const [rows, setRows] = useState([{ ...EMPTY_ROW }]);

  const updateRow = (index, field, value) => {
    const updated = [...rows];
    updated[index] = { ...updated[index], [field]: value };
    setRows(updated);
  };

  const addRow = () => setRows([...rows, { ...EMPTY_ROW }]);

  const removeRow = (index) => {
    if (rows.length === 1) return;
    setRows(rows.filter((_, i) => i !== index));
  };

  const handleAnalyze = () => {
    const labs = rows
      .filter((r) => r.test_name && r.value && r.unit)
      .map((r) => ({
        test_name: r.test_name.trim(),
        value: parseFloat(r.value),
        unit: r.unit.trim(),
      }));
    if (labs.length > 0) onAnalyze(labs);
  };

  const canAnalyze = rows.some((r) => r.test_name && r.value && r.unit) && !loading;

  return (
    <div className="lab-input">
      <div className="input-header">
        <span>Test Name</span>
        <span>Value</span>
        <span>Unit</span>
        <span></span>
      </div>
      {rows.map((row, i) => (
        <div key={i} className="input-row">
          <input
            type="text"
            placeholder="e.g. Hemoglobin"
            value={row.test_name}
            onChange={(e) => updateRow(i, 'test_name', e.target.value)}
          />
          <input
            type="number"
            step="any"
            placeholder="e.g. 8.2"
            value={row.value}
            onChange={(e) => updateRow(i, 'value', e.target.value)}
          />
          <input
            type="text"
            placeholder="e.g. g/dL"
            value={row.unit}
            onChange={(e) => updateRow(i, 'unit', e.target.value)}
          />
          <button type="button" className="btn-remove" onClick={() => removeRow(i)} disabled={rows.length === 1}>
            Remove
          </button>
        </div>
      ))}
      <div className="input-actions">
        <button type="button" className="btn-secondary" onClick={addRow}>+ Add Test</button>
        <button type="button" className="btn-primary" onClick={handleAnalyze} disabled={!canAnalyze}>
          Analyze Results
        </button>
      </div>
    </div>
  );
}
