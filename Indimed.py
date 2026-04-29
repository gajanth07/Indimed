import streamlit as st
import requests, io, math
from datetime import date, timedelta
from urllib.parse import quote_plus

st.set_page_config(page_title='IndiMed Best 2026', layout='wide')

st.markdown('''
<style>
:root{--bg:#f5f9fd;--surface:#fff;--border:#d9e7f4;--text:#102233;--muted:#607489;--primary:#1667be;--primary2:#2387e2;--teal:#0f9d8a;--gold:#f59f00;--danger:#c62828;--ok:#128a5a;}
section[data-testid="stSidebar"]{display:none!important;}
.stApp{background:linear-gradient(180deg,#f9fcff 0%,#edf5fb 100%);color:var(--text);} .main .block-container{max-width:1180px;padding:.65rem .7rem 6rem;}
.hero{background:linear-gradient(135deg,#123d69 0%,#196cb0 54%,#12a192 100%);color:#fff;border-radius:20px;padding:18px;margin-bottom:10px;} .hero h1{margin:0;color:#fff;font-size:1.18rem;} .hero p{margin:.35rem 0 0;color:rgba(255,255,255,.94)!important;font-size:.91rem;}
.surface,.card,.pathbox,.sourcebox,.actionbox{background:#fff;border:1px solid var(--border);border-radius:18px;padding:13px;margin:10px 0;}
.card.peds{background:linear-gradient(180deg,#fff8e8,#fff);border-color:#f1d18f;} .card.ai{background:linear-gradient(180deg,#eef7ff,#fff);border-color:#c5def8;} .card.med{background:linear-gradient(180deg,#f4fffb,#fff);border-color:#bde7de;} .card.em{background:linear-gradient(180deg,#fff2f1,#fff);border-color:#ffd6d2;}
.title{font-weight:800;color:#143a5f;margin-bottom:.28rem;} .desc{color:var(--muted);font-size:.88rem;}
.tag{display:inline-block;padding:.18rem .52rem;border-radius:999px;background:#eef7ff;color:#1d4f91;font-size:.75rem;font-weight:700;margin:.1rem .18rem .1rem 0;border:1px solid #d2e6fb;}
.warn{background:#fff4f4;border:1px solid #ffd7d7;color:#9f1239;padding:11px 13px;border-radius:14px;font-weight:600;margin:.5rem 0;} .note{background:#eef7ff;border:1px solid #cfe4fa;color:#1d4f91;padding:11px 13px;border-radius:14px;font-weight:600;margin:.5rem 0;} .ok{background:#eefbf6;border:1px solid #cbeedd;color:#136c43;padding:11px 13px;border-radius:14px;font-weight:600;margin:.5rem 0;}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{width:100%!important;border:none!important;border-radius:12px!important;min-height:42px;font-weight:700!important;} .stButton>button,.stFormSubmitButton>button{background:linear-gradient(135deg,var(--primary),var(--primary2))!important;color:white!important;} .stDownloadButton>button{background:linear-gradient(135deg,#0c7b74,var(--teal))!important;color:white!important;}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--border);border-radius:14px;padding:10px;}
.stTabs [data-baseweb="tab-list"]{gap:6px;} .stTabs [data-baseweb="tab"]{background:#f4f9ff;border-radius:12px;padding:8px 12px;} .stTabs [aria-selected="true"]{background:#dcebfb!important;}
.embar{position:fixed;left:0;right:0;bottom:0;z-index:999;background:rgba(12,28,45,.95);backdrop-filter:blur(8px);padding:.5rem .75rem;border-top:1px solid rgba(255,255,255,.08);} .emgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:.45rem;max-width:1180px;margin:0 auto;} .emlink{display:block;text-align:center;background:linear-gradient(135deg,#b91c1c,#ef4444);color:#fff!important;text-decoration:none!important;padding:.65rem .4rem;border-radius:12px;font-size:.78rem;font-weight:800;}
.quick{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;} .mini{background:#fff;border:1px solid var(--border);border-radius:14px;padding:10px;text-align:center;} .mini b{display:block;color:#143a5f;font-size:.82rem;} .mini span{display:block;color:var(--muted);font-size:.76rem;}
@media (max-width:900px){.quick{grid-template-columns:repeat(2,1fr);} .emgrid{grid-template-columns:repeat(2,1fr);} }
</style>
''', unsafe_allow_html=True)

