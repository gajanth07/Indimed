import streamlit as st
import io, math, json, sqlite3
from datetime import date, timedelta, datetime
from pathlib import Path

st.set_page_config(page_title='IndiMed Pro 2026 Production', layout='wide')
DB_PATH = Path('output/indimed_clinic.db')

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
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, name TEXT, age TEXT, sex TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, summary TEXT, payload TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS trends (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, metric TEXT, value REAL, unit TEXT, created_at TEXT)')
    conn.commit()
    return conn
conn = get_conn()

def query_df(sql, params=()):
    cur = conn.cursor(); cur.execute(sql, params); rows = cur.fetchall(); cols = [d[0] for d in cur.description] if cur.description else []
    return rows, cols

def save_patient(patient_id, name, age, sex):
    conn.execute('INSERT OR REPLACE INTO patients(patient_id,name,age,sex,updated_at) VALUES(?,?,?,?,?)', (patient_id,name,age,sex,str(datetime.now())))
    conn.commit()

def save_record(patient_id, dept, summary, payload):
    conn.execute('INSERT INTO records(patient_id,dept,summary,payload,created_at) VALUES(?,?,?,?,?)', (patient_id,dept,summary,json.dumps(payload),str(datetime.now())))
    conn.commit()

def save_trend(patient_id, dept, metric, value, unit=''):
    conn.execute('INSERT INTO trends(patient_id,dept,metric,value,unit,created_at) VALUES(?,?,?,?,?,?)', (patient_id,dept,metric,float(value),unit,str(datetime.now())))
    conn.commit()

def schedule_badge(d):
    if d < date.today(): return 'badge-overdue','Overdue'
    if d == date.today(): return 'badge-due','Due today'
    return 'badge-upcoming','Upcoming'

def interp(msg, level='note'): st.markdown(f"<div class='{level}'>{msg}</div>", unsafe_allow_html=True)
def decision_box(status, reason, next_step, red_flags='None entered'):
    style='alert-green' if status=='Normal' else 'alert-yellow' if status=='Borderline' else 'alert-red'
    st.markdown(f"<div class='{style}'><b>Status:</b> {status}<br><b>Reason:</b> {reason}<br><b>Suggested next step:</b> {next_step}<br><b>Red flags / refer now:</b> {red_flags}</div>", unsafe_allow_html=True)
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
    html=f"""<html><head><meta charset='utf-8'><title>IndiMed Report</title><style>body{{font-family:Arial;padding:28px;color:#0f172a}} .box{{border:1px solid #d7e5f2;border-radius:16px;padding:16px;margin:12px 0;background:#f8fbff}}</style></head><body><h1>IndiMed Pro 2026 Report</h1><div class='box'><b>Patient:</b> {patient.get('name','')}<br><b>ID:</b> {patient.get('patient_id','')}<br><b>Age:</b> {patient.get('age','')}<br><b>Sex:</b> {patient.get('sex','')}<br><b>Date:</b> {date.today()}</div><div class='box'><b>Department:</b> {dept}</div><div class='box'><b>Summary:</b> {summary}</div><div class='box'><b>Guideline-linked citation:</b> {cite}</div><div class='box'><b>Clinical note:</b> Clinical decision support only. Verify with local protocol and clinical judgment.</div></body></html>"""
    return io.BytesIO(html.encode())

