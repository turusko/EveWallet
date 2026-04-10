import { Link, Outlet } from 'react-router-dom';
const links=[['/','Dashboard'],['/buckets','Buckets'],['/assets','Assets'],['/inventory','Inventory'],['/industry','Industry'],['/contracts','Contracts'],['/sync','Sync']];
export default function Layout(){return <div className='flex min-h-screen'><aside className='w-56 p-4 border-r border-slate-800'>{links.map(([to,l])=><Link key={to} to={to} className='block py-1 text-slate-300'>{l}</Link>)}</aside><main className='flex-1 p-6'><Outlet/></main></div>}
