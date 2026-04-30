import streamlit as st
import requests, io, math
from datetime import date, timedelta
from urllib.parse import quote_plus

st.set_page_config(page_title='IndiMed Hardened 2026', layout='wide', initial_sidebar_state='collapsed')

st.markdown('''
<style>
:root{--border:#d9e7f4;--text:#102233;--muted:#607489;--primary:#1667be;--primary2:#2387e2;--teal:#0f9d8a;--danger:#c62828;}
section[data-testid="stSidebar"]{display:none!important;}
.stApp{background:linear-gradient(180deg,#f9fcff 0%,#edf5fb 100%);color:var(--text);} .main .block-container{max-width:1100px;padding:.55rem .7rem 3.4rem;}
.hero{background:linear-gradient(135deg,#123d69 0%,#196cb0 52%,#12a192 100%);color:#fff;border-radius:18px;padding:14px;margin-bottom:10px;} .hero h1{margin:0;color:#fff;font-size:1.06rem;} .hero p{margin:.28rem 0 0;color:rgba(255,255,255,.93)!important;font-size:.86rem;}
.card,.box{background:#fff;border:1px solid var(--border);border-radius:15px;padding:11px;margin:8px 0;} .card.peds{background:linear-gradient(180deg,#fff8e8,#fff);border-color:#f1d18f;} .card.ai{background:linear-gradient(180deg,#eef7ff,#fff);border-color:#c5def8;} .card.med{background:linear-gradient(180deg,#f4fffb,#fff);border-color:#bde7de;} .card.em{background:linear-gradient(180deg,#fff2f1,#fff);border-color:#ffd6d2;}
.title{font-weight:800;color:#143a5f;margin-bottom:.2rem;} .desc{color:var(--muted);font-size:.84rem;} .tag{display:inline-block;padding:.16rem .48rem;border-radius:999px;background:#eef7ff;color:#1d4f91;font-size:.7rem;font-weight:700;margin:.06rem .12rem .06rem 0;border:1px solid #d2e6fb;}
.warn,.note,.ok{padding:10px 12px;border-radius:12px;font-weight:600;margin:.45rem 0;} .warn{background:#fff4f4;border:1px solid #ffd7d7;color:#9f1239;} .note{background:#eef7ff;border:1px solid #cfe4fa;color:#1d4f91;} .ok{background:#eefbf6;border:1px solid #cbeedd;color:#136c43;}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{width:100%!important;border:none!important;border-radius:11px!important;min-height:38px;font-weight:700!important;} .stButton>button,.stFormSubmitButton>button{background:linear-gradient(135deg,var(--primary),var(--primary2))!important;color:#fff!important;} .stDownloadButton>button{background:linear-gradient(135deg,#0c7b74,var(--teal))!important;color:#fff!important;}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--border);border-radius:12px;padding:8px;} .stTabs [data-baseweb="tab-list"]{gap:4px;} .stTabs [data-baseweb="tab"]{background:#f4f9ff;border-radius:10px;padding:7px 10px;}
.mini{background:#fff;border:1px solid var(--border);border-radius:12px;padding:8px;text-align:center;} .mini b{display:block;color:#143a5f;font-size:.78rem;} .mini span{display:block;color:var(--muted);font-size:.72rem;}
</style>
''', unsafe_allow_html=True)