DEPT_ICONS={'Medication Safety and Dose':'ðŸ’Š','Metabolic and General Medicine':'ðŸ©º','Pediatrics and Growth':'ðŸ§’','Neonatology':'ðŸ¼','Cardiology (Lipids and Risk)':'â¤ï¸','Gastroenterology (Hepatology)':'ðŸ«€','Neurology (Emergency)':'ðŸ§ ','Nephrology (eGFR Suite)':'ðŸ§ª','Ophthalmology and Orthopedics':'ðŸ‘ï¸','OB/GYN':'ðŸ¤°','ICU / Critical Care':'ðŸ¥','Emergency Medicine':'ðŸš‘','Hematology':'ðŸ©¸','HIV / ART Follow-up':'ðŸ—“ï¸'}
DEPTS=[('Medication Safety and Dose','Drug interaction checks, dose support, renal safety.'),('Metabolic and General Medicine','BMI, BSA, MAP, stewardship support.'),('Pediatrics and Growth','Growth, vaccines, fluids, fever dosing.'),('Neonatology','Prematurity, APGAR, corrected age, feeds.'),('Cardiology (Lipids and Risk)','LDL-C, BP, lipids and risk support.'),('Gastroenterology (Hepatology)','Liver scores and severity support.'),('Neurology (Emergency)','GCS-P and stroke timing support.'),('Nephrology (eGFR Suite)','eGFR and kidney risk support.'),('Ophthalmology and Orthopedics','IOP correction and bone risk.'),('OB/GYN','Pregnancy dating and labor support.'),('ICU / Critical Care','Shock, oxygenation, sepsis concern.'),('Emergency Medicine','Triage, sepsis, rabies PEP.'),('Hematology','Mentzer, ANC, platelet flags.'),('HIV / ART Follow-up','ART milestone planning and support.')]
EVIDENCE={
    'Medication Safety and Dose':('WHO stewardship concepts + local formulary','DDI quick screen and mg/kg support','Keep dosing simple and validated','Interaction database is not exhaustive','WHO AWaRe / local formulary'),
    'Metabolic and General Medicine':('Standard bedside measures','BMI, BSA, MAP, waist/height','Useful for first-pass metabolic risk screening','Not diagnostic alone','Standard bedside screening references'),
    'Pediatrics and Growth':('Pediatric growth and immunization support','Approximate growth screening + vaccine milestone engine','Use trend more than single value','Not a full percentile or catch-up engine','National immunization / pediatric growth references'),
    'Neonatology':('Neonatal bedside support','Prematurity, corrected age, feeds','Corrected age changes interpretation','Fluids vary by setting and illness','Neonatal follow-up references'),
    'Cardiology (Lipids and Risk)':('Current lipid estimation practice','Sampson LDL and BP support','Non-HDL is helpful in hypertriglyceridemia','Treatment still needs full risk context','Lipid guideline / risk estimation references'),
    'Gastroenterology (Hepatology)':('Liver severity score practice','MELD family framework','Scores help triage severity','Acute illness may outpace scores','Liver disease severity guideline references'),
    'Neurology (Emergency)':('Emergency neuro assessment support','GCS/GCS-P and stroke time window','Time-to-action matters','Screening tools do not exclude disease','Stroke and neuro-emergency references'),
    'Nephrology (eGFR Suite)':('Current adult kidney function reporting','CKD-EPI 2021 race-free equation','Confirm chronicity and proteinuria','AKI and extremes may mislead eGFR','Kidney disease guideline references'),
    'Ophthalmology and Orthopedics':('Bedside screening support','IOP correction + simple bone risk cues','Useful for quick first-pass review','Needs specialty confirmation','Ophthalmology / osteoporosis references'),
    'OB/GYN':('Routine obstetric bedside tools','EDD, GA, labor readiness, shock cues','Good for triage planning','Emergencies override score logic','Obstetric guideline references'),
    'ICU / Critical Care':('Critical care bedside assessment','Shock index, oxygenation, sepsis concern','Trend values repeatedly','Deterioration may be rapid','Sepsis / critical care references'),
    'Emergency Medicine':('Acute triage and rabies planning','qSOFA-style screen + ARV planning','Useful for time-sensitive organization','Local protocol alignment is essential','Emergency and rabies PEP references'),
    'Hematology':('Common screening heuristics','Mentzer index, ANC, platelet flags','Helps first-pass sorting','Needs smear and confirmatory labs','Hematology screening references'),
    'HIV / ART Follow-up':('HIV clinic timing support','ART milestone planner','Good adherence and follow-up tool','Local HIV protocol should decide actions','HIV program follow-up references')
}
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, PCV-3'),('9 months',270,'MMR-1, TCV'),('12 months',365,'Hep A-1, Varicella-1'),('15 months',455,'MMR-2, Varicella-2, PCV booster')]
AWARE_DB={'Amoxicillin':'ACCESS','Ampicillin':'ACCESS','Cefalexin':'ACCESS','Doxycycline':'ACCESS','Cefixime':'WATCH','Azithromycin':'WATCH','Ceftriaxone':'WATCH','Piperacillin-Tazobactam':'WATCH','Vancomycin':'WATCH','Meropenem':'RESERVE','Colistin':'RESERVE'}
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
    with st.expander('Persistent patient database / cloud-save ready', expanded=False):
        c1,c2,c3,c4=st.columns(4)
        patient_id=c1.text_input('Patient ID')
        name=c2.text_input('Name')
        age=c3.text_input('Age')
        sex=c4.selectbox('Sex',['Male','Female','Other'])
        if st.button('Save patient to local DB'):
            save_patient(patient_id,name,age,sex)
            st.success('Patient saved to SQLite local database')
        if ids:
            sel=st.selectbox('Load patient', ids)
            if st.button('Show selected patient'):
                st.info(sel)
        interp('SQLite is useful for local persistence, but production cloud deployment should use a remote database such as PostgreSQL, MySQL, or Supabase through secure connections and secrets management.', 'note')
        return {'patient_id':patient_id,'name':name,'age':age,'sex':sex}