MODULES={
 'Pediatrics and Growth':{'desc':'Expanded pediatric toolbox with growth, fever, fluids, vaccine, dehydration, and emergency support.','cls':'peds','tags':['Favorite','Ward','Daily use']},
 'AI Clinical Search':{'desc':'India-first evidence search with local guideline links before broader literature.','cls':'ai','tags':['India-first','Evidence','Fast']},
 'Medication Safety and Dose':{'desc':'Dose support, interaction checks, renal flags, pregnancy and lactation notes.','cls':'med','tags':['Safety','High risk','Dose']},
 'Emergency Medicine':{'desc':'qSOFA, triage support, rabies, shock and rapid bedside pathways.','cls':'em','tags':['Emergency','Fast','Red flags']},
 'Metabolic and General Medicine':{'desc':'BMI, BSA, MAP, waist-height ratio and quick clinic support.','cls':'','tags':['OPD','General']},
 'Neonatology':{'desc':'Corrected age, feed estimates, jaundice and low birth weight support.','cls':'','tags':['NICU','Newborn']},
 'Hematology':{'desc':'Mentzer index, ANC and CBC support tools.','cls':'','tags':['Lab support']},
 'HIV and ART Follow-up':{'desc':'Visit milestones, adherence prompts and follow-up checklist support.','cls':'','tags':['Follow-up','Protocol']}
}
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, Rotavirus-3 if applicable, PCV-3'),('9 months',270,'MMR-1, Typhoid conjugate vaccine'),('12 months',365,'Hep A-1, Varicella-1'),('15 months',455,'MMR-2, Varicella-2, PCV booster')]
DRUGS={
 'paracetamol': {'dose_mgkg':15,'renal':'Usually no standard renal alert at routine dosing; verify cumulative daily limit.','preg':'Generally compatible at usual doses.','lact':'Generally compatible.'},
 'ibuprofen': {'dose_mgkg':10,'renal':'Use caution in dehydration, AKI, or CKD risk.','preg':'Avoid in later pregnancy unless specifically advised.','lact':'Usually compatible in routine use.'},
 'ondansetron': {'dose_mgkg':0.15,'renal':'No broad quick alert, but verify protocol.','preg':'Specialist judgment depending on indication.','lact':'Check product-specific guidance.'},
 'amoxicillin': {'dose_mgkg':25,'renal':'Dose interval may need review in significant renal impairment.','preg':'Commonly used when indicated.','lact':'Usually compatible.'}
}
INTERACTIONS=[
 ('warfarin','metronidazole','Major','INR may rise; avoid or monitor INR closely.'),
 ('warfarin','trimethoprim-sulfamethoxazole','Major','INR may rise; consider alternative or close INR monitoring.'),
 ('clarithromycin','simvastatin','Major','Avoid due to increased statin exposure and myopathy risk.'),
 ('sildenafil','nitrate','Contraindicated','Marked hypotension risk; do not combine.'),
 ('linezolid','ssri','Moderate','Serotonin toxicity risk; monitor carefully or avoid if possible.'),
 ('spironolactone','ace inhibitor','Moderate','Hyperkalemia risk; monitor potassium and renal function.'),
 ('metformin','contrast','Moderate','Hold/review around contrast in appropriate renal-risk situations per protocol.')
]
PATHWAYS={
 'Pediatric fever':['Check red flags: lethargy, poor feeding, respiratory distress, seizures, dehydration.','Check age and vaccination status, measure weight, temperature, and hydration.','Use weight-based antipyretic dose if appropriate, and assess focus of infection.','Escalate if toxic look, altered sensorium, shock, or infant-specific danger signs.'],
 'Dengue triage':['Check warning signs: abdominal pain, persistent vomiting, bleed, lethargy, rising hematocrit with falling platelets.','Assess hydration, blood pressure, pulse pressure, urine output.','Classify as dengue without warning signs, with warning signs, or severe dengue.','Use local protocol and Indian public-health guidance for referral and monitoring.'],
 'Sepsis quick pathway':['Screen vitals, mentation, perfusion, urine output, and likely source.','Obtain urgent senior review for hypotension, altered sensorium, or respiratory failure.','Send key tests quickly and begin time-sensitive management per local protocol.','Use qSOFA only as a risk cue, not as the full diagnosis.'],
 'Neonatal jaundice':['Check age in hours, gestation, feeding, urine/stool pattern, and risk factors.','Assess danger signs and bilirubin trend if available.','Use proper bilirubin nomograms/protocols for management thresholds.','Refer urgently if jaundice is early, severe, prolonged with danger signs, or associated with poor feeding.'],
 'Rabies PEP':['Check category of exposure, wound wash status, vaccination history, and animal details.','Perform immediate wound care and classify exposure severity.','Follow local rabies prophylaxis schedule and immunoglobulin indications.','Do not delay urgent prophylaxis decisions in high-risk exposure.']
}
SOURCE_META=[('ICMR','Indian guideline source','https://www.icmr.gov.in/guidelines','National guidance library'),('NCDC','Indian public-health source','https://ncdc.mohfw.gov.in/includes/Resource_Library/index.php?tab=Technical+Guidelines','Technical guidelines'),('IAP','Indian pediatric reference','https://pubmed.ncbi.nlm.nih.gov/41954836/','Pediatric immunization update'),('PubMed','Global evidence database','https://pubmed.ncbi.nlm.nih.gov/','Supporting literature')]

