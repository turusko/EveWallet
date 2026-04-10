import { Link, Outlet } from 'react-router-dom';
const links = [
  ['/tools', 'Tools Home'],
  ['/tools/dashboard', 'Dashboard'],
  ['/tools/buckets', 'Buckets'],
  ['/tools/assets', 'Assets'],
  ['/tools/inventory', 'Inventory'],
  ['/tools/industry', 'Industry'],
  ['/tools/contracts', 'Contracts'],
  ['/tools/sync', 'Sync']
];
export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="w-56 border-r border-slate-800 p-4">
        {links.map(([to, l]) => (
          <Link key={to} to={to} className="block py-1 text-slate-300">
            {l}
          </Link>
        ))}
        <Link to="/" className="mt-3 block border-t border-slate-800 pt-3 text-slate-400">
          ← Landing
        </Link>
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