def history_tables():
    with st.expander('Multi-patient history tables', expanded=False):
        prows,pcols=query_df('SELECT patient_id,name,age,sex,updated_at FROM patients ORDER BY updated_at DESC')
        rrows,rcols=query_df('SELECT patient_id,dept,summary,created_at FROM records ORDER BY created_at DESC LIMIT 100')
        trows,tcols=query_df('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at DESC LIMIT 200')
        if prows: st.dataframe([dict(zip(pcols,r)) for r in prows], use_container_width=True)
        if rrows: st.dataframe([dict(zip(rcols,r)) for r in rrows], use_container_width=True)
        if trows: st.dataframe([dict(zip(tcols,r)) for r in trows], use_container_width=True)

def conversion_panel():
    with st.expander('Unit conversion everywhere', expanded=False):
        c1,c2,c3=st.columns(3)
        kg=c1.number_input('kg',0.0,500.0,70.0); cm=c2.number_input('cm',0.0,300.0,170.0); ldl=c3.number_input('LDL mg/dL',0.0,500.0,100.0)
        d1,d2,d3=st.columns(3); d1.metric('lb',f'{kg_to_lb(kg):.2f}'); d2.metric('in',f'{cm_to_in(cm):.2f}'); d3.metric('mmol/L',f'{mg_ldl_to_mmol(ldl):.2f}')

def trend_view(patient_id=None):
    with st.expander('Trend charts over time', expanded=False):
        rows,cols=query_df('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at')
        data=[dict(zip(cols,r)) for r in rows if (not patient_id or r[0]==patient_id)]
        if data:
            metrics=sorted({x['metric'] for x in data}); metric=st.selectbox('Metric', metrics)
            vals=[x['value'] for x in data if x['metric']==metric]
            st.line_chart({'value':vals})
            st.dataframe([x for x in data if x['metric']==metric], use_container_width=True)
        else:
            st.info('No stored trends yet.')

