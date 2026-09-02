import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export async function analyzeLabs(labs) {
  const response = await api.post('/analyze_labs', { labs });
  return response.data;
}

export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}
