import { useQuery } from '@tanstack/react-query';
import { apiGet } from '../lib/api';

export function SimpleTablePage({title,path,columns}:{title:string;path:string;columns:string[]}){
  const q=useQuery({queryKey:[path],queryFn:()=>apiGet<any[]>(path)});
  if(q.isLoading) return <div>Loading...</div>;
  if(q.error) return <div>Error loading {title}</div>;
  const rows=q.data||[];
  return <div><h1 className='text-xl mb-3'>{title}</h1>{rows.length===0?<div>No data.</div>:<table className='w-full text-sm'><thead><tr>{columns.map(c=><th key={c} className='text-left'>{c}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i} className='border-t border-slate-800'>{columns.map(c=><td key={c}>{String(r[c]??'')}</td>)}</tr>)}</tbody></table>}</div>
}
