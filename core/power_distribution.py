def distribute_power(supply,areas=None):
    areas=areas or [{'name':'Hospital','demand':180,'priority':1,'capacity':160,'critical':True},{'name':'Residential','demand':260,'priority':3,'capacity':240},{'name':'Commercial','demand':170,'priority':4,'capacity':150},{'name':'Industrial','demand':220,'priority':5,'capacity':200}]
    remaining=max(0,float(supply)); rows=[]
    # Critical-first, then priority-ordered; noncritical remainder shares supply proportionally to unmet demand.
    critical=sorted([a for a in areas if a.get('critical',False)],key=lambda a:a.get('priority',9))
    others=sorted([a for a in areas if not a.get('critical',False)],key=lambda a:a.get('priority',9))
    allocs={}
    for a in critical:
        v=min(float(a['demand']),float(a.get('capacity',a['demand'])),remaining) if a.get('available',True) else 0.0; allocs[a['name']]=v; remaining-=v
    eligible=[a for a in others if a.get('available',True)]; caps={a['name']:min(float(a['demand']),float(a.get('capacity',a['demand']))) for a in eligible}
    while remaining>1e-9 and any(caps.values()):
        total=sum(caps.values()); used=0
        for a in eligible:
            k=a['name']; share=min(caps[k],remaining*caps[k]/total if total else 0); allocs[k]=allocs.get(k,0)+share; caps[k]-=share; used+=share
        remaining-=used
        if used<1e-9: break
    for a in areas:
        req=max(0,float(a['demand'])); al=allocs.get(a['name'],0) if a.get('available',True) else 0; cap=float(a.get('capacity',req))
        rows.append({'name':a['name'],'demand_kw':req,'allocated_kw':round(al,2),'shortage_kw':round(max(0,req-al),2),'capacity_kw':cap,'priority':a.get('priority',5),'critical':bool(a.get('critical',False)),'available':bool(a.get('available',True)),'safe':al<=cap+1e-9,'overload_risk':req>cap,'connection_status':'Demand exceeds simulated capacity' if req>cap else 'Within simulated capacity'})
    return {'supply_kw':supply,'total_demand_kw':round(sum(x['demand_kw'] for x in rows),2),'allocated_kw':round(sum(x['allocated_kw'] for x in rows),2),'areas':rows,'shortage_kw':round(sum(x['shortage_kw'] for x in rows),2),'safe':sum(x['allocated_kw'] for x in rows)<=supply+1e-7 and all(x['safe'] for x in rows),'policy':'Critical services first; remaining available supply is shared proportionally among other eligible areas, bounded by each demand and simulated capacity.'}
