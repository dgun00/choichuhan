import axios from 'axios';

const runtimeBase = typeof window !== 'undefined' && window.LOCALHUB_API_BASE;
const envBase = import.meta.env?.VITE_API_BASE_URL;
const API_BASE = (runtimeBase || envBase || 'http://127.0.0.1:8000').replace(/\/+$/,'');

console.log("API_BASE =", API_BASE);

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export default api;