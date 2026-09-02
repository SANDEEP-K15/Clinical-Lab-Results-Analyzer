const REQUIRED_COLUMNS = ['test_name', 'value', 'unit'];
const MAX_FILE_SIZE = 10 * 1024 * 1024;

export function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) {
    return { valid: false, error: 'CSV must have a header row and at least one data row.', validRows: [], invalidRows: [] };
  }

  const header = lines[0].split(',').map((h) => h.trim().toLowerCase());
  const missing = REQUIRED_COLUMNS.filter((col) => !header.includes(col));
  if (missing.length > 0) {
    return { valid: false, error: `Missing required columns: ${missing.join(', ')}`, validRows: [], invalidRows: [] };
  }

  const testIdx = header.indexOf('test_name');
  const valueIdx = header.indexOf('value');
  const unitIdx = header.indexOf('unit');

  const validRows = [];
  const invalidRows = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const cols = line.split(',').map((c) => c.trim());
    const rowNum = i + 1;
    const errors = [];

    const testName = cols[testIdx] || '';
    const valueStr = cols[valueIdx] || '';
    const unit = cols[unitIdx] || '';

    if (!testName) errors.push('Missing test name');
    if (!valueStr) errors.push('Missing value');
    else if (isNaN(parseFloat(valueStr))) errors.push('Invalid numeric value');
    if (!unit) errors.push('Missing unit');

    if (errors.length > 0) {
      invalidRows.push({ row: rowNum, testName, value: valueStr, unit, errors });
    } else {
      validRows.push({ test_name: testName, value: parseFloat(valueStr), unit });
    }
  }

  return { valid: true, validRows, invalidRows };
}

export function validateFileSize(file) {
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: 'File exceeds maximum size of 10 MB.' };
  }
  return { valid: true };
}
