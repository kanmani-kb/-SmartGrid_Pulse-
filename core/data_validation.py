import pandas as pd
import numpy as np

def validate_energy_csv(raw):
    if raw is None or raw.empty: raise ValueError('The CSV file is empty.')
    cols={str(c).strip().lower():c for c in raw.columns}
    aliases={'timestamp':['timestamp','date','datetime'],'demand_kw':['demand_kw','demand','load_kw','load'],'generation_kw':['generation_kw','generation','supply_kw','supply']}
    rename={}
    for standard,names in aliases.items():
        found=next((cols[x] for x in names if x in cols),None)
        if not found: raise ValueError(f'Missing required column: {standard}. Accepted names: {", ".join(names)}')
        rename[found]=standard
    result=raw.rename(columns=rename).copy()
    result['timestamp']=pd.to_datetime(result['timestamp'],errors='coerce')
    for c in ['demand_kw','generation_kw']: result[c]=pd.to_numeric(result[c],errors='coerce')
    if result[['timestamp','demand_kw','generation_kw']].isna().any().any(): raise ValueError('Required columns contain missing or invalid values. Please clean the CSV and upload again.')
    values=result[['demand_kw','generation_kw']].to_numpy(dtype=float)
    if (values<0).any(): raise ValueError('Demand and generation must be non-negative.')
    if not np.isfinite(values).all(): raise ValueError('Demand and generation must contain finite numeric values only.')
    if len(result)<20: raise ValueError('Please upload at least 20 valid rows for chronological model evaluation.')
    return result.sort_values('timestamp').reset_index(drop=True)
