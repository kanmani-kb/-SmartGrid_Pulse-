import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from core.chennai_grid import build_grid
from core.search_algorithms import compare_searches,graph_data,run_search
from core.csp_allocator import allocate_power
from core.logic_engine import LogicEngine
from core.demand_models import train_compare
from core.power_distribution import distribute_power
from core.experiments import scalability_benchmark

def test_grid_and_search():
    nodes,edges=build_grid(); assert any(n['id']=='NCTPS1' for n in nodes)
    d=compare_searches('BASIN','HOSPITAL'); assert len(d['results'])==3
    for r in d['results']:
        assert r['reached'] and r['path'][0]=='BASIN' and r['path'][-1]=='HOSPITAL'
        assert abs(sum(e['total_cost'] for e in r['edges'])-r['path_cost'])<1e-6

def test_csp_constraints():
    r=allocate_power(100); assert r['allocated_total_kw']<=100
    assert all(x['allocated_kw']<=x['requested_kw'] and x['allocated_kw']<=x['capacity_kw'] for x in r['rows'])

def test_logic_engine():
    e=LogicEngine(); d=e.dashboard(); assert len(d['facts'])>=20 and len(d['rules'])>=10 and len(d['tests'])>=10
    assert e.unify('overloaded(X)','overloaded(line_1)')=={'X':'line_1'}
    assert e.query('unsafe(line_1)')['backward_chaining']['proved']

def test_ml_and_scale():
    df=pd.read_csv(Path(__file__).resolve().parents[1]/'sample_data/chennai_energy_sample.csv',parse_dates=['timestamp'])
    r=train_compare(df); assert len(r['metrics'])==2 and r['best_model']
    s=scalability_benchmark(df); assert [x['factor'] for x in s['rows']]==['1x','10x','100x']

def test_distribution():
    r=distribute_power(100); assert r['allocated_kw']<=100 and r['safe']

def test_csv_validation_aliases_and_errors():
    from core.data_validation import validate_energy_csv
    raw=pd.DataFrame({'datetime':pd.date_range('2026-01-01',periods=25,freq='h'),'load_kw':[10]*25,'supply_kw':[12]*25})
    clean=validate_energy_csv(raw); assert {'timestamp','demand_kw','generation_kw'}.issubset(clean.columns)
    try: validate_energy_csv(pd.DataFrame({'timestamp':['bad'],'demand_kw':[1],'generation_kw':[2]}))
    except ValueError as e: assert 'invalid values' in str(e)
    else: raise AssertionError('Invalid timestamp should be rejected')


def test_report_pdf_and_capacity_warning():
    from core.report_generator import create_report
    from core.power_distribution import distribute_power
    df=pd.read_csv(Path(__file__).resolve().parents[1]/'sample_data/chennai_energy_sample.csv',parse_dates=['timestamp'])
    report=create_report('test dataset',df,{})
    assert report[:4]==b'%PDF'
    result=distribute_power(100,[{'name':'Clinic','demand':150,'priority':1,'capacity':80,'critical':True}])
    assert result['allocated_kw']<=100 and result['areas'][0]['overload_risk']
