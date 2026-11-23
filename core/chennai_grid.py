# Verified facility labels; coordinates are approximate map display points, not survey coordinates.
def build_grid():
    nodes=[
      {'id':'BASIN','name':'Basin Bridge Gas Turbine Power Station','type':'verified_facility','lat':13.1017,'lon':80.2705,'note':'Chennai; facility listing: TNPGCL'},
      {'id':'NCTPS1','name':'North Chennai TPS I','type':'verified_facility','lat':13.2938,'lon':80.3197,'note':'Athipattu, Thiruvallur district; TNPGCL'},
      {'id':'NCTPS2','name':'North Chennai TPS II','type':'verified_facility','lat':13.2900,'lon':80.3218,'note':'Athipattu, Thiruvallur district; TNPGCL'},
      {'id':'SUB_N','name':'Illustrative North distribution node','type':'illustrative_node','lat':13.185,'lon':80.285,'note':'Illustrative only; not a verified named substation'},
      {'id':'SUB_C','name':'Illustrative Central distribution node','type':'illustrative_node','lat':13.075,'lon':80.245,'note':'Illustrative only; not a verified named substation'},
      {'id':'SUB_S','name':'Illustrative South distribution node','type':'illustrative_node','lat':12.985,'lon':80.220,'note':'Illustrative only; not a verified named substation'},
      {'id':'HOSPITAL','name':'Example hospital demand node','type':'simulated_demand','lat':13.060,'lon':80.250,'note':'Fictional demonstration demand node'},
      {'id':'HOME','name':'Example residential demand node','type':'simulated_demand','lat':13.115,'lon':80.235,'note':'Fictional demonstration demand node'},
      {'id':'COMM','name':'Example commercial demand node','type':'simulated_demand','lat':13.045,'lon':80.270,'note':'Fictional demonstration demand node'},
      {'id':'IND','name':'Example industrial demand node','type':'simulated_demand','lat':13.205,'lon':80.305,'note':'Fictional demonstration demand node'}]
    pairs=[('NCTPS1','SUB_N',12,2,1),('NCTPS2','SUB_N',10,1,2),('BASIN','SUB_N',8,3,1),('SUB_N','SUB_C',9,2,1),('BASIN','SUB_C',7,1,2),('SUB_C','SUB_S',8,2,1),('SUB_C','HOSPITAL',3,1,0),('SUB_C','COMM',2,2,1),('SUB_S','HOME',3,1,0),('SUB_N','IND',4,2,2),('SUB_S','HOSPITAL',7,1,1),('SUB_N','HOME',6,1,1)]
    edges=[]
    for i,(a,b,d,c,r) in enumerate(pairs):
        edges.append({'id':f'L{i+1}','from':a,'to':b,'distance_cost':d,'congestion_penalty':c,'risk_penalty':r,'capacity_kw':100+(i%3)*50,'available':i!=9,'simulated':True})
    return nodes,edges
