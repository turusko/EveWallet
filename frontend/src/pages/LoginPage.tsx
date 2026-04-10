import { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet } from '../lib/api';

type LoginResponse = {
  authorization_url: string;
  state: string;
};

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const startLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiGet<LoginResponse>('/auth/login');
      window.location.href = response.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start login.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto flex min-h-screen w-full max-w-lg flex-col justify-center gap-4 p-8">
        <h1 className="text-3xl font-semibold">Login</h1>
        <p className="text-slate-300">
          Sign in with EVE SSO to connect your character data and access sync/reporting tools.
        </p>
        <button
          type="button"
          disabled={loading}
          onClick={startLogin}
          className="w-fit rounded bg-cyan-500 px-4 py-2 font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? 'Redirecting…' : 'Continue with EVE SSO'}
        </button>
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
        <Link to="/" className="text-sm text-cyan-400 hover:text-cyan-300">
          Back to landing page
        </Link>
      </main>
    </div>
  );
}
