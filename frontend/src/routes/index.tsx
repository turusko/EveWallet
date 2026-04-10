import { createBrowserRouter } from 'react-router-dom';
import Layout from '../app/Layout';
import { SimpleTablePage } from '../pages/SimpleTablePage';

export const router = createBrowserRouter([
  {path:'/', element:<Layout/>, children:[
    {index:true, element:<SimpleTablePage title='Dashboard' path='/reports/dashboard' columns={['linked_characters','active_buckets']}/>},
    {path:'buckets', element:<SimpleTablePage title='Buckets' path='/reports/buckets' columns={['bucket_id','realised_pnl','net_estimate']}/>},
    {path:'assets', element:<SimpleTablePage title='Assets' path='/assets' columns={['asset_id','type_id','quantity','location_name','bucket_fk','last_seen_at']}/>},
    {path:'inventory', element:<SimpleTablePage title='Inventory lots' path='/inventory/lots' columns={['type_id','quantity_total','quantity_remaining','unit_cost','location_name']}/>},
    {path:'industry', element:<SimpleTablePage title='Industry jobs' path='/industry/jobs' columns={['eve_job_id','status','product_type_name','runs','cost','bucket_fk']}/>},
    {path:'contracts', element:<SimpleTablePage title='Contracts' path='/contracts' columns={['contract_id','type','status','price','reward','bucket_fk']}/>},
    {path:'sync', element:<SimpleTablePage title='Sync jobs' path='/sync/jobs' columns={['job_type','status','started_at','finished_at']}/>}
  ]}
]);
