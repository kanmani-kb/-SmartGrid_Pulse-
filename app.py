from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from pathlib import Path
import pandas as pd, io
from core.chennai_grid import build_grid
from core.search_algorithms import compare_searches, search_experiments
from core.csp_allocator import allocate_power
from core.logic_engine import LogicEngine
from core.demand_models import train_compare
from core.power_distribution import distribute_power
from core.experiments import scalability_benchmark
from core.report_generator import create_report
from core.data_validation import validate_energy_csv

BASE=Path(__file__).resolve().parent
app=Flask(__name__); app.secret_key='smartgrid-pulse-local-demo-key'
DATA_PATH=BASE/'sample_data'/'chennai_energy_sample.csv'
active_df=pd.read_csv(DATA_PATH, parse_dates=['timestamp'])
active_name='Built-in Chennai-style sample dataset'
last_run={}

def serial_df(df):
    d=df.copy(); d['timestamp']=pd.to_datetime(d['timestamp']).astype(str); return d.to_dict(orient='records')

@app.route('/')
def home(): return redirect(url_for('module1'))
@app.route('/module1')
def module1():
    nodes,edges=build_grid(); return render_template('module1_search.html',nodes=nodes,edges=edges)
@app.route('/module2')
def module2(): return render_template('module2_logic.html')
@app.route('/module3')
def module3():
    return render_template('module3_ml.html',dataset_name=active_name,preview=serial_df(active_df.head(8)),rows=len(active_df))

@app.get('/api/grid')
def api_grid():
    n,e=build_grid(); return jsonify(nodes=n,edges=e)
@app.post('/api/search')
def api_search():
    body=request.get_json(force=True); result=compare_searches(body.get('source','BASIN'),body.get('target','HOSPITAL'),body.get('congestion',0),body.get('risk',0))
    global last_run; last_run['search']=result; return jsonify(result)
@app.get('/api/search-experiments')
def api_search_experiments():
    result=search_experiments(); last_run['search_experiments']=result; return jsonify(result)
@app.post('/api/csp')
def api_csp():
    b=request.get_json(force=True); result=allocate_power(float(b.get('supply',500)),b.get('demands',None)); last_run['csp']=result; return jsonify(result)
@app.get('/api/logic')
def api_logic():
    engine=LogicEngine(); result=engine.dashboard(); last_run['logic']=result; return jsonify(result)
@app.post('/api/logic/query')
def api_logic_query():
    b=request.get_json(force=True); engine=LogicEngine(); result=engine.query(b.get('query','unsafe(line_3)')); last_run['logic_query']=result; return jsonify(result)

@app.post('/upload')
def upload():
    global active_df, active_name
    f=request.files.get('dataset')
    if not f or not f.filename.lower().endswith('.csv'):
        flash('Please choose a CSV file. The active dataset has not been changed.','error'); return redirect(url_for('module3'))
    try:
        raw=validate_energy_csv(pd.read_csv(f))
        active_df=raw; active_name=f'Uploaded: {f.filename}'
        flash(f'CSV validated. {len(raw)} rows are now active.','success')
    except Exception as e: flash(str(e),'error')
    return redirect(url_for('module3'))

@app.get('/api/ml')
def api_ml():
    result=train_compare(active_df); result['dataset_name']=active_name; result['rows']=len(active_df)
    last_run['ml']=result; return jsonify(result)
@app.get('/api/forecast')
def api_forecast():
    from core.demand_models import forecast
    return jsonify(forecast(active_df))
@app.get('/api/scalability')
def api_scalability():
    result=scalability_benchmark(active_df); last_run['scalability']=result; return jsonify(result)
@app.post('/api/distribution')
def api_distribution():
    b=request.get_json(force=True); result=distribute_power(float(b.get('supply',600)),b.get('areas',None)); last_run['distribution']=result; return jsonify(result)
@app.get('/sample.csv')
def sample_csv(): return send_file(DATA_PATH,as_attachment=True,download_name='chennai_energy_sample.csv')
@app.get('/report.pdf')
def report():
    result=create_report(active_name,active_df,last_run)
    return send_file(io.BytesIO(result),mimetype='application/pdf',as_attachment=True,download_name='SmartGrid_Pulse_Report.pdf')
@app.get('/health')
def health(): return jsonify(status='ok',dataset=active_name,rows=len(active_df))

if __name__=='__main__': app.run(debug=True,host='127.0.0.1',port=5000)
