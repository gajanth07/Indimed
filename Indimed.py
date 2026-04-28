import streamlit as st
import io
import math
from datetime import date, timedelta

st.set_page_config(page_title='IndiMed Pro 2026', layout='wide')

st.markdown('''
<style>
:root { --bg:#ffffff; --bg2:#f7faff; --border:#d8e5f4; --text:#0f172a; --muted:#475569; --blue:#2563eb; --violet:#4f46e5; }
.stApp { background: linear-gradient(180deg,var(--bg),var(--bg2)); color: var(--text); }
html, body, [class*="css"] { color: var(--text); }
section[data-testid="stSidebar"] { display:none !important; }
.main .block-container { max-width: 1380px; padding: 1.2rem 1.3rem 2rem; }
.hero { background: linear-gradient(135deg,#ffffff,#edf5ff); border:1px solid #c7dbf3; border-radius:20px; padding:22px; margin-bottom:18px; }
.hero h1 { margin:0; color:#0f172a; }
.hero p { margin:.45rem 0 0; color:#334155 !important; }
.card { background:#fff; border:1px solid var(--border); border-radius:18px; padding:14px; box-shadow:0 4px 18px rgba(37,99,235,.06); }
.card h3 { margin:0 0 .35rem; font-size:1rem; }
.card p { margin:0 0 .8rem; color:#475569 !important; font-size:.92rem; min-height:52px; }
.stButton > button, .stDownloadButton > button { width:100% !important; border:none !important; border-radius:12px !important; font-weight:700 !important; color:white !important; }
.stButton > button { background: linear-gradient(135deg,var(--blue),var(--violet)) !important; }
.stDownloadButton > button { background: linear-gradient(135deg,#047857,#059669) !important; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--border); border-radius:14px; padding:12px; }
[data-testid="stMetricValue"] { color:#0f172a !important; font-weight:800 !important; }
[data-testid="stMetricLabel"] p { color:#475569 !important; }
.stTabs [data-baseweb="tab-list"] { background:#eef5ff; border:1px solid var(--border); border-radius:12px; padding:4px; }
.stTabs [data-baseweb="tab"] { color:#334155; font-weight:700; border-radius:10px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,var(--blue),var(--violet)) !important; color:white !important; }
.alert-red,.alert-yellow,.alert-green,.note { padding:12px 14px; border-radius:12px; font-weight:600; margin:.5rem 0; }
.alert-red { background:#fff1f2; border:1px solid #fecdd3; color:#881337; }
.alert-yellow { background:#fffbeb; border:1px solid #fde68a; color:#92400e; }
.alert-green { background:#ecfdf5; border:1px solid #a7f3d0; color:#065f46; }
.note { background:#eff6ff; border:1px solid #bfdbfe; color:#1e3a8a; }
.badge-access,.badge-watch,.badge-reserve { padding:5px 12px; border-radius:999px; font-weight:800; display:inline-block; }
.badge-access { background:#dcfce7; color:#166534; }
.badge-watch { background:#fef3c7; color:#92400e; }
.badge-reserve { background:#fee2e2; color:#991b1b; }
</style>
''', unsafe_allow_html=True)

def export_note(content):
    return io.BytesIO(content.encode())

def norm_cdf(z):
    b = [0.2316419, 0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429]
    t = 1.0 / (1.0 + b[0] * abs(z))
    poly = t * (b[1] + t * (b[2] + t * (b[3] + t * (b[4] + t * b[5]))))
    pdf_val = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    cdf = 1.0 - pdf_val * poly
    return cdf if z >= 0 else 1.0 - cdf

def z_to_percentile(z):
    return max(1, min(99, round(norm_cdf(z) * 100)))

def sampson_ldl(tc, hdl, tg):
    non_hdl = tc - hdl
    return tc/0.948 - hdl/0.971 - (tg/8.56 + (tg*non_hdl)/2140 - (tg*tg)/16100) - 9.44

def ckd_epi_2021(scr, age, female):
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    val = 142 * (min(scr/k, 1)**a) * (max(scr/k, 1)**-1.2) * (0.9938**age)
    if female:
        val *= 1.012
    return val

def meld3(bili, inr, cr, na, albumin, female):
    bili = max(1.0, bili)
    inr = max(1.0, inr)
    cr = min(3.0, max(1.0, cr))
    na = min(137, max(125, na))
    albumin = min(3.5, max(1.5, albumin))
    sex = 1 if female else 0
    score = 1.33*sex + 4.56*math.log(bili) + 0.82*(137-na) - 0.24*(137-na)*math.log(bili) + 9.09*math.log(inr) + 11.14*math.log(cr) + 1.85*(3.5-albumin) - 1.83*(3.5-albumin)*math.log(cr) + 6
    return round(score)

