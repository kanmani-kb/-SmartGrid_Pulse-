class LogicEngine:
    def __init__(self):
        self.facts={
          'overloaded(line_1)','maintenance(line_2)','high_congestion(line_3)','hospital_needs(hospital_1)',
          'supply_shortage(zone_south)','inactive(substation_4)','capacity_exceeded(line_5)','unsafe(line_6)',
          'safe(line_7)','alternative_exists(route_b)','route_uses(route_a,line_6)','route_uses(route_b,line_7)',
          'connected(line_1,substation_1)','connected(line_2,substation_2)','connected(line_3,substation_3)',
          'active(substation_1)','active(substation_2)','active(substation_3)','priority(hospital_1,high)',
          'demand(zone_south,high)','generation(zone_south,low)','available(line_7)','available(line_8)','no_safe_route(route_c)','grid_emergency','reserve_margin_low','critical_load_active','storm_watch','manual_override_off'}
        self.rules=[
          ('R1','overloaded(X) -> unsafe(X)'),('R2','maintenance(X) -> unavailable(X)'),
          ('R3','high_congestion(X) -> congestion_penalty(X)'),('R4','hospital_needs(X) -> priority_high(X)'),
          ('R5','supply_shortage(X) -> shortage_warning(X)'),('R6','route_uses(R,L) & unsafe(L) -> reject_route(R)'),
          ('R7','inactive(X) -> avoid_substation(X)'),('R8','capacity_exceeded(X) -> overload_warning(X)'),
          ('R9','alternative_exists(R) & safe_route(R) -> prefer_route(R)'),('R10','no_safe_route(X) -> safety_warning(X)')]
        self.derived=set(); self.triggered=[]
    def unify(self,pattern,ground):
        p=pattern.strip().rstrip('.'); g=ground.strip().rstrip('.')
        if '(' not in p or '(' not in g: return {} if p==g else None
        pn,pa=p.split('(',1); gn,ga=g.split('(',1)
        if pn!=gn or pa.rstrip(')') .count(',')!=ga.rstrip(')').count(','): return None
        out={}
        for x,y in zip(pa.rstrip(')').split(','),ga.rstrip(')').split(',')):
            x=x.strip(); y=y.strip()
            if x[:1].isupper():
                if x in out and out[x]!=y: return None
                out[x]=y
            elif x!=y: return None
        return out
    def forward(self):
        changed=True
        while changed:
            changed=False
            all_facts=self.facts|self.derived
            # Single-premise rules R1-R5, R7 and R8.
            for src,dst,rid in [('overloaded','unsafe','R1'),('maintenance','unavailable','R2'),('high_congestion','congestion_penalty','R3'),('hospital_needs','priority_high','R4'),('supply_shortage','shortage_warning','R5'),('inactive','avoid_substation','R7'),('capacity_exceeded','overload_warning','R8'),('no_safe_route','safety_warning','R10')]:
                for f in list(all_facts):
                    if f.startswith(src+'('):
                        target=dst+f[len(src):]
                        if target not in self.derived: self.derived.add(target); self.triggered.append(rid); changed=True
            all_facts=self.facts|self.derived
            # R6: a route using an unsafe line is rejected.
            for f in list(all_facts):
                if f.startswith('route_uses('):
                    route,line=f[len('route_uses('):-1].split(',')
                    if f'unsafe({line})' in all_facts and f'reject_route({route})' not in self.derived:
                        self.derived.add(f'reject_route({route})'); self.triggered.append('R6'); changed=True
                    if f'safe({line})' in all_facts and f'safe_route({route})' not in self.derived:
                        self.derived.add(f'safe_route({route})'); changed=True
            # R9: prefer a safe alternative route.
            for f in list(all_facts):
                if f.startswith('alternative_exists('):
                    route=f[len('alternative_exists('):-1]
                    if f'safe_route({route})' in all_facts and f'prefer_route({route})' not in self.derived:
                        self.derived.add(f'prefer_route({route})'); self.triggered.append('R9'); changed=True
        return sorted(self.derived)
    def backward(self,query,depth=0):
        if query in self.facts or query in self.derived: return {'query':query,'proved':True,'method':'fact lookup / derived fact','rules':[]}
        mapping={'unsafe':'R1','unavailable':'R2','congestion_penalty':'R3','priority_high':'R4','shortage_warning':'R5','overload_warning':'R8'}
        pred=query.split('(',1)[0]
        src={'unsafe':'overloaded','unavailable':'maintenance','congestion_penalty':'high_congestion','priority_high':'hospital_needs','shortage_warning':'supply_shortage','overload_warning':'capacity_exceeded'}.get(pred)
        if src:
            source=src+query[query.find('('):]
            if source in self.facts: return {'query':query,'proved':True,'method':'backward rule '+mapping[pred],'rules':[mapping[pred]],'supporting_fact':source}
        return {'query':query,'proved':False,'method':'no matching fact or rule could prove this query','rules':[]}
    def dashboard(self):
        derived=self.forward(); tests=[('overloaded line becomes unsafe','unsafe(line_1)'),('maintenance line unavailable','unavailable(line_2)'),('congestion penalty inferred','congestion_penalty(line_3)'),('hospital priority inferred','priority_high(hospital_1)'),('shortage warning inferred','shortage_warning(zone_south)'),('capacity warning inferred','overload_warning(line_5)'),('safe alternative fact exists','safe(line_7)'),('inactive substation known','inactive(substation_4)'),('route A uses unsafe line','route_uses(route_a,line_6)'),('route B uses safe line','route_uses(route_b,line_7)'),('unsafe route rejected','reject_route(route_a)'),('inactive substation avoided','avoid_substation(substation_4)'),('safe alternative preferred','prefer_route(route_b)'),('no-safe-route warning','safety_warning(route_c)')]
        results=[]
        for label,q in tests:
            if q in self.facts or q in self.derived: ok=True
            else: ok=self.backward(q)['proved']
            results.append({'scenario':label,'passed':ok,'query':q})
        contradictions=[]
        for positive,negative in [('active','inactive'),('safe','unsafe'),('available','unavailable')]:
            for fact in self.facts|self.derived:
                if fact.startswith(positive+'('):
                    opposite=negative+fact[len(positive):]
                    if opposite in self.facts|self.derived: contradictions.append((fact,opposite))
        return {'facts':sorted(self.facts),'derived':derived,'rules':[{'id':x,'text':y} for x,y in self.rules],'triggered_rules':sorted(set(self.triggered)),'tests':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),'rule_coverage':round(len(set(self.triggered))/len(self.rules)*100,1),'consistency':('No contradictory positive/negative fact pairs found in this compact rule base.' if not contradictions else f'Contradictions detected: {contradictions}'),'note':'Forward chaining derives supported consequences from facts. Backward chaining checks whether a selected query can be proved.'}
    def query(self,q):
        self.forward(); res=self.backward(q)
        if q.startswith('unsafe(') and res['proved']: decision='Reject routes using this connection.'
        elif res['proved']: decision='The query is supported by the current facts and rules.'
        else: decision='Not proven. Do not treat this as a safe/true condition.'
        return {'forward_chaining':sorted(self.derived),'backward_chaining':res,'safety_decision':decision,'facts_used':sorted(self.facts)}
