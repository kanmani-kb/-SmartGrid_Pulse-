import numpy as np, pandas as pd, time
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def feature_frame(df):
    d=df.copy(); d['timestamp']=pd.to_datetime(d['timestamp']); d=d.sort_values('timestamp')
    d['hour']=d.timestamp.dt.hour; d['dayofweek']=d.timestamp.dt.dayofweek; d['month']=d.timestamp.dt.month; d['dayofyear']=d.timestamp.dt.dayofyear
    for c in ['temperature','renewable_kw']:
        if c not in d: d[c]=d['demand_kw'].median() if c=='temperature' else 0
        d[c]=pd.to_numeric(d[c],errors='coerce')
        fill=float(d[c].median()) if d[c].notna().any() else (25.0 if c=='temperature' else 0.0)
        d[c]=d[c].fillna(fill)
    return d, ['hour','dayofweek','month','dayofyear','temperature','renewable_kw']

def train_compare(df):
    d,features=feature_frame(df)
    if len(d)<20: raise ValueError('At least 20 rows are required.')
    X=d[features].astype(float); y=d.demand_kw.astype(float); n=len(d); a=max(1,int(n*.7)); b=max(a+1,int(n*.85)); b=min(b,n-1)
    if a<5 or b-a<2 or n-b<2: raise ValueError('Not enough rows for chronological train/validation/test split.')
    Xtr,Xte=X.iloc[:a],X.iloc[b:]; ytr,yte=y.iloc[:a],y.iloc[b:]
    models={'Decision Tree':DecisionTreeRegressor(max_depth=5,random_state=42),'MLP Neural Network':make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=(32,16),max_iter=700,early_stopping=True,random_state=42))}
    results=[]; predictions={}
    for name,model in models.items():
        t=time.perf_counter(); model.fit(Xtr,ytr); val_pred=model.predict(X.iloc[a:b]);
        val_mae=mean_absolute_error(y.iloc[a:b],val_pred); val_rmse=float(np.sqrt(mean_squared_error(y.iloc[a:b],val_pred)))
        # Refit using train + validation only after validation diagnostics; test remains untouched.
        model.fit(X.iloc[:b],y.iloc[:b]); pred=model.predict(Xte); elapsed=(time.perf_counter()-t)*1000
        mae=mean_absolute_error(yte,pred); rmse=float(np.sqrt(mean_squared_error(yte,pred)))
        results.append({'model':name,'validation_mae_kw':round(float(val_mae),3),'validation_rmse_kw':round(val_rmse,3),'mae_kw':round(float(mae),3),'rmse_kw':round(rmse,3),'fit_predict_ms':round(elapsed,2)})
        predictions[name]={'actual':yte.round(2).tolist(),'predicted':np.round(pred,2).tolist(),'timestamps':d.timestamp.iloc[b:].astype(str).tolist()}
    best=min(results,key=lambda r:r['mae_kw'])
    return {'metrics':results,'best_model':best['model'],'predictions':predictions,'split':{'train':a,'validation':b-a,'test':n-b,'method':'Chronological 70% / 15% / 15%; validation portion is held out before test.'},'date_range':[str(d.timestamp.min()),str(d.timestamp.max())],'features':features}

def forecast(df,model_name=None,steps=24):
    result=train_compare(df); d,features=feature_frame(df); y=d.demand_kw.astype(float); X=d[features].astype(float); cut=max(10,int(len(d)*.85))
    if model_name not in ['Decision Tree','MLP Neural Network']: model_name=result['best_model']
    model=DecisionTreeRegressor(max_depth=5,random_state=42) if model_name=='Decision Tree' else make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=(32,16),max_iter=700,early_stopping=True,random_state=42))
    model.fit(X.iloc[:cut],y.iloc[:cut]); last=pd.to_datetime(d.timestamp.max()); future=pd.date_range(last+pd.Timedelta(hours=1),periods=steps,freq='h')
    f=pd.DataFrame({'timestamp':future}); f['hour']=f.timestamp.dt.hour; f['dayofweek']=f.timestamp.dt.dayofweek; f['month']=f.timestamp.dt.month; f['dayofyear']=f.timestamp.dt.dayofyear; f['temperature']=d.temperature.iloc[-1]; f['renewable_kw']=d.renewable_kw.iloc[-1]
    return {'timestamps':future.astype(str).tolist(),'predicted_kw':np.round(model.predict(f[features]),2).tolist(),'model':model_name}