def interp(msg, level='note'):
    st.markdown(f"<div class='{level}'>{msg}</div>", unsafe_allow_html=True)


def decision_box(status, reason, next_step, red_flags='None entered'):
    style = 'alert-green' if status == 'Normal' else 'alert-yellow' if status == 'Borderline' else 'alert-red'
    st.markdown(f"<div class='{style}'><b>Status:</b> {status}<br><b>Reason:</b> {reason}<br><b>Suggested next step:</b> {next_step}<br><b>Red flags / refer now:</b> {red_flags}</div>", unsafe_allow_html=True)

AWARE_DB = {
    'Amoxicillin':'ACCESS','Ampicillin':'ACCESS','Cefalexin':'ACCESS','Doxycycline':'ACCESS','Cefixime':'WATCH','Azithromycin':'WATCH','Ceftriaxone':'WATCH','Piperacillin-Tazobactam':'WATCH','Vancomycin':'WATCH','Meropenem':'RESERVE','Imipenem':'RESERVE','Colistin':'RESERVE','Linezolid':'RESERVE'
}
DDI_DB = {
    'Sildenafil':['Nitroglycerin','Isosorbide Mononitrate','Amlodipine'],'Clopidogrel':['Omeprazole','Esomeprazole','Aspirin'],'Warfarin':['Aspirin','Ibuprofen','Amiodarone','Clarithromycin','Metronidazole'],'Atorvastatin':['Clarithromycin','Gemfibrozil','Cyclosporine'],'Spironolactone':['Enalapril','Telmisartan','Potassium Chloride'],'Metformin':['Iodinated Contrast','Alcohol'],'Amiodarone':['Warfarin','Digoxin','Simvastatin'],'Digoxin':['Amiodarone','Verapamil','Clarithromycin']
}
GROWTH_REF = {
    'Male': {5:(18.7,2.5,110,4.5),6:(20.5,2.8,116,4.5),7:(22.4,3.2,121,5.0),8:(24.5,3.8,126,5.0),9:(27.0,4.5,131,5.5),10:(29.7,5.5,136,5.5),11:(32.5,6.5,140,6.0),12:(36.0,7.5,146,6.5),13:(40.5,8.5,153,7.0),14:(45.5,9.0,160,7.0),15:(49.5,9.5,164,6.5),16:(53.0,9.5,167,6.0),17:(56.0,9.5,169,6.0),18:(58.0,9.5,170,6.0)},
    'Female': {5:(17.5,2.5,109,4.5),6:(19.5,2.8,114,4.5),7:(21.5,3.2,120,5.0),8:(23.8,4.0,125,5.0),9:(26.5,5.0,130,5.5),10:(30.0,6.0,136,5.5),11:(34.0,7.0,142,6.0),12:(38.0,7.5,148,6.5),13:(42.0,8.0,153,6.0),14:(45.0,8.0,156,6.0),15:(47.5,8.0,157,5.5),16:(49.5,8.0,158,5.5),17:(50.5,8.0,159,5.5),18:(51.5,8.0,160,5.5)}
}
VACCINE_SCHEDULE = [
    ('Birth', 'BCG, OPV-0, Hepatitis B birth dose'),
    ('6 weeks', 'OPV-1, Pentavalent-1, RVV-1, fIPV-1, PCV-1'),
    ('10 weeks', 'OPV-2, Pentavalent-2, RVV-2'),
    ('14 weeks', 'OPV-3, Pentavalent-3, IPV-2/fIPV as per program, RVV-3, PCV-2'),
    ('9-12 months', 'MR-1, JE-1 in endemic areas, PCV booster'),
    ('16-24 months', 'DPT booster-1, OPV booster, MR-2, JE-2 in endemic areas'),
    ('5-6 years', 'DPT booster-2'),
    ('10 years', 'Td'),
    ('16 years', 'Td')
]
DEPTS = [
    ('Medication Safety and Dose', 'Drug interaction checks, dose support, renal safety.'),
    ('Metabolic and General Medicine', 'BMI, body surface area, MAP, AWaRe support.'),
    ('Pediatrics and Growth', 'Growth, fluids, growth chart, vaccine schedule.'),
    ('Cardiology (Lipids and Risk)', 'Sampson LDL-C, non-HDL-C, blood pressure metrics.'),
    ('Gastroenterology (Hepatology)', 'MELD, MELD-Na, MELD 3.0 bedside support.'),
    ('Neurology (Emergency)', 'GCS-P and stroke timing support.'),
    ('Nephrology (eGFR Suite)', 'CKD-EPI 2021 eGFR and proteinuria flags.'),
    ('Ophthalmology and Orthopedics', 'Corrected IOP and bone risk score.'),
    ('OB/GYN', 'Pregnancy dating and labor support.'),
    ('ICU / Critical Care', 'Shock index, P/F ratio, sepsis concern.'),
    ('Emergency Medicine', 'Triage red flags and trauma concern.'),
    ('Hematology', 'Mentzer index, ANC, platelet flags.'),
    ('HIV / ART Follow-up', 'ART date planner and follow-up milestones.')
]