def generic_department_framework(dept, patient):
    source, formula, pearl, pitfalls, cite = EVIDENCE[dept]
    evidence_box(source, formula, pearl, pitfalls, cite)
    st.markdown("<div class='surface'><b>Framework enabled:</b> patient save/load, multi-patient history, trend logging, guideline-linked report export, unit conversion, and structured summary for this department.</div>", unsafe_allow_html=True)
    summary=f'{dept} framework opened.'
    if dept=='Medication Safety and Dose':
        wt=st.number_input('Weight (kg)',1.0,250.0,70.0); mgkg=st.number_input('Dose mg/kg',0.1,500.0,15.0); abx=st.selectbox('Antibiotic',['â€” Select â€”']+sorted(AWARE_DB.keys())); total=wt*mgkg
        st.metric('Single dose', f'{total:.2f} mg'); save_trend(patient.get('patient_id','unknown'), dept, 'Dose mg', total, 'mg'); summary=f'Dose support {total:.2f} mg'
        if abx!='â€” Select â€”':
            cat=AWARE_DB[abx]; badge={'ACCESS':'badge-access','WATCH':'badge-watch','RESERVE':'badge-reserve'}[cat]; st.markdown(f"<span class='{badge}'>{abx}: {cat}</span>", unsafe_allow_html=True)
    elif dept=='Metabolic and General Medicine':
        w=st.number_input('Weight kg',5.0,300.0,70.0); h=st.number_input('Height cm',50.0,250.0,170.0); sbp=st.number_input('SBP',50,250,120); dbp=st.number_input('DBP',30,150,80)
        bmi=w/((h/100)**2); st.metric('BMI', f'{bmi:.2f}'); st.metric('MAP', f'{(sbp+2*dbp)/3:.1f}'); save_trend(patient.get('patient_id','unknown'), dept, 'BMI', bmi, 'kg/mÂ²'); summary=f'BMI {bmi:.2f}'
    elif dept=='Pediatrics and Growth':
        dob=st.date_input('DOB', value=date.today()-timedelta(days=365)); wt=st.number_input('Weight kg',1.0,120.0,10.0); ht=st.number_input('Height cm',30.0,200.0,75.0)
        st.metric('Maintenance fluid/day', f'{(wt*100 if wt<=10 else 1000+(wt-10)*50 if wt<=20 else 1500+(wt-20)*20):.0f} mL/day'); save_trend(patient.get('patient_id','unknown'), dept, 'Weight', wt, 'kg'); save_trend(patient.get('patient_id','unknown'), dept, 'Height', ht, 'cm')
        for band,daynum,vaccines in VACCINE_SCHEDULE:
            due=dob+timedelta(days=daynum); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>{band} <span class='{badge}'>{label}</span></h3><p>{due}<br>{vaccines}</p></div>", unsafe_allow_html=True)
        summary=f'Pediatric follow-up with weight {wt} kg and height {ht} cm'
    elif dept=='Neonatology':
        ga=st.number_input('Gestational age at birth (weeks)',22,44,36); current_wt=st.number_input('Current weight kg',0.5,8.0,2.8); day_life=st.number_input('Day of life',1,28,3)
        st.metric('Corrected prematurity flag', 'Preterm' if ga<37 else 'Term'); st.metric('Feed estimate', f'{current_wt*(80 if day_life<=1 else 100 if day_life<=3 else 120 if day_life<=7 else 150):.0f} mL/day'); save_trend(patient.get('patient_id','unknown'), dept, 'Neonate weight', current_wt, 'kg'); summary=f'GA {ga} weeks, current wt {current_wt} kg'
    elif dept=='Cardiology (Lipids and Risk)':
        tc=st.number_input('TC mg/dL',1.0,500.0,200.0); hdl=st.number_input('HDL mg/dL',1.0,200.0,45.0); tg=st.number_input('TG mg/dL',1.0,1000.0,150.0); sbp=st.number_input('SBP',50,250,120); dbp=st.number_input('DBP',30,150,80)
        ldl=sampson_ldl(tc,hdl,tg); st.metric('LDL-C', f'{ldl:.1f}'); st.metric('Non-HDL', f'{tc-hdl:.1f}'); save_trend(patient.get('patient_id','unknown'), dept, 'LDL-C', ldl, 'mg/dL'); summary=f'LDL-C {ldl:.1f} mg/dL, BP {sbp}/{dbp}'
    elif dept=='Gastroenterology (Hepatology)':
        bili=st.number_input('Bilirubin',0.1,50.0,1.0); inr=st.number_input('INR',0.1,15.0,1.1); cr=st.number_input('Creatinine',0.1,15.0,1.0); score=round(10*((0.957*math.log(max(1,cr)))+(0.378*math.log(max(1,bili)))+(1.12*math.log(max(1,inr))))+6.43,1)
        st.metric('MELD', score); save_trend(patient.get('patient_id','unknown'), dept, 'MELD', score, ''); summary=f'MELD {score}'
    elif dept=='Neurology (Emergency)':
        e=st.select_slider('Eye',[1,2,3,4],value=4); v=st.select_slider('Verbal',[1,2,3,4,5],value=5); m=st.select_slider('Motor',[1,2,3,4,5,6],value=6); gcs=e+v+m
        st.metric('GCS', f'{gcs}/15'); save_trend(patient.get('patient_id','unknown'), dept, 'GCS', gcs, '/15'); summary=f'GCS {gcs}/15'
    elif dept=='Nephrology (eGFR Suite)':
        scr=st.number_input('Creatinine mg/dL',0.1,15.0,1.0); age=st.number_input('Age',18,110,50); sex=st.selectbox('Sex',['Male','Female']); gfr=ckd_epi_2021(scr,age,sex=='Female')
        st.metric('eGFR', f'{gfr:.1f}'); save_trend(patient.get('patient_id','unknown'), dept, 'eGFR', gfr, 'mL/min/1.73mÂ²'); summary=f'eGFR {gfr:.1f}'
    elif dept=='Ophthalmology and Orthopedics':
        iop=st.number_input('Measured IOP',5,60,20); cct=st.number_input('CCT Î¼m',300,800,545); corrected=iop+((545-cct)/50*2.5)
        st.metric('Corrected IOP', f'{corrected:.1f}'); save_trend(patient.get('patient_id','unknown'), dept, 'Corrected IOP', corrected, 'mmHg'); summary=f'Corrected IOP {corrected:.1f} mmHg'
    elif dept=='OB/GYN':
        lmp=st.date_input('LMP', value=date.today()); cycle=st.number_input('Cycle length',21,45,28); edd=lmp+timedelta(days=280+(cycle-28)); ga=(date.today()-lmp).days/7
        st.metric('EDD', str(edd)); st.metric('GA', f'{ga:.1f} weeks'); save_trend(patient.get('patient_id','unknown'), dept, 'Gestational age', ga, 'weeks'); summary=f'GA {ga:.1f} weeks, EDD {edd}'
    elif dept=='ICU / Critical Care':
        hr=st.number_input('Heart rate',20,250,100); sbp=st.number_input('SBP',30,250,110); shock=hr/sbp; st.metric('Shock index', f'{shock:.2f}'); save_trend(patient.get('patient_id','unknown'), dept, 'Shock index', shock, ''); summary=f'Shock index {shock:.2f}'
    elif dept=='Emergency Medicine':
        bite=st.date_input('Date of bite', value=date.today()); category=st.selectbox('Bite category',['Category I','Category II','Category III']); wt=st.number_input('Weight kg for RIG',1.0,200.0,60.0)
        for d in [0,3,7,14,28]:
            due=bite+timedelta(days=d); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>ARV Day {d} <span class='{badge}'>{label}</span></h3><p>{due}</p></div>", unsafe_allow_html=True)
        if category=='Category III': st.metric('ERIG dose', f'{wt*40:.0f} IU'); save_trend(patient.get('patient_id','unknown'), dept, 'Rabies weight', wt, 'kg'); summary=f'Rabies category {category}, weight {wt} kg'
    elif dept=='Hematology':
        hb=st.number_input('Hemoglobin',1.0,25.0,12.0); mcv=st.number_input('MCV',40.0,130.0,85.0); mentzer=mcv/hb if hb else 0
        st.metric('Mentzer index', f'{mentzer:.2f}'); save_trend(patient.get('patient_id','unknown'), dept, 'Mentzer index', mentzer, ''); summary=f'Mentzer index {mentzer:.2f}'
    elif dept=='HIV / ART Follow-up':
        art=st.date_input('ART start', value=date.today()); milestones=[('4 weeks',28),('3 months',90),('6 months',180),('12 months',365)]
        for name,days in milestones:
            due=art+timedelta(days=days); badge,label=schedule_badge(due); st.markdown(f"<div class='card'><h3>{name} <span class='{badge}'>{label}</span></h3><p>{due}</p></div>", unsafe_allow_html=True)
        save_trend(patient.get('patient_id','unknown'), dept, 'ART start offset', 0, 'days'); summary=f'ART follow-up started {art}'
    save_record(patient.get('patient_id','unknown'), dept, summary, {'patient':patient,'dept':dept})
    return summary, cite

