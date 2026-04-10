const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export async function apiGet<T>(path: string): Promise<T> { const r = await fetch(`${API}${path}`); if(!r.ok) throw new Error(await r.text()); return r.json(); }
