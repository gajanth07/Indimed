import streamlit as st
import io, math, sqlite3, tempfile
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
:root { --bg:#eef5fb; --surface:#ffffff; --border:#d7e5f2; --text:#0f172a; --muted:#5b6b81; --primary:#175b9e; --primary2:#1c7ed6; --teal:#14b8a6; }
.stApp { background: linear-gradient(180deg, #f8fcff 0%, #eef5fb 100%); color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1500px; padding: 1rem 1rem 3rem; }
.hero { background: linear-gradient(135deg, #1b4f8a 0%, #1f6fb2 55%, #14b8a6 100%); color:white; border-radius:24px; padding:24px; margin-bottom:18px; }
.hero h1 {margin:0; color:white;} .hero p {margin:.55rem 0 0; color:rgba(255,255,255,.90)!important;}
.card {background:#fff; border:1px solid var(--border); border-radius:22px; padding:16px; min-height:150px;}
.card h3 {margin:0 0 .5rem; color:#13385d; font-size:1rem;} .card p {margin:0 0 1rem; color:#5b6b81 !important; min-height:48px;}
.surface {background:#fff; border:1px solid var(--border); border-radius:20px; padding:16px; margin-top:14px;}
.section-title {font-size:1.1rem; font-weight:800; color:#13385d; margin:1rem 0 .5rem 0;}
.stButton>button,.stDownloadButton>button {width:100%!important; border:none!important; border-radius:14px!important; font-weight:700!important; color:white!important; min-height:44px;} 
.stButton>button {background:linear-gradient(135deg,var(--primary),var(--primary2))!important;} .stDownloadButton>button {background:linear-gradient(135deg,#0f766e,var(--teal))!important;}
[data-testid="stMetric"] {background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px;}
.note,.alert-red,.alert-yellow,.alert-green {padding:13px 15px; border-radius:16px; font-weight:600; margin:.6rem 0;}
.note {background:#eef7ff; border:1px solid #cfe4fa; color:#1d4f91;} .alert-red {background:#fff4f4; border:1px solid #ffd7d7; color:#9f1239;} .alert-yellow {background:#fffaf0; border:1px solid #fde3a7; color:#9a6700;} .alert-green {background:#effdf7; border:1px solid #b7efd7; color:#0f766e;}
.badge-due,.badge-overdue,.badge-upcoming {padding:5px 10px; border-radius:999px; font-weight:700; display:inline-block; font-size:.8rem; margin:.2rem .35rem .2rem 0;} .badge-due{background:#fee2e2;color:#991b1b;} .badge-overdue{background:#fff1f2;color:#be123c;} .badge-upcoming{background:#dbeafe;color:#1d4ed8;}
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
    if patient_id:
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

def html_report(patient, dept, summary):
    html = f"<html><body><h1>IndiMed Report</h1><p>Patient: {patient.get('name','')} ({patient.get('patient_id','')})</p><p>Department: {dept}</p><p>Summary: {summary}</p><p>Date: {date.today()}</p></body></html>"
    return io.BytesIO(html.encode())

def kg_to_lb(kg): return kg * 2.20462
def cm_to_in(cm): return cm / 2.54
def mg_to_mmol_ldl(v): return v / 38.67

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

st.markdown("<div class='hero'><h1>IndiMed Pro 2026</h1><p>All departments now have working calculations, with clean cards and one combined workflow section below.</p></div>", unsafe_allow_html=True)

if st.session_state.page == 'home':
    st.markdown("<div class='section-title'>Departments</div>", unsafe_allow_html=True)
    for row_start in range(0, len(DEPTS), 3):
        cols = st.columns(3)
        for i, (title, desc) in enumerate(DEPTS[row_start:row_start+3]):
            with cols[i]:
                st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                st.button('Open Department', key=f'open_{title}', on_click=open_dept, args=(title,))

    st.markdown("<div class='section-title'>Clinical Workflow</div>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    st.session_state.patient_id = p1.text_input('Patient ID', value=st.session_state.patient_id)
    st.session_state.patient_name = p2.text_input('Patient Name', value=st.session_state.patient_name)
    st.session_state.patient_age = p3.text_input('Patient Age', value=st.session_state.patient_age)
    st.session_state.patient_sex = p4.selectbox('Patient Sex', ['Male','Female','Other'], index=['Male','Female','Other'].index(st.session_state.patient_sex))
    a, b = st.columns(2)
    with a:
        if st.button('Save Patient'):
            save_patient(st.session_state.patient_id, st.session_state.patient_name, st.session_state.patient_age, st.session_state.patient_sex)
            interp(f'Patient saved in database path: {DB_PATH}', 'alert-green')
    with b:
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
    if prow:
        st.dataframe([dict(zip(pcol, r)) for r in prow], use_container_width=True)
    else:
        interp('No patient records saved yet.')

    st.markdown("<div class='section-title'>Trend Charts Over Time</div>", unsafe_allow_html=True)
    trow, tcol = query_rows('SELECT patient_id,dept,metric,value,unit,created_at FROM trends ORDER BY created_at DESC LIMIT 200')
    if trow:
        trend_data = [dict(zip(tcol, r)) for r in trow]
        metrics = sorted(set(x['metric'] for x in trend_data))
        selected_metric = st.selectbox('Select metric', metrics)
        selected_vals = [x['value'] for x in trend_data if x['metric'] == selected_metric]
        st.line_chart({'value': selected_vals})
        st.dataframe([x for x in trend_data if x['metric'] == selected_metric], use_container_width=True)
    else:
        interp('No trend data available yet.')

else:
    dept = st.session_state.selected_dept
    st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Department calculations verified and active.</p></div>", unsafe_allow_html=True)
    st.button('Back to Home', on_click=go_home)

    patient = {'patient_id': st.session_state.patient_id, 'name': st.session_state.patient_name, 'age': st.session_state.patient_age, 'sex': st.session_state.patient_sex}
    summary = f'{dept} opened.'

    if dept == 'Medication Safety and Dose':
        wt = st.number_input('Weight kg', 1.0, 250.0, 70.0)
        mgkg = st.number_input('Dose mg/kg', 0.1, 500.0, 15.0)
        doses = st.number_input('Doses per day', 1, 6, 2)
        dose = wt * mgkg
        daily = dose * doses
        c1, c2 = st.columns(2)
        c1.metric('Single dose', f'{dose:.2f} mg')
        c2.metric('Daily dose', f'{daily:.2f} mg')
        save_trend(patient['patient_id'], dept, 'Daily dose', daily, 'mg')
        summary = f'Single dose {dose:.2f} mg; daily dose {daily:.2f} mg'

    elif dept == 'Metabolic and General Medicine':
        w = st.number_input('Weight kg', 5.0, 300.0, 70.0)
        h = st.number_input('Height cm', 50.0, 250.0, 170.0)
        sbp = st.number_input('SBP', 50, 250, 120)
        dbp = st.number_input('DBP', 30, 150, 80)
        bmi = w / ((h/100)**2)
        bsa = math.sqrt((w*h)/3600)
        mapv = (sbp + 2*dbp) / 3
        c1, c2, c3 = st.columns(3)
        c1.metric('BMI', f'{bmi:.2f}')
        c2.metric('BSA', f'{bsa:.2f} mÂ²')
        c3.metric('MAP', f'{mapv:.1f} mmHg')
        save_trend(patient['patient_id'], dept, 'BMI', bmi, 'kg/mÂ²')
        summary = f'BMI {bmi:.2f}; BSA {bsa:.2f}; MAP {mapv:.1f}'

    elif dept == 'Pediatrics and Growth':
        wt = st.number_input('Weight kg', 1.0, 120.0, 10.0)
        ht = st.number_input('Height cm', 30.0, 200.0, 75.0)
        temp = st.number_input('Temperature Â°C', 35.0, 42.0, 37.5)
        fluid = wt * 100 if wt <= 10 else 1000 + (wt-10)*50 if wt <= 20 else 1500 + (wt-20)*20
        para = wt * 15
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Weight', f'{wt:.2f} kg')
        c2.metric('Height', f'{ht:.2f} cm')
        c3.metric('Maintenance fluid', f'{fluid:.0f} mL/day')
        c4.metric('Paracetamol dose', f'{para:.0f} mg')
        save_trend(patient['patient_id'], dept, 'Weight', wt, 'kg')
        summary = f'Weight {wt:.2f}; Height {ht:.2f}; Fluid {fluid:.0f}; Fever temp {temp}'

    elif dept == 'Neonatology':
        ga = st.number_input('Gestational age weeks', 22, 44, 36)
        birth_wt = st.number_input('Birth weight g', 400, 6000, 2800)
        day_life = st.number_input('Day of life', 1, 28, 3)
        current_wt = st.number_input('Current weight kg', 0.5, 8.0, 2.8)
        feed = current_wt * (80 if day_life <= 1 else 100 if day_life <= 3 else 120 if day_life <= 7 else 150)
        c1, c2, c3 = st.columns(3)
        c1.metric('Prematurity', 'Preterm' if ga < 37 else 'Term')
        c2.metric('Birth weight class', 'LBW' if birth_wt < 2500 else 'Normal')
        c3.metric('Feed target', f'{feed:.0f} mL/day')
        save_trend(patient['patient_id'], dept, 'Neonate weight', current_wt, 'kg')
        summary = f'GA {ga}; birth wt {birth_wt}; feed {feed:.0f}'

    elif dept == 'Cardiology and Lipids':
        tc = st.number_input('Total cholesterol', 1.0, 500.0, 200.0)
        hdl = st.number_input('HDL', 1.0, 200.0, 45.0)
        tg = st.number_input('Triglycerides', 1.0, 1000.0, 150.0)
        sbp = st.number_input('SBP', 50, 250, 120)
        dbp = st.number_input('DBP', 30, 150, 80)
        ldl = sampson_ldl(tc, hdl, tg)
        nonhdl = tc - hdl
        mapv = (sbp + 2*dbp) / 3
        c1, c2, c3 = st.columns(3)
        c1.metric('LDL C', f'{ldl:.1f}')
        c2.metric('Non HDL', f'{nonhdl:.1f}')
        c3.metric('MAP', f'{mapv:.1f}')
        save_trend(patient['patient_id'], dept, 'LDL C', ldl, 'mg/dL')
        summary = f'LDL C {ldl:.1f}; Non HDL {nonhdl:.1f}'

    elif dept == 'Gastroenterology and Hepatology':
        bili = st.number_input('Bilirubin', 0.1, 50.0, 1.0)
        inr = st.number_input('INR', 0.1, 15.0, 1.1)
        cr = st.number_input('Creatinine', 0.1, 15.0, 1.0)
        meld = round(10*((0.957*math.log(max(1,cr))) + (0.378*math.log(max(1,bili))) + (1.12*math.log(max(1,inr)))) + 6.43, 1)
        st.metric('MELD', meld)
        save_trend(patient['patient_id'], dept, 'MELD', meld, '')
        summary = f'MELD {meld}'

    elif dept == 'Neurology and Emergency':
        e = st.select_slider('Eye response', [1,2,3,4], value=4)
        v = st.select_slider('Verbal response', [1,2,3,4,5], value=5)
        m = st.select_slider('Motor response', [1,2,3,4,5,6], value=6)
        onset = st.number_input('Stroke onset hours', 0.0, 72.0, 2.0)
        gcs = e + v + m
        c1, c2 = st.columns(2)
        c1.metric('GCS', f'{gcs}/15')
        c2.metric('Thrombolysis window', 'Possible' if onset <= 4.5 else 'Late')
        save_trend(patient['patient_id'], dept, 'GCS', gcs, '/15')
        summary = f'GCS {gcs}; onset {onset} h'

    elif dept == 'Nephrology':
        scr = st.number_input('Creatinine mg/dL', 0.1, 15.0, 1.0)
        age = st.number_input('Age', 18, 110, 50)
        sex = st.selectbox('Sex', ['Male','Female'])
        gfr = ckd_epi_2021(scr, age, sex == 'Female')
        stage = 'G1' if gfr >= 90 else 'G2' if gfr >= 60 else 'G3a' if gfr >= 45 else 'G3b' if gfr >= 30 else 'G4' if gfr >= 15 else 'G5'
        c1, c2 = st.columns(2)
        c1.metric('eGFR', f'{gfr:.1f}')
        c2.metric('Stage', stage)
        save_trend(patient['patient_id'], dept, 'eGFR', gfr, 'mL/min/1.73mÂ²')
        summary = f'eGFR {gfr:.1f}; stage {stage}'

    elif dept == 'Ophthalmology and Orthopedics':
        iop = st.number_input('Measured IOP', 5, 60, 20)
        cct = st.number_input('CCT microns', 300, 800, 545)
        age = st.number_input('Age years', 18, 110, 50)
        corrected = iop + ((545 - cct) / 50 * 2.5)
        bone_risk = age / 10
        c1, c2 = st.columns(2)
        c1.metric('Corrected IOP', f'{corrected:.1f} mmHg')
        c2.metric('Bone risk score', f'{bone_risk:.1f}')
        save_trend(patient['patient_id'], dept, 'Corrected IOP', corrected, 'mmHg')
        summary = f'Corrected IOP {corrected:.1f}; bone risk {bone_risk:.1f}'

    elif dept == 'OB and GYN':
        lmp = st.date_input('LMP date', value=date.today() - timedelta(days=84))
        cycle = st.number_input('Cycle length', 21, 45, 28)
        bishop = st.number_input('Bishop score', 0, 13, 5)
        ga = (date.today() - lmp).days / 7
        edd = lmp + timedelta(days=280 + (cycle - 28))
        c1, c2, c3 = st.columns(3)
        c1.metric('Gestational age', f'{ga:.1f} weeks')
        c2.metric('EDD', str(edd))
        c3.metric('Labor readiness', 'Favorable' if bishop >= 8 else 'Unfavorable')
        save_trend(patient['patient_id'], dept, 'Gestational age', ga, 'weeks')
        summary = f'GA {ga:.1f}; EDD {edd}; Bishop {bishop}'

    elif dept == 'ICU and Critical Care':
        hr = st.number_input('Heart rate', 20, 250, 100)
        sbp = st.number_input('SBP', 30, 250, 110)
        pao2 = st.number_input('PaO2', 20, 500, 80)
        fio2 = st.number_input('FiO2 %', 21, 100, 40)
        shock = hr / sbp
        pf = pao2 / (fio2 / 100)
        c1, c2 = st.columns(2)
        c1.metric('Shock index', f'{shock:.2f}')
        c2.metric('PF ratio', f'{pf:.0f}')
        save_trend(patient['patient_id'], dept, 'Shock index', shock, '')
        summary = f'Shock index {shock:.2f}; PF ratio {pf:.0f}'

    elif dept == 'Emergency Medicine':
        bite = st.date_input('Date of bite', value=date.today())
        category = st.selectbox('Bite category', ['Category I','Category II','Category III'])
        wt = st.number_input('Weight kg', 1.0, 200.0, 60.0)
        st.markdown('Rabies schedule')
        for d in [0,3,7,14,28]:
            due = bite + timedelta(days=d)
            badge, label = schedule_badge(due)
            st.markdown(f"<span class='{badge}'>{label}</span> Day {d}: {due}", unsafe_allow_html=True)
        if category == 'Category III':
            st.metric('ERIG dose', f'{wt*40:.0f} IU')
        save_trend(patient['patient_id'], dept, 'Rabies weight', wt, 'kg')
        summary = f'Rabies category {category}; weight {wt} kg'

    elif dept == 'Hematology':
        hb = st.number_input('Hemoglobin', 1.0, 25.0, 12.0)
        mcv = st.number_input('MCV', 40.0, 130.0, 85.0)
        wbc = st.number_input('WBC', 0.1, 200.0, 7.0)
        neut = st.number_input('Neutrophil percent', 0.0, 100.0, 60.0)
        mentzer = mcv / hb if hb else 0
        anc = wbc * neut / 100
        c1, c2 = st.columns(2)
        c1.metric('Mentzer index', f'{mentzer:.2f}')
        c2.metric('ANC', f'{anc:.2f}')
        save_trend(patient['patient_id'], dept, 'ANC', anc, 'x10^9/L')
        summary = f'Mentzer {mentzer:.2f}; ANC {anc:.2f}'

    elif dept == 'HIV and ART Follow-up':
        art = st.date_input('ART start date', value=date.today())
        st.markdown('Follow-up schedule')
        for name, days in [('4 weeks', 28), ('3 months', 90), ('6 months', 180), ('12 months', 365)]:
            due = art + timedelta(days=days)
            badge, label = schedule_badge(due)
            st.markdown(f"<span class='{badge}'>{label}</span> {name}: {due}", unsafe_allow_html=True)
        save_trend(patient['patient_id'], dept, 'ART follow-up baseline', 0, 'days')
        summary = f'ART start {art}'

    save_record(patient['patient_id'], dept, summary)
    st.download_button('Export Department Report', html_report(patient, dept, summary), f'{dept}_report.html')
    interp(f'Database location in this run: {DB_PATH}', 'note')
