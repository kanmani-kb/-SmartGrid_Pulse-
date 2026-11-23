from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import io

def create_report(dataset_name,df,runs):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=15*mm,bottomMargin=15*mm)
    s=getSampleStyleSheet(); s.add(ParagraphStyle(name='SmallNote',parent=s['BodyText'],fontSize=8,leading=10,textColor=colors.HexColor('#555555'))); story=[Paragraph('SmartGrid Pulse – Project Run Report',s['Title']),Paragraph('Educational Chennai-region grid simulation; not a live utility control system.',s['Italic']),Spacer(1,8)]
    story += [Paragraph(f'<b>Active dataset:</b> {dataset_name}',s['BodyText']),Paragraph(f'<b>Rows:</b> {len(df)} &nbsp;&nbsp; <b>Date range:</b> {df.timestamp.min()} to {df.timestamp.max()}',s['BodyText']),Spacer(1,10)]
    def section(title): story.append(Paragraph(title,s['Heading2']))
    def table(data):
        t=Table(data,repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9e8ff')),('GRID',(0,0),(-1,-1),.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)])); story.append(t)
    ml=runs.get('ml')
    section('1. Demand model comparison')
    if ml:
        table([['Model','Validation MAE','Test MAE','Test RMSE','Measured ms']]+[[x['model'],x['validation_mae_kw'],x['mae_kw'],x['rmse_kw'],x['fit_predict_ms']] for x in ml['metrics']]); story.append(Paragraph(f"Best by held-out test MAE: {ml['best_model']}. Chronological split: {ml['split']}.",s['BodyText']))
    else: story.append(Paragraph('Run the ML module to add computed metrics.',s['BodyText']))
    section('2. Search algorithm comparison')
    sr=runs.get('search')
    if sr:
        table([['Algorithm','Path cost','Execution ms','Expanded','Reached']]+[[x['algorithm'],x['path_cost'],x['execution_ms'],x['expanded_nodes'],x['reached']] for x in sr['results']])
        story.append(Paragraph(f"Best for this measured route: {sr.get('best_algorithm')}. Selection rule: {sr.get('best_reason')}",s['BodyText']))
    else: story.append(Paragraph('Run a route comparison in Module 1 to add results.',s['BodyText']))
    section('3. Route edge-cost breakdown')
    if sr:
        for x in sr['results']:
            if x['edges']:
                story.append(Paragraph(x['algorithm']+' route',s['Heading3'])); table([['From','To','Distance','Congestion','Risk','Total']]+[[e['from'],e['to'],e['distance_cost'],e['congestion_penalty'],e['risk_penalty'],e['total_cost']] for e in x['edges']])
    section('4. CSP and power distribution')
    cp=runs.get('csp')
    if cp: table([['Area','Requested kW','Allocated kW','Remaining kW','Priority','Constraints']]+[[x['name'],x['requested_kw'],x['allocated_kw'],x['remaining_kw'],x['priority'],x['constraint_ok']] for x in cp['rows']])
    pd=runs.get('distribution')
    if pd: table([['Area','Demand','Allocated','Shortage','Capacity','Safe','Capacity warning']]+[[x['name'],x['demand_kw'],x['allocated_kw'],x['shortage_kw'],x['capacity_kw'],x['safe'],x.get('overload_risk',False)] for x in pd['areas']])
    section('5. Logical reasoning and safety')
    lg=runs.get('logic')
    if lg:
        story.append(Paragraph(f"Inference scenarios passed: {lg['passed']}/{len(lg['tests'])}; rule coverage: {lg['rule_coverage']}%; triggered rules: {', '.join(lg['triggered_rules']) or 'none'}. {lg['consistency']}",s['BodyText']))
        table([['Scenario','Query','Passed']]+[[x['scenario'],x['query'],x['passed']] for x in lg['tests']])
    else: story.append(Paragraph('Run Module 2 reasoning to include measured inference tests, triggered rules and consistency.',s['BodyText']))
    lq=runs.get('logic_query')
    if lq: story.append(Paragraph(f"Selected query: {lq['backward_chaining']['query']}; proved: {lq['backward_chaining']['proved']}; safety decision: {lq['safety_decision']}",s['BodyText']))
    se=runs.get('search_experiments')
    if se:
        section('Search grid-size experiments')
        table([['Grid','Best algorithm','Path cost','Execution ms']]+[[x['size'],x['best_algorithm'],x['path_cost'],x['execution_ms']] for x in se['best_by_size']])
    section('6. Scalability measurements')
    sc=runs.get('scalability')
    if sc: table([['Workload','Records','Execution ms','Peak memory MB']]+[[x['factor'],x['records_processed'],x['execution_ms'],x['peak_memory_mb']] for x in sc['rows']])
    else: story.append(Paragraph('Run scalability tests in Module 3 to add measurements.',s['BodyText']))
    story.append(Spacer(1,10)); story.append(Paragraph('Limitations: simulated feeder links, demand nodes, capacities and allocation policy are illustrative. Facility markers are approximate display locations. No live utility telemetry or control commands are connected.',s['SmallNote']))
    doc.build(story); return buf.getvalue()
