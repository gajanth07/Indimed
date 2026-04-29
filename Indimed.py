import streamlit as st
import io, math, sqlite3, tempfile, requests, xml.etree.ElementTree as ET
from datetime import date, timedelta, datetime
from pathlib import Path
from urllib.parse import quote_plus

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

@st.cache_resource
def get_conn(db_path_str):
    conn = sqlite3.connect(db_path_str, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, name TEXT, age TEXT, sex TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, summary TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS trends (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, metric TEXT, value REAL, unit TEXT, created_at TEXT)')
    conn.commit()
    return conn
conn = get_conn(str(DB_PATH))

st.markdown('''
<style>
:root { --bg:#eef5fb; --surface:#ffffff; --border:#d7e5f2; --text:#0f172a; --muted:#5b6b81; --primary:#175b9e; --primary2:#1c7ed6; --teal:#14b8a6; --gold:#f59e0b; }
.stApp { background: linear-gradient(180deg, #f8fcff 0%, #eef5fb 100%); color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1500px; padding: 1rem 1rem 3rem; }
.hero { background: linear-gradient(135deg, #1b4f8a 0%, #1f6fb2 55%, #14b8a6 100%); color:white; border-radius:24px; padding:24px; margin-bottom:18px; }
.peds-hero { background: linear-gradient(135deg, #f59e0b 0%, #f97316 45%, #1c7ed6 100%); color:white; border-radius:24px; padding:22px; margin:12px 0 18px; }
.hero h1,.peds-hero h1 {margin:0; color:white;} .hero p,.peds-hero p {margin:.55rem 0 0; color:rgba(255,255,255,.92)!important;}
.card,.card-peds {background:#fff; border:1px solid var(--border); border-radius:22px; padding:16px; min-height:170px;}
.card-peds {background:linear-gradient(180deg,#fff8e8,#ffffff); border-color:#f6d28b; box-shadow:0 6px 18px rgba(245,158,11,.08);} .card h3,.card-peds h3 {margin:0 0 .5rem;} .card p,.card-peds p {min-height:54px; color:#5b6b81 !important;}
.section-title {font-size:1.1rem; font-weight:800; color:#13385d; margin:1rem 0 .5rem 0;}
.surface {background:#fff; border:1px solid var(--border); border-radius:20px; padding:16px; margin:14px 0;}
.stButton>button,.stDownloadButton>button {width:100%!important; border:none!important; border-radius:14px!important; font-weight:700!important; color:white!important; min-height:44px;}
.stButton>button {background:linear-gradient(135deg,var(--primary),var(--primary2))!important;} .stDownloadButton>button {background:linear-gradient(135deg,#0f766e,var(--teal))!important;}
[data-testid="stMetric"] {background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px;}
.note,.alert-red,.alert-green,.alert-gold {padding:13px 15px; border-radius:16px; font-weight:600; margin:.6rem 0;}
.note {background:#eef7ff; border:1px solid #cfe4fa; color:#1d4f91;} .alert-red {background:#fff4f4; border:1px solid #ffd7d7; color:#9f1239;} .alert-green {background:#effdf7; border:1px solid #b7efd7; color:#0f766e;} .alert-gold {background:#fff8e8; border:1px solid #f4d08a; color:#8a5a00;}
.badge-due,.badge-overdue,.badge-upcoming {padding:5px 10px; border-radius:999px; font-weight:700; display:inline-block; font-size:.8rem; margin:.2rem .35rem .2rem 0;} .badge-due{background:#fee2e2;color:#991b1b;} .badge-overdue{background:#fff1f2;color:#be123c;} .badge-upcoming{background:#dbeafe;color:#1d4ed8;}
</style>
''', unsafe_allow_html=True)

DEPTS = [
    ('Pediatrics and Growth', 'Expanded pediatric dashboard with growth, dosing, fluids, vaccines, nutrition, emergency and daily care tools.'),
    ('AI Clinical Search', 'Evidence-search assistant for symptoms, PubMed papers, Indian guideline links, and curated trusted sources; not a diagnosis module.'),
    ('Medication Safety and Dose', 'Drug interaction checks, dose support, renal safety.'),
    ('Metabolic and General Medicine', 'BMI, BSA, MAP, stewardship support.'),
    ('Neonatology', 'Prematurity, corrected age, feeds, weight support.'),
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

VACCINE_SCHEDULE = [
    ('Birth', 0, 'BCG, OPV-0, Hepatitis B birth dose'), ('6 weeks', 42, 'DTwP/DTaP-1, IPV-1, Hib-1, Hepatitis B-2, Rotavirus-1, PCV-1'),
    ('10 weeks', 70, 'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'), ('14 weeks', 98, 'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, Rotavirus-3 if applicable, PCV-3'),
    ('6 months', 180, 'Influenza may begin depending on plan'), ('9 months', 270, 'MMR-1, Typhoid conjugate vaccine'), ('12 months', 365, 'Hepatitis A-1, Varicella-1'),
    ('15 months', 455, 'MMR-2, Varicella-2, PCV booster'), ('16-24 months', 540, 'DPT booster-1, OPV booster'), ('5 years', 1825, 'DPT/DTaP booster'), ('10 years', 3650, 'Td/Tdap'), ('16 years', 5840, 'Td booster')
]

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'selected_dept' not in st.session_state: st.session_state.selected_dept = DEPTS[0][0]
if 'patient_id' not in st.session_state: st.session_state.patient_id = ''
if 'patient_name' not in st.session_state: st.session_state.patient_name = ''
if 'patient_age' not in st.session_state: st.session_state.patient_age = ''
if 'patient_sex' not in st.session_state: st.session_state.patient_sex = 'Male'

def save_patient(pid, name, age, sex):
    if pid:
        conn.execute('INSERT OR REPLACE INTO patients(patient_id,name,age,sex,updated_at) VALUES(?,?,?,?,?)', (pid, name, age, sex, str(datetime.now())))
        conn.commit()

def save_record(pid, dept, summary):
    conn.execute('INSERT INTO records(patient_id,dept,summary,created_at) VALUES(?,?,?,?)', (pid or 'unknown', dept, summary, str(datetime.now())))
    conn.commit()

def save_trend(pid, dept, metric, value, unit=''):
    conn.execute('INSERT INTO trends(patient_id,dept,metric,value,unit,created_at) VALUES(?,?,?,?,?,?)', (pid or 'unknown', dept, metric, float(value), unit, str(datetime.now())))
    conn.commit()

def schedule_badge(d):
    if d < date.today(): return 'badge-overdue', 'Overdue'
    if d == date.today(): return 'badge-due', 'Due today'
    return 'badge-upcoming', 'Upcoming'

def render_vaccine_schedule(dob):
    for label, days, items in VACCINE_SCHEDULE:
        due = dob + timedelta(days=days)
        badge, status = schedule_badge(due)
        st.markdown(f"<div class='card'><h3>{label} <span class='{badge}'>{status}</span></h3><p>Date: {due}<br>{items}</p></div>", unsafe_allow_html=True)

def interp(msg, style='note'):
    st.markdown(f"<div class='{style}'>{msg}</div>", unsafe_allow_html=True)

def html_report(patient, dept, summary):
    html = f"<html><body><h1>IndiMed Report</h1><p>Patient: {patient.get('name','')} ({patient.get('patient_id','')})</p><p>Department: {dept}</p><p>Summary: {summary}</p><p>Date: {date.today()}</p></body></html>"
    return io.BytesIO(html.encode())

def sampson_ldl(tc, hdl, tg):
    non_hdl = tc - hdl
    return tc/0.948 - hdl/0.971 - (tg/8.56 + (tg*non_hdl)/2140 - (tg*tg)/16100) - 9.44

def ckd_epi_2021(scr, age, female):
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    val = 142 * (min(scr/k,1)**a) * (max(scr/k,1)**-1.2) * (0.9938**age)
    return val * 1.012 if female else val

def pubmed_search(query, max_results=5):
    try:
        q = quote_plus(query)
        esearch = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax={max_results}&term={q}', timeout=20)
        ids = esearch.json().get('esearchresult', {}).get('idlist', [])
        if not ids:
            return []
        id_str = ','.join(ids)
        esummary = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={id_str}', timeout=20)
        data = esummary.json().get('result', {})
        out = []
        for pid in ids:
            rec = data.get(pid, {})
            out.append({'pmid': pid, 'title': rec.get('title', 'No title'), 'pubdate': rec.get('pubdate', ''), 'source': rec.get('source', ''), 'url': f'https://pubmed.ncbi.nlm.nih.gov/{pid}/'})
        return out
    except Exception:
        return []

def go_home(): st.session_state.page = 'home'
def open_dept(name): st.session_state.selected_dept = name; st.session_state.page = 'dept'

st.markdown("<div class='hero'><h1>IndiMed Pro 2026</h1><p>Pediatrics remains the highlighted department, and the app now includes more submodules across departments plus an evidence-search assistant for symptom-guided literature lookup.</p></div>", unsafe_allow_html=True)

if st.session_state.page == 'home':
    st.markdown("<div class='peds-hero'><h1>Pediatrics and AI Search</h1><p>Pediatrics is the main feature, and an adjacent AI Clinical Search module can search PubMed and link to Indian guideline sources. This search is for evidence support, not final diagnosis.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Departments</div>", unsafe_allow_html=True)
    for row_start in range(0, len(DEPTS), 3):
        cols = st.columns(3)
        for i, (title, desc) in enumerate(DEPTS[row_start:row_start+3]):
            with cols[i]:
                if title in ['Pediatrics and Growth', 'AI Clinical Search']:
                    st.markdown(f"<div class='card-peds'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                st.button('Open Department', key=f'open_{title}', on_click=open_dept, args=(title,))
    p1, p2, p3, p4 = st.columns(4)
    st.session_state.patient_id = p1.text_input('Patient ID', value=st.session_state.patient_id)
    st.session_state.patient_name = p2.text_input('Patient Name', value=st.session_state.patient_name)
    st.session_state.patient_age = p3.text_input('Patient Age', value=st.session_state.patient_age)
    st.session_state.patient_sex = p4.selectbox('Patient Sex', ['Male','Female','Other'], index=['Male','Female','Other'].index(st.session_state.patient_sex))
    if st.button('Save Patient'):
        save_patient(st.session_state.patient_id, st.session_state.patient_name, st.session_state.patient_age, st.session_state.patient_sex)
        interp(f'Patient saved in database path: {DB_PATH}', 'alert-green')
else:
    dept = st.session_state.selected_dept
    patient = {'patient_id': st.session_state.patient_id, 'name': st.session_state.patient_name, 'age': st.session_state.patient_age, 'sex': st.session_state.patient_sex}
    st.button('Back to Home', on_click=go_home)
    summary = f'{dept} opened.'

    if dept == 'Pediatrics and Growth':
        st.markdown("<div class='peds-hero'><h1>Pediatrics and Growth</h1><p>Expanded pediatric dashboard with practical submodules for daily child-care support.</p></div>", unsafe_allow_html=True)
        tabs = st.tabs(['Growth', 'Fever', 'Fluids', 'Vaccine Schedule', 'Nutrition', 'Dehydration', 'Emergency', 'Respiratory', 'Drug Dosing', 'Vitals by Age', 'Daily Care'])
        with tabs[0]:
            age_months = st.number_input('Age in months', 0, 216, 24)
            wt = st.number_input('Weight kg', 1.0, 120.0, 12.0)
            ht = st.number_input('Height cm', 30.0, 220.0, 85.0)
            hc = st.number_input('Head circumference cm', 20.0, 70.0, 47.0)
            bmi = wt / ((ht/100)**2)
            expected_wt = (age_months/2)+4 if age_months <= 12 else (age_months/12)*2+8
            c1,c2,c3,c4 = st.columns(4)
            c1.metric('BMI', f'{bmi:.2f}')
            c2.metric('Head circumference', f'{hc:.1f} cm')
            c3.metric('Expected wt', f'{expected_wt:.1f} kg')
            c4.metric('Difference', f'{wt-expected_wt:.1f} kg')
        with tabs[1]:
            wt2 = st.number_input('Weight kg', 1.0, 120.0, 12.0, key='pf1')
            temp = st.number_input('Temperature Â°C', 35.0, 42.0, 38.2)
            st.metric('Paracetamol dose', f'{wt2*15:.0f} mg')
            st.metric('Ibuprofen dose', f'{wt2*10:.0f} mg')
            st.metric('Fever status', 'Fever' if temp >= 38 else 'No fever')
        with tabs[2]:
            wt3 = st.number_input('Weight kg', 1.0, 120.0, 12.0, key='pf2')
            daily = wt3*100 if wt3 <= 10 else 1000+(wt3-10)*50 if wt3 <= 20 else 1500+(wt3-20)*20
            st.metric('Maintenance fluid', f'{daily:.0f} mL/day')
            st.metric('Hourly fluid', f'{daily/24:.1f} mL/hr')
        with tabs[3]:
            dob = st.date_input('Date of birth', value=date.today()-timedelta(days=450), key='pvax')
            render_vaccine_schedule(dob)
        with tabs[4]:
            wt4 = st.number_input('Weight kg', 1.0, 120.0, 12.0, key='pn1')
            age_y = st.number_input('Age years', 0.0, 18.0, 2.0)
            cal = wt4*100 if age_y < 1 else wt4*90 if age_y < 3 else wt4*80 if age_y < 6 else wt4*70
            protein = wt4*1.2
            st.metric('Calories/day', f'{cal:.0f} kcal')
            st.metric('Protein/day', f'{protein:.1f} g')
        with tabs[5]:
            wt5 = st.number_input('Weight kg', 1.0, 120.0, 12.0, key='pd1')
            degree = st.selectbox('Dehydration', ['None', 'Some', 'Severe'])
            deficit = wt5*50 if degree == 'Some' else wt5*100 if degree == 'Severe' else 0
            ors = wt5*75 if degree == 'Some' else 0
            st.metric('Fluid deficit', f'{deficit:.0f} mL')
            st.metric('ORS over 4 hr', f'{ors:.0f} mL')
        with tabs[6]:
            wt6 = st.number_input('Weight kg', 1.0, 120.0, 16.0, key='pe1')
            glucose = st.number_input('Glucose mg/dL', 10.0, 500.0, 80.0)
            st.metric('Midazolam dose', f'{wt6*0.2:.2f} mg')
            st.metric('D10 bolus', f'{wt6*2:.1f} mL')
            st.metric('Hypoglycemia flag', 'Low' if glucose < 70 else 'Normal')
        with tabs[7]:
            age_y2 = st.number_input('Age years', 0.0, 18.0, 4.0, key='pr1')
            rr = st.number_input('Respiratory rate', 5, 80, 28)
            normal_hi = 40 if age_y2 < 1 else 34 if age_y2 < 3 else 30 if age_y2 < 6 else 24
            st.metric('Fast breathing', 'Yes' if rr > normal_hi else 'No')
            st.metric('Upper normal RR', f'{normal_hi}/min')
        with tabs[8]:
            wt7 = st.number_input('Weight kg', 1.0, 120.0, 15.0, key='pdd1')
            amox = wt7*40
            ond = wt7*0.15
            salbutamol = wt7*0.15
            c1,c2,c3 = st.columns(3)
            c1.metric('Amoxicillin/day', f'{amox:.0f} mg/day')
            c2.metric('Ondansetron dose', f'{ond:.2f} mg')
            c3.metric('Salbutamol oral est.', f'{salbutamol:.2f} mg')
            
        with tabs[9]:
            age_y3 = st.number_input('Age years', 0.0, 18.0, 3.0, key='pvitals')
            sbp_low = 70 + (2*age_y3) if age_y3 <= 10 else 90
            rr_range = '30-40/min' if age_y3 < 1 else '24-34/min' if age_y3 < 3 else '20-30/min' if age_y3 < 6 else '18-25/min'
            c1,c2 = st.columns(2)
            c1.metric('Low SBP alert threshold', f'{sbp_low:.0f} mmHg')
            c2.metric('Expected RR range', rr_range)
        with tabs[10]:
            wt8 = st.number_input('Weight kg', 1.0, 120.0, 14.0, key='pdailycare')
            milk = wt8 * 100
            urine = wt8 * 1
            c1,c2 = st.columns(2)
            c1.metric('Approx fluid need', f'{milk:.0f} mL/day')
            c2.metric('Minimum urine output', f'{urine:.1f} mL/kg/hr')

            summary = 'Expanded pediatric toolbox with additional submodules active'

    elif dept == 'AI Clinical Search':
        st.markdown("<div class='peds-hero'><h1>AI Clinical Search</h1><p>This is an evidence-search assist module, not a diagnosis system. It can search PubMed and link you to Indian guideline sources for symptom-based reading.</p></div>", unsafe_allow_html=True)
        symptom = st.text_input('Enter symptoms or doubt')
        age_group = st.selectbox('Age group', ['General', 'Pediatric', 'Neonate', 'Adult'])
        if st.button('Analyze Research') and symptom:
            interp('This is a clinical-search assist module, not diagnosis. Final clinical judgment must be made by a clinician.', 'alert-red')
            q = f'{symptom} {age_group} guideline OR review'
            results = pubmed_search(q, max_results=5)
            if results:
                st.markdown('### PubMed results')
                for r in results:
                    st.markdown(f"- [{r['title']}]({r['url']}) ({r['source']}, {r['pubdate']})")
            else:
                interp('No PubMed result returned right now. Try simpler terms or a broader symptom phrase.', 'note')
            st.markdown('### Indian guideline links')
            st.markdown('- [ICMR Guidelines](https://www.icmr.gov.in/guidelines)')
            st.markdown('- [National Immunization Schedule PDF](https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/report/National_%20Immunization_Schedule.pdf)')
            st.markdown('- [WHO IMCI](https://www.who.int/teams/maternal-newborn-child-adolescent-health-and-ageing/child-health/integrated-management-of-childhood-illness)')
            st.markdown('- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)')
            st.markdown('- [NCBI E-utilities API docs](https://www.ncbi.nlm.nih.gov/books/NBK25497/)')
            summary = f'Clinical search used for: {symptom}'

    elif dept == 'Medication Safety and Dose':
        tabs = st.tabs(['Dose Support', 'Renal Adjustment'])
        with tabs[0]:
            wt = st.number_input('Weight kg', 1.0, 250.0, 70.0)
            mgkg = st.number_input('Dose mg/kg', 0.1, 500.0, 15.0)
            st.metric('Dose', f'{wt*mgkg:.2f} mg')
        with tabs[1]:
            crcl = st.number_input('Creatinine clearance', 1.0, 200.0, 80.0)
            factor = 1 if crcl >= 60 else 0.75 if crcl >= 30 else 0.5
            st.metric('Adjustment factor', factor)
            summary = 'Medication submodules active'

    elif dept == 'Metabolic and General Medicine':
        tabs = st.tabs(['BMI', 'BSA', 'MAP', 'Waist Ratio'])
        with tabs[0]:
            w = st.number_input('Weight kg', 5.0, 300.0, 70.0)
            h = st.number_input('Height cm', 50.0, 250.0, 170.0)
            st.metric('BMI', f'{w/((h/100)**2):.2f}')
        with tabs[1]:
            w2 = st.number_input('Weight kg', 5.0, 300.0, 70.0, key='mbsa1')
            h2 = st.number_input('Height cm', 50.0, 250.0, 170.0, key='mbsa2')
            st.metric('BSA', f'{math.sqrt((w2*h2)/3600):.2f} mÂ²')
        with tabs[2]:
            sbp = st.number_input('SBP', 50, 250, 120)
            dbp = st.number_input('DBP', 30, 150, 80)
            st.metric('MAP', f'{(sbp+2*dbp)/3:.1f}')
        with tabs[3]:
            waist = st.number_input('Waist cm', 20.0, 250.0, 85.0)
            height = st.number_input('Height cm', 50.0, 250.0, 170.0, key='whrh')
            st.metric('Waist/height', f'{waist/height:.2f}')
            summary = 'Metabolic submodules active'

    elif dept == 'Neonatology':
        tabs = st.tabs(['Feeds', 'Corrected Age', 'Weight Loss', 'Jaundice', 'Daily Fluids'])
        with tabs[0]:
            day = st.number_input('Day of life', 1, 28, 3)
            wt = st.number_input('Weight kg', 0.5, 8.0, 2.8)
            feed = wt * (80 if day <= 1 else 100 if day <= 3 else 120 if day <= 7 else 150)
            st.metric('Feed target', f'{feed:.0f} mL/day')
        with tabs[1]:
            ga = st.number_input('GA at birth weeks', 22, 44, 34)
            chrono = st.number_input('Chronological age weeks', 0, 52, 4)
            st.metric('Corrected age', max(0, chrono - (40-ga)))
        with tabs[2]:
            bw = st.number_input('Birth weight g', 400, 6000, 2800)
            cw = st.number_input('Current weight g', 400, 6000, 2550)
            st.metric('Weight loss', f'{((bw-cw)/bw)*100:.1f}%')
        with tabs[3]:
            bili = st.number_input('Bilirubin', 0.1, 40.0, 10.0)
            ageh = st.number_input('Age in hours', 1, 336, 48)
            st.metric('Jaundice support', 'Watch closely' if bili > 12 and ageh < 72 else 'Routine follow-up')
        with tabs[4]:
            wt2 = st.number_input('Weight kg', 0.5, 8.0, 2.8, key='neo2')
            st.metric('Daily fluids', f'{wt2*150:.0f} mL/day')
            summary = 'Neonatology submodules active'

    elif dept == 'Cardiology and Lipids':
        tabs = st.tabs(['LDL', 'Non HDL', 'Pressure'])
        with tabs[0]:
            tc = st.number_input('Total cholesterol', 1.0, 500.0, 200.0)
            hdl = st.number_input('HDL', 1.0, 200.0, 45.0)
            tg = st.number_input('Triglycerides', 1.0, 1000.0, 150.0)
            st.metric('LDL C', f'{sampson_ldl(tc,hdl,tg):.1f}')
        with tabs[1]:
            tc2 = st.number_input('Total cholesterol', 1.0, 500.0, 200.0, key='cnh1')
            hdl2 = st.number_input('HDL', 1.0, 200.0, 45.0, key='cnh2')
            st.metric('Non HDL', f'{tc2-hdl2:.1f}')
        with tabs[2]:
            sbp = st.number_input('SBP', 50, 250, 120, key='cp1')
            dbp = st.number_input('DBP', 30, 150, 80, key='cp2')
            st.metric('MAP', f'{(sbp+2*dbp)/3:.1f}')
            summary = 'Cardiology submodules active'

    elif dept == 'Gastroenterology and Hepatology':
        tabs = st.tabs(['MELD', 'MELD Na'])
        with tabs[0]:
            bili = st.number_input('Bilirubin', 0.1, 50.0, 1.0)
            inr = st.number_input('INR', 0.1, 15.0, 1.1)
            cr = st.number_input('Creatinine', 0.1, 15.0, 1.0)
            meld = round(10*((0.957*math.log(max(1,cr))) + (0.378*math.log(max(1,bili))) + (1.12*math.log(max(1,inr)))) + 6.43, 1)
            st.metric('MELD', meld)
        with tabs[1]:
            meld2 = st.number_input('MELD value', 1.0, 60.0, 12.0)
            na = st.number_input('Sodium', 100, 160, 137)
            meld_na = round(meld2 + 1.32*(137-max(125,min(137,na))) - (0.033*meld2*(137-max(125,min(137,na)))), 1)
            st.metric('MELD Na', meld_na)
            summary = 'Hepatology submodules active'

    elif dept == 'Neurology and Emergency':
        tabs = st.tabs(['GCS', 'GCS P'])
        with tabs[0]:
            e = st.select_slider('Eye', [1,2,3,4], value=4)
            v = st.select_slider('Verbal', [1,2,3,4,5], value=5)
            m = st.select_slider('Motor', [1,2,3,4,5,6], value=6)
            st.metric('GCS', e+v+m)
        with tabs[1]:
            gcs = st.number_input('GCS', 3, 15, 15)
            pupils = st.selectbox('Pupils', ['Both reactive', 'One unreactive', 'Both unreactive'])
            penalty = 0 if pupils == 'Both reactive' else 1 if pupils == 'One unreactive' else 2
            st.metric('GCS P', gcs-penalty)
            summary = 'Neurology submodules active'

    elif dept == 'Nephrology':
        tabs = st.tabs(['eGFR', 'CKD Stage'])
        with tabs[0]:
            scr = st.number_input('Creatinine mg/dL', 0.1, 15.0, 1.0)
            age = st.number_input('Age', 18, 110, 50)
            sex = st.selectbox('Sex', ['Male','Female'])
            gfr = ckd_epi_2021(scr, age, sex == 'Female')
            st.metric('eGFR', f'{gfr:.1f}')
        with tabs[1]:
            eg = st.number_input('eGFR value', 1.0, 150.0, 75.0)
            stage = 'G1' if eg >= 90 else 'G2' if eg >= 60 else 'G3a' if eg >= 45 else 'G3b' if eg >= 30 else 'G4' if eg >= 15 else 'G5'
            st.metric('CKD stage', stage)
            summary = 'Nephrology submodules active'

    elif dept == 'Ophthalmology and Orthopedics':
        tabs = st.tabs(['Corrected IOP', 'Bone Risk'])
        with tabs[0]:
            iop = st.number_input('Measured IOP', 5, 60, 20)
            cct = st.number_input('CCT microns', 300, 800, 545)
            st.metric('Corrected IOP', f'{iop + ((545-cct)/50*2.5):.1f}')
        with tabs[1]:
            age = st.number_input('Age', 18, 110, 50)
            fracture = st.checkbox('Fragility fracture')
            st.metric('Bone risk score', f'{(age/10)+(2 if fracture else 0):.1f}')
            summary = 'Ophthalmology/orthopedics submodules active'

    elif dept == 'OB and GYN':
        tabs = st.tabs(['Dating', 'Labor'])
        with tabs[0]:
            lmp = st.date_input('LMP date', value=date.today()-timedelta(days=84))
            cycle = st.number_input('Cycle length', 21, 45, 28)
            ga = (date.today()-lmp).days/7
            edd = lmp + timedelta(days=280 + (cycle-28))
            st.metric('Gestational age', f'{ga:.1f} weeks')
            st.metric('EDD', str(edd))
        with tabs[1]:
            bishop = st.number_input('Bishop score', 0, 13, 5)
            st.metric('Labor readiness', 'Favorable' if bishop >= 8 else 'Unfavorable')
            summary = 'OB/GYN submodules active'

    elif dept == 'ICU and Critical Care':
        tabs = st.tabs(['Shock Index', 'PF Ratio'])
        with tabs[0]:
            hr = st.number_input('Heart rate', 20, 250, 100)
            sbp = st.number_input('SBP', 30, 250, 110)
            st.metric('Shock index', f'{hr/sbp:.2f}')
        with tabs[1]:
            pao2 = st.number_input('PaO2', 20, 500, 80)
            fio2 = st.number_input('FiO2 %', 21, 100, 40)
            st.metric('PF ratio', f'{pao2/(fio2/100):.0f}')
            summary = 'ICU submodules active'

    elif dept == 'Emergency Medicine':
        tabs = st.tabs(['qSOFA', 'Rabies'])
        with tabs[0]:
            rr = st.number_input('Respiratory rate', 4, 60, 18)
            sbp = st.number_input('SBP', 30, 250, 120)
            ment = st.checkbox('Altered mental status')
            qsofa = int(rr >= 22) + int(sbp <= 100) + int(ment)
            st.metric('qSOFA', qsofa)
        with tabs[1]:
            bite = st.date_input('Date of bite', value=date.today())
            wt = st.number_input('Weight kg', 1.0, 200.0, 60.0)
            for d in [0,3,7,14,28]:
                due = bite + timedelta(days=d)
                badge, status = schedule_badge(due)
                st.markdown(f"<span class='{badge}'>{status}</span> Day {d}: {due}", unsafe_allow_html=True)
            st.metric('ERIG dose', f'{wt*40:.0f} IU')
            summary = 'Emergency submodules active'

    elif dept == 'Hematology':
        tabs = st.tabs(['Mentzer', 'ANC'])
        with tabs[0]:
            hb = st.number_input('Hemoglobin', 1.0, 25.0, 12.0)
            mcv = st.number_input('MCV', 40.0, 130.0, 85.0)
            st.metric('Mentzer index', f'{mcv/hb:.2f}')
        with tabs[1]:
            wbc = st.number_input('WBC', 0.1, 200.0, 7.0)
            neut = st.number_input('Neutrophil percent', 0.0, 100.0, 60.0)
            st.metric('ANC', f'{wbc*neut/100:.2f}')
            summary = 'Hematology submodules active'

    elif dept == 'HIV and ART Follow-up':
        tabs = st.tabs(['Next Visit', 'Milestones'])
        with tabs[0]:
            art = st.date_input('ART start date', value=date.today())
            st.metric('4-week follow-up', str(art + timedelta(days=28)))
        with tabs[1]:
            art2 = st.date_input('ART start date', value=date.today(), key='hiv2')
            for label, days in [('3 months',90),('6 months',180),('12 months',365)]:
                st.write(label, art2 + timedelta(days=days))
            summary = 'HIV follow-up submodules active'

    save_record(patient['patient_id'], dept, summary)
    st.download_button('Export Department Report', html_report(patient, dept, summary), f'{dept}_report.html')
    interp(f'Database location in this run: {DB_PATH}', 'note')