MODULES={
 'Pediatrics and Growth':{'desc':'Growth, fever, fluids, vaccines, dehydration, ETAT and pediatric emergency tools.','cls':'peds','tags':['Favorite','Ward','Daily use']},
 'Neonatology':{'desc':'Corrected age, feeds, fluids, bilirubin, GIR, jaundice and newborn support.','cls':'peds','tags':['NICU','Newborn']},
 'AI Clinical Search':{'desc':'India-first evidence search with Indian guidance first, literature second.','cls':'ai','tags':['India-first','Evidence','Fast']},
 'Medication Safety and Dose':{'desc':'Dose support, interactions, renal notes, pregnancy and lactation prompts.','cls':'med','tags':['Safety','High risk','Dose']},
 'Emergency Medicine':{'desc':'qSOFA, sepsis cues, dengue triage and rabies PEP support.','cls':'em','tags':['Emergency','Fast','Red flags']},
 'Metabolic and General Medicine':{'desc':'BMI, BSA and MAP quick clinic support.','cls':'','tags':['OPD','General']},
 'Hematology':{'desc':'Mentzer index, ANC and CBC quick support.','cls':'','tags':['Lab support']},
 'HIV and ART Follow-up':{'desc':'Visit milestones and protocol-style follow-up checklist.','cls':'','tags':['Follow-up','Protocol']}
}
SOURCES=[('ICMR','https://www.icmr.gov.in/guidelines','Indian guideline source'),('NCDC','https://ncdc.mohfw.gov.in/includes/Resource_Library/index.php?tab=Technical+Guidelines','Indian technical/public-health guidance'),('IAP','https://pubmed.ncbi.nlm.nih.gov/41954836/','Indian pediatric immunization reference'),('WHO ETAT','https://www.who.int/publications/i/item/9789241510219','Pediatric emergency triage reference'),('PubMed','https://pubmed.ncbi.nlm.nih.gov/','Supporting literature')]
PATHWAYS={'Pediatric fever':['Check red flags: lethargy, poor feeding, respiratory distress, seizures, dehydration.','Check age, vaccination status, weight, temperature, and hydration.','Use weight-based antipyretic dose if appropriate and assess focus of infection.','Escalate if toxic look, altered sensorium, shock, or infant-specific danger signs.'],'Dengue triage':['Check warning signs: abdominal pain, persistent vomiting, bleed, lethargy, rising hematocrit with falling platelets.','Assess hydration, pulse pressure, urine output, and hemodynamic state.','Classify as without warning signs, with warning signs, or severe dengue.','Use Indian protocol/public-health guidance for monitoring and referral.'],'Sepsis quick pathway':['Screen vitals, mentation, perfusion, urine output, and likely source.','Escalate urgently for hypotension, altered sensorium, or respiratory failure.','Send key tests quickly and begin time-sensitive management per protocol.','Use qSOFA as a risk cue, not a full diagnosis.'],'Neonatal jaundice':['Check age in hours, gestation, feeding, urine/stool pattern, and risk factors.','Assess danger signs and bilirubin trend if available.','Use age-specific nomograms/protocols for treatment thresholds.','Refer urgently if jaundice is early, severe, prolonged with danger signs, or associated with poor feeding.'],'Rabies PEP':['Check exposure category, wound wash status, vaccination history, and animal details.','Perform immediate wound care and classify severity.','Follow rabies prophylaxis schedule and immunoglobulin indications.','Do not delay urgent prophylaxis decisions in high-risk exposure.']}
DRUGS={'paracetamol': {'dose_mgkg':15,'renal':'Usually no routine renal alert at standard dosing; verify cumulative daily limit.','preg':'Generally compatible at usual doses.','lact':'Generally compatible.'},'ibuprofen': {'dose_mgkg':10,'renal':'Use caution in dehydration, AKI, or CKD risk.','preg':'Avoid in later pregnancy unless specifically advised.','lact':'Usually compatible in routine use.'},'ondansetron': {'dose_mgkg':0.15,'renal':'No broad quick alert, but verify protocol.','preg':'Specialist judgment depending on indication.','lact':'Check product-specific guidance.'},'amoxicillin': {'dose_mgkg':25,'renal':'Dose interval may need review in significant renal impairment.','preg':'Commonly used when indicated.','lact':'Usually compatible.'}}
INTERACTIONS=[('warfarin','metronidazole','Major','INR may rise; avoid or monitor INR closely.'),('warfarin','trimethoprim-sulfamethoxazole','Major','INR may rise; consider alternative or close INR monitoring.'),('clarithromycin','simvastatin','Major','Avoid due to increased statin exposure and myopathy risk.'),('sildenafil','nitrate','Contraindicated','Marked hypotension risk; do not combine.'),('linezolid','ssri','Moderate','Serotonin toxicity risk; monitor carefully or avoid if possible.')]
VACCINE_SCHEDULE=[('Birth',0,'BCG, OPV-0, Hepatitis B birth dose'),('6 weeks',42,'DTwP/DTaP-1, IPV-1, Hib-1, Hep B-2, Rotavirus-1, PCV-1'),('10 weeks',70,'DTwP/DTaP-2, IPV-2, Hib-2, Rotavirus-2, PCV-2'),('14 weeks',98,'DTwP/DTaP-3, IPV-3/fIPV-2, Hib-3, Rotavirus-3 if applicable, PCV-3'),('9 months',270,'MMR-1, Typhoid conjugate vaccine'),('12 months',365,'Hep A-1, Varicella-1'),('15 months',455,'MMR-2, Varicella-2, PCV booster')]

if 'page' not in st.session_state: st.session_state.page='home'
if 'dept' not in st.session_state: st.session_state.dept='Pediatrics and Growth'
if 'recent' not in st.session_state: st.session_state.recent=[]
if 'favorites' not in st.session_state: st.session_state.favorites=['Pediatrics and Growth','Neonatology','AI Clinical Search','Medication Safety and Dose']
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

def search_modules(q):
    q=q.strip().lower()
    if not q: return list(MODULES.keys())
    return [k for k,v in MODULES.items() if q in ' '.join([k,v['desc'],' '.join(v['tags'])]).lower()]

def calc_bmi(weight_kg, height_cm): return weight_kg/((height_cm/100)**2)
def expected_weight_kg(age_months): return (age_months/2)+4 if age_months<=12 else (age_months/12)*2+8
def maintenance_fluid_ml_day(weight_kg): return weight_kg*100 if weight_kg<=10 else 1000+(weight_kg-10)*50 if weight_kg<=20 else 1500+(weight_kg-20)*20
def bsa_m2(weight_kg, height_cm): return math.sqrt((height_cm*weight_kg)/3600)
def mentzer_index(mcv, rbc): return mcv/rbc if rbc else None
def anc(wbc, neutrophil_pct): return wbc*(neutrophil_pct/100)
def map_calc(sbp, dbp): return (sbp + 2*dbp)/3
def corrected_age_weeks(gestation_birth_weeks, chrono_weeks): return max(0, chrono_weeks-max(0,40-gestation_birth_weeks))
def pediatric_vitals_band(age_years):
    if age_years < 1: return {'rr':'30-60/min','hr':'100-160/min','sbp':'70-100 mmHg'}
    if age_years < 3: return {'rr':'24-40/min','hr':'90-150/min','sbp':'80-110 mmHg'}
    if age_years < 6: return {'rr':'22-34/min','hr':'80-140/min','sbp':'80-110 mmHg'}
    if age_years < 12: return {'rr':'18-30/min','hr':'70-120/min','sbp':'90-120 mmHg'}
    return {'rr':'12-20/min','hr':'60-100/min','sbp':'90-120 mmHg'}
