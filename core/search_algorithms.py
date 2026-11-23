import heapq, time, tracemalloc, math, random
from .chennai_grid import build_grid

def graph_data(congestion=0,risk=0):
    nodes,edges=build_grid(); graph={n['id']:[] for n in nodes}; coords={n['id']:(n['lat'],n['lon']) for n in nodes}
    for e in edges:
        if not e['available']: continue
        cost=e['distance_cost']+e['congestion_penalty']+e['risk_penalty']+float(congestion)*0.15+float(risk)*0.15
        for a,b in [(e['from'],e['to']),(e['to'],e['from'])]: graph[a].append((b,cost,e))
    ratios=[]
    for e in edges:
        a,b=coords[e['from']],coords[e['to']]
        km=haversine(a,b)
        if km>0: ratios.append(e['distance_cost']/km)
    heuristic_scale=min(ratios) if ratios else 0.0
    return graph,coords,heuristic_scale

def haversine(a,b):
    lat1,lon1=a; lat2,lon2=b; r=6371
    p1,p2=math.radians(lat1),math.radians(lat2); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))

def run_search(graph,coords,start,goal,method,heuristic_scale=0.0):
    t0=time.perf_counter(); tracemalloc.start(); frontier=[(0,0,start)]; came={}; costs={start:0}; expanded=0; reached=False
    while frontier:
        _,g_at_push,u=heapq.heappop(frontier)
        if g_at_push != costs.get(u): continue
        if u==goal: reached=True; break
        expanded+=1
        for v,w,_ in graph.get(u,[]):
            nc=costs[u]+w
            if nc<costs.get(v,float('inf')):
                costs[v]=nc; came[v]=u
                if method=='astar': priority=nc+haversine(coords[v],coords[goal])*heuristic_scale
                elif method=='greedy': priority=haversine(coords[v],coords[goal])
                else: priority=nc
                heapq.heappush(frontier,(priority,nc,v))
    path=[]
    if reached:
        cur=goal; path=[cur]
        while cur!=start: cur=came[cur]; path.append(cur)
        path.reverse()
    current,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    return {'algorithm':method.upper(),'path':path,'path_cost':round(costs.get(goal,0),3) if reached else None,'execution_ms':round((time.perf_counter()-t0)*1000,4),'expanded_nodes':expanded,'memory_peak_kb':round(peak/1024,2),'reached':reached}

def compare_searches(source='BASIN',target='HOSPITAL',congestion=0,risk=0):
    graph,coords,heuristic_scale=graph_data(congestion,risk); out=[]
    for m in ['astar','greedy','ucs']:
        x=run_search(graph,coords,source,target,m,heuristic_scale); x['edges']=[]
        for a,b in zip(x['path'],x['path'][1:]):
            e=next(e for _,_,e in graph[a] if _==b) if False else next(item[2] for item in graph[a] if item[0]==b)
            x['edges'].append({'from':a,'to':b,'distance_cost':e['distance_cost'],'congestion_penalty':round(e['congestion_penalty']+float(congestion)*0.15,3),'risk_penalty':round(e['risk_penalty']+float(risk)*0.15,3),'total_cost':round(e['distance_cost']+e['congestion_penalty']+e['risk_penalty']+(float(congestion)+float(risk))*0.15,3)})
        out.append(x)
    viable=[x for x in out if x['reached']]
    best=min(viable,key=lambda x:(x['path_cost'],x['execution_ms'])) if viable else None
    return {'source':source,'target':target,'results':out,'best_algorithm':best['algorithm'] if best else None,'best_reason':'Lowest path cost; execution time breaks ties for this measured run.' if best else 'No route reached the destination.','heuristic_note':f'A* uses {heuristic_scale:.4f} × straight-line kilometres, where the scale is the minimum distance-cost-per-kilometre ratio among simulated links. By the triangle inequality this lower bound is admissible for this graph.'}

def search_experiments():
    # Reproducible grid workloads; measurements are taken from actual runs.
    rows=[]; random.seed(7)
    for size in [4,8,14,20]:
        g={f'n{i}':[] for i in range(size*size)}; coords={f'n{i}':(i//size*0.001,i%size*0.001) for i in range(size*size)}
        for r in range(size):
            for c in range(size):
                u=f'n{r*size+c}'
                for rr,cc in [(r+1,c),(r,c+1)]:
                    if rr<size and cc<size:
                        v=f'n{rr*size+cc}'; w=1+((r*7+c*3)%5)*0.1; g[u].append((v,w,{})); g[v].append((u,w,{}))
        ratios=[w/haversine(coords[u],coords[v]) for u,adj in g.items() for v,w,_ in adj if haversine(coords[u],coords[v])>0]
        scale=min(ratios) if ratios else 0.0
        for m in ['astar','greedy','ucs']:
            z=run_search(g,coords,'n0',f'n{size*size-1}',m,scale); rows.append({'size':f'{size}x{size}','nodes':size*size,**z})
    best_by_size=[]
    for size in ['4x4','8x8','14x14','20x20']:
        group=[r for r in rows if r['size']==size and r['reached']]
        best=min(group,key=lambda r:(r['path_cost'],r['execution_ms'])) if group else None
        best_by_size.append({'size':size,'best_algorithm':best['algorithm'] if best else 'No route','path_cost':best['path_cost'] if best else None,'execution_ms':best['execution_ms'] if best else None})
    return {'rows':rows,'best_by_size':best_by_size,'note':'Timings and peak traced Python allocations are measured locally; repeat runs may vary by machine.'}
