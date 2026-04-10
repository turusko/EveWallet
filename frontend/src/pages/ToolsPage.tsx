import { Link } from 'react-router-dom';

const tools = [
  { to: '/tools/dashboard', title: 'Dashboard', description: 'High-level account and bucket summary.' },
  { to: '/tools/buckets', title: 'Buckets', description: 'Realised PnL and net estimate per bucket.' },
  { to: '/tools/assets', title: 'Assets', description: 'Character assets and current resolved locations.' },
  { to: '/tools/inventory', title: 'Inventory', description: 'Inventory lot quantities and unit costs.' },
  { to: '/tools/industry', title: 'Industry', description: 'Industry job status and output references.' },
  { to: '/tools/contracts', title: 'Contracts', description: 'Contract list and bucket attribution.' },
  { to: '/tools/sync', title: 'Sync Jobs', description: 'Background sync job history and status.' }
];

export function ToolsPage() {
  return (
    <div>
      <h1 className="mb-3 text-2xl font-semibold">Tools</h1>
      <p className="mb-6 text-slate-300">Choose a tool to inspect your current accounting and sync data.</p>
      <div className="grid gap-3 md:grid-cols-2">
        {tools.map((tool) => (
          <Link
            key={tool.to}
            to={tool.to}
            className="rounded border border-slate-700 p-4 transition hover:border-cyan-400 hover:bg-slate-900"
          >
            <h2 className="font-medium text-cyan-300">{tool.title}</h2>
            <p className="mt-1 text-sm text-slate-300">{tool.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