if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_dept' not in st.session_state:
    st.session_state.selected_dept = DEPTS[0][0]

def go_home():
    st.session_state.page = 'home'

def open_dept(name):
    st.session_state.selected_dept = name
    st.session_state.page = 'dept'

if st.session_state.page == 'home':
    st.markdown("<div class='hero'><h1>IndiMed Pro 2026</h1><p>Tap a department card to open its calculator page. This version adds pediatric growth support, vaccine schedule, HIV / ART follow-up planning, and interpretation text after calculations.</p></div>", unsafe_allow_html=True)
    st.markdown('### Departments')
    for row_start in range(0, len(DEPTS), 3):
        cols = st.columns(3)
        for i, (title, desc) in enumerate(DEPTS[row_start:row_start+3]):
            with cols[i]:
                st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
                st.button(f'Open {title}', key=f'open_{title}', on_click=open_dept, args=(title,))
else:
    dept = st.session_state.selected_dept
    top1, top2 = st.columns([5,1])
    with top1:
        st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Department calculator page with interpretation support</p></div>", unsafe_allow_html=True)
    with top2:
        st.button('â† Home', on_click=go_home)

    daily = 0

    if dept == 'Medication Safety and Dose':
        t1, t2, t3 = st.tabs(['DDI Check','Dose Calculator','Extra Safety'])
        with t1:
            current = st.multiselect('Current medicines', sorted(DDI_DB.keys()))
            new = st.selectbox('New medicine', ['â€” Select â€”'] + sorted(DDI_DB.keys()))
            if new != 'â€” Select â€”':
                conflicts = [m for m in current if new in DDI_DB.get(m, []) or m in DDI_DB.get(new, [])]
                if conflicts:
                    interp(f'Potential interaction detected between {new} and {", ".join(conflicts)}. This quick screen suggests closer drug-reference review before prescribing.', 'alert-red')
                elif current:
                    interp('No listed interaction found in the local quick-check database, but this does not replace a full interaction checker.', 'alert-green')
        with t2:
            wt = st.number_input('Weight (kg)', 0.5, 250.0, 70.0)
            mgkg = st.number_input('Dose (mg/kg)', 0.1, 500.0, 15.0)
            doses = st.number_input('Doses/day', 1, 24, 3)
            total = wt * mgkg
            daily = total * doses
            c1,c2,c3 = st.columns(3)
            c1.metric('Single dose', f'{total:.2f} mg')
            c2.metric('Daily dose', f'{daily:.2f} mg')
            c3.metric('Daily dose', f'{daily/1000:.3f} g')
            interp('Interpretation: the app multiplies body weight by the intended mg/kg dose and then by doses/day to estimate total daily exposure.', 'note')
        with t3:
            crcl = st.number_input('Creatinine clearance / eGFR', 1.0, 200.0, 90.0)
            maxdose = st.number_input('Max daily dose (mg)', 1.0, 10000.0, 3000.0)
            st.metric('Dose headroom', f'{max(0, maxdose-daily):.1f} mg')
            if crcl < 30:
                decision_box('Borderline', 'Renal function is reduced by the entered value.', 'Review renal dosing and consider interval adjustment.', 'Rapidly rising creatinine, oliguria, severe toxicity concern')
            else:
                decision_box('Normal', 'Entered renal function does not cross the low-function alert threshold.', 'Proceed with routine dose verification.', 'Unexpected adverse effects or uncertain renal baseline')

    elif dept == 'Metabolic and General Medicine':
        w = st.number_input('Weight (kg)', 5.0, 300.0, 70.0)
        h = st.number_input('Height (cm)', 50.0, 250.0, 170.0)
        waist = st.number_input('Waist (cm)', 20.0, 250.0, 85.0)
        sbp = st.number_input('SBP (mmHg)', 50, 250, 120)
        dbp = st.number_input('DBP (mmHg)', 30, 150, 80)
        abx = st.selectbox('Antibiotic', ['â€” Select â€”'] + sorted(AWARE_DB.keys()))
        bmi = w / ((h/100)**2)
        bsa = math.sqrt((w*h)/3600)
        wht = waist / h
        mapv = (sbp + 2*dbp) / 3
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('BMI', f'{bmi:.2f}')
        c2.metric('BSA', f'{bsa:.2f} mÂ²')
        c3.metric('Waist/Height', f'{wht:.2f}')
        c4.metric('MAP', f'{mapv:.1f} mmHg')
        if bmi >= 30:
            decision_box('High-risk', 'BMI is in the obesity range by the quick adult screening threshold.', 'Assess comorbidity risk, waist pattern, and management plan.', 'Severe obesity with uncontrolled BP, diabetes, breathlessness')
        elif bmi >= 25:
            decision_box('Borderline', 'BMI is in the overweight range by the quick adult screening threshold.', 'Advise risk review, diet and activity assessment.', 'Rapid weight gain or obesity-related complications')
        else:
            decision_box('Normal', 'BMI is below the quick overweight threshold used here.', 'Continue context-based metabolic risk assessment.', 'Unintentional weight loss or systemic illness')
        if abx != 'â€” Select â€”':
            cat = AWARE_DB[abx]
            klass = {'ACCESS':'badge-access','WATCH':'badge-watch','RESERVE':'badge-reserve'}[cat]
            st.markdown(f"<span class='{klass}'>{abx}: {cat}</span>", unsafe_allow_html=True)
            interp(f'{abx} is categorized as {cat} in this stewardship view to support antibiotic-use awareness.', 'note')

    elif dept == 'Pediatrics and Growth':
        t1, t2, t3 = st.tabs(['Growth','Growth Chart View','Vaccines'])
        with t1:
            gender = st.radio('Gender', ['Male','Female'], horizontal=True)
            age = st.number_input('Age (years)', 5, 18, 10)
            wt = st.number_input('Weight (kg)', 5.0, 120.0, 30.0)
            ht = st.number_input('Height (cm)', 80.0, 200.0, 135.0)
            nearest = min(GROWTH_REF[gender].keys(), key=lambda x: abs(x - age))
            wm,wsd,hm,hsd = GROWTH_REF[gender][nearest]
            wz = (wt - wm) / wsd
            hz = (ht - hm) / hsd
            c1,c2,c3,c4 = st.columns(4)
            c1.metric('Weight Z', f'{wz:.2f}')
            c2.metric('Weight percentile', f'{z_to_percentile(wz)}th')
            c3.metric('Height Z', f'{hz:.2f}')
            c4.metric('Height percentile', f'{z_to_percentile(hz)}th')
            wt2 = st.number_input('Weight for fluids (kg)', 1.0, 120.0, 20.0, key='pedfluids')
            maint = wt2*100 if wt2 <= 10 else 1000 + (wt2-10)*50 if wt2 <= 20 else 1500 + (wt2-20)*20
            temp = st.number_input('Temperature (Â°C)', 35.0, 43.0, 38.5)
            dosemgkg = st.number_input('Paracetamol-like dose (mg/kg)', 0.1, 30.0, 15.0)
            c5,c6,c7 = st.columns(3)
            c5.metric('Maintenance/day', f'{maint:.0f} mL/day')
            c6.metric('Hourly rate', f'{maint/24:.1f} mL/hr')
            c7.metric('Single dose', f'{wt2*dosemgkg:.1f} mg')
            if wz < -3 or hz < -3:
                decision_box('High-risk', 'Growth Z score is far below the reference mean.', 'Urgent pediatric growth/nutrition review is advisable.', 'Edema, severe wasting, dehydration, systemic illness')
            elif wz < -2 or hz < -2:
                decision_box('Borderline', 'Growth Z score is below the usual screening threshold.', 'Arrange formal anthropometry review and feeding history.', 'Crossing centiles, developmental concern, recurrent infection')
            else:
                decision_box('Normal', 'Growth values are not below the low screening threshold used here.', 'Continue routine growth monitoring.', 'Weight loss, feeding intolerance, chronic symptoms')
            if temp >= 38.0:
                interp('Fever is present by the entered temperature.', 'alert-yellow')
        with t2:
            age_points = sorted(GROWTH_REF[gender].keys()) if 'gender' in locals() else sorted(GROWTH_REF['Male'].keys())
            sel_gender = gender if 'gender' in locals() else 'Male'
            st.line_chart({
                'Weight mean': [GROWTH_REF[sel_gender][a][0] for a in age_points],
                'Height mean': [GROWTH_REF[sel_gender][a][2] for a in age_points]
            })
            interp('This simple chart shows reference mean growth values by age for the selected sex. It is a quick visual aid, not a full WHO/IAP percentile chart renderer.', 'note')
        with t3:
            child_age = st.selectbox('Child age band', [x[0] for x in VACCINE_SCHEDULE])
            for band, vaccines in VACCINE_SCHEDULE:
                if band == child_age:
                    st.markdown(f"<div class='card'><h3>{band}</h3><p>{vaccines}</p></div>", unsafe_allow_html=True)
            dob = st.date_input('Date of birth for next-vaccine planning', value=date.today() - timedelta(days=42), key='dob_vax')
            weeks = st.selectbox('Target visit', ['6 weeks','10 weeks','14 weeks','9 months','16-24 months'])
            days_map = {'6 weeks':42, '10 weeks':70, '14 weeks':98, '9 months':270, '16-24 months':540}
            due = dob + timedelta(days=days_map[weeks])
            st.metric('Planned vaccine date', str(due))
            interp('This vaccine planner is aligned to an India-style UIP quick schedule view and helps estimate the due date from the date of birth.', 'note')

    elif dept == 'Cardiology (Lipids and Risk)':
        tc = st.number_input('Total cholesterol (mg/dL)', 50, 500, 200)
        hdl = st.number_input('HDL-C (mg/dL)', 10, 150, 45)
        tg = st.number_input('Triglycerides (mg/dL)', 10, 1000, 150)
        sbp = st.number_input('SBP', 50, 250, 120)
        dbp = st.number_input('DBP', 30, 150, 80)
        ldl_s = sampson_ldl(tc, hdl, tg)
        nonhdl = tc - hdl
        ratio = tc / hdl if hdl else 0
        mapv = (sbp + 2*dbp)/3
        pp = sbp - dbp
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric('LDL-C (Sampson)', f'{ldl_s:.1f}')
        c2.metric('Non-HDL-C', f'{nonhdl:.1f}')
        c3.metric('TC/HDL', f'{ratio:.1f}')
        c4.metric('MAP', f'{mapv:.1f}')
        c5.metric('Pulse pressure', f'{pp:.1f}')
        if sbp >= 180 or dbp >= 120:
            decision_box('High-risk', 'Blood pressure is in a severely elevated range.', 'Urgent reassessment with symptom review is needed.', 'Chest pain, neuro deficit, pulmonary edema, severe headache')
        elif sbp >= 140 or dbp >= 90:
            decision_box('Borderline', 'Blood pressure is above a common clinic hypertension threshold.', 'Repeat properly and assess overall cardiovascular risk.', 'End-organ symptoms or very high repeat readings')
        else:
            decision_box('Normal', 'Blood pressure is below the quick hypertension alert threshold used here.', 'Continue routine cardiovascular risk review.', 'Persistent symptoms despite normal office readings')

    elif dept == 'Gastroenterology (Hepatology)':
        female = st.checkbox('Female sex')
        cr = st.number_input('Creatinine (mg/dL)', 0.1, 15.0, 1.0)
        bili = st.number_input('Bilirubin (mg/dL)', 0.1, 50.0, 1.0)
        inr = st.number_input('INR', 0.1, 15.0, 1.1)
        na = st.number_input('Sodium (mmol/L)', 100, 150, 137)
        albumin = st.number_input('Albumin (g/dL)', 1.0, 6.0, 3.5)
        cr_c = max(1.0, min(4.0, cr))
        bili_c = max(1.0, bili)
        inr_c = max(1.0, inr)
        na_b = max(125, min(137, na))
        meld = 10 * ((0.957*math.log(cr_c)) + (0.378*math.log(bili_c)) + (1.12*math.log(inr_c))) + 6.43
        meld_na = meld + 1.32 * (137 - na_b) - (0.033 * meld * (137 - na_b))
        meld_na = max(6, min(40, meld_na))
        meld_3 = meld3(bili, inr, cr, na, albumin, female)
        c1,c2,c3 = st.columns(3)
        c1.metric('MELD', f'{meld:.1f}')
        c2.metric('MELD-Na', f'{meld_na:.1f}')
        c3.metric('MELD 3.0', str(meld_3))
        if meld_3 >= 30:
            decision_box('High-risk', 'MELD 3.0 is markedly elevated.', 'Urgent hepatology or transplant-context review is advisable.', 'Encephalopathy, active bleeding, renal decline, severe hyponatremia')
        elif meld_3 >= 20:
            decision_box('Borderline', 'MELD 3.0 is elevated and may reflect important liver disease severity.', 'Review liver failure complications and follow-up urgency.', 'Rapid decompensation, infection, variceal bleed')
        else:
            decision_box('Normal', 'MELD 3.0 is not in the higher alert bands used here.', 'Continue disease-context review and surveillance.', 'Any acute decompensation signs')

    elif dept == 'Neurology (Emergency)':
        e = st.select_slider('Eye', options=[1,2,3,4], value=4)
        v = st.select_slider('Verbal', options=[1,2,3,4,5], value=5)
        m = st.select_slider('Motor', options=[1,2,3,4,5,6], value=6)
        pup = st.selectbox('Pupils', ['Both reactive','One unreactive','Both unreactive'])
        face = st.checkbox('Face droop')
        arm = st.checkbox('Arm weakness')
        speech = st.checkbox('Speech abnormal')
        onset = st.number_input('Onset hours', 0.0, 72.0, 2.0)
        pscore = {'Both reactive':0,'One unreactive':1,'Both unreactive':2}[pup]
        gcs = e + v + m
        gcsp = gcs - pscore
        c1,c2,c3 = st.columns(3)
        c1.metric('GCS', f'{gcs}/15')
        c2.metric('GCS-P', f'{gcsp}/15')
        c3.metric('FAST positive count', str(sum([face, arm, speech])))
        st.metric('Thrombolysis window', 'Possible' if onset <= 4.5 else 'Outside 4.5h')
        if sum([face, arm, speech]) >= 2 and onset <= 4.5:
            decision_box('High-risk', 'Multiple FAST features are present within a potentially actionable time window.', 'Activate urgent stroke pathway and imaging workflow.', 'Declining consciousness, seizure, airway compromise')
        elif sum([face, arm, speech]) >= 1:
            decision_box('Borderline', 'At least one FAST feature is present.', 'Prompt neurological review is appropriate.', 'New deficit progression or reduced GCS')
        else:
            decision_box('Normal', 'No FAST feature was selected in this screen.', 'Use clinical context; not all strokes are FAST-positive.', 'Any persistent new focal deficit')

    elif dept == 'Nephrology (eGFR Suite)':
        scr = st.number_input('Creatinine (mg/dL)', 0.1, 15.0, 1.0)
        age = st.number_input('Age', 18, 110, 50)
        gender = st.selectbox('Sex', ['Male','Female'])
        protein = st.selectbox('Proteinuria', ['Negative','Trace','1+','2+','3+'])
        gfr = ckd_epi_2021(scr, age, gender == 'Female')
        stage = 'G1' if gfr >= 90 else 'G2' if gfr >= 60 else 'G3a' if gfr >= 45 else 'G3b' if gfr >= 30 else 'G4' if gfr >= 15 else 'G5'
        c1,c2,c3 = st.columns(3)
        c1.metric('eGFR (CKD-EPI 2021)', f'{gfr:.1f}')
        c2.metric('CKD stage', stage)
        c3.metric('Nephrology flag', 'Yes' if protein in ['2+','3+'] else 'No')
        if gfr < 30:
            decision_box('High-risk', 'eGFR is in a severe reduction range.', 'Urgent renal review, medication review, and complication assessment are advisable.', 'Hyperkalemia, fluid overload, uremic symptoms')
        elif gfr < 60:
            decision_box('Borderline', 'eGFR is below 60 mL/min/1.73mÂ², an important CKD threshold if persistent.', 'Repeat, confirm chronicity, and assess albuminuria/proteinuria.', 'Rapid decline, nephrotic syndrome, refractory hypertension')
        else:
            decision_box('Normal', 'eGFR is not below the common CKD stage 3 threshold used in this quick screen.', 'Continue kidney-risk review in clinical context.', 'Proteinuria despite preserved eGFR')

    elif dept == 'Ophthalmology and Orthopedics':
        iop = st.number_input('Measured IOP', 5, 60, 20)
        cct = st.number_input('CCT (Î¼m)', 300, 800, 545)
        prior_fx = st.checkbox('Prior fragility fracture')
        smoker = st.checkbox('Smoker')
        steroid = st.checkbox('Steroid use')
        corrected = iop + ((545 - cct) / 50 * 2.5)
        score = (3 if prior_fx else 0) + (1 if smoker else 0) + (2 if steroid else 0)
        c1,c2 = st.columns(2)
        c1.metric('Corrected IOP', f'{corrected:.1f} mmHg')
        c2.metric('Bone risk score', f'{score}/6')
        if corrected > 30:
            decision_box('High-risk', 'Corrected IOP is markedly elevated.', 'Urgent ophthalmology review is appropriate.', 'Painful red eye, sudden vision change, nausea/vomiting')
        elif corrected > 21:
            decision_box('Borderline', 'Corrected IOP is above a common screening threshold.', 'Arrange ophthalmic review and correlate with disc/field findings.', 'Visual symptoms or angle-closure features')
        else:
            decision_box('Normal', 'Corrected IOP is not above the quick alert threshold used here.', 'Continue routine eye-risk assessment.', 'Any acute visual warning sign')

    elif dept == 'OB/GYN':
        lmp = st.date_input('LMP date', value=date.today())
        cycle = st.number_input('Cycle length (days)', 21, 45, 28)
        bishop = st.number_input('Bishop score', 0, 13, 5)
        si = st.number_input('Shock index', 0.1, 3.0, 0.8)
        apgar = st.number_input('APGAR score', 0, 10, 9)
        ga_weeks = (date.today() - lmp).days / 7
        edd = lmp + timedelta(days=280 + (cycle - 28))
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric('Gestational age', f'{ga_weeks:.1f} weeks')
        c2.metric('EDD', str(edd))
        c3.metric('Labor readiness', 'Favorable' if bishop >= 8 else 'Unfavorable')
        c4.metric('Shock risk', 'High' if si >= 0.9 else 'Lower')
        c5.metric('APGAR', f'{apgar}/10')
        if bishop >= 8:
            decision_box('Normal', 'Bishop score is in a commonly favorable range for induction readiness.', 'Proceed with labor plan per obstetric context.', 'Bleeding, fetal distress, maternal instability')
        elif bishop >= 6:
            decision_box('Borderline', 'Bishop score is intermediate rather than clearly favorable.', 'Consider reassessment or cervical ripening context.', 'Maternal or fetal compromise')
        else:
            decision_box('Borderline', 'Bishop score is not yet favorable.', 'Cervical ripening strategy may be needed before induction.', 'Any obstetric emergency overrides score-based planning')

    elif dept == 'ICU / Critical Care':
        hr = st.number_input('Heart rate', 20, 250, 100)
        sbp = st.number_input('SBP', 30, 250, 110)
        pao2 = st.number_input('PaO2', 20, 500, 80)
        fio2 = st.number_input('FiO2 (%)', 21, 100, 40)
        gcs = st.number_input('GCS', 3, 15, 15)
        lact = st.number_input('Lactate', 0.1, 20.0, 1.5)
        mapv = st.number_input('MAP', 20, 150, 70)
        shock = hr / sbp
        pfr = pao2 / (fio2/100)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Shock index', f'{shock:.2f}')
        c2.metric('P/F ratio', f'{pfr:.0f}')
        c3.metric('Sepsis concern', 'High' if lact >= 2.0 or mapv < 65 else 'Lower')
        c4.metric('Neuro concern', 'Yes' if gcs <= 8 else 'No')
        if pfr < 200 or shock >= 1.0 or mapv < 65:
            decision_box('High-risk', 'Oxygenation and/or perfusion variables are concerning.', 'Urgent critical care reassessment is advisable.', 'Escalating oxygen need, hypotension, altered sensorium')
        elif pfr < 300 or lact >= 2.0:
            decision_box('Borderline', 'There is moderate concern for impaired oxygenation or tissue hypoperfusion.', 'Repeat measurements and correlate with overall ICU picture.', 'Rising lactate, worsening gas exchange')
        else:
            decision_box('Normal', 'The entered perfusion and oxygenation values do not cross the alert thresholds used here.', 'Continue routine monitoring.', 'Any sudden deterioration')

    elif dept == 'Emergency Medicine':
        rr = st.number_input('Respiratory rate', 4, 60, 18)
        spo2 = st.number_input('SpO2', 40, 100, 97)
        temp = st.number_input('Temperature (Â°C)', 34.0, 43.0, 37.0)
        gcs = st.number_input('GCS', 3, 15, 15)
        sbp = st.number_input('SBP', 30, 250, 120)
        hr = st.number_input('Heart rate', 20, 250, 90)
        infection = st.checkbox('Suspected infection')
        mental = st.checkbox('Altered mental state')
        shock = hr / sbp
        qsofa_like = sum([mental, rr >= 22, sbp <= 100])
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Red flag', 'Yes' if rr > 24 or spo2 < 92 or temp >= 39.0 else 'No')
        c2.metric('Shock index', f'{shock:.2f}')
        c3.metric('Trauma concern', 'High' if gcs <= 12 or shock >= 1.0 else 'Lower')
        c4.metric('qSOFA', str(qsofa_like))
        if infection and qsofa_like >= 2:
            decision_box('High-risk', 'Suspected infection with qSOFA 2 or more increases concern for sepsis-related deterioration.', 'Urgent sepsis assessment and escalation are advisable.', 'Persistent hypotension, severe hypoxia, reduced GCS')
        elif qsofa_like == 1 or shock >= 1.0:
            decision_box('Borderline', 'At least one instability feature is present.', 'Repeat vitals, reassess trajectory, and watch closely.', 'Rapid worsening, cyanosis, refractory hypotension')
        else:
            decision_box('Normal', 'The entered data do not trigger the high sepsis-risk screen used here.', 'Continue routine triage with clinical judgment.', 'Any new organ dysfunction')

    elif dept == 'Hematology':
        hb = st.number_input('Hemoglobin', 1.0, 25.0, 12.0)
        mcv = st.number_input('MCV', 40.0, 130.0, 85.0)
        wbc = st.number_input('WBC', 0.1, 200.0, 7.0)
        neut = st.number_input('Neutrophils %', 0.0, 100.0, 60.0)
        bands = st.number_input('Bands %', 0.0, 50.0, 0.0)
        platelets = st.number_input('Platelets', 1.0, 1000.0, 250.0)
        mentzer = mcv / hb if hb else 0
        anc = wbc * (neut + bands) / 100
        c1,c2,c3 = st.columns(3)
        c1.metric('Mentzer index', f'{mentzer:.2f}')
        c2.metric('ANC', f'{anc:.2f} x10^9/L')
        c3.metric('Platelet flag', 'Low' if platelets < 150 else 'Normal')
        if anc < 0.5:
            decision_box('High-risk', 'Absolute neutrophil count is severely low.', 'Urgent infection-risk assessment is required.', 'Fever with neutropenia, sepsis signs')
        elif mentzer >= 13:
            decision_box('Borderline', 'Mentzer index leans toward iron-deficiency pattern in microcytic screening logic.', 'Correlate with ferritin and smear.', 'Symptomatic anemia or bleeding')
        else:
            decision_box('Borderline', 'Mentzer index leans toward thalassemia-trait pattern in screening logic.', 'Correlate with RBC indices and confirmatory testing.', 'Severe anemia or hemolysis signs')

    elif dept == 'HIV / ART Follow-up':
        t1, t2 = st.tabs(['ART Planner','Follow-up Interpretation'])
        with t1:
            art_start = st.date_input('ART start date', value=date.today())
            tb_coinfection = st.checkbox('TB coinfection present')
            cd4_lt_50 = st.checkbox('CD4 < 50 cells/ÂµL')
            follow_4w = art_start + timedelta(days=28)
            follow_3m = art_start + timedelta(days=90)
            follow_6m = art_start + timedelta(days=180)
            follow_12m = art_start + timedelta(days=365)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric('4-week review', str(follow_4w))
            c2.metric('3-month review', str(follow_3m))
            c3.metric('6-month review', str(follow_6m))
            c4.metric('12-month review', str(follow_12m))
            if tb_coinfection:
                if cd4_lt_50:
                    decision_box('Borderline', 'TB coinfection with very low CD4 usually supports earlier ART timing in many care frameworks.', 'Align with HIV/TB protocol and monitor IRIS risk.', 'Severe TB, CNS disease, adherence barriers')
                else:
                    decision_box('Borderline', 'TB coinfection still usually requires timely ART planning.', 'Coordinate HIV and TB follow-up schedules carefully.', 'Clinical deterioration or drug-toxicity concerns')
        with t2:
            interp('Quick schedule logic: early post-ART follow-up is important for adherence, adverse effects, and virologic monitoring. This page is a planning aid, not a replacement for NACO or local HIV clinic protocol.', 'note')

    st.markdown('---')
    st.download_button('Export Report', export_note(f'IndiMed Pro Report\nDepartment: {dept}\nDate: {date.today()}\n'), f'IndiMed_{date.today()}.txt')
    st.markdown("<div class='alert-red'>Clinical Decision Support only. Added modules include pediatric growth support, India-style vaccine schedule planning, and ART follow-up date planning. All outputs require clinician verification before patient treatment decisions.</div>", unsafe_allow_html=True)