def estimate_weight_age(age_years):
    if age_years < 1: return round((age_years*12)/2 + 4,1)
    if age_years <= 5: return round((age_years*2)+8,1)
    return round((age_years*3)+7,1)
def dehydration_extra_ml(weight_kg, severity): return 0 if severity=='No dehydration' else 75*weight_kg if severity=='Some dehydration' else 100*weight_kg
def weight_loss_percent(birth_wt, current_wt): return ((birth_wt-current_wt)/birth_wt)*100 if birth_wt else 0
def neonatal_feed_mlkgday(day_of_life): return {1:60,2:80,3:100,4:120,5:140,6:150,7:160}.get(day_of_life,160)
def neonatal_fluid_mlkgday(day_of_life): return {1:60,2:80,3:100,4:120,5:140,6:150,7:160}.get(day_of_life,160)
def gir_from_dextrose(rate_ml_hr, dextrose_percent, weight_kg): return (rate_ml_hr*(dextrose_percent/100)*1000/60)/weight_kg if weight_kg else 0
def bilirubin_risk(age_hours, bilirubin):
    if age_hours < 24 and bilirubin >= 10: return 'Urgent review'
    if age_hours < 48 and bilirubin >= 15: return 'High / phototherapy review'
    if age_hours < 72 and bilirubin >= 18: return 'High / phototherapy review'
    if bilirubin >= 20: return 'Urgent review'
    return 'Review with age-specific nomogram'
def interaction_checker(drug1, drug2):
    a=drug1.strip().lower(); b=drug2.strip().lower()
    for x,y,sev,msg in INTERACTIONS:
        if {a,b}=={x,y}: return sev,msg
    return 'Low / unknown','No predefined high-priority interaction found in this quick checker.'


def bmi_band(age_years, bmi):
    if age_years < 18:
        return 'Use WHO/IAP age- and sex-specific growth chart percentile; raw BMI alone is not enough.'
    if bmi < 18.5: return 'Underweight range (adult threshold).'
    if bmi < 25: return 'Normal adult range.'
    if bmi < 30: return 'Overweight adult range.'
    return 'Obesity adult range.'

def map_interpret(mapv):
    if mapv < 65: return 'Low MAP cue; interpret with perfusion and shock context.'
    if mapv <= 100: return 'Usual bedside range in many adults; interpret clinically.'
    return 'Elevated MAP cue; interpret with history and end-organ context.'

def mentzer_interpret(val):
    if val < 13: return 'Mentzer <13 can support thalassemia-trait consideration.'
    return 'Mentzer >=13 can support iron deficiency consideration.'

def anc_interpret(age_group, val):
    if age_group=='Neonate':
        return 'Neonatal ANC needs gestational/postnatal-age interpretation; use neonatal reference ranges.'
    if val < 500: return 'Severe neutropenia range.'
    if val < 1000: return 'Moderate neutropenia range.'
    if val < 1500: return 'Mild neutropenia range.'
    return 'No neutropenia by common non-neonatal adult/child cutoffs.'

def qsofa_interpret(score):
    if score >= 2: return 'Higher risk cue; urgent assessment is warranted.'
    return 'Lower qSOFA, but unstable patients still need urgent review.'

def dehydration_plan(weight_kg, severity):
    if severity=='No dehydration':
        return 'Likely no dehydration on selected screen.', 'Use oral fluids/feeding and reassess if symptoms worsen.'
    if severity=='Some dehydration':
        return f'Approx rehydration cue: {75*weight_kg:.0f} mL over about 4 hours.', 'Prefer protocol-based ORS plan; reassess pulse, urine output, and ongoing losses.'
    return f'Approx fluid deficit cue: {100*weight_kg:.0f} mL or protocol-based emergency plan.', 'Severe dehydration needs urgent protocol-based IV/IO assessment and shock review.'

def bilirubin_prompt(age_hours, bilirubin, preterm=False, risk=False):
    tag='Rough warning prompt only.'
    if preterm or risk:
        return 'Use lower treatment thresholds and an institution-approved nomogram/protocol.', tag
    if age_hours < 24 and bilirubin >= 10: return 'Urgent review: early jaundice needs protocol-based assessment.', tag
    if age_hours < 48 and bilirubin >= 15: return 'High-risk prompt: check age-in-hours phototherapy threshold now.', tag
    if age_hours < 72 and bilirubin >= 18: return 'High-risk prompt: check age-in-hours phototherapy threshold now.', tag
    if bilirubin >= 20: return 'Urgent review: severe hyperbilirubinemia threshold may be near or exceeded.', tag
    return 'Needs nomogram check; simplified threshold not enough for treatment decisions.', tag

