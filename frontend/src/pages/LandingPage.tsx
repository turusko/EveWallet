import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto flex min-h-screen max-w-4xl flex-col items-start justify-center gap-6 p-8">
        <p className="text-sm uppercase tracking-widest text-cyan-400">EveWallet</p>
        <h1 className="text-4xl font-semibold">Track profit across wallet, inventory, and industry.</h1>
        <p className="max-w-2xl text-slate-300">
          Land here first, sign in with EVE SSO, then jump into tools for dashboard, assets, contracts, and sync visibility.
        </p>
        <div className="flex gap-3">
          <Link to="/login" className="rounded bg-cyan-500 px-4 py-2 font-medium text-slate-950 hover:bg-cyan-400">
            Login
          </Link>
          <Link to="/tools" className="rounded border border-slate-600 px-4 py-2 font-medium hover:border-slate-400">
            Open Tools
          </Link>
        </div>
      </main>
    </div>
  );
}
