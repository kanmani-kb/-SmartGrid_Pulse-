import time, tracemalloc

def scalability_benchmark(df):
    rows=[]
    for factor in [1,10,100]:
        data=df.copy()
        # Scaled workload is repeated copies with timestamp offsets, not new observations.
        chunks=[]
        for i in range(factor):
            c=data.copy(); c['timestamp']=c['timestamp']+__import__('pandas').to_timedelta(i*len(data),unit='h'); chunks.append(c)
        tracemalloc.start(); t=time.perf_counter(); combined=__import__('pandas').concat(chunks,ignore_index=True)
        # representative processing workload
        summary=combined.groupby(combined['timestamp'].dt.hour)['demand_kw'].agg(['count','mean','max'])
        elapsed=(time.perf_counter()-t)*1000; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
        rows.append({'factor':f'{factor}x','records_processed':len(combined),'execution_ms':round(elapsed,3),'peak_memory_mb':round(peak/1024/1024,3),'groups':len(summary)})
    return {'rows':rows,'note':'Repeated copies of the active dataset used as workload stress tests; they are not additional real observations.'}