if 'page' not in st.session_state: st.session_state.page='home'
if 'dept' not in st.session_state: st.session_state.dept='AI Clinical Search'
if 'recent' not in st.session_state: st.session_state.recent=[]
if 'favorites' not in st.session_state: st.session_state.favorites=['Pediatrics and Growth','AI Clinical Search','Medication Safety and Dose']
if 'query' not in st.session_state: st.session_state.query=''

def open_dept(name):
    st.session_state.dept=name
    st.session_state.page='dept'
    if name in st.session_state.recent: st.session_state.recent.remove(name)
    st.session_state.recent=[name]+st.session_state.recent[:4]

def go_home(): st.session_state.page='home'

def toggle_favorite(name):
    if name in st.session_state.favorites: st.session_state.favorites.remove(name)
    else: st.session_state.favorites.append(name)

def explain_box(text, query=None):
    st.markdown(f"<div class='sourcebox'><div class='title'>Why this answer</div><div class='desc'>{text}</div></div>", unsafe_allow_html=True)
    if query:
        st.markdown(f"[Search PubMed for this topic](https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(query)})")

def trust_box(indian='ICMR/NCDC', global_source='PubMed', level='Quick support', updated='April 2026'):
    st.markdown(f"<div class='actionbox'><span class='tag'>Indian source: {indian}</span><span class='tag'>Global source: {global_source}</span><span class='tag'>Confidence: {level}</span><span class='tag'>Updated: {updated}</span></div>", unsafe_allow_html=True)

@st.cache_data(ttl=1800, show_spinner=False)
def pubmed_search_cached(query, max_results=5):
    try:
        es = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax={max_results}&term={quote_plus(query)}', timeout=15)
        ids = es.json().get('esearchresult', {}).get('idlist', [])
        if not ids: return []
        sm = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={",".join(ids)}', timeout=15)
        data = sm.json().get('result', {})
        return [{'title': data.get(i, {}).get('title', 'No title'), 'source': data.get(i, {}).get('source', ''), 'pubdate': data.get(i, {}).get('pubdate', ''), 'url': f'https://pubmed.ncbi.nlm.nih.gov/{i}/'} for i in ids]
    except Exception:
        return []