def source_badges(indian='ICMR/NCDC', global_src='PubMed', method='Quick-support formula', caution='Needs clinician verification'):
    st.markdown(f"<div class='box'><span class='tag'>Indian source: {indian}</span><span class='tag'>Global source: {global_src}</span><span class='tag'>Method: {method}</span><span class='tag'>Caution: {caution}</span></div>", unsafe_allow_html=True)

def safety_note(text, level='note'):
    st.markdown(f"<div class='{level}'>{text}</div>", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def pubmed_search_cached(query, max_results=4):
    try:
        es=requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax={max_results}&term={quote_plus(query)}', timeout=6)
        ids=es.json().get('esearchresult',{}).get('idlist',[])
        if not ids: return []
        sm=requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={",".join(ids)}', timeout=6)
        data=sm.json().get('result',{})
        return [{'title':data.get(i,{}).get('title','No title'),'source':data.get(i,{}).get('source',''),'pubdate':data.get(i,{}).get('pubdate',''),'url':f'https://pubmed.ncbi.nlm.nih.gov/{i}/'} for i in ids]
    except Exception:
        return []

def html_report(title, summary): return io.BytesIO(f'<html><body><h1>{title}</h1><p>{summary}</p><p>{date.today()}</p></body></html>'.encode())

st.markdown("<div class='hero'><h1>IndiMed Hardened 2026</h1><p>Safer wording, stronger source tags, clinical caution labels, and quick-support outputs designed for verification rather than blind use.</p></div>", unsafe_allow_html=True)

if st.session_state.page=='home':
    st.text_input('Search modules, diseases, or tools', key='query', placeholder='Try: dengue, dose, vaccine, jaundice, sepsis')
    st.markdown("<div class='title'>Departments</div>", unsafe_allow_html=True)
    ordered=[x for x in ['Pediatrics and Growth','Neonatology','AI Clinical Search','Medication Safety and Dose','Emergency Medicine','Metabolic and General Medicine','Hematology','HIV and ART Follow-up'] if x in search_modules(st.session_state.query)]
    for i in range(0,len(ordered),2):
        cols=st.columns(2)
        for j,name in enumerate(ordered[i:i+2]):
            with cols[j]:
                info=MODULES[name]
                tags=''.join([f"<span class='tag'>{t}</span>" for t in info['tags']])
                if st.button(name, key='open_'+name, on_click=open_dept, args=(name,)):
                    pass
                st.markdown(f"<div class='card {info['cls']}' style='margin-top:-42px; padding-top:48px;'><div class='title'>{name}</div><div class='desc'>{info['desc']}</div><div style='margin-top:.3rem'>{tags}</div></div>", unsafe_allow_html=True)
else:
    dept=st.session_state.dept
    st.button('Back to Home', on_click=go_home)
    source_badges(method='Clinician support layer', caution='Not for standalone diagnosis or order entry')

    if dept=='AI Clinical Search':
        with st.form('search'):
            c1,c2=st.columns([2,1])
            symptom=c1.text_input('Symptoms, question, or syndrome')
            age_group=c2.selectbox('Age group',['General','Pediatric','Neonate','Adult'])
            s=st.form_submit_button('Search evidence')
        if s and symptom:
            safety_note('Use this for evidence support only. Final decisions must follow local protocols, bedside assessment, and supervising clinician judgment.','warn')
            st.markdown("<div class='box'><b>ICMR</b><br><a href='https://www.icmr.gov.in/guidelines' target='_blank'>Open ICMR guideline library</a></div>", unsafe_allow_html=True)
            st.markdown("<div class='box'><b>NCDC</b><br><a href='https://ncdc.mohfw.gov.in/includes/Resource_Library/index.php?tab=Technical+Guidelines' target='_blank'>Open NCDC technical guidelines</a></div>", unsafe_allow_html=True)
            if age_group in ['Pediatric','Neonate']:
                st.markdown("<div class='box'><b>IAP</b><br><a href='https://pubmed.ncbi.nlm.nih.gov/41954836/' target='_blank'>Open IAP immunization update</a></div>", unsafe_allow_html=True)
            for r in pubmed_search_cached(f'{symptom} {age_group} India guideline review'):
                st.markdown(f"<div class='box'><a href='{r['url']}' target='_blank'>{r['title']}</a><br><span class='desc'>{r['source']} | {r['pubdate']}</span></div>", unsafe_allow_html=True)

    elif dept=='Pediatrics and Growth':
        tabs=st.tabs(['Growth','Weight estimate','Vitals','Fever','Fluids','Vaccine','Catch-up','Dehydration','ETAT triage','Emergency'])
        with tabs[0]:
            with st.form('p1'):
                c1,c2,c3=st.columns(3)
                age_m=c1.number_input('Age months',0,216,24)
                wt=c2.number_input('Weight kg',1.0,120.0,12.0)
                ht=c3.number_input('Height cm',30.0,220.0,85.0)
                s=st.form_submit_button('Calculate growth')
            if s:
                source_badges(indian='IAP', global_src='Standard bedside growth formula', method='BMI and quick expected-weight formula')
                c1,c2=st.columns(2); bmi=calc_bmi(wt,ht)
                c1.metric('BMI', f'{bmi:.2f}'); c2.metric('Expected weight', f'{expected_weight_kg(age_m):.1f} kg')
                safety_note(bmi_band(age_m/12,bmi),'note')
                safety_note('Screening support only. Confirm with age- and sex-specific growth charts before interpretation.','note')
        with tabs[1]:
            with st.form('p2'):
                age_y=st.number_input('Age years',0.0,18.0,3.0)
                s=st.form_submit_button('Estimate weight')
            if s:
                source_badges(indian='WHO ETAT / bedside estimate', global_src='Emergency weight estimate', method='Age-based estimate')
                st.metric('Estimated weight', f'{estimate_weight_age(age_y):.1f} kg')
                safety_note('Use actual measured weight whenever available. Estimated weight is a backup for emergency support only.','warn')
        with tabs[2]:
            with st.form('p3'):
                age_y=st.number_input('Age years ',0.0,18.0,3.0)
                s=st.form_submit_button('Interpret vitals')
            if s:
                band=pediatric_vitals_band(age_y)
                source_badges(indian='Pediatric triage support', global_src='WHO ETAT', method='Age-band vital reference')
                st.markdown(f"<div class='box'><b>Expected RR</b><br>{band['rr']}<br><b>Expected HR</b><br>{band['hr']}<br><b>Expected SBP</b><br>{band['sbp']}</div>", unsafe_allow_html=True)
                safety_note('Age-band vitals are a reference layer only, not a diagnosis.','note')
                safety_note('Interpret age-based vitals together with perfusion, mental status, hydration, and respiratory effort.','note')
        with tabs[3]:
            with st.form('p4'):
                c1,c2=st.columns(2)
                wt2=c1.number_input('Weight kg ',1.0,120.0,12.0)
                temp=c2.number_input('Temperature Â°C',35.0,42.0,38.4)
                s=st.form_submit_button('Fever support')
            if s:
                source_badges(indian='IAP / local pediatric protocol', global_src='Bedside dosing support', method='Weight-based antipyretic estimate')
                c1,c2,c3=st.columns(3); c1.metric('Paracetamol', f'{wt2*15:.0f} mg'); c2.metric('Ibuprofen', f'{wt2*10:.0f} mg'); c3.metric('Status', 'Fever' if temp>=38 else 'No fever')
                for step in PATHWAYS['Pediatric fever']: st.markdown(f"- {step}")
                safety_note('Dose shown is a quick estimate. Recheck age limits, concentration, dosing interval, dehydration risk, and maximum daily dose.','warn')
        with tabs[4]:
            with st.form('p5'):
                wt3=st.number_input('Weight kg  ',1.0,120.0,12.0)
                s=st.form_submit_button('Fluid support')
            if s:
                daily=maintenance_fluid_ml_day(wt3)
                source_badges(indian='Pediatric ward support', global_src='Holliday-Segar style estimate', method='Maintenance fluid formula')
                c1,c2=st.columns(2); c1.metric('Maintenance fluid', f'{daily:.0f} mL/day'); c2.metric('Hourly rate', f'{daily/24:.1f} mL/hr')
                safety_note('Do not use this as the final plan in shock, renal disease, severe malnutrition, DKA, meningitis, or ICU-level illness without protocol review.','warn')
        with tabs[5]:
            with st.form('p6'):
                dob=st.date_input('Date of birth', value=date.today()-timedelta(days=450))
                s=st.form_submit_button('Show vaccine due dates')
            if s:
                source_badges(indian='IAP / National schedule', global_src='Immunization timing support', method='Date-based due calculation')
                for label,days,items in VACCINE_SCHEDULE:
                    due=dob+timedelta(days=days)
                    st.markdown(f"<div class='box'><b>{label}</b><br>{due}<br><span class='desc'>{items}</span></div>", unsafe_allow_html=True)
                safety_note('Confirm catch-up status, prior documentation, product availability, and local immunization policy before final scheduling.','note')
        with tabs[6]:
            with st.form('p7'):
                missed=st.multiselect('Missed vaccines',['Birth vaccines','6 weeks visit','10 weeks visit','14 weeks visit','9 months visit','12 months visit','15 months visit'])
                s=st.form_submit_button('Catch-up helper')
            if s:
                source_badges(indian='IAP / National schedule', global_src='Catch-up planning support', method='Checklist helper')
                st.markdown("<div class='box'><b>Catch-up suggestion</b><br>Confirm prior records, identify missed visits, and rebuild using current IAP and national guidance without restarting unnecessary doses.</div>", unsafe_allow_html=True)
                for item in missed: st.markdown(f"- {item}")
                safety_note('This is a planning aid, not a definitive catch-up algorithm. Verify live schedule guidance.','warn')
        with tabs[7]:
            with st.form('p8'):
                c1,c2=st.columns(2)
                wt4=c1.number_input('Weight kg   ',1.0,120.0,12.0)
                status=c2.selectbox('Clinical dehydration',['No dehydration','Some dehydration','Severe dehydration'])
                s=st.form_submit_button('Dehydration support')
            if s:
                source_badges(indian='Pediatric protocol support', global_src='WHO-style dehydration estimate', method='Rehydration cue')
                st.metric('Estimated rehydration fluid', f'{dehydration_extra_ml(wt4,status):.0f} mL')
                safety_note('Use formal dehydration protocol for exact route, deficit replacement, sodium strategy, and shock management.','warn')
        with tabs[8]:
            with st.form('p9'):
                c1,c2,c3,c4=st.columns(4)
                can_drink=c1.selectbox('Can drink/feed?',['Yes','No'])
                conv=c2.selectbox('Convulsions?',['No','Yes'])
                distress=c3.selectbox('Severe respiratory distress?',['No','Yes'])
                lethargy=c4.selectbox('Lethargic/unconscious?',['No','Yes'])
                s=st.form_submit_button('ETAT triage')
            if s:
                emergency=any(x=='Yes' for x in [conv,distress,lethargy]) or can_drink=='No'
                source_badges(indian='Emergency pediatric triage support', global_src='WHO ETAT', method='Emergency sign screening')
                st.markdown(f"<div class='{'warn' if emergency else 'ok'}'><b>{'Emergency signs present' if emergency else 'No immediate ETAT emergency sign selected'}</b></div>", unsafe_allow_html=True)
                safety_note('This screens for emergency signs only. It does not replace full triage, examination, or resuscitation protocol.','warn')
        with tabs[9]:
            with st.form('p10'):
                c1,c2=st.columns(2)
                wt5=c1.number_input('Weight kg    ',1.0,120.0,16.0)
                glucose=c2.number_input('Bedside glucose mg/dL',20,600,80)
                s=st.form_submit_button('Emergency quick support')
            if s:
                source_badges(indian='Pediatric emergency support', global_src='Bedside emergency quick-reference', method='Quick dose cue')
                c1,c2,c3=st.columns(3); c1.metric('IN midazolam', f'{wt5*0.2:.2f} mg'); c2.metric('D10 bolus', f'{wt5*2:.0f} mL'); c3.metric('Hypoglycemia flag', 'Yes' if glucose<70 else 'No')
                safety_note('These are emergency quick cues only, not executable medication orders.','warn')
                safety_note('Recheck drug concentration, seizure protocol, IV access plan, and institutional emergency standards before administration.','warn')

    elif dept=='Neonatology':
        tabs=st.tabs(['Corrected age','Feeds','Daily fluids','Weight loss','Glucose/GIR','Bilirubin','Jaundice pathway'])
        with tabs[0]:
            with st.form('n1'):
                c1,c2=st.columns(2)
                gest=c1.number_input('Gestation at birth (weeks)',22,42,34)
                chrono=c2.number_input('Chronological age (weeks)',0,120,10)
                s=st.form_submit_button('Calculate corrected age')
            if s:
                source_badges(indian='Neonatal follow-up support', global_src='Corrected-age method', method='Prematurity adjustment')
                st.metric('Corrected age', f'{corrected_age_weeks(gest,chrono)} weeks')
                safety_note('Use corrected age for developmental interpretation and follow-up context in preterm infants.','note')
        with tabs[1]:
            with st.form('n2'):
                c1,c2=st.columns(2)
                wt=c1.number_input('Weight kg ',0.5,6.0,2.8)
                day=c2.number_input('Day of life',1,28,3)
                s=st.form_submit_button('Calculate feeds')
            if s:
                total=neonatal_feed_mlkgday(day)*wt
                source_badges(indian='Neonatal unit support', global_src='Day-of-life feed estimate', method='mL/kg/day table')
                c1,c2=st.columns(2); c1.metric('Total feed / day', f'{total:.0f} mL/day'); c2.metric('Approx every 3 hours', f'{total/8:.1f} mL/feed')
                safety_note('Final feed plan depends on gestation, illness, feeding route, tolerance, and NICU protocol.','warn')
        with tabs[2]:
            with st.form('n3'):
                c1,c2=st.columns(2)
                wt=c1.number_input('Weight kg  ',0.5,6.0,2.8)
                day=c2.number_input('Day of life ',1,28,3)
                s=st.form_submit_button('Calculate daily fluids')
            if s:
                total=neonatal_fluid_mlkgday(day)*wt
                source_badges(indian='Neonatal unit support', global_src='Day-of-life fluid estimate', method='mL/kg/day table')
                c1,c2=st.columns(2); c1.metric('Daily fluid estimate', f'{total:.0f} mL/day'); c2.metric('Hourly rate', f'{total/24:.1f} mL/hr')
                safety_note('Adjust for prematurity, phototherapy, humidity, sepsis, renal issues, and serum sodium trends.','warn')
        with tabs[3]:
            with st.form('n4'):
                c1,c2=st.columns(2)
                bw=c1.number_input('Birth weight kg',0.5,6.0,3.0)
                cw=c2.number_input('Current weight kg',0.5,6.0,2.7)
                s=st.form_submit_button('Calculate weight loss')
            if s:
                wl=weight_loss_percent(bw,cw)
                source_badges(indian='Newborn feeding review', global_src='Weight-loss percentage', method='Birth vs current weight')
                st.metric('Weight loss', f'{wl:.1f}%')
                safety_note('Interpret with urine output, feeding adequacy, jaundice, dehydration signs, and local newborn review thresholds.','warn' if wl>10 else 'note')
        with tabs[4]:
            with st.form('n5'):
                c1,c2,c3=st.columns(3)
                wt=c1.number_input('Weight kg   ',0.5,6.0,3.0)
                rate=c2.number_input('Infusion rate mL/hr',0.1,50.0,4.0)
                dex=c3.number_input('Dextrose %',2.5,25.0,10.0)
                s=st.form_submit_button('Calculate GIR')
            if s:
                source_badges(indian='NICU glucose support', global_src='GIR formula', method='mg/kg/min calculation')
                st.metric('GIR', f'{gir_from_dextrose(rate,dex,wt):.2f} mg/kg/min')
                safety_note('Always verify infusion composition, access, hypoglycemia protocol, and monitoring plan.','warn')
        with tabs[5]:
            with st.form('n6'):
                c1,c2=st.columns(2)
                ageh=c1.number_input('Age in hours',0,720,36)
                bili=c2.number_input('Total bilirubin mg/dL',0.0,40.0,12.0)
                preterm=st.checkbox('Preterm infant')
                risk=st.checkbox('Neurotoxicity / higher-risk features')
                s=st.form_submit_button('Assess bilirubin')
            if s:
                risk_text,tag=bilirubin_prompt(ageh,bili,preterm,risk)
                source_badges(indian='Neonatal jaundice protocol support', global_src='Age-in-hours bilirubin logic', method='Risk prompt only')
                st.markdown(f"<div class='{'warn' if 'Urgent' in risk_text or 'High' in risk_text else 'note'}'><b>{risk_text}</b></div>", unsafe_allow_html=True)
                safety_note(tag,'warn')
                safety_note('This is not a substitute for a validated bilirubin nomogram or local phototherapy/exchange protocol.','warn')
        with tabs[6]:
            source_badges(indian='Neonatal protocol support', global_src='Jaundice pathway', method='Checklist workflow')
            for step in PATHWAYS['Neonatal jaundice']: st.markdown(f"- {step}")
            safety_note('Use local NICU/newborn jaundice thresholds for treatment decisions.','warn')

    elif dept=='Medication Safety and Dose':
        tabs=st.tabs(['Dose','Interaction','Renal','Pregnancy/Lactation'])
        with tabs[0]:
            with st.form('m1'):
                c1,c2=st.columns(2)
                drug=c1.selectbox('Drug',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                wt=c2.number_input('Weight kg',1.0,200.0,20.0)
                s=st.form_submit_button('Calculate dose')
            if s:
                source_badges(indian='Drug-safety quick support', global_src='Weight-based dose estimate', method='mg/kg calculation')
                st.metric('Estimated single dose', f"{DRUGS[drug]['dose_mgkg']*wt:.2f} mg")
                safety_note('Check formulation, route, interval, renal/hepatic status, and age-band limits before prescribing or administering.','warn')
        with tabs[1]:
            with st.form('m2'):
                c1,c2=st.columns(2)
                d1=c1.text_input('Drug 1','warfarin')
                d2=c2.text_input('Drug 2','metronidazole')
                s=st.form_submit_button('Check interaction')
            if s:
                sev,msg=interaction_checker(d1,d2)
                source_badges(indian='Medication-safety quick support', global_src='Interaction cue', method='Small high-priority interaction list')
                st.markdown(f"<div class='{'warn' if sev in ['Contraindicated','Major','Moderate'] else 'ok'}'><b>{sev}</b><br>{msg}</div>", unsafe_allow_html=True)
                safety_note('This is not a complete interaction database. Review the full regimen, OTC drugs, supplements, and monitoring plan.','warn')
        with tabs[2]:
            with st.form('m3'):
                c1,c2=st.columns(2)
                drug2=c1.selectbox('Drug for renal note',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                egfr=c2.number_input('eGFR',0.0,200.0,60.0)
                s=st.form_submit_button('Show renal alert')
            if s:
                msg=DRUGS[drug2]['renal']
                if egfr<30: msg='High renal-risk situation. '+msg
                elif egfr<60: msg='Moderate renal-risk situation. '+msg
                source_badges(indian='Renal dosing alert support', global_src='Broad renal caution', method='Non-drug-specific alert layer')
                safety_note(msg,'note')
                safety_note('Use a trusted renal dosing reference for final interval or dose changes.','warn')
        with tabs[3]:
            with st.form('m4'):
                d=st.selectbox('Drug for pregnancy/lactation note',['paracetamol','ibuprofen','ondansetron','amoxicillin'])
                s=st.form_submit_button('Show notes')
            if s:
                source_badges(indian='Medication-safety support', global_src='Brief pregnancy/lactation prompt', method='Quick note only')
                st.markdown(f"<div class='box'><b>Pregnancy</b><br>{DRUGS[d]['preg']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='box'><b>Lactation</b><br>{DRUGS[d]['lact']}</div>", unsafe_allow_html=True)
                safety_note('Use a dedicated teratology/lactation reference for definitive decisions.','warn')

    elif dept=='Emergency Medicine':
        tabs=st.tabs(['qSOFA','Dengue','Rabies'])
        with tabs[0]:
            with st.form('e1'):
                c1,c2,c3=st.columns(3)
                rr=c1.number_input('Respiratory rate',0,80,24)
                sbp=c2.number_input('SBP',40,250,100)
                gcs=c3.number_input('GCS',3,15,15)
                s=st.form_submit_button('Calculate qSOFA')
            if s:
                score=(1 if rr>=22 else 0)+(1 if sbp<=100 else 0)+(1 if gcs<15 else 0)
                source_badges(indian='Emergency protocol support', global_src='qSOFA', method='Risk cue')
                st.metric('qSOFA', score)
                safety_note(qsofa_interpret(score),'note')
                for step in PATHWAYS['Sepsis quick pathway']: st.markdown(f"- {step}")
                safety_note('qSOFA is not a sepsis diagnosis and should not delay escalation in a clinically unstable patient.','warn')
        with tabs[1]:
            source_badges(indian='NCDC / local dengue protocol', global_src='Dengue triage pathway', method='Checklist workflow')
            for step in PATHWAYS['Dengue triage']: st.markdown(f"- {step}")
            safety_note('Use official dengue monitoring and referral protocols for final management.','warn')
        with tabs[2]:
            source_badges(indian='Rabies prophylaxis support', global_src='Rabies pathway', method='Checklist workflow')
            for step in PATHWAYS['Rabies PEP']: st.markdown(f"- {step}")
            safety_note('Verify local rabies vaccine and immunoglobulin schedules before administration.','warn')

    elif dept=='Metabolic and General Medicine':
        with st.form('g1'):
            c1,c2,c3,c4=st.columns(4)
            wt=c1.number_input('Weight kg',1.0,250.0,70.0)
            ht=c2.number_input('Height cm',30.0,250.0,170.0)
            sbp=c3.number_input('SBP ',50,300,120)
            dbp=c4.number_input('DBP ',30,200,80)
            s=st.form_submit_button('Calculate')
        if s:
            source_badges(indian='General bedside support', global_src='Standard formulas', method='BMI/BSA/MAP')
            bmi=calc_bmi(wt,ht); bsa=bsa_m2(wt,ht); mapv=map_calc(sbp,dbp)
            c1,c2,c3=st.columns(3); c1.metric('BMI', f'{bmi:.2f}'); c2.metric('BSA', f'{bsa:.2f} mÂ²'); c3.metric('MAP', f'{mapv:.1f} mmHg')
            safety_note(bmi_band(18,bmi),'note')
            safety_note(map_interpret(mapv),'note')
            safety_note('Interpret values in clinical context; these are support calculations only.','note')

    elif dept=='Hematology':
        with st.form('h1'):
            c1,c2,c3,c4=st.columns(4)
            mcv=c1.number_input('MCV',40.0,130.0,70.0)
            rbc=c2.number_input('RBC count',1.0,10.0,5.0)
            wbc=c3.number_input('WBC /uL',100.0,200000.0,6000.0)
            neut=c4.number_input('Neutrophils %',0.0,100.0,50.0)
            s=st.form_submit_button('Calculate')
        if s:
            source_badges(indian='CBC quick support', global_src='Standard hematology formulas', method='Mentzer and ANC')
            mi=mentzer_index(mcv,rbc); av=anc(wbc,neut)
            c1,c2=st.columns(2); c1.metric('Mentzer index', f'{mi:.2f}'); c2.metric('ANC', f'{av:.0f} /uL')
            age_group=st.selectbox('ANC interpretation group',['Child/Adult','Neonate'], key='anc_age_group')
            safety_note(mentzer_interpret(mi),'note')
            safety_note(anc_interpret(age_group,av),'note')
            safety_note('Use CBC trend, smear, ferritin/iron profile, and full clinical context for interpretation.','note')

    elif dept=='HIV and ART Follow-up':
        with st.form('a1'):
            visit=st.selectbox('Follow-up milestone',['Baseline','2 weeks','1 month','3 months','6 months'])
            s=st.form_submit_button('Show checklist')
        if s:
            source_badges(indian='ART follow-up support', global_src='Checklist workflow', method='Visit milestone checklist')
            checklists={'Baseline':['Confirm regimen, baseline labs, adherence counseling, opportunistic infection review.'],'2 weeks':['Early tolerance check, adherence check, danger symptoms review.'],'1 month':['Side effects, adherence reinforcement, interaction review.'],'3 months':['Clinical response, adherence, lab follow-up per protocol.'],'6 months':['Long-term adherence, adverse effects, viral load strategy per protocol.']}
            for item in checklists[visit]: st.markdown(f"- {item}")
            safety_note('Follow national or institutional ART protocols for final monitoring schedule and laboratory timing.','note')

    with st.expander('Sources and trust'):
        for name,url,desc in SOURCES:
            st.markdown(f"<div class='box'><b>{name}</b><br><a href='{url}' target='_blank'>{desc}</a></div>", unsafe_allow_html=True)
    st.download_button('Export current view', html_report(dept, f'Hardened export from {dept} module'), file_name=f'{dept}_hardened_report.html')
