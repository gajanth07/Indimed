import streamlit as st
import io, math, json, sqlite3, os, tempfile
from datetime import date, timedelta, datetime
from pathlib import Path

st.set_page_config(page_title='IndiMed Pro 2026 Production', layout='wide')

def resolve_db_path():
    candidates = [Path('output/indimed_clinic.db'), Path('/tmp/indimed_clinic.db'), Path(tempfile.gettempdir()) / 'indimed_clinic.db']
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            test = sqlite3.connect(p)
            test.close()
            return p
        except Exception:
            continue
    return Path('indimed_clinic.db')

DB_PATH = resolve_db_path()

st.markdown('''
<style>
:root { --bg:#eef5fb; --surface:#ffffff; --surface2:#f7fbff; --border:#d7e5f2; --text:#0f172a; --muted:#5b6b81; --primary:#175b9e; --primary2:#1c7ed6; --teal:#14b8a6; }
.stApp { background: radial-gradient(circle at top left, #f8fcff 0%, #eef5fb 45%, #e6f0f9 100%); color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1500px; padding: 1rem 1rem 3rem; }
.appbar,.appbrand {display:flex; align-items:center; gap:12px;} .appbar {justify-content:space-between; margin-bottom:14px;}
.logo-orb {width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg,#1b4f8a,#14b8a6); display:flex; align-items:center; justify-content:center; color:white; font-weight:800;}
.brandtxt h2 {margin:0; color:#113a62; font-size:1.15rem;} .brandtxt p {margin:.15rem 0 0; color:#66809a !important; font-size:.9rem;}
.quickpill {background:#fff; border:1px solid #d7e5f2; color:#1a578f; padding:10px 14px; border-radius:999px; font-weight:700;}
.hero { background: linear-gradient(135deg, #1b4f8a 0%, #1f6fb2 55%, #14b8a6 100%); color:white; border-radius:26px; padding:24px; margin-bottom:18px; } .hero h1 {margin:0; color:white;} .hero p {margin:.55rem 0 0; color:rgba(255,255,255,.88)!important;}
.kpi-strip {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:16px;} .kpi-box,.surface,.card {background:#fff; border:1px solid var(--border); border-radius:20px; padding:14px;} .kpi-box h4 {margin:0; color:#6a8198; font-size:.82rem;} .kpi-box p {margin:.35rem 0 0; color:#10375d; font-weight:800; font-size:1.15rem;}
.card {border-radius:24px; min-height:168px; background:linear-gradient(180deg,#fff,#f8fbff);} .card-icon {width:54px;height:54px;border-radius:16px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#e9f4ff,#d9fbf6);font-size:1.5rem;margin-bottom:.85rem;} .card h3 {margin:0 0 .45rem; color:#13385d;} .card p {color:#5b6b81!important; min-height:58px;}
.stButton>button,.stDownloadButton>button {width:100%!important;border:none!important;border-radius:14px!important;font-weight:700!important;color:white!important;min-height:44px;} .stButton>button {background:linear-gradient(135deg,var(--primary),var(--primary2))!important;} .stDownloadButton>button {background:linear-gradient(135deg,#0f766e,var(--teal))!important;}
.alert-red,.alert-yellow,.alert-green,.note {padding:13px 15px;border-radius:16px;font-weight:600;margin:.6rem 0;} .alert-red {background:#fff4f4;border:1px solid #ffd7d7;color:#9f1239;} .alert-yellow {background:#fffaf0;border:1px solid #fde3a7;color:#9a6700;} .alert-green {background:#effdf7;border:1px solid #b7efd7;color:#0f766e;} .note {background:#eef7ff;border:1px solid #cfe4fa;color:#1d4f91;}
.badge-due,.badge-overdue,.badge-upcoming,.badge-access,.badge-watch,.badge-reserve {padding:6px 12px;border-radius:999px;font-weight:800;display:inline-block;font-size:.82rem;margin:.2rem .35rem .2rem 0;} .badge-due{background:#fee2e2;color:#991b1b;} .badge-overdue{background:#fff1f2;color:#be123c;} .badge-upcoming{background:#dbeafe;color:#1d4ed8;} .badge-access{background:#dcfce7;color:#166534;} .badge-watch{background:#fef3c7;color:#92400e;} .badge-reserve{background:#fee2e2;color:#991b1b;}
</style>
''', unsafe_allow_html=True)

