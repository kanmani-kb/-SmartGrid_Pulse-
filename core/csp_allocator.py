def allocate_power(supply,demands=None):
    areas=demands or [
      {'name':'Hospital','demand':180,'priority':1,'capacity':160,'available':True,'kind':'critical'},
      {'name':'Water services','demand':100,'priority':2,'capacity':90,'available':True,'kind':'critical'},
      {'name':'Residential','demand':240,'priority':3,'capacity':220,'available':True,'kind':'normal'},
      {'name':'Commercial','demand':150,'priority':4,'capacity':130,'available':True,'kind':'normal'},
      {'name':'Industrial','demand':190,'priority':5,'capacity':170,'available':True,'kind':'normal'}]
    remaining=max(0,float(supply)); result=[]
    for a in sorted(areas,key=lambda x:(x.get('priority',5),x['name'])):
        requested=max(0,float(a['demand'])); cap=max(0,float(a.get('capacity',requested)))
        eligible=bool(a.get('available',True)); alloc=min(requested,cap,remaining) if eligible else 0
        remaining-=alloc
        result.append({'name':a['name'],'requested_kw':requested,'allocated_kw':round(alloc,2),'remaining_kw':round(requested-alloc,2),'priority':a.get('priority',5),'available':eligible,'capacity_kw':cap,'satisfied':alloc>=requested,'constraint_ok':alloc<=requested and alloc<=cap})
    return {'supply_kw':float(supply),'allocated_total_kw':round(sum(x['allocated_kw'] for x in result),2),'remaining_supply_kw':round(remaining,2),'rows':result,'constraints_satisfied':sum(x['allocated_kw'] for x in result)<=supply+1e-9 and all(x['constraint_ok'] for x in result),'explanation':'Critical services are considered first, then other areas in priority order. Allocation is capped by demand, connection capacity and remaining supply; it is priority-based, not equal sharing.'}
