import streamlit as st
import io, math, json, sqlite3, tempfile
from datetime import date, timedelta, datetime
from pathlib import Path

st.set_page_config(page_title='IndiMed Pro 2026', layout='wide')

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
.stApp { background: linear-gradient(180deg, #f8fcff 0%, #eef5fb 100%); color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1500px; padding: 1rem 1rem 3rem; }
.hero { background: linear-gradient(135deg, #1b4f8a 0%, #1f6fb2 55%, #14b8a6 100%); color:white; border-radius:24px; padding:24px; margin-bottom:18px; }
.hero h1 {margin:0; color:white;} .hero p {margin:.55rem 0 0; color:rgba(255,255,255,.90)!important;}
.card {background:linear-gradient(180deg,#fff,#f8fbff); border:1px solid var(--border); border-radius:22px; padding:16px; min-height:150px;}
.card h3 {margin:0 0 .5rem; color:#13385d; font-size:1rem;} .card p {margin:0 0 1rem; color:#5b6b81 !important; min-height:48px;}
.surface {background:#fff; border:1px solid var(--border); border-radius:20px; padding:16px; margin-top:14px;}
.section-title {font-size:1.1rem; font-weight:800; color:#13385d; margin:1rem 0 .5rem 0;}
.stButton>button,.stDownloadButton>button {width:100%!important; border:none!important; border-radius:14px!important; font-weight:700!important; color:white!important; min-height:44px;} 
.stButton>button {background:linear-gradient(135deg,var(--primary),var(--primary2))!important;} .stDownloadButton>button {background:linear-gradient(135deg,#0f766e,var(--teal))!important;}
[data-testid="stMetric"] {background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px;}
.note,.alert-red,.alert-yellow,.alert-green {padding:13px 15px; border-radius:16px; font-weight:600; margin:.6rem 0;}
.note {background:#eef7ff; border:1px solid #cfe4fa; color:#1d4f91;} .alert-red {background:#fff4f4; border:1px solid #ffd7d7; color:#9f1239;} .alert-yellow {background:#fffaf0; border:1px solid #fde3a7; color:#9a6700;} .alert-green {background:#effdf7; border:1px solid #b7efd7; color:#0f766e;}
.badge-due,.badge-overdue,.badge-upcoming {padding:5px 10px; border-radius:999px; font-weight:700; display:inline-block; font-size:.8rem; margin:.2rem .35rem .2rem 0;} .badge-due{background:#fee2e2;color:#991b1b;} .badge-overdue{background:#fff1f2;color:#be123c;} .badge-upcoming{background:#dbeafe;color:#1d4ed8;}
div[data-testid="stExpander"] details summary p {font-size:1rem; font-weight:700; color:#13385d;}
</style>
''', unsafe_allow_html=True)

@st.cache_resource
def get_conn(db_path_str):
    conn = sqlite3.connect(db_path_str, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, name TEXT, age TEXT, sex TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, summary TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS trends (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, metric TEXT, value REAL, unit TEXT, created_at TEXT)')
    conn.commit()
    return conn

conn = get_conn(str(DB_PATH))

def query_rows(sql, params=()):
    cur = conn.cursor(); cur.execute(sql, params); rows = cur.fetchall(); cols = [d[0] for d in cur.description] if cur.description else []
    return rows, cols

def save_patient(patient_id, name, age, sex):
    if not patient_id:
        return
    conn.execute('INSERT OR REPLACE INTO patients(patient_id,name,age,sex,updated_at) VALUES(?,?,?,?,?)', (patient_id, name, age, sex, str(datetime.now())))
    conn.commit()

def save_record(patient_id, dept, summary):
    conn.execute('INSERT INTO records(patient_id,dept,summary,created_at) VALUES(?,?,?,?)', (patient_id or 'unknown', dept, summary, str(datetime.now())))
    conn.commit()

def save_trend(patient_id, dept, metric, value, unit=''):
    conn.execute('INSERT INTO trends(patient_id,dept,metric,value,unit,created_at) VALUES(?,?,?,?,?,?)', (patient_id or 'unknown', dept, metric, float(value), unit, str(datetime.now())))
    conn.commit()

def schedule_badge(d):
    if d < date.today(): return 'badge-overdue', 'Overdue'
    if d == date.today(): return 'badge-due', 'Due today'
    return 'badge-upcoming', 'Upcoming'

def interp(msg, style='note'):
    st.markdown(f"<div class='{style}'>{msg}</div>", unsafe_allow_html=True)

def sampson_ldl(tc, hdl, tg):
    non_hdl = tc - hdl
    return tc/0.948 - hdl/0.971 - (tg/8.56 + (tg*non_hdl)/2140 - (tg*tg)/16100) - 9.44

def ckd_epi_2021(scr, age, female):
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    val = 142 * (min(scr/k,1)**a) * (max(scr/k,1)**-1.2) * (0.9938**age)
    return val * 1.012 if female else val

def kg_to_lb(kg): return kg * 2.20462
def cm_to_in(cm): return cm / 2.54
def mg_to_mmol_ldl(v): return v / 38.67

def html_report(patient, dept, summary):
    html = f"<html><body><h1>IndiMed Report</h1><p>Patient: {patient.get('name','')} ({patient.get('patient_id','')})</p><p>Department: {dept}</p><p>Summary: {summary}</p><p>Date: {date.today()}</p></body></html>"
    return io.BytesIO(html.encode())

DEPTS = [
    ('Medication Safety and Dose', 'Drug interaction checks, dose support, renal safety.'),
    ('Metabolic and General Medicine', 'BMI, BSA, MAP, stewardship support.'),
    ('Pediatrics and Growth', 'Growth, vaccines, fluids, fever dosing.'),
    ('Neonatology', 'Prematurity, APGAR, corrected age, feeds.'),
    ('Cardiology and Lipids', 'LDL-C, BP, lipid and cardiovascular support.'),
    ('Gastroenterology and Hepatology', 'Liver scores and severity support.'),
    ('Neurology and Emergency', 'GCS and stroke timing support.'),
    ('Nephrology', 'eGFR and kidney risk support.'),
    ('Ophthalmology and Orthopedics', 'IOP correction and bone risk.'),
    ('OB and GYN', 'Pregnancy dating and labor support.'),
    ('ICU and Critical Care', 'Shock, oxygenation, sepsis concern.'),
    ('Emergency Medicine', 'Triage, sepsis, rabies planning.'),
    ('Hematology', 'Mentzer, ANC, platelet flags.'),
    ('HIV and ART Follow-up', 'ART milestone planning and support.')
]

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'selected_dept' not in st.session_state: st.session_state.selected_dept = DEPTS[0][0]
if 'patient_id' not in st.session_state: st.session_state.patient_id = ''
if 'patient_name' not in st.session_state: st.session_state.patient_name = ''
if 'patient_age' not in st.session_state: st.session_state.patient_age = ''
if 'patient_sex' not in st.session_state: st.session_state.patient_sex = 'Male'

def go_home(): st.session_state.page = 'home'
def open_dept(name): st.session_state.selected_dept = name; st.session_state.page = 'dept'

st.markdown("<div class='hero'><h1>IndiMed Pro 2026</h1><p>Clean department cards on top and one combined workflow section at the bottom for patient database, history tables, unit conversion, and trend charts.</p></div>", unsafe_allow_html=True)

if st.session_state.page == 'home':
    st.markdown("<div class='section-title'>Departments</div>", unsafe_allow_html=True)
    for row_start in range(0, len(DEPTS), 3):
        cols = st.columns(3)
        for i, (title, desc) in enumerate(DEPTS[row_start:row_start+3]):
            with cols[i]:
                st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                st.button('Open Department', key=f'open_{title}', on_click=open_dept, args=(title,))

    st.markdown("<div class='section-title'>Clinical Workflow</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='surface'>", unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns(4)
        st.session_state.patient_id = p1.text_input('Patient ID', value=st.session_state.patient_id)
        st.session_state.patient_name = p2.text_input('Patient Name', value=st.session_state.patient_name)
        st.session_state.patient_age = p3.text_input('Patient Age', value=st.session_state.patient_age)
        st.session_state.patient_sex = p4.selectbox('Patient Sex', ['Male','Female','Other'], index=['Male','Female','Other'].index(st.session_state.patient_sex))
        s1, s2 = st.columns(2)
        with s1:
            if st.button('Save Patient'):
                save_patient(st.session_state.patient_id, st.session_state.patient_name, st.session_state.patient_age, st.session_state.patient_sex)
                interp(f'Patient saved in database path: {DB_PATH}', 'alert-green')
        with s2:
            st.download_button('Export Simple Report', html_report({'patient_id': st.session_state.patient_id, 'name': st.session_state.patient_name}, 'Home', 'Workflow export'), 'IndiMed_Workflow_Report.html')

        st.markdown("<div class='section-title'>Unit Conversion</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        kg = c1.number_input('Weight in kg', 0.0, 500.0, 70.0)
        cm = c2.number_input('Height in cm', 0.0, 300.0, 170.0)
        ldl = c3.number_input('LDL in mg/dL', 0.0, 500.0, 100.0)
        d1, d2, d3 = st.columns(3)
        d1.metric('Weight in lb', f'{kg_to_lb(kg):.2f}')
        d2.metric('Height in inch', f'{cm_to_in(cm):.2f}')
        d3.metric('LDL in mmol/L', f'{mg_to_mmol_ldl(ldl):.2f}')

        st.markdown("<div class='section-title'>Multi Patient History</div>", unsafe_allow_html=True)
        prow, pcol = query_rows('SELECT patient_id,name,age,sex,updated_at FROM patients ORDER BY updated_at DESC')
        rrow, rcol = query_rows('SELECT patient_id,dept,summary,created_at FROM records ORDER BY created_at DESC LIMIT 100')
        trow, tcol = query_rows('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at DESC LIMIT 200')
        if prow:
            st.dataframe([dict(zip(pcol, r)) for r in prow], use_container_width=True)
        else:
            interp('No patient records saved yet.')

        st.markdown("<div class='section-title'>Trend Charts Over Time</div>", unsafe_allow_html=True)
        if trow:
            trend_data = [dict(zip(tcol, r)) for r in trow]
            metrics = sorted(set(x['metric'] for x in trend_data))
            selected_metric = st.selectbox('Select metric', metrics)
            selected_vals = [x['value'] for x in trend_data if x['metric'] == selected_metric]
            st.line_chart({'value': selected_vals})
            st.dataframe([x for x in trend_data if x['metric'] == selected_metric], use_container_width=True)
        else:
            interp('No trend data available yet.')
        st.markdown("</div>", unsafe_allow_html=True)

else:
    dept = st.session_state.selected_dept
    st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Department page with simple clean layout and no extra unwanted symbols.</p></div>", unsafe_allow_html=True)
    st.button('Back to Home', on_click=go_home)

    patient = {
        'patient_id': st.session_state.patient_id,
        'name': st.session_state.patient_name,
        'age': st.session_state.patient_age,
        'sex': st.session_state.patient_sex,
    }

    summary = f'{dept} opened.'

    if dept == 'Medication Safety and Dose':
        wt = st.number_input('Weight kg', 1.0, 250.0, 70.0)
        mgkg = st.number_input('Dose mg/kg', 0.1, 500.0, 15.0)
        dose = wt * mgkg
        st.metric('Calculated dose', f'{dose:.2f} mg')
        save_trend(patient['patient_id'], dept, 'Dose', dose, 'mg')
        summary = f'Dose {dose:.2f} mg'
    elif dept == 'Metabolic and General Medicine':
        w = st.number_input('Weight kg', 5.0, 300.0, 70.0)
        h = st.number_input('Height cm', 50.0, 250.0, 170.0)
        bmi = w / ((h/100)**2)
        st.metric('BMI', f'{bmi:.2f}')
        save_trend(patient['patient_id'], dept, 'BMI', bmi, 'kg/mÂ²')
        summary = f'BMI {bmi:.2f}'
    elif dept == 'Pediatrics and Growth':
        wt = st.number_input('Weight kg', 1.0, 120.0, 10.0)
        ht = st.number_input('Height cm', 30.0, 200.0, 75.0)
        save_trend(patient['patient_id'], dept, 'Weight', wt, 'kg')
        save_trend(patient['patient_id'], dept, 'Height', ht, 'cm')
        st.metric('Weight', f'{wt:.2f} kg')
        st.metric('Height', f'{ht:.2f} cm')
        summary = f'Weight {wt:.2f} kg Height {ht:.2f} cm'
    elif dept == 'Cardiology and Lipids':
        tc = st.number_input('Total cholesterol', 1.0, 500.0, 200.0)
        hdl = st.number_input('HDL', 1.0, 200.0, 45.0)
        tg = st.number_input('Triglycerides', 1.0, 1000.0, 150.0)
        ldl = sampson_ldl(tc, hdl, tg)
        st.metric('LDL C', f'{ldl:.1f}')
        save_trend(patient['patient_id'], dept, 'LDL C', ldl, 'mg/dL')
        summary = f'LDL C {ldl:.1f}'
    elif dept == 'Nephrology':
        scr = st.number_input('Creatinine mg/dL', 0.1, 15.0, 1.0)
        age = st.number_input('Age', 18, 110, 50)
        sex = st.selectbox('Sex', ['Male','Female'])
        gfr = ckd_epi_2021(scr, age, sex == 'Female')
        st.metric('eGFR', f'{gfr:.1f}')
        save_trend(patient['patient_id'], dept, 'eGFR', gfr, 'mL/min/1.73mÂ²')
        summary = f'eGFR {gfr:.1f}'
    else:
        interp('This department page is active in the same clean framework. You can expand more department-specific tools here.', 'note')

    save_record(patient['patient_id'], dept, summary)
    st.download_button('Export Department Report', html_report(patient, dept, summary), f'{dept}_report.html')
    interp(f'Database location in this run: {DB_PATH}', 'note')