patient = patient_selector()
history_tables()
conversion_panel()
trend_view(patient.get('patient_id'))

if st.session_state.page=='home':
    st.markdown("<div class='appbar'><div class='appbrand'><div class='logo-orb'>IM</div><div class='brandtxt'><h2>IndiMed Pro 2026 Production</h2><p>Persistent patient database, multi-patient history, full department framework, and guideline-linked reporting</p></div></div><div class='quickpill'>Production-style CDS shell</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero'><h1>Persistent Clinical Workflow</h1><p>This build adds a SQLite-backed local database, cloud-ready architecture notes, history tables, trend storage, and guideline-linked report export across every department framework.</p></div>", unsafe_allow_html=True)
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
    interp('Local SQLite gives semi-persistent storage in local use, while production cloud persistence should move to an external database connection for reliability.', 'note')
else:
    dept=st.session_state.selected_dept
    top1,top2=st.columns([5,1])
    with top1: st.markdown(f"<div class='hero'><h1>{DEPT_ICONS.get(dept,'â€¢')} {dept}</h1><p>Full framework: persistence, trend logging, structured summary, and guideline-linked export</p></div>", unsafe_allow_html=True)
    with top2: st.button('Home', on_click=go_home)
    summary, cite = generic_department_framework(dept, patient)
    st.download_button('Export guideline-linked HTML report', html_report(patient, dept, summary, cite), f'IndiMed_{dept[:10]}_{date.today()}.html')
    interp('Clinical decision support only. This production-style build uses local SQLite persistence and can be migrated to a cloud database for durable multi-user storage.', 'alert-red')
