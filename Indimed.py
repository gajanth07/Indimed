import streamlit as st
import io, math, sqlite3, tempfile, requests
from datetime import date, timedelta, datetime
from pathlib import Path
from urllib.parse import quote_plus

st.set_page_config(page_title='IndiMed Pro 2026', layout='wide')

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
    conn.execute('CREATE TABLE IF NOT EXISTS trends (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, dept TEXT, metric TEXT, value REAL, unit TEXT, created_at TEXT)')
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
.dept-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px;}
.dept-card {background:linear-gradient(180deg,#fff,#f9fbff); border:1px solid var(--border); border-radius:18px; padding:14px; min-height:128px;}
.dept-card.peds {background:linear-gradient(180deg,#fff8e8,#fff); border-color:#f1d18f;}
.dept-card.ai {background:linear-gradient(180deg,#eef8ff,#fff); border-color:#b9daf8;}
.dept-title {font-weight:800; color:#153a60; margin-bottom:.45rem; font-size:.96rem;}
.dept-desc {color:#5b6b81; font-size:.88rem; min-height:46px; margin-bottom:.7rem;}
.surface {background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px; margin:12px 0;}
.explain {background:#f8fbff; border:1px solid #d6e6f8; border-radius:16px; padding:12px 14px; margin-top:10px;}
.stButton>button,.stDownloadButton>button {width:100%!important; border:none!important; border-radius:12px!important; font-weight:700!important; color:white!important; min-height:42px;}
.stButton>button {background:linear-gradient(135deg,var(--primary),var(--primary2))!important;} .stDownloadButton>button {background:linear-gradient(135deg,#0d7c74,var(--teal))!important;}
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
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, Rotavirus-3 if applicable, PCV-3'),('6 months',180,'Influenza may begin depending on plan'),('9 months',270,'MMR-1, Typhoid conjugate vaccine'),('12 months',365,'Hepatitis A-1, Varicella-1'),('15 months',455,'MMR-2, Varicella-2, PCV booster'),('16-24 months',540,'DPT booster-1, OPV booster'),('5 years',1825,'DPT/DTaP booster'),('10 years',3650,'Td/Tdap'),('16 years',5840,'Td booster')]

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
    if not a or not b:
        return 'Enter both medicines','Please type both medicine names.'
    if a==b:
        return 'Duplicate entry','Both names are the same medicine.'
    if frozenset([a,b]) in INTERACTION_RULES:
        return INTERACTION_RULES[frozenset([a,b])]
    suggestions=sorted({x for pair in INTERACTION_RULES for x in pair if a in x or b in x})
    tail = (' Known examples in this app: ' + ', '.join(suggestions[:6])) if suggestions else ''
    return 'No mapped interaction found','This offline checker has no stored rule for this exact pair yet.' + tail

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
    html=f"<html><body><h1>IndiMed Report</h1><p>Patient: {patient.get('name','')} ({patient.get('patient_id','')})</p><p>Department: {dept}</p><p>Summary: {summary}</p><p>Date: {date.today()}</p></body></html>"
    return io.BytesIO(html.encode())

def go_home(): st.session_state.page='home'
def open_dept(name): st.session_state.selected_dept=name; st.session_state.page='dept'

st.markdown("<div class='hero'><h1>IndiMed Pro 2026</h1><p>Refined for faster mobile access: priority departments first, compact cards, better visual hierarchy, and explanation panels after calculations.</p></div>", unsafe_allow_html=True)
st.markdown("<div class='ribbon'>Quick access: the priority modules are Pediatrics, AI Clinical Search, and Medication Safety so you can reach them with fewer taps.</div>", unsafe_allow_html=True)

if st.session_state.page=='home':
    st.markdown("<div class='section-title'>Fast access departments</div>", unsafe_allow_html=True)
    cards=''.join([f"<div class='dept-card {cls}'><div class='dept-title'>{title}</div><div class='dept-desc'>{desc}</div></div>" for title,desc,cls in DEPTS])
    st.markdown(f"<div class='dept-grid'>{cards}</div>", unsafe_allow_html=True)
    for i in range(0,len(DEPTS),3):
        cols=st.columns(3)
        for j,(title,_,_) in enumerate(DEPTS[i:i+3]):
            cols[j].button(f'Open {title}', key=f'open_{title}', on_click=open_dept, args=(title,))
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
    st.button('Back to Home', on_click=go_home)
    st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Compact tools with instant explanation and fast research links.</p></div>", unsafe_allow_html=True)
    summary=f'{dept} opened.'

    if dept=='Medication Safety and Dose':
        tabs=st.tabs(['Dose Support','Drug Interaction','Renal Adjustment'])
        with tabs[0]:
            wt=st.number_input('Weight kg',1.0,250.0,70.0)
            mgkg=st.number_input('Dose mg/kg',0.1,500.0,15.0)
            freq=st.number_input('Doses/day',1,6,2)
            single=wt*mgkg; daily=single*freq
            c1,c2=st.columns(2); c1.metric('Single dose', f'{single:.2f} mg'); c2.metric('Daily dose', f'{daily:.2f} mg')
            explain_block('Explanation', f'This uses weight-based dosing: single dose = weight Ã— mg/kg, and daily dose = single dose Ã— doses per day. Verify maximum daily limits and renal/hepatic status before prescribing.', 'weight based dosing pediatrics review')
            summary=f'Dose {single:.2f} mg'
        with tabs[1]:
            d1=st.text_input('Medicine 1')
            d2=st.text_input('Medicine 2')
            if st.button('Check interaction now'):
                sev,note=interaction_checker(d1,d2)
                box='alert-red' if sev in ['Major','Moderate'] else 'note'
                st.markdown(f"<div class='{box}'><b>{sev}</b><br>{note}</div>", unsafe_allow_html=True)
                explain_block('Interaction note', 'This checker is local and rule-based, so it only knows the medicine pairs stored in the app. For uncommon pairs, use the linked literature search and a full drug reference.', f'{d1} {d2} drug interaction')
                summary=f'Interaction checked: {sev}'
        with tabs[2]:
            crcl=st.number_input('Creatinine clearance',1.0,200.0,80.0)
            factor=1 if crcl>=60 else 0.75 if crcl>=30 else 0.5
            st.metric('Dose factor', factor)
            explain_block('Explanation', 'This is a simple dose-adjustment factor to remind you that reduced renal function often requires a lower maintenance dose or longer interval. It is a quick aid, not a drug-specific renal nomogram.', 'renal dose adjustment drug review')
    elif dept=='Pediatrics and Growth':
        tabs=st.tabs(['Growth','Fever','Fluids','Vaccine','Nutrition','Dehydration','Emergency'])
        with tabs[0]:
            age_m=st.number_input('Age months',0,216,24)
            wt=st.number_input('Weight kg',1.0,120.0,12.0)
            ht=st.number_input('Height cm',30.0,220.0,85.0)
            bmi=wt/((ht/100)**2); expected=(age_m/2)+4 if age_m<=12 else (age_m/12)*2+8
            c1,c2=st.columns(2); c1.metric('BMI', f'{bmi:.2f}'); c2.metric('Expected wt', f'{expected:.1f} kg')
            explain_block('Explanation', 'BMI gives a quick body-size estimate, while the expected-weight formula is a rough bedside age-based estimate. Both are screening aids and should be interpreted with growth charts, feeding history, and illness severity.', 'pediatric growth chart bmi review')
        with tabs[1]:
            wt2=st.number_input('Weight kg',1.0,120.0,12.0, key='pfx')
            temp=st.number_input('Temperature',35.0,42.0,38.4)
            st.metric('Paracetamol dose', f'{wt2*15:.0f} mg'); st.metric('Ibuprofen dose', f'{wt2*10:.0f} mg')
            explain_block('Explanation', 'This section estimates common antipyretic doses from body weight. Recheck interval, daily maximum, dehydration status, and age-specific restrictions before use.', 'pediatric paracetamol ibuprofen dosing review')
        with tabs[2]:
            wt3=st.number_input('Weight kg',1.0,120.0,12.0, key='pfl')
            daily=wt3*100 if wt3<=10 else 1000+(wt3-10)*50 if wt3<=20 else 1500+(wt3-20)*20
            st.metric('Maintenance fluid', f'{daily:.0f} mL/day'); st.metric('Hourly rate', f'{daily/24:.1f} mL/hr')
            explain_block('Explanation', 'This uses the Holliday-Segar maintenance fluid approach for quick bedside estimation. Ongoing losses, shock, renal disease, and cardiac disease can make real fluid plans very different.', 'Holliday Segar maintenance fluid children review')
        with tabs[3]:
            dob=st.date_input('DOB', value=date.today()-timedelta(days=450))
            render_vaccine_schedule(dob)
            explain_block('Explanation', 'The schedule is generated from date of birth so every milestone gets a due date automatically. Match it against your national and local schedule before acting.', 'India national immunization schedule child')
        with tabs[4]:
            wt4=st.number_input('Weight kg',1.0,120.0,12.0, key='pfn')
            age_y=st.number_input('Age years',0.0,18.0,2.0)
            cal=wt4*100 if age_y<1 else wt4*90 if age_y<3 else wt4*80 if age_y<6 else wt4*70
            st.metric('Calories/day', f'{cal:.0f} kcal'); st.metric('Protein/day', f'{wt4*1.2:.1f} g')
            explain_block('Explanation', 'These are quick daily nutrition estimates based mainly on age and weight. Nutrition planning still depends on disease state, prematurity, malnutrition, and feeding route.', 'pediatric calorie requirement review')
        with tabs[5]:
            wt5=st.number_input('Weight kg',1.0,120.0,12.0, key='pfd')
            deg=st.selectbox('Dehydration',['None','Some','Severe'])
            deficit=wt5*50 if deg=='Some' else wt5*100 if deg=='Severe' else 0
            st.metric('Fluid deficit', f'{deficit:.0f} mL'); st.metric('ORS over 4 hr', f'{wt5*75:.0f} mL' if deg=='Some' else '0 mL')
            explain_block('Explanation', 'This provides a quick dehydration replacement estimate used in common diarrhea care frameworks. Severe dehydration, persistent vomiting, shock, or electrolyte derangement need a more individualized plan.', 'WHO dehydration ORS child guideline')
        with tabs[6]:
            wt6=st.number_input('Weight kg',1.0,120.0,16.0, key='pfe')
            glucose=st.number_input('Glucose mg/dL',10.0,500.0,80.0)
            st.metric('Midazolam dose', f'{wt6*0.2:.2f} mg'); st.metric('D10 bolus', f'{wt6*2:.1f} mL')
            explain_block('Explanation', 'These emergency values are quick support numbers for common pediatric bedside decisions. Confirm route, concentration, and institutional emergency protocol before using them clinically.', 'pediatric emergency seizure glucose guideline')
            summary='Pediatrics calculations active'
    elif dept=='AI Clinical Search':
        symptom=st.text_input('Enter symptoms or question')
        age_group=st.selectbox('Age group',['General','Pediatric','Neonate','Adult'])
        if st.button('Analyze research') and symptom:
            st.markdown("<div class='alert-red'>This is a clinical-search assist module, not a diagnosis engine.</div>", unsafe_allow_html=True)
            res=pubmed_search(f'{symptom} {age_group} guideline review',5)
            if res:
                for r in res:
                    st.markdown(f"- [{r['title']}]({r['url']}) ({r['source']}, {r['pubdate']})")
            explain_block('How to use this', 'Use this result list to read evidence quickly, compare guideline wording, and support clinician review. Search quality depends on how specific your symptom terms are.', symptom + ' guideline review')
            summary='AI search used'
    elif dept=='Metabolic and General Medicine':
        tabs=st.tabs(['BMI','BSA','MAP'])
        with tabs[0]:
            w=st.number_input('Weight kg',5.0,300.0,70.0); h=st.number_input('Height cm',50.0,250.0,170.0)
            st.metric('BMI', f'{w/((h/100)**2):.2f}'); explain_block('Explanation','BMI is a body-size screening measure and not a diagnosis by itself. Use it together with symptoms, exam, and metabolic risk context.', 'BMI interpretation review')
        with tabs[1]:
            w2=st.number_input('Weight kg',5.0,300.0,70.0, key='mb1'); h2=st.number_input('Height cm',50.0,250.0,170.0, key='mb2')
            st.metric('BSA', f'{math.sqrt((w2*h2)/3600):.2f} mÂ²'); explain_block('Explanation','BSA is commonly used for drug dosing and physiologic normalization. It is a calculation aid and does not replace clinical dose adjustment.', 'body surface area dosing review')
        with tabs[2]:
            sbp=st.number_input('SBP',50,250,120); dbp=st.number_input('DBP',30,150,80)
            st.metric('MAP', f'{(sbp+2*dbp)/3:.1f}'); explain_block('Explanation','MAP estimates average arterial pressure and is often used in perfusion assessment. It should be interpreted with pulse pressure, lactate, mentation, and urine output.', 'mean arterial pressure clinical review')
    elif dept=='Neonatology':
        day=st.number_input('Day of life',1,28,3); wt=st.number_input('Weight kg',0.5,8.0,2.8)
        feed=wt*(80 if day<=1 else 100 if day<=3 else 120 if day<=7 else 150)
        st.metric('Feed target', f'{feed:.0f} mL/day')
        explain_block('Explanation','This estimates daily feed volume by neonatal age and weight as a quick bedside guide. Prematurity, NEC risk, respiratory support, and fluid balance can change the actual plan.', 'neonate feed volume guideline')
    elif dept=='Cardiology and Lipids':
        tc=st.number_input('Total cholesterol',1.0,500.0,200.0); hdl=st.number_input('HDL',1.0,200.0,45.0); tg=st.number_input('Triglycerides',1.0,1000.0,150.0)
        ldl=sampson_ldl(tc,hdl,tg); st.metric('LDL-C', f'{ldl:.1f}')
        explain_block('Explanation','This estimates LDL-C using a modern formula that performs better than older fixed-ratio methods in some triglyceride ranges. Interpret with overall cardiovascular risk and fasting status where relevant.', 'Sampson LDL equation review')
    elif dept=='Gastroenterology and Hepatology':
        bili=st.number_input('Bilirubin',0.1,50.0,1.0); inr=st.number_input('INR',0.1,15.0,1.1); cr=st.number_input('Creatinine',0.1,15.0,1.0)
        meld=round(10*((0.957*math.log(max(1,cr)))+(0.378*math.log(max(1,bili)))+(1.12*math.log(max(1,inr))))+6.43,1); st.metric('MELD', meld)
        explain_block('Explanation','MELD summarizes liver disease severity using bilirubin, INR, and creatinine. It is useful for risk estimation but does not capture the whole bedside picture.', 'MELD score review')
    elif dept=='Neurology and Emergency':
        e=st.select_slider('Eye',[1,2,3,4],value=4); v=st.select_slider('Verbal',[1,2,3,4,5],value=5); m=st.select_slider('Motor',[1,2,3,4,5,6],value=6)
        gcs=e+v+m; st.metric('GCS', gcs)
        explain_block('Explanation','GCS gives a structured description of neurologic responsiveness. Serial trends and cause of coma matter more than a single isolated score.', 'Glasgow Coma Scale review')
    elif dept=='Nephrology':
        scr=st.number_input('Creatinine mg/dL',0.1,15.0,1.0); age=st.number_input('Age',18,110,50); sex=st.selectbox('Sex',['Male','Female'])
        gfr=ckd_epi_2021(scr,age,sex=='Female'); st.metric('eGFR', f'{gfr:.1f}')
        explain_block('Explanation','This uses the CKD-EPI 2021 creatinine equation for quick kidney function estimation. Acute kidney injury, unstable creatinine, and unusual body habitus can limit accuracy.', 'CKD-EPI 2021 review')
    elif dept=='Ophthalmology and Orthopedics':
        iop=st.number_input('Measured IOP',5,60,20); cct=st.number_input('CCT microns',300,800,545)
        corr=iop+((545-cct)/50*2.5); st.metric('Corrected IOP', f'{corr:.1f}')
        explain_block('Explanation','This gives a rough corneal-thickness adjusted IOP estimate. It is a screening aid and does not replace full glaucoma assessment.', 'central corneal thickness IOP correction review')
    elif dept=='OB and GYN':
        lmp=st.date_input('LMP date', value=date.today()-timedelta(days=84)); cycle=st.number_input('Cycle length',21,45,28)
        ga=(date.today()-lmp).days/7; edd=lmp+timedelta(days=280+(cycle-28)); st.metric('Gestational age', f'{ga:.1f} weeks'); st.metric('EDD', str(edd))
        explain_block('Explanation','This estimates gestational age and expected date of delivery from the last menstrual period. Irregular cycles and uncertain dates reduce reliability, so ultrasound dating may be needed.', 'pregnancy dating LMP review')
    elif dept=='ICU and Critical Care':
        hr=st.number_input('Heart rate',20,250,100); sbp=st.number_input('SBP',30,250,110)
        shock=hr/sbp; st.metric('Shock index', f'{shock:.2f}')
        explain_block('Explanation','Shock index is a fast perfusion warning sign calculated as heart rate divided by systolic blood pressure. It is useful for screening, but clinical context and serial reassessment matter most.', 'shock index critical care review')
    elif dept=='Emergency Medicine':
        rr=st.number_input('Respiratory rate',4,60,18); sbp=st.number_input('SBP',30,250,120); ment=st.checkbox('Altered mental status')
        qsofa=int(rr>=22)+int(sbp<=100)+int(ment); st.metric('qSOFA', qsofa)
        explain_block('Explanation','qSOFA is a rapid bedside screen for possible high-risk infection-related deterioration. It should not be used alone to rule sepsis in or out.', 'qSOFA sepsis review')
    elif dept=='Hematology':
        hb=st.number_input('Hemoglobin',1.0,25.0,12.0); mcv=st.number_input('MCV',40.0,130.0,85.0)
        mentzer=mcv/hb; st.metric('Mentzer index', f'{mentzer:.2f}')
        explain_block('Explanation','Mentzer index is a quick microcytic anemia screening aid often used to think about iron deficiency versus thalassemia trait. It is only a clue and not a confirmatory test.', 'Mentzer index review')
    elif dept=='HIV and ART Follow-up':
        art=st.date_input('ART start date', value=date.today()); due=art+timedelta(days=28)
        st.metric('Next follow-up', str(due))
        explain_block('Explanation','This gives a simple early follow-up date from the ART start date. Real follow-up planning should match your program protocol, regimen, labs, and adherence needs.', 'ART follow up guideline')

    save_record(patient['patient_id'], dept, summary)
    st.download_button('Export Department Report', html_report(patient, dept, summary), f'{dept}_report.html')