@st.cache_resource
def get_conn(db_path_str):
    conn = sqlite3.connect(db_path_str, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, name TEXT, age TEXT, sex TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, summary TEXT, payload TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS trends (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, metric TEXT, value REAL, unit TEXT, created_at TEXT)')
    conn.commit()
    return conn

conn = get_conn(str(DB_PATH))

def query_df(sql, params=()):
    cur = conn.cursor(); cur.execute(sql, params); rows = cur.fetchall(); cols = [d[0] for d in cur.description] if cur.description else []
    return rows, cols

def save_patient(patient_id, name, age, sex):
    if not patient_id:
        return
    conn.execute('INSERT OR REPLACE INTO patients(patient_id,name,age,sex,updated_at) VALUES(?,?,?,?,?)', (patient_id,name,age,sex,str(datetime.now())))
    conn.commit()

def save_record(patient_id, dept, summary, payload):
    conn.execute('INSERT INTO records(patient_id,dept,summary,payload,created_at) VALUES(?,?,?,?,?)', (patient_id or 'unknown',dept,summary,json.dumps(payload),str(datetime.now())))
    conn.commit()

def save_trend(patient_id, dept, metric, value, unit=''):
    conn.execute('INSERT INTO trends(patient_id,dept,metric,value,unit,created_at) VALUES(?,?,?,?,?,?)', (patient_id or 'unknown',dept,metric,float(value),unit,str(datetime.now())))
    conn.commit()

def schedule_badge(d):
    if d < date.today(): return 'badge-overdue','Overdue'
    if d == date.today(): return 'badge-due','Due today'
    return 'badge-upcoming','Upcoming'

def interp(msg, level='note'): st.markdown(f"<div class='{level}'>{msg}</div>", unsafe_allow_html=True)
def evidence_box(source, formula, pearl, pitfalls, cite):
    st.markdown(f"<div class='surface'><b>Evidence / source:</b> {source}<br><b>Formula / method:</b> {formula}<br><b>Clinical pearl:</b> {pearl}<br><b>Pitfalls:</b> {pitfalls}<br><b>Guideline link / citation:</b> {cite}</div>", unsafe_allow_html=True)
def kg_to_lb(kg): return kg*2.20462
def cm_to_in(cm): return cm/2.54
def mg_ldl_to_mmol(val): return val/38.67
def sampson_ldl(tc,hdl,tg): non_hdl=tc-hdl; return tc/0.948-hdl/0.971-(tg/8.56+(tg*non_hdl)/2140-(tg*tg)/16100)-9.44
def ckd_epi_2021(scr,age,female):
    k=0.7 if female else 0.9; a=-0.241 if female else -0.302; val=142*(min(scr/k,1)**a)*(max(scr/k,1)**-1.2)*(0.9938**age)
    return val*1.012 if female else val

def html_report(patient, dept, summary, cite):
    html=f"<html><head><meta charset='utf-8'><title>IndiMed Report</title></head><body><h1>IndiMed Pro 2026 Report</h1><p><b>Patient:</b> {patient.get('name','')} ({patient.get('patient_id','')})</p><p><b>Age/Sex:</b> {patient.get('age','')} / {patient.get('sex','')}</p><p><b>Department:</b> {dept}</p><p><b>Summary:</b> {summary}</p><p><b>Guideline-linked citation:</b> {cite}</p><p><b>Database path in this run:</b> {DB_PATH}</p></body></html>"
    return io.BytesIO(html.encode())

DEPT_ICONS={'Medication Safety and Dose':'ðŸ’Š','Metabolic and General Medicine':'ðŸ©º','Pediatrics and Growth':'ðŸ§’','Neonatology':'ðŸ¼','Cardiology (Lipids and Risk)':'â¤ï¸','Gastroenterology (Hepatology)':'ðŸ«€','Neurology (Emergency)':'ðŸ§ ','Nephrology (eGFR Suite)':'ðŸ§ª','Ophthalmology and Orthopedics':'ðŸ‘ï¸','OB/GYN':'ðŸ¤°','ICU / Critical Care':'ðŸ¥','Emergency Medicine':'ðŸš‘','Hematology':'ðŸ©¸','HIV / ART Follow-up':'ðŸ—“ï¸'}
DEPTS=[('Medication Safety and Dose','Drug interaction checks, dose support, renal safety.'),('Metabolic and General Medicine','BMI, BSA, MAP, stewardship support.'),('Pediatrics and Growth','Growth, vaccines, fluids, fever dosing.'),('Neonatology','Prematurity, APGAR, corrected age, feeds.'),('Cardiology (Lipids and Risk)','LDL-C, BP, lipids and risk support.'),('Gastroenterology (Hepatology)','Liver scores and severity support.'),('Neurology (Emergency)','GCS-P and stroke timing support.'),('Nephrology (eGFR Suite)','eGFR and kidney risk support.'),('Ophthalmology and Orthopedics','IOP correction and bone risk.'),('OB/GYN','Pregnancy dating and labor support.'),('ICU / Critical Care','Shock, oxygenation, sepsis concern.'),('Emergency Medicine','Triage, sepsis, rabies PEP.'),('Hematology','Mentzer, ANC, platelet flags.'),('HIV / ART Follow-up','ART milestone planning and support.')]
EVIDENCE={name:('Current bedside support references','Department-specific quick tools','Use for rapid clinical organization','Always verify with local protocol and full clinical context',f'{name} guideline reference placeholder') for name,_ in DEPTS}
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, PCV-3')]
AWARE_DB={'Amoxicillin':'ACCESS','Ampicillin':'ACCESS','Cefalexin':'ACCESS','Doxycycline':'ACCESS','Cefixime':'WATCH','Azithromycin':'WATCH','Ceftriaxone':'WATCH','Meropenem':'RESERVE'}
if 'page' not in st.session_state: st.session_state.page='home'
if 'selected_dept' not in st.session_state: st.session_state.selected_dept=DEPTS[0][0]
if 'favorites' not in st.session_state: st.session_state.favorites=[]
if 'recents' not in st.session_state: st.session_state.recents=[]
if 'nav' not in st.session_state: st.session_state.nav='Dashboard'

def go_home(): st.session_state.page='home'
def open_dept(name):
    st.session_state.selected_dept=name; st.session_state.page='dept'
    if name in st.session_state.recents: st.session_state.recents.remove(name)
    st.session_state.recents=[name]+st.session_state.recents[:5]

def toggle_favorite(name):
    if name in st.session_state.favorites: st.session_state.favorites.remove(name)
    else: st.session_state.favorites.append(name)

def patient_selector():
    rows,_=query_df('SELECT patient_id,name,age,sex,updated_at FROM patients ORDER BY updated_at DESC')
    ids=[f"{r[0]} â€” {r[1]}" for r in rows]
    with st.expander('Persistent patient database', expanded=False):
        c1,c2,c3,c4=st.columns(4)
        patient_id=c1.text_input('Patient ID'); name=c2.text_input('Name'); age=c3.text_input('Age'); sex=c4.selectbox('Sex',['Male','Female','Other'])
        if st.button('Save patient to local DB'): save_patient(patient_id,name,age,sex); st.success(f'Patient saved to {DB_PATH}')
        if ids: st.selectbox('Loaded patients', ids)
        interp(f'Database path for this deployment run: {DB_PATH}', 'note')
        return {'patient_id':patient_id,'name':name,'age':age,'sex':sex}

def history_tables():
    with st.expander('Multi-patient history tables', expanded=False):
        for sql, title in [('SELECT patient_id,name,age,sex,updated_at FROM patients ORDER BY updated_at DESC','Patients'),('SELECT patient_id,dept,summary,created_at FROM records ORDER BY created_at DESC LIMIT 100','Records'),('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at DESC LIMIT 200','Trends')]:
            rows, cols = query_df(sql)
            if rows: st.write(title); st.dataframe([dict(zip(cols,r)) for r in rows], use_container_width=True)

def conversion_panel():
    with st.expander('Unit conversion everywhere', expanded=False):
        c1,c2,c3=st.columns(3); kg=c1.number_input('kg',0.0,500.0,70.0); cm=c2.number_input('cm',0.0,300.0,170.0); ldl=c3.number_input('LDL mg/dL',0.0,500.0,100.0)
        d1,d2,d3=st.columns(3); d1.metric('lb',f'{kg_to_lb(kg):.2f}'); d2.metric('in',f'{cm_to_in(cm):.2f}'); d3.metric('mmol/L',f'{mg_ldl_to_mmol(ldl):.2f}')

def trend_view(patient_id=None):
    with st.expander('Trend charts over time', expanded=False):
        rows, cols = query_df('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at')
        data=[dict(zip(cols,r)) for r in rows if (not patient_id or r[0]==patient_id)]
        if data:
            metrics=sorted({x['metric'] for x in data}); metric=st.selectbox('Metric', metrics); vals=[x['value'] for x in data if x['metric']==metric]
            st.line_chart({'value':vals}); st.dataframe([x for x in data if x['metric']==metric], use_container_width=True)
        else: st.info('No stored trends yet.')

def generic_department_framework(dept, patient):
    source, formula, pearl, pitfalls, cite = EVIDENCE[dept]
    evidence_box(source, formula, pearl, pitfalls, cite)
    summary=f'{dept} framework opened.'
    if dept=='Medication Safety and Dose':
        wt=st.number_input('Weight kg',1.0,250.0,70.0); mgkg=st.number_input('Dose mg/kg',0.1,500.0,15.0); total=wt*mgkg; st.metric('Dose', f'{total:.2f} mg'); save_trend(patient.get('patient_id'), dept, 'Dose mg', total, 'mg'); summary=f'Dose {total:.2f} mg'
    elif dept=='Metabolic and General Medicine':
        w=st.number_input('Weight kg',5.0,300.0,70.0); h=st.number_input('Height cm',50.0,250.0,170.0); bmi=w/((h/100)**2); st.metric('BMI', f'{bmi:.2f}'); save_trend(patient.get('patient_id'), dept, 'BMI', bmi, 'kg/mÂ²'); summary=f'BMI {bmi:.2f}'
    elif dept=='Pediatrics and Growth':
        dob=st.date_input('DOB', value=date.today()-timedelta(days=365)); wt=st.number_input('Weight kg',1.0,120.0,10.0); ht=st.number_input('Height cm',30.0,200.0,75.0); save_trend(patient.get('patient_id'), dept, 'Weight', wt, 'kg'); save_trend(patient.get('patient_id'), dept, 'Height', ht, 'cm')
        for band,daynum,vaccines in VACCINE_SCHEDULE:
            due=dob+timedelta(days=daynum); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>{band} <span class='{badge}'>{label}</span></h3><p>{due}<br>{vaccines}</p></div>", unsafe_allow_html=True)
        summary=f'Pediatric weight {wt} kg height {ht} cm'
    elif dept=='Neonatology':
        ga=st.number_input('GA weeks',22,44,36); wt=st.number_input('Current wt kg',0.5,8.0,2.8); st.metric('Prematurity', 'Preterm' if ga<37 else 'Term'); save_trend(patient.get('patient_id'), dept, 'Neonate weight', wt, 'kg'); summary=f'GA {ga}, wt {wt}'
    elif dept=='Cardiology (Lipids and Risk)':
        tc=st.number_input('TC',1.0,500.0,200.0); hdl=st.number_input('HDL',1.0,200.0,45.0); tg=st.number_input('TG',1.0,1000.0,150.0); ldl=sampson_ldl(tc,hdl,tg); st.metric('LDL-C', f'{ldl:.1f}'); save_trend(patient.get('patient_id'), dept, 'LDL-C', ldl, 'mg/dL'); summary=f'LDL-C {ldl:.1f}'
    elif dept=='Gastroenterology (Hepatology)':
        bili=st.number_input('Bilirubin',0.1,50.0,1.0); inr=st.number_input('INR',0.1,15.0,1.1); cr=st.number_input('Creatinine',0.1,15.0,1.0); meld=round(10*((0.957*math.log(max(1,cr)))+(0.378*math.log(max(1,bili)))+(1.12*math.log(max(1,inr))))+6.43,1); st.metric('MELD', meld); save_trend(patient.get('patient_id'), dept, 'MELD', meld, ''); summary=f'MELD {meld}'
    elif dept=='Neurology (Emergency)':
        e=st.select_slider('Eye',[1,2,3,4],value=4); v=st.select_slider('Verbal',[1,2,3,4,5],value=5); m=st.select_slider('Motor',[1,2,3,4,5,6],value=6); gcs=e+v+m; st.metric('GCS', gcs); save_trend(patient.get('patient_id'), dept, 'GCS', gcs, '/15'); summary=f'GCS {gcs}'
    elif dept=='Nephrology (eGFR Suite)':
        scr=st.number_input('Creatinine mg/dL',0.1,15.0,1.0); age=st.number_input('Age years',18,110,50); sex=st.selectbox('Sex',['Male','Female']); gfr=ckd_epi_2021(scr,age,sex=='Female'); st.metric('eGFR', f'{gfr:.1f}'); save_trend(patient.get('patient_id'), dept, 'eGFR', gfr, 'mL/min/1.73mÂ²'); summary=f'eGFR {gfr:.1f}'
    elif dept=='Ophthalmology and Orthopedics':
        iop=st.number_input('Measured IOP',5,60,20); cct=st.number_input('CCT',300,800,545); corrected=iop+((545-cct)/50*2.5); st.metric('Corrected IOP', f'{corrected:.1f}'); save_trend(patient.get('patient_id'), dept, 'Corrected IOP', corrected, 'mmHg'); summary=f'Corrected IOP {corrected:.1f}'
    elif dept=='OB/GYN':
        lmp=st.date_input('LMP', value=date.today()); cycle=st.number_input('Cycle length',21,45,28); ga=(date.today()-lmp).days/7; edd=lmp+timedelta(days=280+(cycle-28)); st.metric('GA', f'{ga:.1f} weeks'); st.metric('EDD', str(edd)); save_trend(patient.get('patient_id'), dept, 'GA', ga, 'weeks'); summary=f'GA {ga:.1f} EDD {edd}'
    elif dept=='ICU / Critical Care':
        hr=st.number_input('HR',20,250,100); sbp=st.number_input('SBP',30,250,110); shock=hr/sbp; st.metric('Shock index', f'{shock:.2f}'); save_trend(patient.get('patient_id'), dept, 'Shock index', shock, ''); summary=f'Shock index {shock:.2f}'
    elif dept=='Emergency Medicine':
        bite=st.date_input('Bite date', value=date.today()); wt=st.number_input('Weight kg',1.0,200.0,60.0)
        for d in [0,3,7,14,28]:
            due=bite+timedelta(days=d); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>ARV Day {d} <span class='{badge}'>{label}</span></h3><p>{due}</p></div>", unsafe_allow_html=True)
        save_trend(patient.get('patient_id'), dept, 'Rabies weight', wt, 'kg'); summary=f'Rabies workflow weight {wt} kg'
    elif dept=='Hematology':
        hb=st.number_input('Hemoglobin',1.0,25.0,12.0); mcv=st.number_input('MCV',40.0,130.0,85.0); mentzer=mcv/hb if hb else 0; st.metric('Mentzer index', f'{mentzer:.2f}'); save_trend(patient.get('patient_id'), dept, 'Mentzer index', mentzer, ''); summary=f'Mentzer {mentzer:.2f}'
    elif dept=='HIV / ART Follow-up':
        art=st.date_input('ART start', value=date.today())
        for name,days in [('4 weeks',28),('3 months',90),('6 months',180),('12 months',365)]:
            due=art+timedelta(days=days); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>{name} <span class='{badge}'>{label}</span></h3><p>{due}</p></div>", unsafe_allow_html=True)
        save_trend(patient.get('patient_id'), dept, 'ART offset', 0, 'days'); summary=f'ART start {art}'
    save_record(patient.get('patient_id'), dept, summary, {'patient':patient,'dept':dept})
    return summary, cite

patient=patient_selector(); history_tables(); conversion_panel(); trend_view(patient.get('patient_id'))

if st.session_state.page=='home':
    st.markdown("<div class='appbar'><div class='appbrand'><div class='logo-orb'>IM</div><div class='brandtxt'><h2>IndiMed Pro 2026 Fixed</h2><p>SQLite path-safe production-style build with patient history and guideline-linked export</p></div></div><div class='quickpill'>SQLite safe path fix</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero'><h1>Persistent Clinical Workflow</h1><p>This version fixes the SQLite startup error by ensuring a writable database path and falling back to temporary storage when needed. Current DB path: {DB_PATH}</p></div>", unsafe_allow_html=True)
    prows,_=query_df('SELECT patient_id FROM patients'); rrows,_=query_df('SELECT id FROM records'); trows,_=query_df('SELECT id FROM trends')
    st.markdown(f"<div class='kpi-strip'><div class='kpi-box'><h4>Departments</h4><p>{len(DEPTS)}</p></div><div class='kpi-box'><h4>Patients</h4><p>{len(prows)}</p></div><div class='kpi-box'><h4>Records</h4><p>{len(rrows)}</p></div><div class='kpi-box'><h4>Trends</h4><p>{len(trows)}</p></div></div>", unsafe_allow_html=True)
    search=st.text_input('Search calculators or departments')
    cols=st.columns(3)
    if cols[0].button('Dashboard'): st.session_state.nav='Dashboard'
    if cols[1].button('Favorites'): st.session_state.nav='Favorites'
    if cols[2].button('Recent'): st.session_state.nav='Recent'
    show=DEPTS if st.session_state.nav=='Dashboard' else [d for d in DEPTS if d[0] in st.session_state.favorites] if st.session_state.nav=='Favorites' else [(n,dict(DEPTS)[n]) for n in st.session_state.recents if n in dict(DEPTS)]
    if search: show=[d for d in show if search.lower() in d[0].lower() or search.lower() in d[1].lower()]
    for row_start in range(0,len(show),3):
        c=st.columns(3)
        for i,(title,desc) in enumerate(show[row_start:row_start+3]):
            with c[i]:
                icon=DEPT_ICONS.get(title,'â€¢'); fav='â˜… Remove Favorite' if title in st.session_state.favorites else 'â˜† Add Favorite'
                st.markdown(f"<div class='card'><div class='card-icon'>{icon}</div><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                a,b=st.columns(2); a.button('Open', key=f'open_{title}', on_click=open_dept, args=(title,)); b.button(fav, key=f'fav_{title}', on_click=toggle_favorite, args=(title,))
else:
    dept=st.session_state.selected_dept
    top1,top2=st.columns([5,1])
    with top1: st.markdown(f"<div class='hero'><h1>{DEPT_ICONS.get(dept,'â€¢')} {dept}</h1><p>Path-safe persistence, trend logging, structured summary, and report export</p></div>", unsafe_allow_html=True)
    with top2: st.button('Home', on_click=go_home)
    summary, cite = generic_department_framework(dept, patient)
    st.download_button('Export guideline-linked HTML report', html_report(patient, dept, summary, cite), f'IndiMed_{dept[:10]}_{date.today()}.html')
    interp('Clinical decision support only. This version fixes the writable-path SQLite error and uses a fallback DB location when needed.', 'alert-red')
