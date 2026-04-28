import streamlit as st
import io
import math
from datetime import date, timedelta

st.set_page_config(page_title='IndiMed Pro 2026', layout='wide', page_icon='ðŸ©º')

st.markdown('''
<style>
:root {
  --bg1:#06101d; --bg2:#0d1c34; --card:#101c30; --border:#28456b;
  --text:#f8fbff; --muted:#d7e7ff; --soft:#a9c4eb; --blue:#3b82f6;
  --green:#22c55e; --red:#ef4444; --yellow:#f59e0b;
}
.stApp {background: linear-gradient(180deg,var(--bg1),var(--bg2)); color: var(--text);} 
html, body, [class*="css"] {color: var(--text);} 
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#08111f,#132746) !important; border-right:1px solid var(--border);} 
.main .block-container {padding: 1.2rem 1.4rem;} 
h1,h2,h3,h4,p,label,div,span {color: var(--text);} 
.hero {background: linear-gradient(135deg,#10203d,#17356a,#2452a8); border:1px solid #3b5f99; border-radius:18px; padding:20px; margin-bottom:16px;}
.hero p {color: var(--muted) !important;}
.stButton>button,.stDownloadButton>button {border:none !important; border-radius:12px !important; font-weight:700 !important; width:100% !important; color:white !important;}
.stButton>button {background: linear-gradient(135deg,#2563eb,#4f46e5) !important;}
.stDownloadButton>button {background: linear-gradient(135deg,#047857,#059669) !important;}
[data-testid="stMetric"] {background: linear-gradient(135deg,#0e1728,#16233a); border:1px solid var(--border); border-radius:14px; padding:12px;}
[data-testid="stMetricValue"] {color: var(--text) !important; font-weight:800 !important;}
[data-testid="stMetricLabel"] p {color: var(--muted) !important;}
.stTabs [data-baseweb="tab-list"] {background:#0f172a; border:1px solid var(--border); border-radius:12px; padding:4px;}
.stTabs [data-baseweb="tab"] {color: var(--muted); font-weight:700; border-radius:10px;}
.stTabs [aria-selected="true"] {background: linear-gradient(135deg,#2563eb,#4f46e5) !important; color:white !important;}
.alert-red,.alert-yellow,.alert-green {padding:12px 14px; border-radius:12px; font-weight:700;}
.alert-red {background:#3b0b12; border:1px solid #7f1d1d; color:#fecaca;}
.alert-yellow {background:#3b2a07; border:1px solid #92400e; color:#fde68a;}
.alert-green {background:#082b16; border:1px solid #166534; color:#bbf7d0;}
.badge-access,.badge-watch,.badge-reserve {padding:5px 12px; border-radius:999px; font-weight:800; display:inline-block;}
.badge-access {background:#14532d; color:#86efac;} .badge-watch {background:#78350f; color:#fde68a;} .badge-reserve {background:#7f1d1d; color:#fecaca;}
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

AWARE_DB = {
    'Amoxicillin':'ACCESS','Ampicillin':'ACCESS','Cefalexin':'ACCESS','Doxycycline':'ACCESS',
    'Cefixime':'WATCH','Azithromycin':'WATCH','Ceftriaxone':'WATCH','Piperacillin-Tazobactam':'WATCH',
    'Vancomycin':'WATCH','Meropenem':'RESERVE','Imipenem':'RESERVE','Colistin':'RESERVE','Linezolid':'RESERVE'
}
DDI_DB = {
    'Sildenafil':['Nitroglycerin','Isosorbide Mononitrate','Amlodipine'],
    'Clopidogrel':['Omeprazole','Esomeprazole','Aspirin'],
    'Warfarin':['Aspirin','Ibuprofen','Amiodarone','Clarithromycin'],
    'Atorvastatin':['Clarithromycin','Gemfibrozil'],
    'Spironolactone':['Enalapril','Telmisartan','Potassium Chloride'],
    'Amiodarone':['Warfarin','Digoxin'],
    'Digoxin':['Amiodarone','Verapamil']
}
GROWTH_REF = {
    'Male': {5:(18.7,2.5,110,4.5),10:(29.7,5.5,136,5.5),15:(49.5,9.5,164,6.5),18:(58.0,9.5,170,6.0)},
    'Female': {5:(17.5,2.5,109,4.5),10:(30.0,6.0,136,5.5),15:(47.5,8.0,157,5.5),18:(51.5,8.0,160,5.5)}
}
DEPTS = [
    'ðŸ’Š Medication Safety & Dose','âš–ï¸ Metabolic & General Med','ðŸ‘¶ Pediatrics & Growth','â¤ï¸ Cardiology (Lipids/Risk)',
    'ðŸ« Gastroenterology (Hepatology)','ðŸ§  Neurology (Emergency)','ðŸ©¸ Nephrology (eGFR Suite)','ðŸ‘ï¸ Ophthal & Ortho',
    'ðŸ¤° OB/GYN','ðŸ« ICU / Critical Care','ðŸš‘ Emergency Medicine','ðŸ§¬ Hematology'
]

with st.sidebar:
    st.markdown('## ðŸ©º IndiMed Pro 2026')
    dept = st.selectbox('Department', DEPTS)
    st.caption('Bright UI edition â€¢ India-focused CDS prototype')

st.markdown(f"<div class='hero'><h1>{dept}</h1><p>Choose inputs below to calculate clinical support values.</p></div>", unsafe_allow_html=True)

daily = 0

if dept == 'ðŸ’Š Medication Safety & Dose':
    t1, t2, t3 = st.tabs(['DDI Check','Dose Calculator','Extra Safety'])
    with t1:
        current = st.multiselect('Current medicines', sorted(DDI_DB.keys()))
        new = st.selectbox('New medicine', ['â€” Select â€”'] + sorted(DDI_DB.keys()))
        if new != 'â€” Select â€”':
            conflicts = [m for m in current if new in DDI_DB.get(m, []) or m in DDI_DB.get(new, [])]
            if conflicts:
                st.markdown(f"<div class='alert-red'>Interaction: {new} with {', '.join(conflicts)}</div>", unsafe_allow_html=True)
            elif current:
                st.markdown("<div class='alert-green'>No listed interaction found.</div>", unsafe_allow_html=True)
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
    with t3:
        crcl = st.number_input('Creatinine clearance / eGFR', 1.0, 200.0, 90.0)
        maxdose = st.number_input('Max daily dose (mg)', 1.0, 10000.0, 3000.0)
        st.metric('Max dose headroom', f'{max(0, maxdose-daily):.1f} mg')
        if crcl < 30:
            st.markdown("<div class='alert-yellow'>Renal dose adjustment needed</div>", unsafe_allow_html=True)
elif dept == 'âš–ï¸ Metabolic & General Med':
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
    if abx != 'â€” Select â€”':
        cat = AWARE_DB[abx]
        klass = {'ACCESS':'badge-access','WATCH':'badge-watch','RESERVE':'badge-reserve'}[cat]
        st.markdown(f"<span class='{klass}'>{abx}: {cat}</span>", unsafe_allow_html=True)
elif dept == 'ðŸ‘¶ Pediatrics & Growth':
    gender = st.radio('Gender', ['Male','Female'], horizontal=True)
    age = st.selectbox('Age (years)', [5,10,15,18])
    wt = st.number_input('Weight (kg)', 5.0, 120.0, 30.0)
    ht = st.number_input('Height (cm)', 80.0, 200.0, 135.0)
    wm,wsd,hm,hsd = GROWTH_REF[gender][age]
    wz = (wt - wm) / wsd
    hz = (ht - hm) / hsd
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Wt Z', f'{wz:.2f}')
    c2.metric('Wt %ile', f'{z_to_percentile(wz)}th')
    c3.metric('Ht Z', f'{hz:.2f}')
    c4.metric('Ht %ile', f'{z_to_percentile(hz)}th')
    wt2 = st.number_input('Weight for fluids (kg)', 1.0, 120.0, 20.0)
    maint = wt2*100 if wt2 <= 10 else 1000 + (wt2-10)*50 if wt2 <= 20 else 1500 + (wt2-20)*20
    c5,c6 = st.columns(2)
    c5.metric('Maintenance fluids/day', f'{maint:.0f} mL/day')
    c6.metric('Hourly rate', f'{maint/24:.1f} mL/hr')
elif dept == 'â¤ï¸ Cardiology (Lipids/Risk)':
    tc = st.number_input('Total cholesterol', 50, 500, 200)
    hdl = st.number_input('HDL-C', 10, 150, 45)
    tg = st.number_input('Triglycerides', 10, 1000, 150)
    sbp = st.number_input('SBP', 50, 250, 120)
    dbp = st.number_input('DBP', 30, 150, 80)
    ldl = tc - hdl - (tg/5.0)
    nonhdl = tc - hdl
    ratio = tc / hdl if hdl else 0
    mapv = (sbp + 2*dbp)/3
    pp = sbp - dbp
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric('LDL-C', f'{ldl:.1f}')
    c2.metric('Non-HDL-C', f'{nonhdl:.1f}')
    c3.metric('TC/HDL', f'{ratio:.1f}')
    c4.metric('MAP', f'{mapv:.1f}')
    c5.metric('Pulse pressure', f'{pp:.1f}')
elif dept == 'ðŸ« Gastroenterology (Hepatology)':
    cr = max(st.number_input('Creatinine (mg/dL)', 0.1, 15.0, 1.0), 1.0)
    bili = max(st.number_input('Bilirubin (mg/dL)', 0.1, 50.0, 1.0), 1.0)
    inr = max(st.number_input('INR', 0.1, 15.0, 1.1), 1.0)
    na = st.number_input('Sodium (mmol/L)', 100, 150, 137)
    meld = 10 * ((0.957*math.log(cr)) + (0.378*math.log(bili)) + (1.12*math.log(inr))) + 6.43
    na_b = max(125, min(140, na))
    meld_na = max(6, min(40, meld - na_b - (0.025 * meld * (140 - na_b)) + 140))
    albumin = st.number_input('Albumin (g/dL)', 1.0, 6.0, 3.5)
    c1,c2,c3 = st.columns(3)
    c1.metric('MELD', f'{meld:.1f}')
    c2.metric('MELD-Na', f'{meld_na:.1f}')
    c3.metric('Albumin', f'{albumin:.1f}')
elif dept == 'ðŸ§  Neurology (Emergency)':
    e = st.select_slider('Eye', options=[1,2,3,4], value=4)
    v = st.select_slider('Verbal', options=[1,2,3,4,5], value=5)
    m = st.select_slider('Motor', options=[1,2,3,4,5,6], value=6)
    pup = st.selectbox('Pupils', ['Both reactive','One unreactive','Both unreactive'])
    onset = st.number_input('Stroke onset hours', 0.0, 72.0, 2.0)
    pscore = {'Both reactive':0, 'One unreactive':1, 'Both unreactive':2}[pup]
    gcs = e + v + m
    gcsp = gcs - pscore
    c1,c2 = st.columns(2)
    c1.metric('GCS', f'{gcs}/15')
    c2.metric('GCS-P', f'{gcsp}/15')
    st.metric('Thrombolysis window', 'Possible' if onset <= 4.5 else 'Outside 4.5h')
elif dept == 'ðŸ©¸ Nephrology (eGFR Suite)':
    scr = st.number_input('Creatinine (mg/dL)', 0.1, 15.0, 1.0)
    age = st.number_input('Age', 18, 110, 50)
    gender = st.selectbox('Gender', ['Male','Female'])
    protein = st.selectbox('Proteinuria', ['Negative','Trace','1+','2+','3+'])
    k = 0.7 if gender == 'Female' else 0.9
    a = -0.241 if gender == 'Female' else -0.302
    gfr = 142 * (min(scr/k, 1)**a) * (max(scr/k, 1)**-1.2) * (0.9938**age)
    if gender == 'Female':
        gfr *= 1.012
    stage = 'G1' if gfr >= 90 else 'G2' if gfr >= 60 else 'G3a' if gfr >= 45 else 'G3b' if gfr >= 30 else 'G4' if gfr >= 15 else 'G5'
    c1,c2,c3 = st.columns(3)
    c1.metric('eGFR', f'{gfr:.1f}')
    c2.metric('CKD stage', stage)
    c3.metric('Nephrology flag', 'Yes' if protein in ['2+','3+'] else 'No')
elif dept == 'ðŸ‘ï¸ Ophthal & Ortho':
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
elif dept == 'ðŸ¤° OB/GYN':
    lmp = st.date_input('LMP date', value=date.today())
    cycle = st.number_input('Cycle length (days)', 21, 45, 28)
    bishop = st.number_input('Bishop score', 0, 13, 5)
    apgar = st.number_input('APGAR score', 0, 10, 9)
    ga_weeks = (date.today() - lmp).days / 7
    edd = lmp + timedelta(days=280 + (cycle - 28))
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Gestational age', f'{ga_weeks:.1f} weeks')
    c2.metric('EDD', str(edd))
    c3.metric('Labor readiness', 'Favorable' if bishop >= 8 else 'Unfavorable')
    c4.metric('APGAR', f'{apgar}/10')
elif dept == 'ðŸ« ICU / Critical Care':
    hr = st.number_input('Heart rate', 20, 250, 100)
    sbp = st.number_input('SBP', 30, 250, 110)
    pao2 = st.number_input('PaO2', 20, 500, 80)
    fio2 = st.number_input('FiO2 (%)', 21, 100, 40)
    gcs = st.number_input('GCS', 3, 15, 15)
    lact = st.number_input('Lactate', 0.1, 20.0, 1.5)
    shock = hr / sbp
    pfr = pao2 / (fio2/100)
    c1,c2,c3 = st.columns(3)
    c1.metric('Shock index', f'{shock:.2f}')
    c2.metric('P/F ratio', f'{pfr:.0f}')
    c3.metric('Sepsis concern', 'High' if lact >= 2.0 or gcs <= 8 else 'Lower')
elif dept == 'ðŸš‘ Emergency Medicine':
    rr = st.number_input('Respiratory rate', 4, 60, 18)
    spo2 = st.number_input('SpO2', 40, 100, 97)
    temp = st.number_input('Temperature (Â°C)', 34.0, 43.0, 37.0)
    gcs = st.number_input('GCS', 3, 15, 15)
    sbp = st.number_input('SBP', 30, 250, 120)
    hr = st.number_input('Heart rate', 20, 250, 90)
    shock = hr / sbp
    c1,c2,c3 = st.columns(3)
    c1.metric('Red flag', 'Yes' if rr > 24 or spo2 < 92 or temp >= 39.0 else 'No')
    c2.metric('Shock index', f'{shock:.2f}')
    c3.metric('Trauma concern', 'High' if gcs <= 12 or shock >= 1.0 else 'Lower')
elif dept == 'ðŸ§¬ Hematology':
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

st.markdown('---')
st.download_button('Export Report', export_note(f'IndiMed Pro Report\nDepartment: {dept}\nDate: {date.today()}\n'), f'IndiMed_{date.today()}.txt')
st.markdown("<div class='alert-red'>Clinical Decision Support only. Use under registered practitioner supervision.</div>", unsafe_allow_html=True)