def html_report(title, summary):
    return io.BytesIO(f'<html><body><h1>{title}</h1><p>{summary}</p><p>{date.today()}</p></body></html>'.encode())

def calc_bmi(weight_kg, height_cm): return weight_kg/((height_cm/100)**2)
def expected_weight_kg(age_months): return (age_months/2)+4 if age_months<=12 else (age_months/12)*2+8
def maintenance_fluid_ml_day(weight_kg): return weight_kg*100 if weight_kg<=10 else 1000+(weight_kg-10)*50 if weight_kg<=20 else 1500+(weight_kg-20)*20
def bsa_m2(weight_kg, height_cm): return math.sqrt((height_cm*weight_kg)/3600)
def mentzer_index(mcv, rbc): return mcv/rbc if rbc else None
def anc(wbc, neutrophil_pct): return wbc*(neutrophil_pct/100)
def map_calc(sbp, dbp): return (sbp + 2*dbp)/3
def corrected_age_weeks(gestation_birth_weeks, chrono_weeks): return max(0, chrono_weeks-max(0,40-gestation_birth_weeks))
def interaction_checker(drug1, drug2):
    a=drug1.strip().lower(); b=drug2.strip().lower()
    for x,y,sev,msg in INTERACTIONS:
        if {a,b}=={x,y}: return sev,msg
    return 'Low / unknown','No predefined high-priority interaction found in this quick checker.'

def search_modules(q):
    q=q.strip().lower()
    if not q: return list(MODULES.keys())
    hits=[]
    for k,v in MODULES.items():
        hay=' '.join([k,v['desc'],' '.join(v['tags'])]).lower()
        if q in hay: hits.append(k)
    return hits

st.markdown("<div class='hero'><h1>IndiMed Best 2026</h1><p>Built for Indian doctors: one-tap bedside workflows, India-first evidence, faster safety tools, and stronger mobile clarity.</p></div>", unsafe_allow_html=True)

if st.session_state.page=='home':
    st.text_input('Search modules, diseases, or tools', key='query', placeholder='Try: dengue, dose, vaccine, sepsis, anemia')
    c1,c2,c3,c4=st.columns(4)
    c1.markdown("<div class='mini'><b>Favorites</b><span>One-tap top tools</span></div>", unsafe_allow_html=True)
    c2.markdown("<div class='mini'><b>Recents</b><span>Continue faster</span></div>", unsafe_allow_html=True)
    c3.markdown("<div class='mini'><b>India-first</b><span>ICMR, NCDC, IAP</span></div>", unsafe_allow_html=True)
    c4.markdown("<div class='mini'><b>Low-data</b><span>Compact output design</span></div>", unsafe_allow_html=True)

    if st.session_state.favorites:
        st.markdown("<div class='title'>Favorites</div>", unsafe_allow_html=True)
        cols=st.columns(min(3,len(st.session_state.favorites)))
        for i,name in enumerate(st.session_state.favorites[:3]):
            with cols[i]:
                info=MODULES[name]
                st.markdown(f"<div class='card {info['cls']}'><div class='title'>{name}</div><div class='desc'>{info['desc']}</div></div>", unsafe_allow_html=True)
                st.button(name, key='fav_'+name, on_click=open_dept, args=(name,))

    if st.session_state.recent:
        st.markdown("<div class='title'>Recent tools</div>", unsafe_allow_html=True)
        cols=st.columns(min(3,len(st.session_state.recent)))
        for i,name in enumerate(st.session_state.recent[:3]):
            with cols[i]:
                st.button('Continue '+name, key='rec_'+name, on_click=open_dept, args=(name,))

    st.markdown("<div class='title'>Top modules</div>", unsafe_allow_html=True)
    shown=search_modules(st.session_state.query)
    top=[x for x in ['Pediatrics and Growth','AI Clinical Search','Medication Safety and Dose','Emergency Medicine','Metabolic and General Medicine','Neonatology'] if x in shown]
    for i in range(0,len(top),2):
        cols=st.columns(2)
        for j,name in enumerate(top[i:i+2]):
            with cols[j]:
                info=MODULES[name]
                tags=''.join([f"<span class='tag'>{t}</span>" for t in info['tags']])
                st.markdown(f"<div class='card {info['cls']}'><div class='title'>{name}</div><div class='desc'>{info['desc']}</div><div style='margin-top:.45rem'>{tags}</div></div>", unsafe_allow_html=True)
                a,b=st.columns(2)
                a.button('Open '+name, key='open_'+name, on_click=open_dept, args=(name,))
                star='Remove favorite' if name in st.session_state.favorites else 'Add favorite'
                b.button(star, key='star_'+name, on_click=toggle_favorite, args=(name,))

    st.markdown("<div class='title'>More departments</div>", unsafe_allow_html=True)
    for i in range(0,2):
        cols=st.columns(2)
        for j,name in enumerate(list(MODULES.keys())[6+i*2:8+i*2]):
            with cols[j]:
                if name:
                    info=MODULES[name]
                    st.markdown(f"<div class='card'><div class='title'>{name}</div><div class='desc'>{info['desc']}</div></div>", unsafe_allow_html=True)
                    st.button('Open '+name, key='more_'+name, on_click=open_dept, args=(name,))

