import streamlit as st
import io, math, sqlite3, tempfile, requests
from datetime import date, timedelta, datetime
from pathlib import Path
from urllib.parse import quote_plus

st.set_page_config(page_title='PRI Prototype', layout='wide')

def resolve_db_path():
    candidates = [Path('output/indimed_clinic.db'), Path('/tmp/indimed_clinic.db'), Path(tempfile.gettempdir()) / 'indimed_clinic.db']
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            t = sqlite3.connect(p); t.close(); return p
        except Exception:
            continue
    return Path('indimed_clinic.db')
DB_PATH = resolve_db_path()

@st.cache_resource
def get_conn(db_path_str):
    conn = sqlite3.connect(db_path_str, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS patients (patient_id TEXT PRIMARY KEY, name TEXT, age TEXT, sex TEXT, updated_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, summary TEXT, created_at TEXT)')
    conn.commit()
    return conn
conn = get_conn(str(DB_PATH))

st.markdown('''
<style>
:root { --bg:#f4f8fc; --surface:#ffffff; --surface2:#f8fbff; --border:#dbe7f3; --text:#102133; --muted:#5d7188; --primary:#1463b8; --primary2:#1e88e5; --teal:#0f9d8a; --gold:#d28b00; }
.stApp { background: linear-gradient(180deg, #f9fcff 0%, #eef5fb 100%); color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1350px; padding: .8rem .8rem 3rem; }
.hero { background: linear-gradient(135deg, #155b9a 0%, #1f7cc8 60%, #12a9a0 100%); color:white; border-radius:20px; padding:18px; margin-bottom:14px; }
.hero h1 {margin:0; font-size:1.35rem; color:white;} .hero p {margin:.4rem 0 0; color:rgba(255,255,255,.92)!important; font-size:.94rem;}
.ribbon {background:linear-gradient(135deg,#fff7e7,#fff); border:1px solid #f3d59a; color:#8a5b00; border-radius:16px; padding:12px 14px; margin-bottom:12px; font-weight:700;}
.section-title {font-size:1.05rem; font-weight:800; color:#13385d; margin:.8rem 0 .45rem 0;}
.dept-wrap {margin-bottom:10px;}
.dept-btn button {background:transparent!important; color:inherit!important; border:0!important; box-shadow:none!important; padding:0!important; min-height:unset!important;}
.dept-card {background:linear-gradient(180deg,#fff,#f9fbff); border:1px solid var(--border); border-radius:18px; padding:14px; min-height:112px; margin-bottom:2px;}
.dept-card.peds {background:linear-gradient(180deg,#fff8e8,#fff); border-color:#f1d18f;}
.dept-card.ai {background:linear-gradient(180deg,#eef8ff,#fff); border-color:#b9daf8;}
.dept-title {font-weight:800; color:#153a60; margin-bottom:.45rem; font-size:.98rem;}
.dept-desc {color:#5b6b81; font-size:.89rem;}
.surface {background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px; margin:12px 0;}
.explain {background:#f8fbff; border:1px solid #d6e6f8; border-radius:16px; padding:12px 14px; margin-top:10px;}
.stDownloadButton>button {width:100%!important; border:none!important; border-radius:12px!important; font-weight:700!important; color:white!important; min-height:42px; background:linear-gradient(135deg,#0d7c74,var(--teal))!important;}
[data-testid="stMetric"] {background:#fff; border:1px solid var(--border); border-radius:14px; padding:10px;}
.note,.alert-red,.alert-green,.alert-gold {padding:12px 14px; border-radius:14px; font-weight:600; margin:.5rem 0;}
.note {background:#eef7ff; border:1px solid #cfe4fa; color:#1d4f91;} .alert-red {background:#fff4f4; border:1px solid #ffd7d7; color:#9f1239;} .alert-green {background:#effdf7; border:1px solid #b7efd7; color:#0f766e;} .alert-gold {background:#fff8e8; border:1px solid #f4d08a; color:#8a5a00;}
.badge-due,.badge-overdue,.badge-upcoming {padding:5px 10px; border-radius:999px; font-weight:700; display:inline-block; font-size:.78rem; margin:.2rem .35rem .2rem 0;} .badge-due{background:#fee2e2;color:#991b1b;} .badge-overdue{background:#fff1f2;color:#be123c;} .badge-upcoming{background:#dbeafe;color:#1d4ed8;}
@media (max-width: 640px){ .main .block-container{padding:.55rem .55rem 3rem;} .hero h1{font-size:1.18rem;} }
</style>
''', unsafe_allow_html=True)

DEPTS = [
    ('Pediatrics and Growth','Expanded pediatric toolbox for daily child-care support.','peds'),
    ('AI Clinical Search','Fast evidence search for symptoms, PubMed, and trusted links.','ai'),
    ('Medication Safety and Dose','Dose support, interaction checker, renal adjustment.',''),
    ('Metabolic and General Medicine','BMI, BSA, MAP, waist-height ratio.',''),
    ('Neonatology','Feeds, corrected age, weight loss, jaundice.',''),
    ('Cardiology and Lipids','LDL, non-HDL, pressure tools.',''),
    ('Gastroenterology and Hepatology','MELD and MELD-Na support.',''),
    ('Neurology and Emergency','GCS and GCS-P support.',''),
    ('Nephrology','eGFR and CKD stage support.',''),
    ('Ophthalmology and Orthopedics','Corrected IOP and bone risk.',''),
    ('OB and GYN','Pregnancy dating and labor readiness.',''),
    ('ICU and Critical Care','Shock index and PF ratio.',''),
    ('Emergency Medicine','qSOFA and rabies schedule.',''),
    ('Hematology','Mentzer and ANC support.',''),
    ('HIV and ART Follow-up','Visit milestones and ART follow-up.','')
]
INTERACTION_RULES = {
    frozenset(['warfarin','metronidazole']): ('Major','High bleeding risk; monitor INR closely or avoid combination.'),
    frozenset(['warfarin','azithromycin']): ('Moderate','Possible INR increase; closer monitoring may be needed.'),
    frozenset(['warfarin','ibuprofen']): ('Major','Bleeding risk rises with NSAID use.'),
    frozenset(['amlodipine','simvastatin']): ('Moderate','Simvastatin exposure can rise; consider lower statin dose.'),
    frozenset(['aspirin','clopidogrel']): ('Moderate','Bleeding risk increases, though combination may be intended in selected patients.'),
    frozenset(['ceftriaxone','calcium']): ('Major','Avoid mixing in neonates because of precipitation risk.'),
    frozenset(['paracetamol','ibuprofen']): ('Mild','Often co-used with dosing and interval attention.'),
    frozenset(['amoxicillin','paracetamol']): ('No major known interaction','Common pair in routine care; still review dosing and patient context.')
}
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, Rotavirus-3 if applicable, PCV-3')]

if 'page' not in st.session_state: st.session_state.page='home'
if 'selected_dept' not in st.session_state: st.session_state.selected_dept='Pediatrics and Growth'
if 'patient_id' not in st.session_state: st.session_state.patient_id=''
if 'patient_name' not in st.session_state: st.session_state.patient_name=''
if 'patient_age' not in st.session_state: st.session_state.patient_age=''
if 'patient_sex' not in st.session_state: st.session_state.patient_sex='Male'

def save_patient(pid,name,age,sex):
    if pid:
        conn.execute('INSERT OR REPLACE INTO patients(patient_id,name,age,sex,updated_at) VALUES(?,?,?,?,?)',(pid,name,age,sex,str(datetime.now())))
        conn.commit()

def save_record(pid,dept,summary):
    conn.execute('INSERT INTO records(patient_id,dept,summary,created_at) VALUES(?,?,?,?)',(pid or 'unknown',dept,summary,str(datetime.now())))
    conn.commit()

def schedule_badge(d):
    if d < date.today(): return 'badge-overdue','Overdue'
    if d == date.today(): return 'badge-due','Due today'
    return 'badge-upcoming','Upcoming'

def render_vaccine_schedule(dob):
    for label,days,items in VACCINE_SCHEDULE:
        due=dob+timedelta(days=days); badge,status=schedule_badge(due)
        st.markdown(f"<div class='surface'><b>{label}</b> <span class='{badge}'>{status}</span><br>Date: {due}<br>{items}</div>", unsafe_allow_html=True)

def explain_block(title, text, search_term=None):
    st.markdown(f"<div class='explain'><b>{title}</b><br>{text}</div>", unsafe_allow_html=True)
    if search_term:
        q=quote_plus(search_term)
        st.markdown(f"[Open PubMed search](https://pubmed.ncbi.nlm.nih.gov/?term={q})")

def interaction_checker(d1,d2):
    a=d1.strip().lower(); b=d2.strip().lower()
    if not a or not b: return 'Enter both medicines','Please type both medicine names.'
    if a==b: return 'Duplicate entry','Both names are the same medicine.'
    if frozenset([a,b]) in INTERACTION_RULES: return INTERACTION_RULES[frozenset([a,b])]
    return 'No mapped interaction found','This offline checker has no stored rule for this exact pair yet.'

def pubmed_search(query,max_results=5):
    try:
        es=requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax={max_results}&term={quote_plus(query)}',timeout=15)
        ids=es.json().get('esearchresult',{}).get('idlist',[])
        if not ids: return []
        sm=requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={",".join(ids)}',timeout=15)
        data=sm.json().get('result',{})
        return [{'title':data.get(i,{}).get('title','No title'),'source':data.get(i,{}).get('source',''),'pubdate':data.get(i,{}).get('pubdate',''),'url':f'https://pubmed.ncbi.nlm.nih.gov/{i}/'} for i in ids]
    except Exception:
        return []

def sampson_ldl(tc,hdl,tg):
    non_hdl=tc-hdl
    return tc/0.948-hdl/0.971-(tg/8.56+(tg*non_hdl)/2140-(tg*tg)/16100)-9.44

def ckd_epi_2021(scr,age,female):
    k=0.7 if female else 0.9; a=-0.241 if female else -0.302
    val=142*(min(scr/k,1)**a)*(max(scr/k,1)**-1.2)*(0.9938**age)
    return val*1.012 if female else val

def html_report(patient,dept,summary):
    html=f"<html><body><h1>PRI Prototype Report</h1><p>Patient: {patient.get('name','')} ({patient.get('patient_id','')})</p><p>Department: {dept}</p><p>Summary: {summary}</p><p>Date: {date.today()}</p></body></html>"
    return io.BytesIO(html.encode())

def go_home(): st.session_state.page='home'
def open_dept(name): st.session_state.selected_dept=name; st.session_state.page='dept'

st.markdown("<div class='hero'><h1>PRI Prototype</h1><p>Single-tap department access with no separate open button under each card.</p></div>", unsafe_allow_html=True)
st.markdown("<div class='ribbon'>Fast access: tap the department card once to open it.</div>", unsafe_allow_html=True)

if st.session_state.page=='home':
    st.markdown("<div class='section-title'>Fast access departments</div>", unsafe_allow_html=True)
    for title, desc, cls in DEPTS:
        st.markdown("<div class='dept-wrap'>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='dept-btn'>", unsafe_allow_html=True)
            if st.button(title, key=f'open_{title}', use_container_width=True):
                open_dept(title)
            st.markdown(f"<div class='dept-card {cls}'><div class='dept-title'>{title}</div><div class='dept-desc'>{desc}</div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    p1,p2,p3,p4=st.columns(4)
    st.session_state.patient_id=p1.text_input('Patient ID', value=st.session_state.patient_id)
    st.session_state.patient_name=p2.text_input('Patient Name', value=st.session_state.patient_name)
    st.session_state.patient_age=p3.text_input('Patient Age', value=st.session_state.patient_age)
    st.session_state.patient_sex=p4.selectbox('Patient Sex',['Male','Female','Other'], index=['Male','Female','Other'].index(st.session_state.patient_sex))
    if st.button('Save Patient'):
        save_patient(st.session_state.patient_id, st.session_state.patient_name, st.session_state.patient_age, st.session_state.patient_sex)
        st.markdown("<div class='alert-green'>Patient saved.</div>", unsafe_allow_html=True)
else:
    dept=st.session_state.selected_dept
    patient={'patient_id':st.session_state.patient_id,'name':st.session_state.patient_name,'age':st.session_state.patient_age,'sex':st.session_state.patient_sex}
    if st.button('Back to Home'): go_home()
    st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Compact tools with instant explanation and fast research links.</p></div>", unsafe_allow_html=True)
    summary=f'{dept} opened.'

    if dept=='Medication Safety and Dose':
        tabs=st.tabs(['Dose Support','Drug Interaction','Renal Adjustment'])
        with tabs[0]:
            wt=st.number_input('Weight kg',1.0,250.0,70.0); mgkg=st.number_input('Dose mg/kg',0.1,500.0,15.0); freq=st.number_input('Doses/day',1,6,2)
            single=wt*mgkg; daily=single*freq
            c1,c2=st.columns(2); c1.metric('Single dose', f'{single:.2f} mg'); c2.metric('Daily dose', f'{daily:.2f} mg')
            explain_block('Explanation', 'This uses weight-based dosing and then multiplies by the number of doses per day. Check drug-specific maximum limits and organ function before prescribing.', 'weight based dosing pediatrics review')
            summary=f'Dose {single:.2f} mg'
        with tabs[1]:
            d1=st.text_input('Medicine 1'); d2=st.text_input('Medicine 2')
            if st.button('Check interaction now'):
                sev,note=interaction_checker(d1,d2)
                box='alert-red' if sev in ['Major','Moderate'] else 'note'
                st.markdown(f"<div class='{box}'><b>{sev}</b><br>{note}</div>", unsafe_allow_html=True)
                explain_block('Interaction note', 'This is a local rule-based checker for common medicine pairs in the app. For uncommon pairs, use literature search and a full drug reference.', f'{d1} {d2} drug interaction')
                summary=f'Interaction checked: {sev}'
        with tabs[2]:
            crcl=st.number_input('Creatinine clearance',1.0,200.0,80.0)
            factor=1 if crcl>=60 else 0.75 if crcl>=30 else 0.5
            st.metric('Dose factor', factor)
            explain_block('Explanation', 'This is a quick renal-adjustment reminder factor, not a drug-specific renal nomogram.', 'renal dose adjustment drug review')
    elif dept=='Pediatrics and Growth':
        tabs=st.tabs(['Growth','Fever','Fluids','Vaccine'])
        with tabs[0]:
            age_m=st.number_input('Age months',0,216,24); wt=st.number_input('Weight kg',1.0,120.0,12.0); ht=st.number_input('Height cm',30.0,220.0,85.0)
            bmi=wt/((ht/100)**2); expected=(age_m/2)+4 if age_m<=12 else (age_m/12)*2+8
            c1,c2=st.columns(2); c1.metric('BMI', f'{bmi:.2f}'); c2.metric('Expected wt', f'{expected:.1f} kg')
            explain_block('Explanation', 'BMI is a quick body-size estimate, and the expected-weight formula is a rough bedside age-based estimate. Use growth charts for proper interpretation.', 'pediatric growth chart bmi review')
        with tabs[1]:
            wt2=st.number_input('Weight kg',1.0,120.0,12.0, key='pfx'); st.metric('Paracetamol dose', f'{wt2*15:.0f} mg'); st.metric('Ibuprofen dose', f'{wt2*10:.0f} mg')
            explain_block('Explanation', 'These are quick weight-based fever medicine estimates. Recheck dose interval and maximum daily dose before use.', 'pediatric paracetamol ibuprofen dosing review')
        with tabs[2]:
            wt3=st.number_input('Weight kg',1.0,120.0,12.0, key='pfl'); daily=wt3*100 if wt3<=10 else 1000+(wt3-10)*50 if wt3<=20 else 1500+(wt3-20)*20
            st.metric('Maintenance fluid', f'{daily:.0f} mL/day'); st.metric('Hourly rate', f'{daily/24:.1f} mL/hr')
            explain_block('Explanation', 'This uses a quick Holliday-Segar style maintenance fluid estimate. Real fluid plans can differ in shock, renal disease, or ongoing losses.', 'Holliday Segar maintenance fluid children review')
        with tabs[3]:
            dob=st.date_input('DOB', value=date.today()-timedelta(days=450)); render_vaccine_schedule(dob)
            explain_block('Explanation', 'The schedule is generated automatically from date of birth. Match it with your current local schedule before using it in care.', 'India national immunization schedule child')
            summary='Pediatrics calculations active'
    elif dept=='AI Clinical Search':
        symptom=st.text_input('Enter symptoms or question'); age_group=st.selectbox('Age group',['General','Pediatric','Neonate','Adult'])
        if st.button('Analyze research') and symptom:
            st.markdown("<div class='alert-red'>This is a clinical-search assist module, not a diagnosis engine.</div>", unsafe_allow_html=True)
            res=pubmed_search(f'{symptom} {age_group} guideline review',5)
            if res:
                for r in res: st.markdown(f"- [{r['title']}]({r['url']}) ({r['source']}, {r['pubdate']})")
            explain_block('How to use this', 'Use this result list to read evidence quickly and support clinician review. Search quality depends on symptom wording.', symptom + ' guideline review')
            summary='AI search used'
    else:
        st.markdown("<div class='surface'>Department loaded. This section keeps the same refined layout and can be expanded further.</div>", unsafe_allow_html=True)

    save_record(patient['patient_id'], dept, summary)
    st.download_button('Export Department Report', html_report(patient, dept, summary), f'{dept}_report.html')
