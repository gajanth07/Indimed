import streamlit as st
from datetime import date, timedelta
import io
import math

# --- Configuration & UI (India‑style hospital dashboard) ---
st.set_page_config(
    page_title="IndiMed Pro 2026: India CDS",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Global India‑dark theme */
:root {
    --bg-100: #07111f;
    --bg-150: #0a1a30;
    --accent-1: #2563eb;
    --accent-2: #14532d;
    --fg-100: #e5eefb;
    --fg-200: #cbd5e1;
    --border-100: #1f3357;
}
* { font-family: 'Inter', sans-serif; }
body, html, [class*="css"] {
    background: linear-gradient(180deg, var(--bg-100) 0%, var(--bg-150) 100%);
    color: var(--fg-100);
}

.hero {
    background: linear-gradient(135deg, #0f172a, #172554, #1d4ed8);
    border: 1px solid #274b86;
    border-radius: 20px;
    padding: 24px 26px;
    margin: 0 0 20px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.hero h1 { margin: 0; font-size: 1.9rem; font-weight: 800; }
.hero p { margin: 8px 0 0 0; color: #bfd2f7; font-size: 0.95rem; }

.card {
    background: rgba(10, 18, 33, 0.94);
    border: 1px solid #1e3358;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}

/* Buttons & metrics */
.stButton > button, .stDownloadButton > button {
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    width: 100% !important;
    height: 3em !important;
}
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: white !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #065f46, #047857) !important;
    color: white !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0b1220, #111b30);
    border: 1px solid #21385f;
    border-radius: 16px;
    padding: 16px 18px;
}
[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] p {
    color: #8ca3c7 !important; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.8px;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0f172a;
    border-radius: 14px;
    padding: 6px;
    border: 1px solid #223a62;
}
.stTabs [data-baseweb="tab"] { color: #94a3b8; border-radius: 10px; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #2563eb, #4f46e5) !important; color: white !important; }

/* Alerts */
.alert-red { background: linear-gradient(135deg, #3b0000, #5b0b0b); border: 1px solid #ef4444; color: #fecaca; padding: 14px 16px; border-radius: 14px; font-weight: 700; }
.alert-yellow { background: linear-gradient(135deg, #3f2a00, #5a4100); border: 1px solid #f59e0b; color: #fde68a; padding: 14px 16px; border-radius: 14px; font-weight: 700; }
.alert-green { background: linear-gradient(135deg, #052e16, #0f3d23); border: 1px solid #22c55e; color: #bbf7d0; padding: 14px 16px; border-radius: 14px; font-weight: 700; }

/* Categories */
.badge-access { background: #14532d; color: #86efac; padding: 5px 14px; border-radius: 999px; font-weight: 800; display: inline-block; font-size: 0.85rem; }
.badge-watch { background: #4a2f00; color: #fde68a; padding: 5px 14px; border-radius: 999px; font-weight: 800; display: inline-block; font-size: 0.85rem; }
.badge-reserve { background: #4a0d0d; color: #fca5a5; padding: 5px 14px; border-radius: 999px; font-weight: 800; display: inline-block; font-size: 0.85rem; }

.smallnote { color: #94a3b8; font-size: 0.9rem; }

/* Footer */
.footer-banner {
    background: #172554;
    border-top: 1px solid #274b86;
    border-radius: 16px;
    padding: 16px 18px;
    margin-top: 18px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Helpers ---
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

# --- 3. India‑aligned databases ---
AWARE_DB = {
    "Amoxicillin": "ACCESS", "Ampicillin": "ACCESS", "Cefalexin": "ACCESS",
    "Doxycycline": "ACCESS",
    "Cefixime": "WATCH", "Azithromycin": "WATCH", "Ceftriaxone": "WATCH",
    "Piperacillin‑Tazobactam": "WATCH", "Vancomycin": "WATCH",
    "Meropenem": "RESERVE", "Imipenem": "RESERVE", "Colistin": "RESERVE",
    "Tigecycline": "RESERVE", "Linezolid": "RESERVE",
}

DDI_DB = {
    "Sildenafil": ["Nitroglycerin", "Isosorbide Mononitrate", "Amlodipine"],
    "Clopidogrel": ["Omeprazole", "Esomeprazole", "Aspirin"],
    "Warfarin": ["Aspirin", "Ibuprofen", "Amiodarone", "Clarithromycin", "Metronidazole"],
    "Atorvastatin": ["Clarithromycin", "Gemfibrozil", "Cyclosporine"],
    "Spironolactone": ["Enalapril", "Telmisartan", "Potassium Chloride"],
    "Metformin": ["Iodinated Contrast", "Alcohol"],
    "Amiodarone": ["Warfarin", "Digoxin", "Simvastatin"],
    "Digoxin": ["Amiodarone", "Clarithromycin", "Verapamil"],
}

GROWTH_REF = {
    "Male": {
        5:  (18.7, 2.5, 110, 4.5),
        6:  (20.5, 2.8, 116, 4.5),
        7:  (22.4, 3.2, 121, 5.0),
        8:  (24.5, 3.8, 126, 5.0),
        9:  (27.0, 4.5, 131, 5.5),
        10: (29.7, 5.5, 136, 5.5),
        11: (32.5, 6.5, 140, 6.0),
        12: (36.0, 7.5, 146, 6.5),
        13: (40.5, 8.5, 153, 7.0),
        14: (45.5, 9.0, 160, 7.0),
        15: (49.5, 9.5, 164, 6.5),
        16: (53.0, 9.5, 167, 6.0),
        17: (56.0, 9.5, 169, 6.0),
        18: (58.0, 9.5, 170, 6.0),
    },
    "Female": {
        5:  (17.5, 2.5, 109, 4.5),
        6:  (19.5, 2.8, 114, 4.5),
        7:  (21.5, 3.2, 120, 5.0),
        8:  (23.8, 4.0, 125, 5.0),
        9:  (26.5, 5.0, 130, 5.5),
        10: (30.0, 6.0, 136, 5.5),
        11: (34.0, 7.0, 142, 6.0),
        12: (38.0, 7.5, 148, 6.5),
        13: (42.0, 8.0, 153, 6.0),
        14: (45.0, 8.0, 156, 6.0),
        15: (47.5, 8.0, 157, 5.5),
        16: (49.5, 8.0, 158, 5.5),
        17: (50.5, 8.0, 159, 5.5),
        18: (51.5, 8.0, 160, 5.5),
    },
}

# --- 4. Department list (exact match) ---
DEPTS = {
    "🔍 Symptom Search AI": "Search‑based differential support",
    "💊 Medication Safety & Dose": "Drug safety and dose checks",
    "⚖️ Metabolic & General Med (ICMR 2026)": "BMI, waist‑height, BP, AWaRe",
    "👶 Pediatrics (IAP 2015)": "Growth‑Z, fluids, fever dose",
    "❤️ Cardiology (Lipids/Risk)": "LDL‑C, MAP, TC‑HDL‑ratio",
    "🫁 Gastroenterology (MELD‑Na/Child‑Pugh)": "MELD, MELD‑Na, Child‑like score",
    "🧠 Neurology (GCS‑P / Stroke)": "GCS‑P, FAST, triage flags",
    "🩸 Nephrology (eGFR/CKD)": "CKD‑EPI 2021, CKD‑stage",
    "👁️ Ophthal & Ortho / FRAX": "IOP correction, bone‑risk score",
    "🤰 OB/GYN (Pregnancy‑India)": "EDD, gestational age, APGAR/PPH",
    "🫁 ICU (India SaO2/MAP)": "Shock index, PF‑ratio",
    "🚑 Emergency (Triage/SepticScreen)": "Triage flags, qSOFA‑like screen",
    "🧬 Hematology (Anemia/ANC)": "Mentzer, ANC, platelet flags",
}

icons = {
    "🔍 Symptom Search AI": "🔍",
    "💊 Medication Safety & Dose": "💊",
    "⚖️ Metabolic & General Med (ICMR 2026)": "⚖️",
    "👶 Pediatrics (IAP 2015)": "👶",
    "❤️ Cardiology (Lipids/Risk)": "❤️",
    "🫁 Gastroenterology (MELD‑Na/Child‑Pugh)": "🫁",
    "🧠 Neurology (GCS‑P / Stroke)": "🧠",
    "🩸 Nephrology (eGFR/CKD)": "🩸",
    "👁️ Ophthal & Ortho / FRAX": "👁️",
    "🤰 OB/GYN (Pregnancy‑India)": "🤰",
    "🫁 ICU (India SaO2/MAP)": "🫁",
    "🚑 Emergency (Triage/SepticScreen)": "🚑",
    "🧬 Hematology (Anemia/ANC)": "🧬",
}

# --- 5. Sidebar ---
with st.sidebar:
    st.markdown("## 🩺 IndiMed Pro 2026")
    st.markdown("India‑oriented CDS Assistant")
    dept = st.selectbox("Department", list(DEPTS.keys()), index=0)
    st.caption("Standards: ICMR 2026 / IAP 2015 / WHO / CKD‑EPI / UNOS")
    st.markdown("---")
    st.markdown("Patient safety notice:", unsafe_allow_html=True)
    st.markdown(
        '<div class="smallnote"><b>🛑 This is a decision‑support prototype.</b> Use under supervision of a registered practitioner.</div>',
        unsafe_allow_html=True
    )

# --- 6. Hero + report object ---
st.markdown(
    f'<div class="hero"><h1>{icons[dept]} {dept}</h1><p>{DEPTS[dept]}</p></div>',
    unsafe_allow_html=True
)
report = {"department": dept, "date": str(date.today()), "calculations": {}}

# --- 7. Formula‑corrected department implementations ---

if dept == "🔍 Symptom Search AI":
    symp = st.text_area(
        "Patient presentation",
        height=120,
        placeholder="e.g., fever, cough, neck stiffness, 3 days, 28‑year‑female",
    )
    if st.button("🔍 Analyze Research") and symp:
        st.markdown('<div class="card"><b>Search note</b><br><span class="smallnote">This is an evidence‑search assistant; final diagnosis must be made by a clinician.</span></div>', unsafe_allow_html=True)
        st.info("This is a clinical‑search assist module (not diagnosis).")

elif dept == "💊 Medication Safety & dose":