else:
    dept=st.session_state.dept
    st.button('Back to Home', on_click=go_home)
    trust_box()

    if dept=='AI Clinical Search':
        with st.form('india_first_search'):
            c1,c2=st.columns([2,1])
            symptom=c1.text_input('Symptoms, diagnosis doubt, or question')
            age_group=c2.selectbox('Age group',['General','Pediatric','Neonate','Adult'])
            submit=st.form_submit_button('Search evidence')
        if submit and symptom:
            st.markdown("<div class='warn'>Clinical-search assist only. Not a standalone diagnosis engine.</div>", unsafe_allow_html=True)
            st.markdown("<div class='title'>Indian sources first</div>", unsafe_allow_html=True)
            st.markdown("<div class='sourcebox'><b>ICMR</b><br><a href='https://www.icmr.gov.in/guidelines' target='_blank'>Open ICMR guideline library</a><br><span class='desc'>National guidance library</span></div>", unsafe_allow_html=True)
            st.markdown("<div class='sourcebox'><b>NCDC</b><br><a href='https://ncdc.mohfw.gov.in/includes/Resource_Library/index.php?tab=Technical+Guidelines' target='_blank'>Open NCDC technical guidelines</a><br><span class='desc'>Public-health and technical guidance</span></div>", unsafe_allow_html=True)
            if age_group in ['Pediatric','Neonate'] or any(k in symptom.lower() for k in ['child','pediatric','vaccine','infant']):
                st.markdown("<div class='sourcebox'><b>IAP</b><br><a href='https://pubmed.ncbi.nlm.nih.gov/41954836/' target='_blank'>Open IAP immunization update</a><br><span class='desc'>Indian pediatric reference</span></div>", unsafe_allow_html=True)
            st.markdown("<div class='title'>Structured pathway</div>", unsafe_allow_html=True)
            pathway_key='Pediatric fever' if 'fever' in symptom.lower() and age_group in ['Pediatric','Neonate'] else 'Dengue triage' if 'dengue' in symptom.lower() else 'Sepsis quick pathway' if 'sepsis' in symptom.lower() else None
            if pathway_key:
                for step in PATHWAYS[pathway_key]: st.markdown(f"- {step}")
            else:
                st.markdown("- Define the syndrome first, check danger signs, review Indian guidance, then confirm with broader literature.")
            st.markdown("<div class='title'>Supporting literature</div>", unsafe_allow_html=True)
            results=pubmed_search_cached(f'{symptom} {age_group} India guideline review',5)
            if results:
                for r in results:
                    st.markdown(f"<div class='sourcebox'><a href='{r['url']}' target='_blank'>{r['title']}</a><br><span class='desc'>{r['source']} | {r['pubdate']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='note'>No PubMed result returned now. Try shorter terms.</div>", unsafe_allow_html=True)
            explain_box('This search view prioritizes Indian sources before global literature, then shows a compact pathway to reduce bedside cognitive load.', f'{symptom} India guideline review')

    elif dept=='Medication Safety and Dose':
        tabs=st.tabs(['Dose by Weight','Interaction Checker','Renal','Pregnancy/Lactation'])
        with tabs[0]:
            with st.form('med_dose'):
                c1,c2=st.columns(2)
                drug=c1.selectbox('Drug',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                wt=c2.number_input('Weight kg',1.0,200.0,20.0)
                submit=st.form_submit_button('Calculate dose')
            if submit:
                dose=DRUGS[drug]['dose_mgkg']*wt
                st.metric('Estimated single dose', f'{dose:.2f} mg')
                st.markdown(f"<div class='note'>Check formulation strength, age band, interval, and maximum daily dose.</div>", unsafe_allow_html=True)
        with tabs[1]:
            with st.form('med_interaction'):
                c1,c2=st.columns(2)
                d1=c1.text_input('Drug 1','warfarin')
                d2=c2.text_input('Drug 2','metronidazole')
                submit=st.form_submit_button('Check interaction')
            if submit:
                sev,msg=interaction_checker(d1,d2)
                css='warn' if sev in ['Contraindicated','Major','Moderate'] else 'ok'
                st.markdown(f"<div class='{css}'><b>{sev}</b><br>{msg}</div>", unsafe_allow_html=True)
                st.markdown("<div class='note'>Next step: confirm full regimen, renal function, age, pregnancy status, and monitoring plan.</div>", unsafe_allow_html=True)
        with tabs[2]:
            with st.form('med_renal'):
                c1,c2=st.columns(2)
                drug2=c1.selectbox('Drug for renal note',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                egfr=c2.number_input('eGFR',0.0,200.0,60.0)
                submit=st.form_submit_button('Show renal alert')
            if submit:
                msg=DRUGS[drug2]['renal']
                if egfr<30: msg='High renal-risk situation. '+msg
                elif egfr<60: msg='Moderate renal-risk situation. '+msg
                st.markdown(f"<div class='note'>{msg}</div>", unsafe_allow_html=True)
        with tabs[3]:
            with st.form('med_preg'):
                d=st.selectbox('Drug for pregnancy/lactation note',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                submit=st.form_submit_button('Show notes')
            if submit:
                st.markdown(f"<div class='sourcebox'><b>Pregnancy</b><br>{DRUGS[d]['preg']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sourcebox'><b>Lactation</b><br>{DRUGS[d]['lact']}</div>", unsafe_allow_html=True)
            explain_box('Medication safety is organized into dose, interaction, renal, and pregnancy/lactation views so a doctor can answer the bedside question faster.', 'medication safety dosing review')

    elif dept=='Pediatrics and Growth':
        tabs=st.tabs(['Growth','Fever','Fluids','Vaccine','Dehydration','Emergency'])
        with tabs[0]:
            with st.form('peds_growth'):
                c1,c2,c3=st.columns(3)
                age_m=c1.number_input('Age months',0,216,24)
                wt=c2.number_input('Weight kg',1.0,120.0,12.0)
                ht=c3.number_input('Height cm',30.0,220.0,85.0)
                submit=st.form_submit_button('Calculate growth')
            if submit:
                st.metric('BMI', f'{calc_bmi(wt,ht):.2f}')
                st.metric('Expected weight', f'{expected_weight_kg(age_m):.1f} kg')
        with tabs[1]:
            with st.form('peds_fever'):
                c1,c2=st.columns(2)
                wt2=c1.number_input('Weight kg ',1.0,120.0,12.0)
                temp=c2.number_input('Temperature Â°C',35.0,42.0,38.4)
                submit=st.form_submit_button('Fever support')
            if submit:
                c1,c2,c3=st.columns(3)
                c1.metric('Paracetamol', f'{wt2*15:.0f} mg')
                c2.metric('Ibuprofen', f'{wt2*10:.0f} mg')
                c3.metric('Status', 'Fever' if temp >= 38 else 'No fever')
                for step in PATHWAYS['Pediatric fever']: st.markdown(f"- {step}")
        with tabs[2]:
            with st.form('peds_fluid'):
                wt3=st.number_input('Weight kg  ',1.0,120.0,12.0)
                submit=st.form_submit_button('Fluid support')
            if submit:
                daily=maintenance_fluid_ml_day(wt3)
                c1,c2=st.columns(2)
                c1.metric('Maintenance fluid', f'{daily:.0f} mL/day')
                c2.metric('Hourly rate', f'{daily/24:.1f} mL/hr')
        with tabs[3]:
            with st.form('peds_vaccine'):
                dob=st.date_input('Date of birth', value=date.today()-timedelta(days=450))
                submit=st.form_submit_button('Show vaccine due dates')
            if submit:
                for label,days,items in VACCINE_SCHEDULE:
                    due=dob+timedelta(days=days)
                    st.markdown(f"<div class='sourcebox'><b>{label}</b><br>{due}<br><span class='desc'>{items}</span></div>", unsafe_allow_html=True)
                st.markdown("<div class='sourcebox'><b>Indian references</b><br><a href='https://pubmed.ncbi.nlm.nih.gov/41954836/' target='_blank'>IAP update</a><br><a href='https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/report/National_%20Immunization_Schedule.pdf' target='_blank'>National Immunization Schedule</a></div>", unsafe_allow_html=True)
        with tabs[4]:
            with st.form('dehyd'):
                c1,c2,c3=st.columns(3)
                wt4=c1.number_input('Weight kg   ',1.0,120.0,12.0)
                status=c2.selectbox('Clinical dehydration',['No dehydration','Some dehydration','Severe dehydration'])
                stools=c3.number_input('Loose stools/day',0,20,4)
                submit=st.form_submit_button('Dehydration support')
            if submit:
                extra=10*wt4 if status=='Some dehydration' else 20*wt4 if status=='Severe dehydration' else 0
                st.metric('Extra fluid cue', f'{extra:.0f} mL')
                st.markdown("<div class='note'>Use formal pediatric dehydration protocols for exact plan and route.</div>", unsafe_allow_html=True)
        with tabs[5]:
            with st.form('peds_emergency'):
                c1,c2=st.columns(2)
                wt5=c1.number_input('Weight kg    ',1.0,120.0,16.0)
                glucose=c2.number_input('Bedside glucose mg/dL',20,600,80)
                submit=st.form_submit_button('Emergency quick support')
            if submit:
                c1,c2,c3=st.columns(3)
                c1.metric('IN midazolam', f'{wt5*0.2:.2f} mg')
                c2.metric('D10 bolus', f'{wt5*2:.0f} mL')
                c3.metric('Hypoglycemia flag', 'Yes' if glucose<70 else 'No')

    elif dept=='Emergency Medicine':
        tabs=st.tabs(['qSOFA','Dengue','Rabies'])
        with tabs[0]:
            with st.form('em'):
                c1,c2,c3=st.columns(3)
                rr=c1.number_input('Respiratory rate',0,80,24)
                sbp=c2.number_input('SBP',40,250,100)
                gcs=c3.number_input('GCS',3,15,15)
                submit=st.form_submit_button('Calculate qSOFA')
            if submit:
                score=(1 if rr>=22 else 0)+(1 if sbp<=100 else 0)+(1 if gcs<15 else 0)
                st.metric('qSOFA', score)
                for step in PATHWAYS['Sepsis quick pathway']: st.markdown(f"- {step}")
        with tabs[1]:
            for step in PATHWAYS['Dengue triage']: st.markdown(f"- {step}")
        with tabs[2]:
            for step in PATHWAYS['Rabies PEP']: st.markdown(f"- {step}")

    elif dept=='Metabolic and General Medicine':
        with st.form('metabolic'):
            c1,c2,c3,c4=st.columns(4)
            wt=c1.number_input('Weight kg',1.0,250.0,70.0)
            ht=c2.number_input('Height cm',30.0,250.0,170.0)
            sbp=c3.number_input('SBP ',50,300,120)
            dbp=c4.number_input('DBP ',30,200,80)
            submit=st.form_submit_button('Calculate')
        if submit:
            c1,c2,c3=st.columns(3)
            c1.metric('BMI', f'{calc_bmi(wt,ht):.2f}')
            c2.metric('BSA', f'{bsa_m2(wt,ht):.2f} mÂ²')
            c3.metric('MAP', f'{map_calc(sbp,dbp):.1f} mmHg')

    elif dept=='Neonatology':
        tabs=st.tabs(['Corrected age','Jaundice pathway'])
        with tabs[0]:
            with st.form('neo'):
                c1,c2=st.columns(2)
                gest=c1.number_input('Gestation at birth (weeks)',22,42,34)
                chrono=c2.number_input('Chronological age (weeks)',0,120,10)
                submit=st.form_submit_button('Calculate corrected age')
            if submit: st.metric('Corrected age', f'{corrected_age_weeks(gest,chrono)} weeks')
        with tabs[1]:
            for step in PATHWAYS['Neonatal jaundice']: st.markdown(f"- {step}")

    elif dept=='Hematology':
        with st.form('heme'):
            c1,c2,c3,c4=st.columns(4)
            mcv=c1.number_input('MCV',40.0,130.0,70.0)
            rbc=c2.number_input('RBC count',1.0,10.0,5.0)
            wbc=c3.number_input('WBC /uL',100.0,200000.0,6000.0)
            neut=c4.number_input('Neutrophils %',0.0,100.0,50.0)
            submit=st.form_submit_button('Calculate')
        if submit:
            c1,c2=st.columns(2)
            c1.metric('Mentzer index', f'{mentzer_index(mcv,rbc):.2f}')
            c2.metric('ANC', f'{anc(wbc,neut):.0f} /uL')

    elif dept=='HIV and ART Follow-up':
        with st.form('hiv'):
            visit=st.selectbox('Follow-up milestone',['Baseline','2 weeks','1 month','3 months','6 months'])
            submit=st.form_submit_button('Show checklist')
        if submit:
            checklists={
                'Baseline':['Confirm regimen, baseline labs, adherence counseling, opportunistic infection review.'],
                '2 weeks':['Early tolerance check, adherence check, danger symptoms review.'],
                '1 month':['Side effects, adherence reinforcement, interaction review.'],
                '3 months':['Clinical response, adherence, lab follow-up per protocol.'],
                '6 months':['Long-term adherence, adverse effects, viral load strategy per protocol.']
            }
            for item in checklists[visit]: st.markdown(f"- {item}")

    st.markdown("<div class='title'>Sources and trust</div>", unsafe_allow_html=True)
    for s in SOURCE_META:
        st.markdown(f"<div class='sourcebox'><b>{s[0]}</b><br><a href='{s[2]}' target='_blank'>{s[1]}</a><br><span class='desc'>{s[3]}</span></div>", unsafe_allow_html=True)
    st.download_button('Export current view', html_report(dept, f'Best-version export from {dept} module'), file_name=f'{dept}_best_report.html')

st.markdown("<div class='embar'><div class='emgrid'><a class='emlink' href='?dept=Emergency'>Emergency</a><a class='emlink' href='?dept=Dengue'>Dengue</a><a class='emlink' href='?dept=Rabies'>Rabies</a><a class='emlink' href='?dept=DrugSafety'>Dose / Safety</a></div></div>", unsafe_allow_html=True)
