# Indimed upgraded build
# Includes lactation-drug catalog merge into dose calculator, growth percentile helper support, head circumference support scaffolding, and pictorial percentile projection helpers.
# Exact under-5 WHO/IAP LMS plotting still requires full official dataset embedding for final chart-grade accuracy.

# Final updated Indimed app build assembled from the latest provided GitHub source.
# Includes prior architecture updates already present in the source file, plus this release note header.
# Important: full source-mapped verification for every calculator and all 200+ drugs is not yet completed; use embedded clinical-support outputs with guideline confirmation.

import json
PROTOCOL_REGISTRY = {
  "bmi": {
    "protocol": "WHO Growth Standards + IAP pediatric nutrition/obesity guidance",
    "year": "WHO standards; IAP topic guidance",
    "thresholds": "Age- and sex-specific growth charts required",
    "exclusions": [
      "Do not use adult BMI categories in children",
      "Edema can distort interpretation"
    ],
    "red_flags": [
      "Rapid weight loss",
      "Edema",
      "Faltering growth",
      "Systemic symptoms"
    ],
    "alternatives": [
      "Constitutional thinness",
      "Endocrine disease",
      "Chronic disease",
      "Measurement error"
    ]
  },
  "dehydration": {
    "protocol": "ICMR STW Acute Diarrhea",
    "year": "2019",
    "thresholds": "Plan A/B/C by dehydration class",
    "exclusions": [
      "Use caution in SAM, cardiac disease, renal disease"
    ],
    "red_flags": [
      "Lethargy",
      "Drinks poorly",
      "Shock signs",
      "Severe malnutrition"
    ],
    "alternatives": [
      "DKA",
      "Sepsis",
      "Surgical abdomen",
      "Adrenal crisis"
    ]
  },
  "map": {
    "protocol": "WHO ETAT + ICMR pediatric sepsis/shock workflow",
    "year": "WHO ETAT 2016; ICMR STW 2019",
    "thresholds": "Low perfusion concern if below age floor",
    "exclusions": [
      "Do not use MAP alone to exclude shock"
    ],
    "red_flags": [
      "Cold extremities",
      "Prolonged CRT",
      "Altered sensorium",
      "Weak pulses"
    ],
    "alternatives": [
      "Wrong cuff size",
      "Device error",
      "Cardiac disease",
      "Dehydration"
    ]
  },
  "mentzer": {
    "protocol": "IAP anemia guidance + Indian pediatric anemia context",
    "year": "IAP 2022",
    "thresholds": "Lower values favor thal trait pattern, higher values favor IDA pattern",
    "exclusions": [
      "Not diagnostic alone"
    ],
    "red_flags": [
      "Severe pallor",
      "Hemolysis signs",
      "Transfusion need"
    ],
    "alternatives": [
      "Mixed deficiency",
      "Chronic inflammation",
      "Lead exposure",
      "Hemoglobinopathy"
    ]
  },
  "anc": {
    "protocol": "Indian hematology/pediatric unit protocol",
    "year": "Unit policy",
    "thresholds": "Severity banding by ANC level",
    "exclusions": [
      "Interpret with fever and trend"
    ],
    "red_flags": [
      "Fever",
      "Toxic look",
      "Mucositis",
      "Recurrent infection"
    ],
    "alternatives": [
      "Viral suppression",
      "Drug effect",
      "Autoimmune neutropenia",
      "Marrow failure"
    ]
  },
  "bilirubin": {
    "protocol": "Neonatal jaundice protocol / unit nomogram",
    "year": "Unit policy",
    "thresholds": "Hour-specific bilirubin thresholds",
    "exclusions": [
      "Do not decide phototherapy by a single untimed value"
    ],
    "red_flags": [
      "<24h jaundice",
      "Poor feeding",
      "Lethargy",
      "Prematurity"
    ],
    "alternatives": [
      "Hemolysis",
      "Sepsis",
      "G6PD deficiency",
      "Cholestasis"
    ]
  },
  "gir": {
    "protocol": "NICU hypoglycemia protocol",
    "year": "Unit policy",
    "thresholds": "Clinical target varies by infant and glucose trend",
    "exclusions": [
      "Do not use GIR without bedside glucose data"
    ],
    "red_flags": [
      "Symptomatic hypoglycemia",
      "Seizure",
      "Recurrent low sugar"
    ],
    "alternatives": [
      "Hyperinsulinism",
      "Sepsis",
      "Pump error",
      "Wrong concentration"
    ]
  },
  "bsa": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "maintenance_fluid": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "expected_weight": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "weight_loss": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "corrected_age": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "qsofa": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "sodium_deficit": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "free_water_deficit": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "corrected_sodium": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "corrected_calcium": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "anion_gap": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "infusion_rate": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "neonatal_feed": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "neonatal_fluid": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  },
  "bolus": {
    "protocol": "Indian clinical protocol context",
    "year": "Clinical standard",
    "thresholds": "Calculator-specific context dependent range",
    "exclusions": [
      "Requires clinical correlation"
    ],
    "red_flags": [
      "Unstable patient",
      "Result inconsistent with exam"
    ],
    "alternatives": [
      "Measurement error",
      "Mixed pathology",
      "Context-specific differential"
    ]
  }
}
THRESHOLD_REGISTRY = {
  "pediatric_map_floor_formula": "SBP lower limit approx <70 if <1 year; else <70 + 2*age years",
  "fever_definition": "Core temperature >= 38.0 C or axillary > 37.5 C",
  "dehydration_plans": "No dehydration, Some dehydration, Severe dehydration",
  "qsofa_range": "0-3",
  "mentzer_hint": "<13 favors thal trait pattern; >13 favors IDA pattern support only"
}

DRUG_DATABASE = {
    "paracetamol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ibuprofen": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amoxicillin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amoxicillin clavulanate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefixime": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ceftriaxone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefotaxime": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cephalexin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "azithromycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "clarithromycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "clindamycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "metronidazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vancomycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amikacin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "gentamicin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "piperacillin tazobactam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "meropenem": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "linezolid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "flucloxacillin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "doxycycline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "oseltamivir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "acyclovir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "fluconazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amphotericin b": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "albendazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "mebendazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "artesunate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "artemether lumefantrine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "chloroquine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "primaquine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "salbutamol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "levosalbutamol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ipratropium": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "budesonide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "beclomethasone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "hydrocortisone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "prednisolone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dexamethasone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "methylprednisolone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "montelukast": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cetirizine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "chlorpheniramine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "pheniramine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "adrenaline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "noradrenaline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dopamine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dobutamine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "milrinone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "furosemide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "spironolactone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "mannitol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "diazepam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "midazolam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "lorazepam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "phenytoin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "levetiracetam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "phenobarbital": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "valproate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "carbamazepine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "clobazam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ondansetron": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "domperidone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "pantoprazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "omeprazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "famotidine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "lactulose": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "zinc": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ors": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vitamin a": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vitamin d": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "iron folic acid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "calcium carbonate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "magnesium sulfate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "potassium chloride": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "sodium bicarbonate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dextrose 10": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dextrose 25": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "normal saline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ringer lactate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dns": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "insulin regular": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "insulin nph": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "metformin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "glucagon": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "levothyroxine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "hydralazine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amlodipine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "enalapril": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "captopril": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "propranolol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "digoxin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "adenosine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amiodarone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "atropine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "aspirin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "clopidogrel": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "heparin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "enoxaparin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "warfarin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tranexamic acid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "packed red cells": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "platelets": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "fresh frozen plasma": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "albumin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "surfactant": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "caffeine citrate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "aminophylline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "theophylline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "sildenafil": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "bosentan": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "isoniazid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rifampicin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "pyrazinamide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ethambutol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "streptomycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "pyridoxine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "co trimoxazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "nitrofurantoin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "colistin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "clotrimazole": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "nystatin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "permethrin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ivermectin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "hydroxyurea": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "folic acid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cyanocobalamin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "epoetin alfa": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "allopurinol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rasburicase": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cyclophosphamide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "methotrexate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vincristine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dactinomycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "etoposide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "doxorubicin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "daunorubicin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "mesna": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "granisetron": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "morphine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "fentanyl": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tramadol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ketamine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "propofol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "thiopentone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rocuronium": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vecuronium": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "succinylcholine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "glycopyrrolate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "neostigmine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "lignocaine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "bupivacaine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "chloral hydrate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "melatonin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "haloperidol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "risperidone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "olanzapine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "sertraline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "fluoxetine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "abacavir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "lamivudine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "zidovudine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tenofovir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dolutegravir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "efavirenz": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "lopinavir ritonavir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "nevirapine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ampicillin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ampicillin sulbactam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefepime": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ertapenem": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tigecycline": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "aztreonam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "teicoplanin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefoperazone sulbactam": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefuroxime": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefpodoxime": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tobramycin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "mupirocin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "povidone iodine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "silver sulfadiazine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "oral rehydration salts": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rifaximin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ursodeoxycholic acid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "loperamide": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "chloramphenicol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rabies vaccine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "rabies immunoglobulin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "anti snake venom": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "tetanus toxoid": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "vitamin k": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "phytonadione": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "naloxone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "flumazenil": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "desmopressin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "prednisone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "calcitriol": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "phosphate supplement": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "sodium chloride 3": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "levocarnitine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "biotin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "thiamine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "riboflavin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "pyridostigmine": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "dapsone": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "artemether": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "benzathine penicillin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "penicillin g": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefazolin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "cefadroxil": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "amikacin sulfate": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "levofloxacin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "moxifloxacin": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "valganciclovir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'},
    "ganciclovir": {'dose':'Check weight, age, renal function, indication, and local protocol before finalizing dose.','route':'PO/IV/IM as applicable','note':'Decision-support entry; verify exact formulation and department protocol.'}
}

def drug_lookup(name):
    key=(name or '').strip().lower()
    return DRUG_DATABASE.get(key)

def iap_percentile_hint(metric, age, sex, value):
    if metric=='bmi':
        if value < 13: return 'Likely low percentile zone; plot on IAP or WHO age- and sex-specific chart.'
        if value < 17: return 'Likely mid percentile zone in many children; confirm on IAP chart.'
        if value < 23: return 'May be above average depending on age and sex; use IAP BMI chart.'
        return 'Likely high percentile zone; confirm overweight or obesity cut-offs on IAP chart.'
    if metric=='weight':
        return 'Weight percentile must be interpreted on IAP or WHO growth chart using exact age and sex.'
    if metric=='height':
        return 'Height percentile must be interpreted on IAP or WHO growth chart using exact age and sex.'
    return 'Plot on the relevant IAP or WHO growth chart for exact percentile.'

def render_growth_visual(metric, percentile_text):
    st.markdown('**Growth percentile visual guide**')
    st.progress(50)
    st.caption('Simplified visual percentile lane: 3rd | 10th | 25th | 50th | 75th | 90th | 97th')
    st.caption(percentile_text)

def registry_protocol(calc):
    return PROTOCOL_REGISTRY.get(calc, {
        'protocol':'Indian clinical protocol context',
        'year':'Clinical standard',
        'thresholds':'Context dependent',
        'exclusions':['Clinical correlation needed'],
        'red_flags':['Clinical instability'],
        'alternatives':['Measurement error','Mixed pathology']
    })

def registry_block(calc, value=None, unit=''):
    meta = registry_protocol(calc)
    lines = [
        f"Result: {value} {unit}".strip(),
        f"Protocol: {meta['protocol']} ({meta['year']})",
        f"Threshold frame: {meta['thresholds']}",
        'Exclusion / limitation points:'
    ]
    lines += [f"- {x}" for x in meta['exclusions']]
    lines.append('Red flags:')
    lines += [f"- {x}" for x in meta['red_flags']]
    lines.append('Alternative diagnoses / explanations:')
    lines += [f"- {x}" for x in meta['alternatives']]
    return lines

def render_registry_block(calc, value=None, unit=''):
    st.markdown('**Registry protocol block**')
    for line in registry_block(calc, value=value, unit=unit):
        st.markdown(line if line.startswith('- ') else f'- {line}')

import streamlit as st
import streamlit.components.v1 as components
import requests, io, math
from datetime import date, timedelta
from urllib.parse import quote_plus



# --- UI repair helpers added in latest patch ---
LACTATION_EXTRA_DRUGS = {
    'domperidone': {'dose':'Lactation-related use requires indication-specific prescribing and cardiac-risk review.','route':'PO','note':'Shown for catalog consistency; verify indication and protocol.'},
    'metoclopramide': {'dose':'Use only with indication-specific review; monitor adverse neurologic effects.','route':'PO/IV','note':'Shown for catalog consistency; verify indication and protocol.'},
    'cabergoline': {'dose':'Dose depends on lactation suppression protocol and indication.','route':'PO','note':'Not a routine pediatric dose tool entry; verify specialist indication.'},
    'bromocriptine': {'dose':'Use only with specialist protocol confirmation.','route':'PO','note':'Shown for catalog consistency; verify maternal indication and safety context.'}
}

if 'DRUG_DATABASE' in globals() and isinstance(DRUG_DATABASE, dict):
    for _k,_v in LACTATION_EXTRA_DRUGS.items():
        DRUG_DATABASE.setdefault(_k,_v)


def simple_percentile_band(percentile):
    if percentile is None:
        return 'Percentile unavailable'
    if percentile < 3:
        return '<3rd percentile'
    if percentile < 10:
        return '3rd-10th percentile'
    if percentile < 25:
        return '10th-25th percentile'
    if percentile < 50:
        return '25th-50th percentile'
    if percentile == 50:
        return '50th percentile'
    if percentile < 75:
        return '50th-75th percentile'
    if percentile < 90:
        return '75th-90th percentile'
    if percentile < 97:
        return '90th-97th percentile'
    return '>97th percentile'


def infer_percentile_from_bmi(age_years, sex, bmi):
    if bmi is None or bmi <= 0:
        return None
    if age_years < 2:
        if bmi < 14:
            return 3
        if bmi < 16:
            return 25
        if bmi < 18:
            return 50
        if bmi < 19:
            return 75
        return 97
    if bmi < 13:
        return 3
    if bmi < 15:
        return 10
    if bmi < 17:
        return 50
    if bmi < 19:
        return 75
    if bmi < 23:
        return 90
    return 97


def percentile_to_zscore(percentile):
    if percentile is None:
        return None
    p = max(0.1, min(99.9, float(percentile)))
    anchors = [
        (0.1, -3.09),
        (3, -1.88),
        (10, -1.28),
        (25, -0.67),
        (50, 0.0),
        (75, 0.67),
        (90, 1.28),
        (97, 1.88),
        (99.9, 3.09),
    ]
    for (p1, z1), (p2, z2) in zip(anchors, anchors[1:]):
        if p1 <= p <= p2:
            frac = (p - p1) / (p2 - p1) if p2 != p1 else 0
            return round(z1 + frac * (z2 - z1), 2)
    return 0.0


def pediatric_dose_entry(name):
    key=(name or '').strip().lower()
    if key in DRUGS:
        base=DRUGS[key].copy()
        base.setdefault('source','DRUGS')
        return base
    db=DRUG_DATABASE.get(key, {}) if 'DRUG_DATABASE' in globals() else {}
    dose_text = db.get('dose') if isinstance(db, dict) else None
    mgkg = None
    if isinstance(dose_text, str):
        import re
        m = re.search(r'(\d+(?:\.\d+)?)\s*mg\s*/\s*kg', dose_text.lower())
        if m:
            mgkg = float(m.group(1))
    if mgkg is not None:
        return {
            'dose_mgkg': mgkg,
            'renal': db.get('renal','Verify renal adjustment.'),
            'preg': db.get('preg','Verify pregnancy safety with current reference.'),
            'lact': db.get('lact', db.get('note','Verify lactation safety with current reference.')),
            'route': db.get('route','Varies'),
            'source':'DRUG_DATABASE'
        }
    if isinstance(db, dict) and db:
        return {
            'dose_text': db.get('dose','Dose requires protocol-specific verification.'),
            'renal': db.get('renal','Verify renal adjustment.'),
            'preg': db.get('preg','Verify pregnancy safety with current reference.'),
            'lact': db.get('lact', db.get('note','Verify lactation safety with current reference.')),
            'route': db.get('route','Varies'),
            'source':'DRUG_DATABASE_TEXT'
        }
    return None


def render_pictorial_percentile_projection(title, sex, percentile):
    st.markdown(f'**{title}**')
    marks = [3,10,25,50,75,90,97]
    cols = st.columns(len(marks))
    for i,m in enumerate(marks):
        active = percentile is not None and abs(percentile - m) == min(abs(percentile-x) for x in marks)
        label = f"{'ðŸ”µ' if sex.lower().startswith('m') else 'ðŸŸ£' if active else 'âšª'} {m}" if active else str(m)
        cols[i].markdown(f"<div style='text-align:center;padding:6px;border-radius:8px;background:{'#dbeafe' if active and sex.lower().startswith('m') else '#f3e8ff' if active else '#f3f4f6'}'>{label}</div>", unsafe_allow_html=True)
    if percentile is not None:
        st.caption(f'Projected {sex} percentile position: about {percentile}th percentile ({simple_percentile_band(percentile)}).')


def render_percentile_graph(percentile, sex='Child', age_months=None):
    st.markdown('**Growth percentile graph**')
    accent = '#2563eb' if str(sex).lower().startswith('m') else '#9333ea'
    pct = 50 if percentile is None else max(1, min(99, int(percentile)))
    age_months = 24 if age_months is None else max(0, min(216, float(age_months)))
    x = age_months / 216 * 100
    bands = [
        ('3rd', 18), ('10th', 30), ('25th', 40), ('50th', 50), ('75th', 60), ('90th', 70), ('97th', 82)
    ]
    curve_svg = []
    for label, y in bands:
        curve_svg.append(f"<path d='M 6 {y} C 22 {y-6}, 40 {y-8}, 58 {y-4} S 84 {y+4}, 94 {y}' fill='none' stroke='#cbd5e1' stroke-width='1.6' stroke-dasharray='4 4'/>")
        curve_svg.append(f"<text x='96' y='{y+3}' font-size='9' fill='#64748b'>{label}</text>")
    marker_y = min(bands, key=lambda item: abs(int(item[0].replace('rd','').replace('th','')) - pct))[1]
    months_ticks = ''.join([f"<text x='{6 + (m/216)*88:.1f}' y='96' font-size='8' text-anchor='middle' fill='#64748b'>{int(m)}</text>" for m in [0,24,60,120,180,216]])
    svg = f"""
    <svg viewBox='0 0 100 100' width='100%' height='220' aria-label='Growth percentile chart'>
      <rect x='0' y='0' width='100' height='100' rx='8' fill='white'/>
      <line x1='6' y1='10' x2='6' y2='88' stroke='#94a3b8' stroke-width='1.2'/>
      <line x1='6' y1='88' x2='94' y2='88' stroke='#94a3b8' stroke-width='1.2'/>
      <text x='2' y='12' font-size='8' fill='#64748b' transform='rotate(-90 2 12)'>Percentile</text>
      <text x='42' y='99' font-size='8' fill='#64748b'>Age (months)</text>
      {''.join(curve_svg)}
      <line x1='{x:.1f}' y1='10' x2='{x:.1f}' y2='88' stroke='{accent}' stroke-width='1.2' stroke-dasharray='3 3'/>
      <circle cx='{x:.1f}' cy='{marker_y}' r='3.2' fill='{accent}'/>
      <rect x='{max(8,min(72,x-10)):.1f}' y='{max(8,marker_y-16):.1f}' width='22' height='10' rx='4' fill='{accent}'/>
      <text x='{max(19,min(83,x+1)):.1f}' y='{max(15,marker_y-9):.1f}' font-size='7.5' text-anchor='middle' fill='white'>{pct}th %ile</text>
      {months_ticks}
    </svg>
    """
    st.markdown(f"<div style='background:#fff;border:1px solid #dbe4ee;border-radius:14px;padding:8px 10px 6px 10px;margin:8px 0 10px 0'>{svg}</div>", unsafe_allow_html=True)
    st.caption(f'Age-positioned percentile display for {sex.lower()} child at {age_months:.0f} months. WHO publishes official BMI-for-age and head-circumference-for-age reference tables for under-5 children, WHO publishes expanded BMI-for-age reference tables for 5-19 years, and the revised IAP 5-18 year Indian charts were constructed using Cole LMS method.')

WHO_LMS_SOURCES = {
    'bmi_u5': 'WHO Child Growth Standards BMI-for-age tables provide Excel/PDF z-score references for boys and girls from birth to 5 years.',
    'hc_u5': 'WHO Child Growth Standards head circumference-for-age tables provide z-score references for boys and girls from birth to 5 years.',
    'bmi_5_19': 'WHO 5-19 years BMI-for-age expanded tables provide z-score and percentile reference spreadsheets for boys and girls.',
    'iap_5_18': 'Revised IAP 5-18 year charts were constructed using Cole LMS method for Indian children.'
}

def lms_method_note(age_months, metric):
    if metric == 'bmi' and age_months <= 60:
        return 'Exact WHO BMI-for-age LMS data should be embedded here for exact z-score and percentile calculation under 5 years.'
    if metric == 'head_circumference' and age_months <= 60:
        return 'Exact WHO head-circumference-for-age LMS data should be embedded here for exact z-score and percentile calculation under 5 years.'
    return 'For older children, WHO/IAP LMS reference tables should be embedded for exact percentile and z-score calculation.'

def render_head_circumference_support(age_months, sex, hc_cm):
    st.markdown('**Head circumference support**')
    st.caption(lms_method_note(age_months, 'head_circumference'))
    st.caption('Exact WHO under-5 head circumference LMS plotting is not fully embedded yet; this section captures measurement and gives visual support framing.')
    approx = None
    if age_months is not None and hc_cm:
        if age_months <= 3:
            approx = 'Needs newborn/early infant chart review'
        elif age_months <= 12:
            approx = 'Use WHO/IAP under-5 head circumference chart'
        elif age_months <= 60:
            approx = 'Plot on under-5 chart for age/sex confirmation'
        else:
            approx = 'Head circumference chart support usually focuses on under-5 age band'
    st.info(f'Entered HC: {hc_cm:.1f} cm | Sex: {sex} | Age: {age_months:.1f} months' if hc_cm is not None else 'Enter head circumference to continue')
    exact = who_hcfa_exact(age_months, sex, hc_cm) if age_months is not None and age_months <= 60 and hc_cm is not None and hc_cm > 0 else None
    if exact:
        c1,c2,c3 = st.columns(3)
        c1.metric('HC percentile', f"{exact['percentile']:.1f}th")
        c2.metric('HC z score', f"{exact['zscore']:+.2f}")
        c3.metric('HC median', f"{exact['median']:.1f} cm")
    if approx:
        st.write(approx)

WHO_HCFA_BOYS_Z = [{'Month': 0, 'L': 1.0, 'M': 34.4618, 'S': 0.03686, 'SD': 1.2703, 'SD3neg': 30.7, 'SD2neg': 31.9, 'SD1neg': 33.2, 'SD0': 34.5, 'SD1': 35.7, 'SD2': 37.0, 'SD3': 38.3}, {'Month': 1, 'L': 1.0, 'M': 37.2759, 'S': 0.03133, 'SD': 1.1679, 'SD3neg': 33.8, 'SD2neg': 34.9, 'SD1neg': 36.1, 'SD0': 37.3, 'SD1': 38.4, 'SD2': 39.6, 'SD3': 40.8}, {'Month': 2, 'L': 1.0, 'M': 39.1285, 'S': 0.02997, 'SD': 1.1727, 'SD3neg': 35.6, 'SD2neg': 36.8, 'SD1neg': 38.0, 'SD0': 39.1, 'SD1': 40.3, 'SD2': 41.5, 'SD3': 42.6}, {'Month': 3, 'L': 1.0, 'M': 40.5135, 'S': 0.02918, 'SD': 1.1822, 'SD3neg': 37.0, 'SD2neg': 38.1, 'SD1neg': 39.3, 'SD0': 40.5, 'SD1': 41.7, 'SD2': 42.9, 'SD3': 44.1}, {'Month': 4, 'L': 1.0, 'M': 41.6317, 'S': 0.02868, 'SD': 1.194, 'SD3neg': 38.0, 'SD2neg': 39.2, 'SD1neg': 40.4, 'SD0': 41.6, 'SD1': 42.8, 'SD2': 44.0, 'SD3': 45.2}, {'Month': 5, 'L': 1.0, 'M': 42.5576, 'S': 0.02837, 'SD': 1.2074, 'SD3neg': 38.9, 'SD2neg': 40.1, 'SD1neg': 41.4, 'SD0': 42.6, 'SD1': 43.8, 'SD2': 45.0, 'SD3': 46.2}, {'Month': 6, 'L': 1.0, 'M': 43.3306, 'S': 0.02817, 'SD': 1.2206, 'SD3neg': 39.7, 'SD2neg': 40.9, 'SD1neg': 42.1, 'SD0': 43.3, 'SD1': 44.6, 'SD2': 45.8, 'SD3': 47.0}, {'Month': 7, 'L': 1.0, 'M': 43.9803, 'S': 0.02804, 'SD': 1.2332, 'SD3neg': 40.3, 'SD2neg': 41.5, 'SD1neg': 42.7, 'SD0': 44.0, 'SD1': 45.2, 'SD2': 46.4, 'SD3': 47.7}, {'Month': 8, 'L': 1.0, 'M': 44.53, 'S': 0.02796, 'SD': 1.2451, 'SD3neg': 40.8, 'SD2neg': 42.0, 'SD1neg': 43.3, 'SD0': 44.5, 'SD1': 45.8, 'SD2': 47.0, 'SD3': 48.3}, {'Month': 9, 'L': 1.0, 'M': 44.9998, 'S': 0.02792, 'SD': 1.2564, 'SD3neg': 41.2, 'SD2neg': 42.5, 'SD1neg': 43.7, 'SD0': 45.0, 'SD1': 46.3, 'SD2': 47.5, 'SD3': 48.8}, {'Month': 10, 'L': 1.0, 'M': 45.4051, 'S': 0.0279, 'SD': 1.2668, 'SD3neg': 41.6, 'SD2neg': 42.9, 'SD1neg': 44.1, 'SD0': 45.4, 'SD1': 46.7, 'SD2': 47.9, 'SD3': 49.2}, {'Month': 11, 'L': 1.0, 'M': 45.7573, 'S': 0.02789, 'SD': 1.2762, 'SD3neg': 41.9, 'SD2neg': 43.2, 'SD1neg': 44.5, 'SD0': 45.8, 'SD1': 47.0, 'SD2': 48.3, 'SD3': 49.6}, {'Month': 12, 'L': 1.0, 'M': 46.0661, 'S': 0.02789, 'SD': 1.2848, 'SD3neg': 42.2, 'SD2neg': 43.5, 'SD1neg': 44.8, 'SD0': 46.1, 'SD1': 47.4, 'SD2': 48.6, 'SD3': 49.9}, {'Month': 13, 'L': 1.0, 'M': 46.3395, 'S': 0.02789, 'SD': 1.2924, 'SD3neg': 42.5, 'SD2neg': 43.8, 'SD1neg': 45.0, 'SD0': 46.3, 'SD1': 47.6, 'SD2': 48.9, 'SD3': 50.2}, {'Month': 14, 'L': 1.0, 'M': 46.5844, 'S': 0.02791, 'SD': 1.3002, 'SD3neg': 42.7, 'SD2neg': 44.0, 'SD1neg': 45.3, 'SD0': 46.6, 'SD1': 47.9, 'SD2': 49.2, 'SD3': 50.5}, {'Month': 15, 'L': 1.0, 'M': 46.806, 'S': 0.02792, 'SD': 1.3068, 'SD3neg': 42.9, 'SD2neg': 44.2, 'SD1neg': 45.5, 'SD0': 46.8, 'SD1': 48.1, 'SD2': 49.4, 'SD3': 50.7}, {'Month': 16, 'L': 1.0, 'M': 47.0088, 'S': 0.02795, 'SD': 1.3139, 'SD3neg': 43.1, 'SD2neg': 44.4, 'SD1neg': 45.7, 'SD0': 47.0, 'SD1': 48.3, 'SD2': 49.6, 'SD3': 51.0}, {'Month': 17, 'L': 1.0, 'M': 47.1962, 'S': 0.02797, 'SD': 1.3201, 'SD3neg': 43.2, 'SD2neg': 44.6, 'SD1neg': 45.9, 'SD0': 47.2, 'SD1': 48.5, 'SD2': 49.8, 'SD3': 51.2}, {'Month': 18, 'L': 1.0, 'M': 47.3711, 'S': 0.028, 'SD': 1.3264, 'SD3neg': 43.4, 'SD2neg': 44.7, 'SD1neg': 46.0, 'SD0': 47.4, 'SD1': 48.7, 'SD2': 50.0, 'SD3': 51.4}, {'Month': 19, 'L': 1.0, 'M': 47.5357, 'S': 0.02803, 'SD': 1.3324, 'SD3neg': 43.5, 'SD2neg': 44.9, 'SD1neg': 46.2, 'SD0': 47.5, 'SD1': 48.9, 'SD2': 50.2, 'SD3': 51.5}, {'Month': 20, 'L': 1.0, 'M': 47.6919, 'S': 0.02806, 'SD': 1.3382, 'SD3neg': 43.7, 'SD2neg': 45.0, 'SD1neg': 46.4, 'SD0': 47.7, 'SD1': 49.0, 'SD2': 50.4, 'SD3': 51.7}, {'Month': 21, 'L': 1.0, 'M': 47.8408, 'S': 0.0281, 'SD': 1.3443, 'SD3neg': 43.8, 'SD2neg': 45.2, 'SD1neg': 46.5, 'SD0': 47.8, 'SD1': 49.2, 'SD2': 50.5, 'SD3': 51.9}, {'Month': 22, 'L': 1.0, 'M': 47.9833, 'S': 0.02813, 'SD': 1.3498, 'SD3neg': 43.9, 'SD2neg': 45.3, 'SD1neg': 46.6, 'SD0': 48.0, 'SD1': 49.3, 'SD2': 50.7, 'SD3': 52.0}, {'Month': 23, 'L': 1.0, 'M': 48.1201, 'S': 0.02817, 'SD': 1.3555, 'SD3neg': 44.1, 'SD2neg': 45.4, 'SD1neg': 46.8, 'SD0': 48.1, 'SD1': 49.5, 'SD2': 50.8, 'SD3': 52.2}, {'Month': 24, 'L': 1.0, 'M': 48.2515, 'S': 0.02821, 'SD': 1.3612, 'SD3neg': 44.2, 'SD2neg': 45.5, 'SD1neg': 46.9, 'SD0': 48.3, 'SD1': 49.6, 'SD2': 51.0, 'SD3': 52.3}, {'Month': 25, 'L': 1.0, 'M': 48.3777, 'S': 0.02825, 'SD': 1.3667, 'SD3neg': 44.3, 'SD2neg': 45.6, 'SD1neg': 47.0, 'SD0': 48.4, 'SD1': 49.7, 'SD2': 51.1, 'SD3': 52.5}, {'Month': 26, 'L': 1.0, 'M': 48.4989, 'S': 0.0283, 'SD': 1.3725, 'SD3neg': 44.4, 'SD2neg': 45.8, 'SD1neg': 47.1, 'SD0': 48.5, 'SD1': 49.9, 'SD2': 51.2, 'SD3': 52.6}, {'Month': 27, 'L': 1.0, 'M': 48.6151, 'S': 0.02834, 'SD': 1.3778, 'SD3neg': 44.5, 'SD2neg': 45.9, 'SD1neg': 47.2, 'SD0': 48.6, 'SD1': 50.0, 'SD2': 51.4, 'SD3': 52.7}, {'Month': 28, 'L': 1.0, 'M': 48.7264, 'S': 0.02838, 'SD': 1.3829, 'SD3neg': 44.6, 'SD2neg': 46.0, 'SD1neg': 47.3, 'SD0': 48.7, 'SD1': 50.1, 'SD2': 51.5, 'SD3': 52.9}, {'Month': 29, 'L': 1.0, 'M': 48.8331, 'S': 0.02842, 'SD': 1.3878, 'SD3neg': 44.7, 'SD2neg': 46.1, 'SD1neg': 47.4, 'SD0': 48.8, 'SD1': 50.2, 'SD2': 51.6, 'SD3': 53.0}, {'Month': 30, 'L': 1.0, 'M': 48.9351, 'S': 0.02847, 'SD': 1.3932, 'SD3neg': 44.8, 'SD2neg': 46.1, 'SD1neg': 47.5, 'SD0': 48.9, 'SD1': 50.3, 'SD2': 51.7, 'SD3': 53.1}, {'Month': 31, 'L': 1.0, 'M': 49.0327, 'S': 0.02851, 'SD': 1.3979, 'SD3neg': 44.8, 'SD2neg': 46.2, 'SD1neg': 47.6, 'SD0': 49.0, 'SD1': 50.4, 'SD2': 51.8, 'SD3': 53.2}, {'Month': 32, 'L': 1.0, 'M': 49.126, 'S': 0.02855, 'SD': 1.4026, 'SD3neg': 44.9, 'SD2neg': 46.3, 'SD1neg': 47.7, 'SD0': 49.1, 'SD1': 50.5, 'SD2': 51.9, 'SD3': 53.3}, {'Month': 33, 'L': 1.0, 'M': 49.2153, 'S': 0.02859, 'SD': 1.4071, 'SD3neg': 45.0, 'SD2neg': 46.4, 'SD1neg': 47.8, 'SD0': 49.2, 'SD1': 50.6, 'SD2': 52.0, 'SD3': 53.4}, {'Month': 34, 'L': 1.0, 'M': 49.3007, 'S': 0.02863, 'SD': 1.4115, 'SD3neg': 45.1, 'SD2neg': 46.5, 'SD1neg': 47.9, 'SD0': 49.3, 'SD1': 50.7, 'SD2': 52.1, 'SD3': 53.5}, {'Month': 35, 'L': 1.0, 'M': 49.3826, 'S': 0.02867, 'SD': 1.4158, 'SD3neg': 45.1, 'SD2neg': 46.6, 'SD1neg': 48.0, 'SD0': 49.4, 'SD1': 50.8, 'SD2': 52.2, 'SD3': 53.6}, {'Month': 36, 'L': 1.0, 'M': 49.4612, 'S': 0.02871, 'SD': 1.42, 'SD3neg': 45.2, 'SD2neg': 46.6, 'SD1neg': 48.0, 'SD0': 49.5, 'SD1': 50.9, 'SD2': 52.3, 'SD3': 53.7}, {'Month': 37, 'L': 1.0, 'M': 49.5367, 'S': 0.02875, 'SD': 1.4242, 'SD3neg': 45.3, 'SD2neg': 46.7, 'SD1neg': 48.1, 'SD0': 49.5, 'SD1': 51.0, 'SD2': 52.4, 'SD3': 53.8}, {'Month': 38, 'L': 1.0, 'M': 49.6093, 'S': 0.02878, 'SD': 1.4278, 'SD3neg': 45.3, 'SD2neg': 46.8, 'SD1neg': 48.2, 'SD0': 49.6, 'SD1': 51.0, 'SD2': 52.5, 'SD3': 53.9}, {'Month': 39, 'L': 1.0, 'M': 49.6791, 'S': 0.02882, 'SD': 1.4318, 'SD3neg': 45.4, 'SD2neg': 46.8, 'SD1neg': 48.2, 'SD0': 49.7, 'SD1': 51.1, 'SD2': 52.5, 'SD3': 54.0}, {'Month': 40, 'L': 1.0, 'M': 49.7465, 'S': 0.02886, 'SD': 1.4357, 'SD3neg': 45.4, 'SD2neg': 46.9, 'SD1neg': 48.3, 'SD0': 49.7, 'SD1': 51.2, 'SD2': 52.6, 'SD3': 54.1}, {'Month': 41, 'L': 1.0, 'M': 49.8116, 'S': 0.02889, 'SD': 1.4391, 'SD3neg': 45.5, 'SD2neg': 46.9, 'SD1neg': 48.4, 'SD0': 49.8, 'SD1': 51.3, 'SD2': 52.7, 'SD3': 54.1}, {'Month': 42, 'L': 1.0, 'M': 49.8745, 'S': 0.02893, 'SD': 1.4429, 'SD3neg': 45.5, 'SD2neg': 47.0, 'SD1neg': 48.4, 'SD0': 49.9, 'SD1': 51.3, 'SD2': 52.8, 'SD3': 54.2}, {'Month': 43, 'L': 1.0, 'M': 49.9354, 'S': 0.02896, 'SD': 1.4461, 'SD3neg': 45.6, 'SD2neg': 47.0, 'SD1neg': 48.5, 'SD0': 49.9, 'SD1': 51.4, 'SD2': 52.8, 'SD3': 54.3}, {'Month': 44, 'L': 1.0, 'M': 49.9942, 'S': 0.02899, 'SD': 1.4493, 'SD3neg': 45.6, 'SD2neg': 47.1, 'SD1neg': 48.5, 'SD0': 50.0, 'SD1': 51.4, 'SD2': 52.9, 'SD3': 54.3}, {'Month': 45, 'L': 1.0, 'M': 50.0512, 'S': 0.02903, 'SD': 1.453, 'SD3neg': 45.7, 'SD2neg': 47.1, 'SD1neg': 48.6, 'SD0': 50.1, 'SD1': 51.5, 'SD2': 53.0, 'SD3': 54.4}, {'Month': 46, 'L': 1.0, 'M': 50.1064, 'S': 0.02906, 'SD': 1.4561, 'SD3neg': 45.7, 'SD2neg': 47.2, 'SD1neg': 48.7, 'SD0': 50.1, 'SD1': 51.6, 'SD2': 53.0, 'SD3': 54.5}, {'Month': 47, 'L': 1.0, 'M': 50.1598, 'S': 0.02909, 'SD': 1.4592, 'SD3neg': 45.8, 'SD2neg': 47.2, 'SD1neg': 48.7, 'SD0': 50.2, 'SD1': 51.6, 'SD2': 53.1, 'SD3': 54.5}, {'Month': 48, 'L': 1.0, 'M': 50.2115, 'S': 0.02912, 'SD': 1.4622, 'SD3neg': 45.8, 'SD2neg': 47.3, 'SD1neg': 48.7, 'SD0': 50.2, 'SD1': 51.7, 'SD2': 53.1, 'SD3': 54.6}, {'Month': 49, 'L': 1.0, 'M': 50.2617, 'S': 0.02915, 'SD': 1.4651, 'SD3neg': 45.9, 'SD2neg': 47.3, 'SD1neg': 48.8, 'SD0': 50.3, 'SD1': 51.7, 'SD2': 53.2, 'SD3': 54.7}, {'Month': 50, 'L': 1.0, 'M': 50.3105, 'S': 0.02918, 'SD': 1.4681, 'SD3neg': 45.9, 'SD2neg': 47.4, 'SD1neg': 48.8, 'SD0': 50.3, 'SD1': 51.8, 'SD2': 53.2, 'SD3': 54.7}, {'Month': 51, 'L': 1.0, 'M': 50.3578, 'S': 0.02921, 'SD': 1.471, 'SD3neg': 45.9, 'SD2neg': 47.4, 'SD1neg': 48.9, 'SD0': 50.4, 'SD1': 51.8, 'SD2': 53.3, 'SD3': 54.8}, {'Month': 52, 'L': 1.0, 'M': 50.4039, 'S': 0.02924, 'SD': 1.4738, 'SD3neg': 46.0, 'SD2neg': 47.5, 'SD1neg': 48.9, 'SD0': 50.4, 'SD1': 51.9, 'SD2': 53.4, 'SD3': 54.8}, {'Month': 53, 'L': 1.0, 'M': 50.4488, 'S': 0.02927, 'SD': 1.4766, 'SD3neg': 46.0, 'SD2neg': 47.5, 'SD1neg': 49.0, 'SD0': 50.4, 'SD1': 51.9, 'SD2': 53.4, 'SD3': 54.9}, {'Month': 54, 'L': 1.0, 'M': 50.4926, 'S': 0.02929, 'SD': 1.4789, 'SD3neg': 46.1, 'SD2neg': 47.5, 'SD1neg': 49.0, 'SD0': 50.5, 'SD1': 52.0, 'SD2': 53.5, 'SD3': 54.9}, {'Month': 55, 'L': 1.0, 'M': 50.5354, 'S': 0.02932, 'SD': 1.4817, 'SD3neg': 46.1, 'SD2neg': 47.6, 'SD1neg': 49.1, 'SD0': 50.5, 'SD1': 52.0, 'SD2': 53.5, 'SD3': 55.0}, {'Month': 56, 'L': 1.0, 'M': 50.5772, 'S': 0.02935, 'SD': 1.4844, 'SD3neg': 46.1, 'SD2neg': 47.6, 'SD1neg': 49.1, 'SD0': 50.6, 'SD1': 52.1, 'SD2': 53.5, 'SD3': 55.0}, {'Month': 57, 'L': 1.0, 'M': 50.6183, 'S': 0.02938, 'SD': 1.4872, 'SD3neg': 46.2, 'SD2neg': 47.6, 'SD1neg': 49.1, 'SD0': 50.6, 'SD1': 52.1, 'SD2': 53.6, 'SD3': 55.1}, {'Month': 58, 'L': 1.0, 'M': 50.6587, 'S': 0.0294, 'SD': 1.4894, 'SD3neg': 46.2, 'SD2neg': 47.7, 'SD1neg': 49.2, 'SD0': 50.7, 'SD1': 52.1, 'SD2': 53.6, 'SD3': 55.1}, {'Month': 59, 'L': 1.0, 'M': 50.6984, 'S': 0.02943, 'SD': 1.4921, 'SD3neg': 46.2, 'SD2neg': 47.7, 'SD1neg': 49.2, 'SD0': 50.7, 'SD1': 52.2, 'SD2': 53.7, 'SD3': 55.2}, {'Month': 60, 'L': 1.0, 'M': 50.7375, 'S': 0.02946, 'SD': 1.4947, 'SD3neg': 46.3, 'SD2neg': 47.7, 'SD1neg': 49.2, 'SD0': 50.7, 'SD1': 52.2, 'SD2': 53.7, 'SD3': 55.2}]

WHO_HCFA_GIRLS_Z = [{'Month': 0, 'L': 1.0, 'M': 33.8787, 'S': 0.03496, 'SD': 1.1844, 'SD3neg': 30.3, 'SD2neg': 31.5, 'SD1neg': 32.7, 'SD0': 33.9, 'SD1': 35.1, 'SD2': 36.2, 'SD3': 37.4}, {'Month': 1, 'L': 1.0, 'M': 36.5463, 'S': 0.0321, 'SD': 1.1731, 'SD3neg': 33.0, 'SD2neg': 34.2, 'SD1neg': 35.4, 'SD0': 36.5, 'SD1': 37.7, 'SD2': 38.9, 'SD3': 40.1}, {'Month': 2, 'L': 1.0, 'M': 38.2521, 'S': 0.03168, 'SD': 1.2118, 'SD3neg': 34.6, 'SD2neg': 35.8, 'SD1neg': 37.0, 'SD0': 38.3, 'SD1': 39.5, 'SD2': 40.7, 'SD3': 41.9}, {'Month': 3, 'L': 1.0, 'M': 39.5328, 'S': 0.0314, 'SD': 1.2413, 'SD3neg': 35.8, 'SD2neg': 37.1, 'SD1neg': 38.3, 'SD0': 39.5, 'SD1': 40.8, 'SD2': 42.0, 'SD3': 43.3}, {'Month': 4, 'L': 1.0, 'M': 40.5817, 'S': 0.03119, 'SD': 1.2657, 'SD3neg': 36.8, 'SD2neg': 38.1, 'SD1neg': 39.3, 'SD0': 40.6, 'SD1': 41.8, 'SD2': 43.1, 'SD3': 44.4}, {'Month': 5, 'L': 1.0, 'M': 41.459, 'S': 0.03102, 'SD': 1.2861, 'SD3neg': 37.6, 'SD2neg': 38.9, 'SD1neg': 40.2, 'SD0': 41.5, 'SD1': 42.7, 'SD2': 44.0, 'SD3': 45.3}, {'Month': 6, 'L': 1.0, 'M': 42.1995, 'S': 0.03087, 'SD': 1.3027, 'SD3neg': 38.3, 'SD2neg': 39.6, 'SD1neg': 40.9, 'SD0': 42.2, 'SD1': 43.5, 'SD2': 44.8, 'SD3': 46.1}, {'Month': 7, 'L': 1.0, 'M': 42.829, 'S': 0.03075, 'SD': 1.317, 'SD3neg': 38.9, 'SD2neg': 40.2, 'SD1neg': 41.5, 'SD0': 42.8, 'SD1': 44.1, 'SD2': 45.5, 'SD3': 46.8}, {'Month': 8, 'L': 1.0, 'M': 43.3671, 'S': 0.03063, 'SD': 1.3283, 'SD3neg': 39.4, 'SD2neg': 40.7, 'SD1neg': 42.0, 'SD0': 43.4, 'SD1': 44.7, 'SD2': 46.0, 'SD3': 47.4}, {'Month': 9, 'L': 1.0, 'M': 43.83, 'S': 0.03053, 'SD': 1.3381, 'SD3neg': 39.8, 'SD2neg': 41.2, 'SD1neg': 42.5, 'SD0': 43.8, 'SD1': 45.2, 'SD2': 46.5, 'SD3': 47.8}, {'Month': 10, 'L': 1.0, 'M': 44.2319, 'S': 0.03044, 'SD': 1.3464, 'SD3neg': 40.2, 'SD2neg': 41.5, 'SD1neg': 42.9, 'SD0': 44.2, 'SD1': 45.6, 'SD2': 46.9, 'SD3': 48.3}, {'Month': 11, 'L': 1.0, 'M': 44.5844, 'S': 0.03035, 'SD': 1.3531, 'SD3neg': 40.5, 'SD2neg': 41.9, 'SD1neg': 43.2, 'SD0': 44.6, 'SD1': 45.9, 'SD2': 47.3, 'SD3': 48.6}, {'Month': 12, 'L': 1.0, 'M': 44.8965, 'S': 0.03027, 'SD': 1.359, 'SD3neg': 40.8, 'SD2neg': 42.2, 'SD1neg': 43.5, 'SD0': 44.9, 'SD1': 46.3, 'SD2': 47.6, 'SD3': 49.0}, {'Month': 13, 'L': 1.0, 'M': 45.1752, 'S': 0.03019, 'SD': 1.3638, 'SD3neg': 41.1, 'SD2neg': 42.4, 'SD1neg': 43.8, 'SD0': 45.2, 'SD1': 46.5, 'SD2': 47.9, 'SD3': 49.3}, {'Month': 14, 'L': 1.0, 'M': 45.4265, 'S': 0.03012, 'SD': 1.3683, 'SD3neg': 41.3, 'SD2neg': 42.7, 'SD1neg': 44.1, 'SD0': 45.4, 'SD1': 46.8, 'SD2': 48.2, 'SD3': 49.5}, {'Month': 15, 'L': 1.0, 'M': 45.6551, 'S': 0.03006, 'SD': 1.3724, 'SD3neg': 41.5, 'SD2neg': 42.9, 'SD1neg': 44.3, 'SD0': 45.7, 'SD1': 47.0, 'SD2': 48.4, 'SD3': 49.8}, {'Month': 16, 'L': 1.0, 'M': 45.865, 'S': 0.02999, 'SD': 1.3755, 'SD3neg': 41.7, 'SD2neg': 43.1, 'SD1neg': 44.5, 'SD0': 45.9, 'SD1': 47.2, 'SD2': 48.6, 'SD3': 50.0}, {'Month': 17, 'L': 1.0, 'M': 46.0598, 'S': 0.02993, 'SD': 1.3786, 'SD3neg': 41.9, 'SD2neg': 43.3, 'SD1neg': 44.7, 'SD0': 46.1, 'SD1': 47.4, 'SD2': 48.8, 'SD3': 50.2}, {'Month': 18, 'L': 1.0, 'M': 46.2424, 'S': 0.02987, 'SD': 1.3813, 'SD3neg': 42.1, 'SD2neg': 43.5, 'SD1neg': 44.9, 'SD0': 46.2, 'SD1': 47.6, 'SD2': 49.0, 'SD3': 50.4}, {'Month': 19, 'L': 1.0, 'M': 46.4152, 'S': 0.02982, 'SD': 1.3841, 'SD3neg': 42.3, 'SD2neg': 43.6, 'SD1neg': 45.0, 'SD0': 46.4, 'SD1': 47.8, 'SD2': 49.2, 'SD3': 50.6}, {'Month': 20, 'L': 1.0, 'M': 46.5801, 'S': 0.02977, 'SD': 1.3867, 'SD3neg': 42.4, 'SD2neg': 43.8, 'SD1neg': 45.2, 'SD0': 46.6, 'SD1': 48.0, 'SD2': 49.4, 'SD3': 50.7}, {'Month': 21, 'L': 1.0, 'M': 46.7384, 'S': 0.02972, 'SD': 1.3891, 'SD3neg': 42.6, 'SD2neg': 44.0, 'SD1neg': 45.3, 'SD0': 46.7, 'SD1': 48.1, 'SD2': 49.5, 'SD3': 50.9}, {'Month': 22, 'L': 1.0, 'M': 46.8913, 'S': 0.02967, 'SD': 1.3913, 'SD3neg': 42.7, 'SD2neg': 44.1, 'SD1neg': 45.5, 'SD0': 46.9, 'SD1': 48.3, 'SD2': 49.7, 'SD3': 51.1}, {'Month': 23, 'L': 1.0, 'M': 47.0391, 'S': 0.02962, 'SD': 1.3933, 'SD3neg': 42.9, 'SD2neg': 44.3, 'SD1neg': 45.6, 'SD0': 47.0, 'SD1': 48.4, 'SD2': 49.8, 'SD3': 51.2}, {'Month': 24, 'L': 1.0, 'M': 47.1822, 'S': 0.02957, 'SD': 1.3952, 'SD3neg': 43.0, 'SD2neg': 44.4, 'SD1neg': 45.8, 'SD0': 47.2, 'SD1': 48.6, 'SD2': 50.0, 'SD3': 51.4}, {'Month': 25, 'L': 1.0, 'M': 47.3204, 'S': 0.02953, 'SD': 1.3974, 'SD3neg': 43.1, 'SD2neg': 44.5, 'SD1neg': 45.9, 'SD0': 47.3, 'SD1': 48.7, 'SD2': 50.1, 'SD3': 51.5}, {'Month': 26, 'L': 1.0, 'M': 47.4536, 'S': 0.02949, 'SD': 1.3994, 'SD3neg': 43.3, 'SD2neg': 44.7, 'SD1neg': 46.1, 'SD0': 47.5, 'SD1': 48.9, 'SD2': 50.3, 'SD3': 51.7}, {'Month': 27, 'L': 1.0, 'M': 47.5817, 'S': 0.02945, 'SD': 1.4013, 'SD3neg': 43.4, 'SD2neg': 44.8, 'SD1neg': 46.2, 'SD0': 47.6, 'SD1': 49.0, 'SD2': 50.4, 'SD3': 51.8}, {'Month': 28, 'L': 1.0, 'M': 47.7045, 'S': 0.02941, 'SD': 1.403, 'SD3neg': 43.5, 'SD2neg': 44.9, 'SD1neg': 46.3, 'SD0': 47.7, 'SD1': 49.1, 'SD2': 50.5, 'SD3': 51.9}, {'Month': 29, 'L': 1.0, 'M': 47.8219, 'S': 0.02937, 'SD': 1.4045, 'SD3neg': 43.6, 'SD2neg': 45.0, 'SD1neg': 46.4, 'SD0': 47.8, 'SD1': 49.2, 'SD2': 50.6, 'SD3': 52.0}, {'Month': 30, 'L': 1.0, 'M': 47.934, 'S': 0.02933, 'SD': 1.4059, 'SD3neg': 43.7, 'SD2neg': 45.1, 'SD1neg': 46.5, 'SD0': 47.9, 'SD1': 49.3, 'SD2': 50.7, 'SD3': 52.2}, {'Month': 31, 'L': 1.0, 'M': 48.041, 'S': 0.02929, 'SD': 1.4071, 'SD3neg': 43.8, 'SD2neg': 45.2, 'SD1neg': 46.6, 'SD0': 48.0, 'SD1': 49.4, 'SD2': 50.9, 'SD3': 52.3}, {'Month': 32, 'L': 1.0, 'M': 48.1432, 'S': 0.02926, 'SD': 1.4087, 'SD3neg': 43.9, 'SD2neg': 45.3, 'SD1neg': 46.7, 'SD0': 48.1, 'SD1': 49.6, 'SD2': 51.0, 'SD3': 52.4}, {'Month': 33, 'L': 1.0, 'M': 48.2408, 'S': 0.02922, 'SD': 1.4096, 'SD3neg': 44.0, 'SD2neg': 45.4, 'SD1neg': 46.8, 'SD0': 48.2, 'SD1': 49.7, 'SD2': 51.1, 'SD3': 52.5}, {'Month': 34, 'L': 1.0, 'M': 48.3343, 'S': 0.02919, 'SD': 1.4109, 'SD3neg': 44.1, 'SD2neg': 45.5, 'SD1neg': 46.9, 'SD0': 48.3, 'SD1': 49.7, 'SD2': 51.2, 'SD3': 52.6}, {'Month': 35, 'L': 1.0, 'M': 48.4239, 'S': 0.02915, 'SD': 1.4116, 'SD3neg': 44.2, 'SD2neg': 45.6, 'SD1neg': 47.0, 'SD0': 48.4, 'SD1': 49.8, 'SD2': 51.2, 'SD3': 52.7}, {'Month': 36, 'L': 1.0, 'M': 48.5099, 'S': 0.02912, 'SD': 1.4126, 'SD3neg': 44.3, 'SD2neg': 45.7, 'SD1neg': 47.1, 'SD0': 48.5, 'SD1': 49.9, 'SD2': 51.3, 'SD3': 52.7}, {'Month': 37, 'L': 1.0, 'M': 48.5926, 'S': 0.02909, 'SD': 1.4136, 'SD3neg': 44.4, 'SD2neg': 45.8, 'SD1neg': 47.2, 'SD0': 48.6, 'SD1': 50.0, 'SD2': 51.4, 'SD3': 52.8}, {'Month': 38, 'L': 1.0, 'M': 48.6722, 'S': 0.02906, 'SD': 1.4144, 'SD3neg': 44.4, 'SD2neg': 45.8, 'SD1neg': 47.3, 'SD0': 48.7, 'SD1': 50.1, 'SD2': 51.5, 'SD3': 52.9}, {'Month': 39, 'L': 1.0, 'M': 48.7489, 'S': 0.02903, 'SD': 1.4152, 'SD3neg': 44.5, 'SD2neg': 45.9, 'SD1neg': 47.3, 'SD0': 48.7, 'SD1': 50.2, 'SD2': 51.6, 'SD3': 53.0}, {'Month': 40, 'L': 1.0, 'M': 48.8228, 'S': 0.029, 'SD': 1.4159, 'SD3neg': 44.6, 'SD2neg': 46.0, 'SD1neg': 47.4, 'SD0': 48.8, 'SD1': 50.2, 'SD2': 51.7, 'SD3': 53.1}, {'Month': 41, 'L': 1.0, 'M': 48.8941, 'S': 0.02897, 'SD': 1.4165, 'SD3neg': 44.6, 'SD2neg': 46.1, 'SD1neg': 47.5, 'SD0': 48.9, 'SD1': 50.3, 'SD2': 51.7, 'SD3': 53.1}, {'Month': 42, 'L': 1.0, 'M': 48.9629, 'S': 0.02894, 'SD': 1.417, 'SD3neg': 44.7, 'SD2neg': 46.1, 'SD1neg': 47.5, 'SD0': 49.0, 'SD1': 50.4, 'SD2': 51.8, 'SD3': 53.2}, {'Month': 43, 'L': 1.0, 'M': 49.0294, 'S': 0.02891, 'SD': 1.4174, 'SD3neg': 44.8, 'SD2neg': 46.2, 'SD1neg': 47.6, 'SD0': 49.0, 'SD1': 50.4, 'SD2': 51.9, 'SD3': 53.3}, {'Month': 44, 'L': 1.0, 'M': 49.0937, 'S': 0.02888, 'SD': 1.4178, 'SD3neg': 44.8, 'SD2neg': 46.3, 'SD1neg': 47.7, 'SD0': 49.1, 'SD1': 50.5, 'SD2': 51.9, 'SD3': 53.3}, {'Month': 45, 'L': 1.0, 'M': 49.156, 'S': 0.02886, 'SD': 1.4186, 'SD3neg': 44.9, 'SD2neg': 46.3, 'SD1neg': 47.7, 'SD0': 49.2, 'SD1': 50.6, 'SD2': 52.0, 'SD3': 53.4}, {'Month': 46, 'L': 1.0, 'M': 49.2164, 'S': 0.02883, 'SD': 1.4189, 'SD3neg': 45.0, 'SD2neg': 46.4, 'SD1neg': 47.8, 'SD0': 49.2, 'SD1': 50.6, 'SD2': 52.1, 'SD3': 53.5}, {'Month': 47, 'L': 1.0, 'M': 49.2751, 'S': 0.0288, 'SD': 1.4191, 'SD3neg': 45.0, 'SD2neg': 46.4, 'SD1neg': 47.9, 'SD0': 49.3, 'SD1': 50.7, 'SD2': 52.1, 'SD3': 53.5}, {'Month': 48, 'L': 1.0, 'M': 49.3321, 'S': 0.02878, 'SD': 1.4198, 'SD3neg': 45.1, 'SD2neg': 46.5, 'SD1neg': 47.9, 'SD0': 49.3, 'SD1': 50.8, 'SD2': 52.2, 'SD3': 53.6}, {'Month': 49, 'L': 1.0, 'M': 49.3877, 'S': 0.02875, 'SD': 1.4199, 'SD3neg': 45.1, 'SD2neg': 46.5, 'SD1neg': 48.0, 'SD0': 49.4, 'SD1': 50.8, 'SD2': 52.2, 'SD3': 53.6}, {'Month': 50, 'L': 1.0, 'M': 49.4419, 'S': 0.02873, 'SD': 1.4205, 'SD3neg': 45.2, 'SD2neg': 46.6, 'SD1neg': 48.0, 'SD0': 49.4, 'SD1': 50.9, 'SD2': 52.3, 'SD3': 53.7}, {'Month': 51, 'L': 1.0, 'M': 49.4947, 'S': 0.0287, 'SD': 1.4205, 'SD3neg': 45.2, 'SD2neg': 46.7, 'SD1neg': 48.1, 'SD0': 49.5, 'SD1': 50.9, 'SD2': 52.3, 'SD3': 53.8}, {'Month': 52, 'L': 1.0, 'M': 49.5464, 'S': 0.02868, 'SD': 1.421, 'SD3neg': 45.3, 'SD2neg': 46.7, 'SD1neg': 48.1, 'SD0': 49.5, 'SD1': 51.0, 'SD2': 52.4, 'SD3': 53.8}, {'Month': 53, 'L': 1.0, 'M': 49.5969, 'S': 0.02865, 'SD': 1.421, 'SD3neg': 45.3, 'SD2neg': 46.8, 'SD1neg': 48.2, 'SD0': 49.6, 'SD1': 51.0, 'SD2': 52.4, 'SD3': 53.9}, {'Month': 54, 'L': 1.0, 'M': 49.6464, 'S': 0.02863, 'SD': 1.4214, 'SD3neg': 45.4, 'SD2neg': 46.8, 'SD1neg': 48.2, 'SD0': 49.6, 'SD1': 51.1, 'SD2': 52.5, 'SD3': 53.9}, {'Month': 55, 'L': 1.0, 'M': 49.6947, 'S': 0.02861, 'SD': 1.4218, 'SD3neg': 45.4, 'SD2neg': 46.9, 'SD1neg': 48.3, 'SD0': 49.7, 'SD1': 51.1, 'SD2': 52.5, 'SD3': 54.0}, {'Month': 56, 'L': 1.0, 'M': 49.7421, 'S': 0.02859, 'SD': 1.4221, 'SD3neg': 45.5, 'SD2neg': 46.9, 'SD1neg': 48.3, 'SD0': 49.7, 'SD1': 51.2, 'SD2': 52.6, 'SD3': 54.0}, {'Month': 57, 'L': 1.0, 'M': 49.7885, 'S': 0.02856, 'SD': 1.422, 'SD3neg': 45.5, 'SD2neg': 46.9, 'SD1neg': 48.4, 'SD0': 49.8, 'SD1': 51.2, 'SD2': 52.6, 'SD3': 54.1}, {'Month': 58, 'L': 1.0, 'M': 49.8341, 'S': 0.02854, 'SD': 1.4223, 'SD3neg': 45.6, 'SD2neg': 47.0, 'SD1neg': 48.4, 'SD0': 49.8, 'SD1': 51.3, 'SD2': 52.7, 'SD3': 54.1}, {'Month': 59, 'L': 1.0, 'M': 49.8789, 'S': 0.02852, 'SD': 1.4226, 'SD3neg': 45.6, 'SD2neg': 47.0, 'SD1neg': 48.5, 'SD0': 49.9, 'SD1': 51.3, 'SD2': 52.7, 'SD3': 54.1}, {'Month': 60, 'L': 1.0, 'M': 49.9229, 'S': 0.0285, 'SD': 1.4228, 'SD3neg': 45.7, 'SD2neg': 47.1, 'SD1neg': 48.5, 'SD0': 49.9, 'SD1': 51.3, 'SD2': 52.8, 'SD3': 54.2}]

WHO_HCFA_BOYS_P = [{'Month': 0, 'L': 1.0, 'M': 34.4618, 'S': 0.03686, 'SD': 1.27026, 'P01': 30.5, 'P1': 31.5, 'P3': 32.1, 'P5': 32.4, 'P10': 32.8, 'P15': 33.1, 'P25': 33.6, 'P50': 34.5, 'P75': 35.3, 'P85': 35.8, 'P90': 36.1, 'P95': 36.6, 'P97': 36.9, 'P99': 37.4, 'P999': 38.4}, {'Month': 1, 'L': 1.0, 'M': 37.2759, 'S': 0.03133, 'SD': 1.16785, 'P01': 33.7, 'P1': 34.6, 'P3': 35.1, 'P5': 35.4, 'P10': 35.8, 'P15': 36.1, 'P25': 36.5, 'P50': 37.3, 'P75': 38.1, 'P85': 38.5, 'P90': 38.8, 'P95': 39.2, 'P97': 39.5, 'P99': 40.0, 'P999': 40.9}, {'Month': 2, 'L': 1.0, 'M': 39.1285, 'S': 0.02997, 'SD': 1.17268, 'P01': 35.5, 'P1': 36.4, 'P3': 36.9, 'P5': 37.2, 'P10': 37.6, 'P15': 37.9, 'P25': 38.3, 'P50': 39.1, 'P75': 39.9, 'P85': 40.3, 'P90': 40.6, 'P95': 41.1, 'P97': 41.3, 'P99': 41.9, 'P999': 42.8}, {'Month': 3, 'L': 1.0, 'M': 40.5135, 'S': 0.02918, 'SD': 1.18218, 'P01': 36.9, 'P1': 37.8, 'P3': 38.3, 'P5': 38.6, 'P10': 39.0, 'P15': 39.3, 'P25': 39.7, 'P50': 40.5, 'P75': 41.3, 'P85': 41.7, 'P90': 42.0, 'P95': 42.5, 'P97': 42.7, 'P99': 43.3, 'P999': 44.2}, {'Month': 4, 'L': 1.0, 'M': 41.6317, 'S': 0.02868, 'SD': 1.194, 'P01': 37.9, 'P1': 38.9, 'P3': 39.4, 'P5': 39.7, 'P10': 40.1, 'P15': 40.4, 'P25': 40.8, 'P50': 41.6, 'P75': 42.4, 'P85': 42.9, 'P90': 43.2, 'P95': 43.6, 'P97': 43.9, 'P99': 44.4, 'P999': 45.3}, {'Month': 5, 'L': 1.0, 'M': 42.5576, 'S': 0.02837, 'SD': 1.20736, 'P01': 38.8, 'P1': 39.7, 'P3': 40.3, 'P5': 40.6, 'P10': 41.0, 'P15': 41.3, 'P25': 41.7, 'P50': 42.6, 'P75': 43.4, 'P85': 43.8, 'P90': 44.1, 'P95': 44.5, 'P97': 44.8, 'P99': 45.4, 'P999': 46.3}, {'Month': 6, 'L': 1.0, 'M': 43.3306, 'S': 0.02817, 'SD': 1.22062, 'P01': 39.6, 'P1': 40.5, 'P3': 41.0, 'P5': 41.3, 'P10': 41.8, 'P15': 42.1, 'P25': 42.5, 'P50': 43.3, 'P75': 44.2, 'P85': 44.6, 'P90': 44.9, 'P95': 45.3, 'P97': 45.6, 'P99': 46.2, 'P999': 47.1}, {'Month': 7, 'L': 1.0, 'M': 43.9803, 'S': 0.02804, 'SD': 1.23321, 'P01': 40.2, 'P1': 41.1, 'P3': 41.7, 'P5': 42.0, 'P10': 42.4, 'P15': 42.7, 'P25': 43.1, 'P50': 44.0, 'P75': 44.8, 'P85': 45.3, 'P90': 45.6, 'P95': 46.0, 'P97': 46.3, 'P99': 46.8, 'P999': 47.8}, {'Month': 8, 'L': 1.0, 'M': 44.53, 'S': 0.02796, 'SD': 1.24506, 'P01': 40.7, 'P1': 41.6, 'P3': 42.2, 'P5': 42.5, 'P10': 42.9, 'P15': 43.2, 'P25': 43.7, 'P50': 44.5, 'P75': 45.4, 'P85': 45.8, 'P90': 46.1, 'P95': 46.6, 'P97': 46.9, 'P99': 47.4, 'P999': 48.4}, {'Month': 9, 'L': 1.0, 'M': 44.9998, 'S': 0.02792, 'SD': 1.25639, 'P01': 41.1, 'P1': 42.1, 'P3': 42.6, 'P5': 42.9, 'P10': 43.4, 'P15': 43.7, 'P25': 44.2, 'P50': 45.0, 'P75': 45.8, 'P85': 46.3, 'P90': 46.6, 'P95': 47.1, 'P97': 47.4, 'P99': 47.9, 'P999': 48.9}, {'Month': 10, 'L': 1.0, 'M': 45.4051, 'S': 0.0279, 'SD': 1.2668, 'P01': 41.5, 'P1': 42.5, 'P3': 43.0, 'P5': 43.3, 'P10': 43.8, 'P15': 44.1, 'P25': 44.6, 'P50': 45.4, 'P75': 46.3, 'P85': 46.7, 'P90': 47.0, 'P95': 47.5, 'P97': 47.8, 'P99': 48.4, 'P999': 49.3}, {'Month': 11, 'L': 1.0, 'M': 45.7573, 'S': 0.02789, 'SD': 1.27617, 'P01': 41.8, 'P1': 42.8, 'P3': 43.4, 'P5': 43.7, 'P10': 44.1, 'P15': 44.4, 'P25': 44.9, 'P50': 45.8, 'P75': 46.6, 'P85': 47.1, 'P90': 47.4, 'P95': 47.9, 'P97': 48.2, 'P99': 48.7, 'P999': 49.7}, {'Month': 12, 'L': 1.0, 'M': 46.0661, 'S': 0.02789, 'SD': 1.28478, 'P01': 42.1, 'P1': 43.1, 'P3': 43.6, 'P5': 44.0, 'P10': 44.4, 'P15': 44.7, 'P25': 45.2, 'P50': 46.1, 'P75': 46.9, 'P85': 47.4, 'P90': 47.7, 'P95': 48.2, 'P97': 48.5, 'P99': 49.1, 'P999': 50.0}, {'Month': 13, 'L': 1.0, 'M': 46.3395, 'S': 0.02789, 'SD': 1.29241, 'P01': 42.3, 'P1': 43.3, 'P3': 43.9, 'P5': 44.2, 'P10': 44.7, 'P15': 45.0, 'P25': 45.5, 'P50': 46.3, 'P75': 47.2, 'P85': 47.7, 'P90': 48.0, 'P95': 48.5, 'P97': 48.8, 'P99': 49.3, 'P999': 50.3}, {'Month': 14, 'L': 1.0, 'M': 46.5844, 'S': 0.02791, 'SD': 1.30017, 'P01': 42.6, 'P1': 43.6, 'P3': 44.1, 'P5': 44.4, 'P10': 44.9, 'P15': 45.2, 'P25': 45.7, 'P50': 46.6, 'P75': 47.5, 'P85': 47.9, 'P90': 48.3, 'P95': 48.7, 'P97': 49.0, 'P99': 49.6, 'P999': 50.6}, {'Month': 15, 'L': 1.0, 'M': 46.806, 'S': 0.02792, 'SD': 1.30682, 'P01': 42.8, 'P1': 43.8, 'P3': 44.3, 'P5': 44.7, 'P10': 45.1, 'P15': 45.5, 'P25': 45.9, 'P50': 46.8, 'P75': 47.7, 'P85': 48.2, 'P90': 48.5, 'P95': 49.0, 'P97': 49.3, 'P99': 49.8, 'P999': 50.8}, {'Month': 16, 'L': 1.0, 'M': 47.0088, 'S': 0.02795, 'SD': 1.3139, 'P01': 42.9, 'P1': 44.0, 'P3': 44.5, 'P5': 44.8, 'P10': 45.3, 'P15': 45.6, 'P25': 46.1, 'P50': 47.0, 'P75': 47.9, 'P85': 48.4, 'P90': 48.7, 'P95': 49.2, 'P97': 49.5, 'P99': 50.1, 'P999': 51.1}, {'Month': 17, 'L': 1.0, 'M': 47.1962, 'S': 0.02797, 'SD': 1.32008, 'P01': 43.1, 'P1': 44.1, 'P3': 44.7, 'P5': 45.0, 'P10': 45.5, 'P15': 45.8, 'P25': 46.3, 'P50': 47.2, 'P75': 48.1, 'P85': 48.6, 'P90': 48.9, 'P95': 49.4, 'P97': 49.7, 'P99': 50.3, 'P999': 51.3}, {'Month': 18, 'L': 1.0, 'M': 47.3711, 'S': 0.028, 'SD': 1.32639, 'P01': 43.3, 'P1': 44.3, 'P3': 44.9, 'P5': 45.2, 'P10': 45.7, 'P15': 46.0, 'P25': 46.5, 'P50': 47.4, 'P75': 48.3, 'P85': 48.7, 'P90': 49.1, 'P95': 49.6, 'P97': 49.9, 'P99': 50.5, 'P999': 51.5}, {'Month': 19, 'L': 1.0, 'M': 47.5357, 'S': 0.02803, 'SD': 1.33243, 'P01': 43.4, 'P1': 44.4, 'P3': 45.0, 'P5': 45.3, 'P10': 45.8, 'P15': 46.2, 'P25': 46.6, 'P50': 47.5, 'P75': 48.4, 'P85': 48.9, 'P90': 49.2, 'P95': 49.7, 'P97': 50.0, 'P99': 50.6, 'P999': 51.7}, {'Month': 20, 'L': 1.0, 'M': 47.6919, 'S': 0.02806, 'SD': 1.33823, 'P01': 43.6, 'P1': 44.6, 'P3': 45.2, 'P5': 45.5, 'P10': 46.0, 'P15': 46.3, 'P25': 46.8, 'P50': 47.7, 'P75': 48.6, 'P85': 49.1, 'P90': 49.4, 'P95': 49.9, 'P97': 50.2, 'P99': 50.8, 'P999': 51.8}, {'Month': 21, 'L': 1.0, 'M': 47.8408, 'S': 0.0281, 'SD': 1.34433, 'P01': 43.7, 'P1': 44.7, 'P3': 45.3, 'P5': 45.6, 'P10': 46.1, 'P15': 46.4, 'P25': 46.9, 'P50': 47.8, 'P75': 48.7, 'P85': 49.2, 'P90': 49.6, 'P95': 50.1, 'P97': 50.4, 'P99': 51.0, 'P999': 52.0}, {'Month': 22, 'L': 1.0, 'M': 47.9833, 'S': 0.02813, 'SD': 1.34977, 'P01': 43.8, 'P1': 44.8, 'P3': 45.4, 'P5': 45.8, 'P10': 46.3, 'P15': 46.6, 'P25': 47.1, 'P50': 48.0, 'P75': 48.9, 'P85': 49.4, 'P90': 49.7, 'P95': 50.2, 'P97': 50.5, 'P99': 51.1, 'P999': 52.2}, {'Month': 23, 'L': 1.0, 'M': 48.1201, 'S': 0.02817, 'SD': 1.35554, 'P01': 43.9, 'P1': 45.0, 'P3': 45.6, 'P5': 45.9, 'P10': 46.4, 'P15': 46.7, 'P25': 47.2, 'P50': 48.1, 'P75': 49.0, 'P85': 49.5, 'P90': 49.9, 'P95': 50.3, 'P97': 50.7, 'P99': 51.3, 'P999': 52.3}, {'Month': 24, 'L': 1.0, 'M': 48.2515, 'S': 0.02821, 'SD': 1.36117, 'P01': 44.0, 'P1': 45.1, 'P3': 45.7, 'P5': 46.0, 'P10': 46.5, 'P15': 46.8, 'P25': 47.3, 'P50': 48.3, 'P75': 49.2, 'P85': 49.7, 'P90': 50.0, 'P95': 50.5, 'P97': 50.8, 'P99': 51.4, 'P999': 52.5}, {'Month': 25, 'L': 1.0, 'M': 48.3777, 'S': 0.02825, 'SD': 1.36667, 'P01': 44.2, 'P1': 45.2, 'P3': 45.8, 'P5': 46.1, 'P10': 46.6, 'P15': 47.0, 'P25': 47.5, 'P50': 48.4, 'P75': 49.3, 'P85': 49.8, 'P90': 50.1, 'P95': 50.6, 'P97': 50.9, 'P99': 51.6, 'P999': 52.6}, {'Month': 26, 'L': 1.0, 'M': 48.4989, 'S': 0.0283, 'SD': 1.37252, 'P01': 44.3, 'P1': 45.3, 'P3': 45.9, 'P5': 46.2, 'P10': 46.7, 'P15': 47.1, 'P25': 47.6, 'P50': 48.5, 'P75': 49.4, 'P85': 49.9, 'P90': 50.3, 'P95': 50.8, 'P97': 51.1, 'P99': 51.7, 'P999': 52.7}, {'Month': 27, 'L': 1.0, 'M': 48.6151, 'S': 0.02834, 'SD': 1.37775, 'P01': 44.4, 'P1': 45.4, 'P3': 46.0, 'P5': 46.3, 'P10': 46.8, 'P15': 47.2, 'P25': 47.7, 'P50': 48.6, 'P75': 49.5, 'P85': 50.0, 'P90': 50.4, 'P95': 50.9, 'P97': 51.2, 'P99': 51.8, 'P999': 52.9}, {'Month': 28, 'L': 1.0, 'M': 48.7264, 'S': 0.02838, 'SD': 1.38286, 'P01': 44.5, 'P1': 45.5, 'P3': 46.1, 'P5': 46.5, 'P10': 47.0, 'P15': 47.3, 'P25': 47.8, 'P50': 48.7, 'P75': 49.7, 'P85': 50.2, 'P90': 50.5, 'P95': 51.0, 'P97': 51.3, 'P99': 51.9, 'P999': 53.0}, {'Month': 29, 'L': 1.0, 'M': 48.8331, 'S': 0.02842, 'SD': 1.38784, 'P01': 44.5, 'P1': 45.6, 'P3': 46.2, 'P5': 46.6, 'P10': 47.1, 'P15': 47.4, 'P25': 47.9, 'P50': 48.8, 'P75': 49.8, 'P85': 50.3, 'P90': 50.6, 'P95': 51.1, 'P97': 51.4, 'P99': 52.1, 'P999': 53.1}, {'Month': 30, 'L': 1.0, 'M': 48.9351, 'S': 0.02847, 'SD': 1.39318, 'P01': 44.6, 'P1': 45.7, 'P3': 46.3, 'P5': 46.6, 'P10': 47.1, 'P15': 47.5, 'P25': 48.0, 'P50': 48.9, 'P75': 49.9, 'P85': 50.4, 'P90': 50.7, 'P95': 51.2, 'P97': 51.6, 'P99': 52.2, 'P999': 53.2}, {'Month': 31, 'L': 1.0, 'M': 49.0327, 'S': 0.02851, 'SD': 1.39792, 'P01': 44.7, 'P1': 45.8, 'P3': 46.4, 'P5': 46.7, 'P10': 47.2, 'P15': 47.6, 'P25': 48.1, 'P50': 49.0, 'P75': 50.0, 'P85': 50.5, 'P90': 50.8, 'P95': 51.3, 'P97': 51.7, 'P99': 52.3, 'P999': 53.4}, {'Month': 32, 'L': 1.0, 'M': 49.126, 'S': 0.02855, 'SD': 1.40255, 'P01': 44.8, 'P1': 45.9, 'P3': 46.5, 'P5': 46.8, 'P10': 47.3, 'P15': 47.7, 'P25': 48.2, 'P50': 49.1, 'P75': 50.1, 'P85': 50.6, 'P90': 50.9, 'P95': 51.4, 'P97': 51.8, 'P99': 52.4, 'P999': 53.5}, {'Month': 33, 'L': 1.0, 'M': 49.2153, 'S': 0.02859, 'SD': 1.40707, 'P01': 44.9, 'P1': 45.9, 'P3': 46.6, 'P5': 46.9, 'P10': 47.4, 'P15': 47.8, 'P25': 48.3, 'P50': 49.2, 'P75': 50.2, 'P85': 50.7, 'P90': 51.0, 'P95': 51.5, 'P97': 51.9, 'P99': 52.5, 'P999': 53.6}, {'Month': 34, 'L': 1.0, 'M': 49.3007, 'S': 0.02863, 'SD': 1.41148, 'P01': 44.9, 'P1': 46.0, 'P3': 46.6, 'P5': 47.0, 'P10': 47.5, 'P15': 47.8, 'P25': 48.3, 'P50': 49.3, 'P75': 50.3, 'P85': 50.8, 'P90': 51.1, 'P95': 51.6, 'P97': 52.0, 'P99': 52.6, 'P999': 53.7}, {'Month': 35, 'L': 1.0, 'M': 49.3826, 'S': 0.02867, 'SD': 1.4158, 'P01': 45.0, 'P1': 46.1, 'P3': 46.7, 'P5': 47.1, 'P10': 47.6, 'P15': 47.9, 'P25': 48.4, 'P50': 49.4, 'P75': 50.3, 'P85': 50.8, 'P90': 51.2, 'P95': 51.7, 'P97': 52.0, 'P99': 52.7, 'P999': 53.8}, {'Month': 36, 'L': 1.0, 'M': 49.4612, 'S': 0.02871, 'SD': 1.42003, 'P01': 45.1, 'P1': 46.2, 'P3': 46.8, 'P5': 47.1, 'P10': 47.6, 'P15': 48.0, 'P25': 48.5, 'P50': 49.5, 'P75': 50.4, 'P85': 50.9, 'P90': 51.3, 'P95': 51.8, 'P97': 52.1, 'P99': 52.8, 'P999': 53.8}, {'Month': 37, 'L': 1.0, 'M': 49.5367, 'S': 0.02875, 'SD': 1.42418, 'P01': 45.1, 'P1': 46.2, 'P3': 46.9, 'P5': 47.2, 'P10': 47.7, 'P15': 48.1, 'P25': 48.6, 'P50': 49.5, 'P75': 50.5, 'P85': 51.0, 'P90': 51.4, 'P95': 51.9, 'P97': 52.2, 'P99': 52.8, 'P999': 53.9}, {'Month': 38, 'L': 1.0, 'M': 49.6093, 'S': 0.02878, 'SD': 1.42776, 'P01': 45.2, 'P1': 46.3, 'P3': 46.9, 'P5': 47.3, 'P10': 47.8, 'P15': 48.1, 'P25': 48.6, 'P50': 49.6, 'P75': 50.6, 'P85': 51.1, 'P90': 51.4, 'P95': 52.0, 'P97': 52.3, 'P99': 52.9, 'P999': 54.0}, {'Month': 39, 'L': 1.0, 'M': 49.6791, 'S': 0.02882, 'SD': 1.43175, 'P01': 45.3, 'P1': 46.3, 'P3': 47.0, 'P5': 47.3, 'P10': 47.8, 'P15': 48.2, 'P25': 48.7, 'P50': 49.7, 'P75': 50.6, 'P85': 51.2, 'P90': 51.5, 'P95': 52.0, 'P97': 52.4, 'P99': 53.0, 'P999': 54.1}, {'Month': 40, 'L': 1.0, 'M': 49.7465, 'S': 0.02886, 'SD': 1.43568, 'P01': 45.3, 'P1': 46.4, 'P3': 47.0, 'P5': 47.4, 'P10': 47.9, 'P15': 48.3, 'P25': 48.8, 'P50': 49.7, 'P75': 50.7, 'P85': 51.2, 'P90': 51.6, 'P95': 52.1, 'P97': 52.4, 'P99': 53.1, 'P999': 54.2}, {'Month': 41, 'L': 1.0, 'M': 49.8116, 'S': 0.02889, 'SD': 1.43906, 'P01': 45.4, 'P1': 46.5, 'P3': 47.1, 'P5': 47.4, 'P10': 48.0, 'P15': 48.3, 'P25': 48.8, 'P50': 49.8, 'P75': 50.8, 'P85': 51.3, 'P90': 51.7, 'P95': 52.2, 'P97': 52.5, 'P99': 53.2, 'P999': 54.3}, {'Month': 42, 'L': 1.0, 'M': 49.8745, 'S': 0.02893, 'SD': 1.44287, 'P01': 45.4, 'P1': 46.5, 'P3': 47.2, 'P5': 47.5, 'P10': 48.0, 'P15': 48.4, 'P25': 48.9, 'P50': 49.9, 'P75': 50.8, 'P85': 51.4, 'P90': 51.7, 'P95': 52.2, 'P97': 52.6, 'P99': 53.2, 'P999': 54.3}, {'Month': 43, 'L': 1.0, 'M': 49.9354, 'S': 0.02896, 'SD': 1.44613, 'P01': 45.5, 'P1': 46.6, 'P3': 47.2, 'P5': 47.6, 'P10': 48.1, 'P15': 48.4, 'P25': 49.0, 'P50': 49.9, 'P75': 50.9, 'P85': 51.4, 'P90': 51.8, 'P95': 52.3, 'P97': 52.7, 'P99': 53.3, 'P999': 54.4}, {'Month': 44, 'L': 1.0, 'M': 49.9942, 'S': 0.02899, 'SD': 1.44933, 'P01': 45.5, 'P1': 46.6, 'P3': 47.3, 'P5': 47.6, 'P10': 48.1, 'P15': 48.5, 'P25': 49.0, 'P50': 50.0, 'P75': 51.0, 'P85': 51.5, 'P90': 51.9, 'P95': 52.4, 'P97': 52.7, 'P99': 53.4, 'P999': 54.5}, {'Month': 45, 'L': 1.0, 'M': 50.0512, 'S': 0.02903, 'SD': 1.45299, 'P01': 45.6, 'P1': 46.7, 'P3': 47.3, 'P5': 47.7, 'P10': 48.2, 'P15': 48.5, 'P25': 49.1, 'P50': 50.1, 'P75': 51.0, 'P85': 51.6, 'P90': 51.9, 'P95': 52.4, 'P97': 52.8, 'P99': 53.4, 'P999': 54.5}, {'Month': 46, 'L': 1.0, 'M': 50.1064, 'S': 0.02906, 'SD': 1.45609, 'P01': 45.6, 'P1': 46.7, 'P3': 47.4, 'P5': 47.7, 'P10': 48.2, 'P15': 48.6, 'P25': 49.1, 'P50': 50.1, 'P75': 51.1, 'P85': 51.6, 'P90': 52.0, 'P95': 52.5, 'P97': 52.8, 'P99': 53.5, 'P999': 54.6}, {'Month': 47, 'L': 1.0, 'M': 50.1598, 'S': 0.02909, 'SD': 1.45915, 'P01': 45.7, 'P1': 46.8, 'P3': 47.4, 'P5': 47.8, 'P10': 48.3, 'P15': 48.6, 'P25': 49.2, 'P50': 50.2, 'P75': 51.1, 'P85': 51.7, 'P90': 52.0, 'P95': 52.6, 'P97': 52.9, 'P99': 53.6, 'P999': 54.7}, {'Month': 48, 'L': 1.0, 'M': 50.2115, 'S': 0.02912, 'SD': 1.46216, 'P01': 45.7, 'P1': 46.8, 'P3': 47.5, 'P5': 47.8, 'P10': 48.3, 'P15': 48.7, 'P25': 49.2, 'P50': 50.2, 'P75': 51.2, 'P85': 51.7, 'P90': 52.1, 'P95': 52.6, 'P97': 53.0, 'P99': 53.6, 'P999': 54.7}, {'Month': 49, 'L': 1.0, 'M': 50.2617, 'S': 0.02915, 'SD': 1.46513, 'P01': 45.7, 'P1': 46.9, 'P3': 47.5, 'P5': 47.9, 'P10': 48.4, 'P15': 48.7, 'P25': 49.3, 'P50': 50.3, 'P75': 51.2, 'P85': 51.8, 'P90': 52.1, 'P95': 52.7, 'P97': 53.0, 'P99': 53.7, 'P999': 54.8}, {'Month': 50, 'L': 1.0, 'M': 50.3105, 'S': 0.02918, 'SD': 1.46806, 'P01': 45.8, 'P1': 46.9, 'P3': 47.5, 'P5': 47.9, 'P10': 48.4, 'P15': 48.8, 'P25': 49.3, 'P50': 50.3, 'P75': 51.3, 'P85': 51.8, 'P90': 52.2, 'P95': 52.7, 'P97': 53.1, 'P99': 53.7, 'P999': 54.8}, {'Month': 51, 'L': 1.0, 'M': 50.3578, 'S': 0.02921, 'SD': 1.47095, 'P01': 45.8, 'P1': 46.9, 'P3': 47.6, 'P5': 47.9, 'P10': 48.5, 'P15': 48.8, 'P25': 49.4, 'P50': 50.4, 'P75': 51.3, 'P85': 51.9, 'P90': 52.2, 'P95': 52.8, 'P97': 53.1, 'P99': 53.8, 'P999': 54.9}, {'Month': 52, 'L': 1.0, 'M': 50.4039, 'S': 0.02924, 'SD': 1.47381, 'P01': 45.8, 'P1': 47.0, 'P3': 47.6, 'P5': 48.0, 'P10': 48.5, 'P15': 48.9, 'P25': 49.4, 'P50': 50.4, 'P75': 51.4, 'P85': 51.9, 'P90': 52.3, 'P95': 52.8, 'P97': 53.2, 'P99': 53.8, 'P999': 55.0}, {'Month': 53, 'L': 1.0, 'M': 50.4488, 'S': 0.02927, 'SD': 1.47664, 'P01': 45.9, 'P1': 47.0, 'P3': 47.7, 'P5': 48.0, 'P10': 48.6, 'P15': 48.9, 'P25': 49.5, 'P50': 50.4, 'P75': 51.4, 'P85': 52.0, 'P90': 52.3, 'P95': 52.9, 'P97': 53.2, 'P99': 53.9, 'P999': 55.0}, {'Month': 54, 'L': 1.0, 'M': 50.4926, 'S': 0.02929, 'SD': 1.47893, 'P01': 45.9, 'P1': 47.1, 'P3': 47.7, 'P5': 48.1, 'P10': 48.6, 'P15': 49.0, 'P25': 49.5, 'P50': 50.5, 'P75': 51.5, 'P85': 52.0, 'P90': 52.4, 'P95': 52.9, 'P97': 53.3, 'P99': 53.9, 'P999': 55.1}, {'Month': 55, 'L': 1.0, 'M': 50.5354, 'S': 0.02932, 'SD': 1.4817, 'P01': 46.0, 'P1': 47.1, 'P3': 47.7, 'P5': 48.1, 'P10': 48.6, 'P15': 49.0, 'P25': 49.5, 'P50': 50.5, 'P75': 51.5, 'P85': 52.1, 'P90': 52.4, 'P95': 53.0, 'P97': 53.3, 'P99': 54.0, 'P999': 55.1}, {'Month': 56, 'L': 1.0, 'M': 50.5772, 'S': 0.02935, 'SD': 1.48444, 'P01': 46.0, 'P1': 47.1, 'P3': 47.8, 'P5': 48.1, 'P10': 48.7, 'P15': 49.0, 'P25': 49.6, 'P50': 50.6, 'P75': 51.6, 'P85': 52.1, 'P90': 52.5, 'P95': 53.0, 'P97': 53.4, 'P99': 54.0, 'P999': 55.2}, {'Month': 57, 'L': 1.0, 'M': 50.6183, 'S': 0.02938, 'SD': 1.48717, 'P01': 46.0, 'P1': 47.2, 'P3': 47.8, 'P5': 48.2, 'P10': 48.7, 'P15': 49.1, 'P25': 49.6, 'P50': 50.6, 'P75': 51.6, 'P85': 52.2, 'P90': 52.5, 'P95': 53.1, 'P97': 53.4, 'P99': 54.1, 'P999': 55.2}, {'Month': 58, 'L': 1.0, 'M': 50.6587, 'S': 0.0294, 'SD': 1.48937, 'P01': 46.1, 'P1': 47.2, 'P3': 47.9, 'P5': 48.2, 'P10': 48.8, 'P15': 49.1, 'P25': 49.7, 'P50': 50.7, 'P75': 51.7, 'P85': 52.2, 'P90': 52.6, 'P95': 53.1, 'P97': 53.5, 'P99': 54.1, 'P999': 55.3}, {'Month': 59, 'L': 1.0, 'M': 50.6984, 'S': 0.02943, 'SD': 1.49205, 'P01': 46.1, 'P1': 47.2, 'P3': 47.9, 'P5': 48.2, 'P10': 48.8, 'P15': 49.2, 'P25': 49.7, 'P50': 50.7, 'P75': 51.7, 'P85': 52.2, 'P90': 52.6, 'P95': 53.2, 'P97': 53.5, 'P99': 54.2, 'P999': 55.3}, {'Month': 60, 'L': 1.0, 'M': 50.7375, 'S': 0.02946, 'SD': 1.49473, 'P01': 46.1, 'P1': 47.3, 'P3': 47.9, 'P5': 48.3, 'P10': 48.8, 'P15': 49.2, 'P25': 49.7, 'P50': 50.7, 'P75': 51.7, 'P85': 52.3, 'P90': 52.7, 'P95': 53.2, 'P97': 53.5, 'P99': 54.2, 'P999': 55.4}]

WHO_HCFA_GIRLS_P = [{'Month': 0, 'L': 1.0, 'M': 33.8787, 'S': 0.03496, 'SD': 1.1844, 'P01': 30.2, 'P1': 31.1, 'P3': 31.7, 'P5': 31.9, 'P10': 32.4, 'P15': 32.7, 'P25': 33.1, 'P50': 33.9, 'P75': 34.7, 'P85': 35.1, 'P90': 35.4, 'P95': 35.8, 'P97': 36.1, 'P99': 36.6, 'P999': 37.5}, {'Month': 1, 'L': 1.0, 'M': 36.5463, 'S': 0.0321, 'SD': 1.17314, 'P01': 32.9, 'P1': 33.8, 'P3': 34.3, 'P5': 34.6, 'P10': 35.0, 'P15': 35.3, 'P25': 35.8, 'P50': 36.5, 'P75': 37.3, 'P85': 37.8, 'P90': 38.0, 'P95': 38.5, 'P97': 38.8, 'P99': 39.3, 'P999': 40.2}, {'Month': 2, 'L': 1.0, 'M': 38.2521, 'S': 0.03168, 'SD': 1.21183, 'P01': 34.5, 'P1': 35.4, 'P3': 36.0, 'P5': 36.3, 'P10': 36.7, 'P15': 37.0, 'P25': 37.4, 'P50': 38.3, 'P75': 39.1, 'P85': 39.5, 'P90': 39.8, 'P95': 40.2, 'P97': 40.5, 'P99': 41.1, 'P999': 42.0}, {'Month': 3, 'L': 1.0, 'M': 39.5328, 'S': 0.0314, 'SD': 1.24133, 'P01': 35.7, 'P1': 36.6, 'P3': 37.2, 'P5': 37.5, 'P10': 37.9, 'P15': 38.2, 'P25': 38.7, 'P50': 39.5, 'P75': 40.4, 'P85': 40.8, 'P90': 41.1, 'P95': 41.6, 'P97': 41.9, 'P99': 42.4, 'P999': 43.4}, {'Month': 4, 'L': 1.0, 'M': 40.5817, 'S': 0.03119, 'SD': 1.26574, 'P01': 36.7, 'P1': 37.6, 'P3': 38.2, 'P5': 38.5, 'P10': 39.0, 'P15': 39.3, 'P25': 39.7, 'P50': 40.6, 'P75': 41.4, 'P85': 41.9, 'P90': 42.2, 'P95': 42.7, 'P97': 43.0, 'P99': 43.5, 'P999': 44.5}, {'Month': 5, 'L': 1.0, 'M': 41.459, 'S': 0.03102, 'SD': 1.28606, 'P01': 37.5, 'P1': 38.5, 'P3': 39.0, 'P5': 39.3, 'P10': 39.8, 'P15': 40.1, 'P25': 40.6, 'P50': 41.5, 'P75': 42.3, 'P85': 42.8, 'P90': 43.1, 'P95': 43.6, 'P97': 43.9, 'P99': 44.5, 'P999': 45.4}, {'Month': 6, 'L': 1.0, 'M': 42.1995, 'S': 0.03087, 'SD': 1.3027, 'P01': 38.2, 'P1': 39.2, 'P3': 39.7, 'P5': 40.1, 'P10': 40.5, 'P15': 40.8, 'P25': 41.3, 'P50': 42.2, 'P75': 43.1, 'P85': 43.5, 'P90': 43.9, 'P95': 44.3, 'P97': 44.6, 'P99': 45.2, 'P999': 46.2}, {'Month': 7, 'L': 1.0, 'M': 42.829, 'S': 0.03075, 'SD': 1.31699, 'P01': 38.8, 'P1': 39.8, 'P3': 40.4, 'P5': 40.7, 'P10': 41.1, 'P15': 41.5, 'P25': 41.9, 'P50': 42.8, 'P75': 43.7, 'P85': 44.2, 'P90': 44.5, 'P95': 45.0, 'P97': 45.3, 'P99': 45.9, 'P999': 46.9}, {'Month': 8, 'L': 1.0, 'M': 43.3671, 'S': 0.03063, 'SD': 1.32833, 'P01': 39.3, 'P1': 40.3, 'P3': 40.9, 'P5': 41.2, 'P10': 41.7, 'P15': 42.0, 'P25': 42.5, 'P50': 43.4, 'P75': 44.3, 'P85': 44.7, 'P90': 45.1, 'P95': 45.6, 'P97': 45.9, 'P99': 46.5, 'P999': 47.5}, {'Month': 9, 'L': 1.0, 'M': 43.83, 'S': 0.03053, 'SD': 1.33813, 'P01': 39.7, 'P1': 40.7, 'P3': 41.3, 'P5': 41.6, 'P10': 42.1, 'P15': 42.4, 'P25': 42.9, 'P50': 43.8, 'P75': 44.7, 'P85': 45.2, 'P90': 45.5, 'P95': 46.0, 'P97': 46.3, 'P99': 46.9, 'P999': 48.0}, {'Month': 10, 'L': 1.0, 'M': 44.2319, 'S': 0.03044, 'SD': 1.34642, 'P01': 40.1, 'P1': 41.1, 'P3': 41.7, 'P5': 42.0, 'P10': 42.5, 'P15': 42.8, 'P25': 43.3, 'P50': 44.2, 'P75': 45.1, 'P85': 45.6, 'P90': 46.0, 'P95': 46.4, 'P97': 46.8, 'P99': 47.4, 'P999': 48.4}, {'Month': 11, 'L': 1.0, 'M': 44.5844, 'S': 0.03035, 'SD': 1.35314, 'P01': 40.4, 'P1': 41.4, 'P3': 42.0, 'P5': 42.4, 'P10': 42.9, 'P15': 43.2, 'P25': 43.7, 'P50': 44.6, 'P75': 45.5, 'P85': 46.0, 'P90': 46.3, 'P95': 46.8, 'P97': 47.1, 'P99': 47.7, 'P999': 48.8}, {'Month': 12, 'L': 1.0, 'M': 44.8965, 'S': 0.03027, 'SD': 1.35902, 'P01': 40.7, 'P1': 41.7, 'P3': 42.3, 'P5': 42.7, 'P10': 43.2, 'P15': 43.5, 'P25': 44.0, 'P50': 44.9, 'P75': 45.8, 'P85': 46.3, 'P90': 46.6, 'P95': 47.1, 'P97': 47.5, 'P99': 48.1, 'P999': 49.1}, {'Month': 13, 'L': 1.0, 'M': 45.1752, 'S': 0.03019, 'SD': 1.36384, 'P01': 41.0, 'P1': 42.0, 'P3': 42.6, 'P5': 42.9, 'P10': 43.4, 'P15': 43.8, 'P25': 44.3, 'P50': 45.2, 'P75': 46.1, 'P85': 46.6, 'P90': 46.9, 'P95': 47.4, 'P97': 47.7, 'P99': 48.3, 'P999': 49.4}, {'Month': 14, 'L': 1.0, 'M': 45.4265, 'S': 0.03012, 'SD': 1.36825, 'P01': 41.2, 'P1': 42.2, 'P3': 42.9, 'P5': 43.2, 'P10': 43.7, 'P15': 44.0, 'P25': 44.5, 'P50': 45.4, 'P75': 46.3, 'P85': 46.8, 'P90': 47.2, 'P95': 47.7, 'P97': 48.0, 'P99': 48.6, 'P999': 49.7}, {'Month': 15, 'L': 1.0, 'M': 45.6551, 'S': 0.03006, 'SD': 1.37239, 'P01': 41.4, 'P1': 42.5, 'P3': 43.1, 'P5': 43.4, 'P10': 43.9, 'P15': 44.2, 'P25': 44.7, 'P50': 45.7, 'P75': 46.6, 'P85': 47.1, 'P90': 47.4, 'P95': 47.9, 'P97': 48.2, 'P99': 48.8, 'P999': 49.9}, {'Month': 16, 'L': 1.0, 'M': 45.865, 'S': 0.02999, 'SD': 1.37549, 'P01': 41.6, 'P1': 42.7, 'P3': 43.3, 'P5': 43.6, 'P10': 44.1, 'P15': 44.4, 'P25': 44.9, 'P50': 45.9, 'P75': 46.8, 'P85': 47.3, 'P90': 47.6, 'P95': 48.1, 'P97': 48.5, 'P99': 49.1, 'P999': 50.1}, {'Month': 17, 'L': 1.0, 'M': 46.0598, 'S': 0.02993, 'SD': 1.37857, 'P01': 41.8, 'P1': 42.9, 'P3': 43.5, 'P5': 43.8, 'P10': 44.3, 'P15': 44.6, 'P25': 45.1, 'P50': 46.1, 'P75': 47.0, 'P85': 47.5, 'P90': 47.8, 'P95': 48.3, 'P97': 48.7, 'P99': 49.3, 'P999': 50.3}, {'Month': 18, 'L': 1.0, 'M': 46.2424, 'S': 0.02987, 'SD': 1.38126, 'P01': 42.0, 'P1': 43.0, 'P3': 43.6, 'P5': 44.0, 'P10': 44.5, 'P15': 44.8, 'P25': 45.3, 'P50': 46.2, 'P75': 47.2, 'P85': 47.7, 'P90': 48.0, 'P95': 48.5, 'P97': 48.8, 'P99': 49.5, 'P999': 50.5}, {'Month': 19, 'L': 1.0, 'M': 46.4152, 'S': 0.02982, 'SD': 1.3841, 'P01': 42.1, 'P1': 43.2, 'P3': 43.8, 'P5': 44.1, 'P10': 44.6, 'P15': 45.0, 'P25': 45.5, 'P50': 46.4, 'P75': 47.3, 'P85': 47.8, 'P90': 48.2, 'P95': 48.7, 'P97': 49.0, 'P99': 49.6, 'P999': 50.7}, {'Month': 20, 'L': 1.0, 'M': 46.5801, 'S': 0.02977, 'SD': 1.38669, 'P01': 42.3, 'P1': 43.4, 'P3': 44.0, 'P5': 44.3, 'P10': 44.8, 'P15': 45.1, 'P25': 45.6, 'P50': 46.6, 'P75': 47.5, 'P85': 48.0, 'P90': 48.4, 'P95': 48.9, 'P97': 49.2, 'P99': 49.8, 'P999': 50.9}, {'Month': 21, 'L': 1.0, 'M': 46.7384, 'S': 0.02972, 'SD': 1.38907, 'P01': 42.4, 'P1': 43.5, 'P3': 44.1, 'P5': 44.5, 'P10': 45.0, 'P15': 45.3, 'P25': 45.8, 'P50': 46.7, 'P75': 47.7, 'P85': 48.2, 'P90': 48.5, 'P95': 49.0, 'P97': 49.4, 'P99': 50.0, 'P999': 51.0}, {'Month': 22, 'L': 1.0, 'M': 46.8913, 'S': 0.02967, 'SD': 1.39126, 'P01': 42.6, 'P1': 43.7, 'P3': 44.3, 'P5': 44.6, 'P10': 45.1, 'P15': 45.4, 'P25': 46.0, 'P50': 46.9, 'P75': 47.8, 'P85': 48.3, 'P90': 48.7, 'P95': 49.2, 'P97': 49.5, 'P99': 50.1, 'P999': 51.2}, {'Month': 23, 'L': 1.0, 'M': 47.0391, 'S': 0.02962, 'SD': 1.3933, 'P01': 42.7, 'P1': 43.8, 'P3': 44.4, 'P5': 44.7, 'P10': 45.3, 'P15': 45.6, 'P25': 46.1, 'P50': 47.0, 'P75': 48.0, 'P85': 48.5, 'P90': 48.8, 'P95': 49.3, 'P97': 49.7, 'P99': 50.3, 'P999': 51.3}, {'Month': 24, 'L': 1.0, 'M': 47.1822, 'S': 0.02957, 'SD': 1.39518, 'P01': 42.9, 'P1': 43.9, 'P3': 44.6, 'P5': 44.9, 'P10': 45.4, 'P15': 45.7, 'P25': 46.2, 'P50': 47.2, 'P75': 48.1, 'P85': 48.6, 'P90': 49.0, 'P95': 49.5, 'P97': 49.8, 'P99': 50.4, 'P999': 51.5}, {'Month': 25, 'L': 1.0, 'M': 47.3204, 'S': 0.02953, 'SD': 1.39737, 'P01': 43.0, 'P1': 44.1, 'P3': 44.7, 'P5': 45.0, 'P10': 45.5, 'P15': 45.9, 'P25': 46.4, 'P50': 47.3, 'P75': 48.3, 'P85': 48.8, 'P90': 49.1, 'P95': 49.6, 'P97': 49.9, 'P99': 50.6, 'P999': 51.6}, {'Month': 26, 'L': 1.0, 'M': 47.4536, 'S': 0.02949, 'SD': 1.39941, 'P01': 43.1, 'P1': 44.2, 'P3': 44.8, 'P5': 45.2, 'P10': 45.7, 'P15': 46.0, 'P25': 46.5, 'P50': 47.5, 'P75': 48.4, 'P85': 48.9, 'P90': 49.2, 'P95': 49.8, 'P97': 50.1, 'P99': 50.7, 'P999': 51.8}, {'Month': 27, 'L': 1.0, 'M': 47.5817, 'S': 0.02945, 'SD': 1.40128, 'P01': 43.3, 'P1': 44.3, 'P3': 44.9, 'P5': 45.3, 'P10': 45.8, 'P15': 46.1, 'P25': 46.6, 'P50': 47.6, 'P75': 48.5, 'P85': 49.0, 'P90': 49.4, 'P95': 49.9, 'P97': 50.2, 'P99': 50.8, 'P999': 51.9}, {'Month': 28, 'L': 1.0, 'M': 47.7045, 'S': 0.02941, 'SD': 1.40299, 'P01': 43.4, 'P1': 44.4, 'P3': 45.1, 'P5': 45.4, 'P10': 45.9, 'P15': 46.3, 'P25': 46.8, 'P50': 47.7, 'P75': 48.7, 'P85': 49.2, 'P90': 49.5, 'P95': 50.0, 'P97': 50.3, 'P99': 51.0, 'P999': 52.0}, {'Month': 29, 'L': 1.0, 'M': 47.8219, 'S': 0.02937, 'SD': 1.40453, 'P01': 43.5, 'P1': 44.6, 'P3': 45.2, 'P5': 45.5, 'P10': 46.0, 'P15': 46.4, 'P25': 46.9, 'P50': 47.8, 'P75': 48.8, 'P85': 49.3, 'P90': 49.6, 'P95': 50.1, 'P97': 50.5, 'P99': 51.1, 'P999': 52.2}, {'Month': 30, 'L': 1.0, 'M': 47.934, 'S': 0.02933, 'SD': 1.4059, 'P01': 43.6, 'P1': 44.7, 'P3': 45.3, 'P5': 45.6, 'P10': 46.1, 'P15': 46.5, 'P25': 47.0, 'P50': 47.9, 'P75': 48.9, 'P85': 49.4, 'P90': 49.7, 'P95': 50.2, 'P97': 50.6, 'P99': 51.2, 'P999': 52.3}, {'Month': 31, 'L': 1.0, 'M': 48.041, 'S': 0.02929, 'SD': 1.40712, 'P01': 43.7, 'P1': 44.8, 'P3': 45.4, 'P5': 45.7, 'P10': 46.2, 'P15': 46.6, 'P25': 47.1, 'P50': 48.0, 'P75': 49.0, 'P85': 49.5, 'P90': 49.8, 'P95': 50.4, 'P97': 50.7, 'P99': 51.3, 'P999': 52.4}, {'Month': 32, 'L': 1.0, 'M': 48.1432, 'S': 0.02926, 'SD': 1.40867, 'P01': 43.8, 'P1': 44.9, 'P3': 45.5, 'P5': 45.8, 'P10': 46.3, 'P15': 46.7, 'P25': 47.2, 'P50': 48.1, 'P75': 49.1, 'P85': 49.6, 'P90': 49.9, 'P95': 50.5, 'P97': 50.8, 'P99': 51.4, 'P999': 52.5}, {'Month': 33, 'L': 1.0, 'M': 48.2408, 'S': 0.02922, 'SD': 1.4096, 'P01': 43.9, 'P1': 45.0, 'P3': 45.6, 'P5': 45.9, 'P10': 46.4, 'P15': 46.8, 'P25': 47.3, 'P50': 48.2, 'P75': 49.2, 'P85': 49.7, 'P90': 50.0, 'P95': 50.6, 'P97': 50.9, 'P99': 51.5, 'P999': 52.6}, {'Month': 34, 'L': 1.0, 'M': 48.3343, 'S': 0.02919, 'SD': 1.41088, 'P01': 44.0, 'P1': 45.1, 'P3': 45.7, 'P5': 46.0, 'P10': 46.5, 'P15': 46.9, 'P25': 47.4, 'P50': 48.3, 'P75': 49.3, 'P85': 49.8, 'P90': 50.1, 'P95': 50.7, 'P97': 51.0, 'P99': 51.6, 'P999': 52.7}, {'Month': 35, 'L': 1.0, 'M': 48.4239, 'S': 0.02915, 'SD': 1.41156, 'P01': 44.1, 'P1': 45.1, 'P3': 45.8, 'P5': 46.1, 'P10': 46.6, 'P15': 47.0, 'P25': 47.5, 'P50': 48.4, 'P75': 49.4, 'P85': 49.9, 'P90': 50.2, 'P95': 50.7, 'P97': 51.1, 'P99': 51.7, 'P999': 52.8}, {'Month': 36, 'L': 1.0, 'M': 48.5099, 'S': 0.02912, 'SD': 1.41261, 'P01': 44.1, 'P1': 45.2, 'P3': 45.9, 'P5': 46.2, 'P10': 46.7, 'P15': 47.0, 'P25': 47.6, 'P50': 48.5, 'P75': 49.5, 'P85': 50.0, 'P90': 50.3, 'P95': 50.8, 'P97': 51.2, 'P99': 51.8, 'P999': 52.9}, {'Month': 37, 'L': 1.0, 'M': 48.5926, 'S': 0.02909, 'SD': 1.41356, 'P01': 44.2, 'P1': 45.3, 'P3': 45.9, 'P5': 46.3, 'P10': 46.8, 'P15': 47.1, 'P25': 47.6, 'P50': 48.6, 'P75': 49.5, 'P85': 50.1, 'P90': 50.4, 'P95': 50.9, 'P97': 51.3, 'P99': 51.9, 'P999': 53.0}, {'Month': 38, 'L': 1.0, 'M': 48.6722, 'S': 0.02906, 'SD': 1.41441, 'P01': 44.3, 'P1': 45.4, 'P3': 46.0, 'P5': 46.3, 'P10': 46.9, 'P15': 47.2, 'P25': 47.7, 'P50': 48.7, 'P75': 49.6, 'P85': 50.1, 'P90': 50.5, 'P95': 51.0, 'P97': 51.3, 'P99': 52.0, 'P999': 53.0}, {'Month': 39, 'L': 1.0, 'M': 48.7489, 'S': 0.02903, 'SD': 1.41518, 'P01': 44.4, 'P1': 45.5, 'P3': 46.1, 'P5': 46.4, 'P10': 46.9, 'P15': 47.3, 'P25': 47.8, 'P50': 48.7, 'P75': 49.7, 'P85': 50.2, 'P90': 50.6, 'P95': 51.1, 'P97': 51.4, 'P99': 52.0, 'P999': 53.1}, {'Month': 40, 'L': 1.0, 'M': 48.8228, 'S': 0.029, 'SD': 1.41586, 'P01': 44.4, 'P1': 45.5, 'P3': 46.2, 'P5': 46.5, 'P10': 47.0, 'P15': 47.4, 'P25': 47.9, 'P50': 48.8, 'P75': 49.8, 'P85': 50.3, 'P90': 50.6, 'P95': 51.2, 'P97': 51.5, 'P99': 52.1, 'P999': 53.2}, {'Month': 41, 'L': 1.0, 'M': 48.8941, 'S': 0.02897, 'SD': 1.41646, 'P01': 44.5, 'P1': 45.6, 'P3': 46.2, 'P5': 46.6, 'P10': 47.1, 'P15': 47.4, 'P25': 47.9, 'P50': 48.9, 'P75': 49.8, 'P85': 50.4, 'P90': 50.7, 'P95': 51.2, 'P97': 51.6, 'P99': 52.2, 'P999': 53.3}, {'Month': 42, 'L': 1.0, 'M': 48.9629, 'S': 0.02894, 'SD': 1.41699, 'P01': 44.6, 'P1': 45.7, 'P3': 46.3, 'P5': 46.6, 'P10': 47.1, 'P15': 47.5, 'P25': 48.0, 'P50': 49.0, 'P75': 49.9, 'P85': 50.4, 'P90': 50.8, 'P95': 51.3, 'P97': 51.6, 'P99': 52.3, 'P999': 53.3}, {'Month': 43, 'L': 1.0, 'M': 49.0294, 'S': 0.02891, 'SD': 1.41744, 'P01': 44.6, 'P1': 45.7, 'P3': 46.4, 'P5': 46.7, 'P10': 47.2, 'P15': 47.6, 'P25': 48.1, 'P50': 49.0, 'P75': 50.0, 'P85': 50.5, 'P90': 50.8, 'P95': 51.4, 'P97': 51.7, 'P99': 52.3, 'P999': 53.4}, {'Month': 44, 'L': 1.0, 'M': 49.0937, 'S': 0.02888, 'SD': 1.41783, 'P01': 44.7, 'P1': 45.8, 'P3': 46.4, 'P5': 46.8, 'P10': 47.3, 'P15': 47.6, 'P25': 48.1, 'P50': 49.1, 'P75': 50.1, 'P85': 50.6, 'P90': 50.9, 'P95': 51.4, 'P97': 51.8, 'P99': 52.4, 'P999': 53.5}, {'Month': 45, 'L': 1.0, 'M': 49.156, 'S': 0.02886, 'SD': 1.41864, 'P01': 44.8, 'P1': 45.9, 'P3': 46.5, 'P5': 46.8, 'P10': 47.3, 'P15': 47.7, 'P25': 48.2, 'P50': 49.2, 'P75': 50.1, 'P85': 50.6, 'P90': 51.0, 'P95': 51.5, 'P97': 51.8, 'P99': 52.5, 'P999': 53.5}, {'Month': 46, 'L': 1.0, 'M': 49.2164, 'S': 0.02883, 'SD': 1.41891, 'P01': 44.8, 'P1': 45.9, 'P3': 46.5, 'P5': 46.9, 'P10': 47.4, 'P15': 47.7, 'P25': 48.3, 'P50': 49.2, 'P75': 50.2, 'P85': 50.7, 'P90': 51.0, 'P95': 51.6, 'P97': 51.9, 'P99': 52.5, 'P999': 53.6}, {'Month': 47, 'L': 1.0, 'M': 49.2751, 'S': 0.0288, 'SD': 1.41912, 'P01': 44.9, 'P1': 46.0, 'P3': 46.6, 'P5': 46.9, 'P10': 47.5, 'P15': 47.8, 'P25': 48.3, 'P50': 49.3, 'P75': 50.2, 'P85': 50.7, 'P90': 51.1, 'P95': 51.6, 'P97': 51.9, 'P99': 52.6, 'P999': 53.7}, {'Month': 48, 'L': 1.0, 'M': 49.3321, 'S': 0.02878, 'SD': 1.41978, 'P01': 44.9, 'P1': 46.0, 'P3': 46.7, 'P5': 47.0, 'P10': 47.5, 'P15': 47.9, 'P25': 48.4, 'P50': 49.3, 'P75': 50.3, 'P85': 50.8, 'P90': 51.2, 'P95': 51.7, 'P97': 52.0, 'P99': 52.6, 'P999': 53.7}, {'Month': 49, 'L': 1.0, 'M': 49.3877, 'S': 0.02875, 'SD': 1.4199, 'P01': 45.0, 'P1': 46.1, 'P3': 46.7, 'P5': 47.1, 'P10': 47.6, 'P15': 47.9, 'P25': 48.4, 'P50': 49.4, 'P75': 50.3, 'P85': 50.9, 'P90': 51.2, 'P95': 51.7, 'P97': 52.1, 'P99': 52.7, 'P999': 53.8}, {'Month': 50, 'L': 1.0, 'M': 49.4419, 'S': 0.02873, 'SD': 1.42047, 'P01': 45.1, 'P1': 46.1, 'P3': 46.8, 'P5': 47.1, 'P10': 47.6, 'P15': 48.0, 'P25': 48.5, 'P50': 49.4, 'P75': 50.4, 'P85': 50.9, 'P90': 51.3, 'P95': 51.8, 'P97': 52.1, 'P99': 52.7, 'P999': 53.8}, {'Month': 51, 'L': 1.0, 'M': 49.4947, 'S': 0.0287, 'SD': 1.4205, 'P01': 45.1, 'P1': 46.2, 'P3': 46.8, 'P5': 47.2, 'P10': 47.7, 'P15': 48.0, 'P25': 48.5, 'P50': 49.5, 'P75': 50.5, 'P85': 51.0, 'P90': 51.3, 'P95': 51.8, 'P97': 52.2, 'P99': 52.8, 'P999': 53.9}, {'Month': 52, 'L': 1.0, 'M': 49.5464, 'S': 0.02868, 'SD': 1.42099, 'P01': 45.2, 'P1': 46.2, 'P3': 46.9, 'P5': 47.2, 'P10': 47.7, 'P15': 48.1, 'P25': 48.6, 'P50': 49.5, 'P75': 50.5, 'P85': 51.0, 'P90': 51.4, 'P95': 51.9, 'P97': 52.2, 'P99': 52.9, 'P999': 53.9}, {'Month': 53, 'L': 1.0, 'M': 49.5969, 'S': 0.02865, 'SD': 1.42095, 'P01': 45.2, 'P1': 46.3, 'P3': 46.9, 'P5': 47.3, 'P10': 47.8, 'P15': 48.1, 'P25': 48.6, 'P50': 49.6, 'P75': 50.6, 'P85': 51.1, 'P90': 51.4, 'P95': 51.9, 'P97': 52.3, 'P99': 52.9, 'P999': 54.0}, {'Month': 54, 'L': 1.0, 'M': 49.6464, 'S': 0.02863, 'SD': 1.42138, 'P01': 45.3, 'P1': 46.3, 'P3': 47.0, 'P5': 47.3, 'P10': 47.8, 'P15': 48.2, 'P25': 48.7, 'P50': 49.6, 'P75': 50.6, 'P85': 51.1, 'P90': 51.5, 'P95': 52.0, 'P97': 52.3, 'P99': 53.0, 'P999': 54.0}, {'Month': 55, 'L': 1.0, 'M': 49.6947, 'S': 0.02861, 'SD': 1.42177, 'P01': 45.3, 'P1': 46.4, 'P3': 47.0, 'P5': 47.4, 'P10': 47.9, 'P15': 48.2, 'P25': 48.7, 'P50': 49.7, 'P75': 50.7, 'P85': 51.2, 'P90': 51.5, 'P95': 52.0, 'P97': 52.4, 'P99': 53.0, 'P999': 54.1}, {'Month': 56, 'L': 1.0, 'M': 49.7421, 'S': 0.02859, 'SD': 1.42213, 'P01': 45.3, 'P1': 46.4, 'P3': 47.1, 'P5': 47.4, 'P10': 47.9, 'P15': 48.3, 'P25': 48.8, 'P50': 49.7, 'P75': 50.7, 'P85': 51.2, 'P90': 51.6, 'P95': 52.1, 'P97': 52.4, 'P99': 53.1, 'P999': 54.1}, {'Month': 57, 'L': 1.0, 'M': 49.7885, 'S': 0.02856, 'SD': 1.42196, 'P01': 45.4, 'P1': 46.5, 'P3': 47.1, 'P5': 47.4, 'P10': 48.0, 'P15': 48.3, 'P25': 48.8, 'P50': 49.8, 'P75': 50.7, 'P85': 51.3, 'P90': 51.6, 'P95': 52.1, 'P97': 52.5, 'P99': 53.1, 'P999': 54.2}, {'Month': 58, 'L': 1.0, 'M': 49.8341, 'S': 0.02854, 'SD': 1.42227, 'P01': 45.4, 'P1': 46.5, 'P3': 47.2, 'P5': 47.5, 'P10': 48.0, 'P15': 48.4, 'P25': 48.9, 'P50': 49.8, 'P75': 50.8, 'P85': 51.3, 'P90': 51.7, 'P95': 52.2, 'P97': 52.5, 'P99': 53.1, 'P999': 54.2}, {'Month': 59, 'L': 1.0, 'M': 49.8789, 'S': 0.02852, 'SD': 1.42255, 'P01': 45.5, 'P1': 46.6, 'P3': 47.2, 'P5': 47.5, 'P10': 48.1, 'P15': 48.4, 'P25': 48.9, 'P50': 49.9, 'P75': 50.8, 'P85': 51.4, 'P90': 51.7, 'P95': 52.2, 'P97': 52.6, 'P99': 53.2, 'P999': 54.3}, {'Month': 60, 'L': 1.0, 'M': 49.9229, 'S': 0.0285, 'SD': 1.4228, 'P01': 45.5, 'P1': 46.6, 'P3': 47.2, 'P5': 47.6, 'P10': 48.1, 'P15': 48.4, 'P25': 49.0, 'P50': 49.9, 'P75': 50.9, 'P85': 51.4, 'P90': 51.7, 'P95': 52.3, 'P97': 52.6, 'P99': 53.2, 'P999': 54.3}]


def who_hcfa_exact(age_months, sex, hc_cm):
    if age_months is None or hc_cm is None:
        return None
    month = int(round(float(age_months)))
    if month < 0 or month > 60:
        return None
    sx = str(sex).lower()
    zrows = WHO_HCFA_BOYS_Z if sx.startswith('m') else WHO_HCFA_GIRLS_Z
    prows = WHO_HCFA_BOYS_P if sx.startswith('m') else WHO_HCFA_GIRLS_P
    zrow = next((r for r in zrows if r['Month'] == month), None)
    prow = next((r for r in prows if r['Month'] == month), None)
    if not zrow or not prow:
        return None
    z_pairs = [(-3,zrow.get('SD3neg')),(-2,zrow.get('SD2neg')),(-1,zrow.get('SD1neg')),(0,zrow.get('SD0')),(1,zrow.get('SD1')),(2,zrow.get('SD2')),(3,zrow.get('SD3'))]
    percentile_cols = [('P01',0.1),('P1',1),('P3',3),('P5',5),('P10',10),('P15',15),('P25',25),('P50',50),('P75',75),('P85',85),('P90',90),('P95',95),('P97',97),('P99',99),('P999',99.9)]
    p_pairs = [(pct, prow.get(col)) for col,pct in percentile_cols if prow.get(col) is not None]
    z_est = None
    for (z1,v1),(z2,v2) in zip(z_pairs, z_pairs[1:]):
        if v1 is None or v2 is None:
            continue
        lo,hi = sorted([v1,v2])
        if lo <= hc_cm <= hi and v2 != v1:
            frac = (hc_cm - v1)/(v2 - v1)
            z_est = round(z1 + frac*(z2-z1),2)
            break
    if z_est is None:
        if hc_cm < z_pairs[0][1]:
            z_est = -3.0
        elif hc_cm > z_pairs[-1][1]:
            z_est = 3.0
    p_est = None
    for (p1,v1),(p2,v2) in zip(p_pairs, p_pairs[1:]):
        lo,hi = sorted([v1,v2])
        if lo <= hc_cm <= hi and v2 != v1:
            frac = (hc_cm - v1)/(v2 - v1)
            p_est = round(p1 + frac*(p2-p1),1)
            break
    if p_est is None:
        if hc_cm < p_pairs[0][1]:
            p_est = p_pairs[0][0]
        elif hc_cm > p_pairs[-1][1]:
            p_est = p_pairs[-1][0]
    return {'month': month, 'zscore': z_est, 'percentile': p_est, 'median': zrow.get('SD0')}

st.set_page_config(page_title='IndiMed X', layout='wide', initial_sidebar_state='collapsed')

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
DRUGS={'paracetamol': {'dose_mgkg':15,'renal':'Usually no routine renal alert at standard dosing; verify cumulative daily limit.','preg':'Generally compatible at usual doses.','lact':'Generally compatible.','route':'PO/IV'},'ibuprofen': {'dose_mgkg':10,'renal':'Use caution in dehydration, AKI, or CKD risk.','preg':'Avoid in later pregnancy unless specifically advised.','lact':'Usually compatible in routine use.','route':'PO'},'ondansetron': {'dose_mgkg':0.15,'renal':'No broad quick alert, but verify protocol.','preg':'Specialist judgment depending on indication.','lact':'Check product-specific guidance.','route':'PO/IV'},'amoxicillin': {'dose_mgkg':25,'renal':'Dose interval may need review in significant renal impairment.','preg':'Commonly used when indicated.','lact':'Usually compatible.','route':'PO'},'linezolid': {'dose_mgkg':10,'renal':'No routine renal-field input needed for this calculator; verify interval and indication separately.','preg':'Specialist judgment depending on indication.','lact':'Verify with current reference if clinically relevant.','route':'PO/IV'},'cefixime': {'dose_mgkg':8,'route':'PO'},'ceftriaxone': {'dose_mgkg':50,'route':'IV/IM'},'cefotaxime': {'dose_mgkg':50,'route':'IV'},'cephalexin': {'dose_mgkg':25,'route':'PO'},'azithromycin': {'dose_mgkg':10,'route':'PO'},'clindamycin': {'dose_mgkg':10,'route':'PO/IV'},'metronidazole': {'dose_mgkg':7.5,'route':'PO/IV'},'salbutamol': {'dose_text':'Inhaled dosing depends on device, age, and severity; use inhalation protocol rather than mg/kg single-dose math.','route':'Neb/Inhaled'},'budesonide': {'dose_text':'Inhaled/nebulized dosing depends on formulation and severity; use product-specific pediatric protocol.','route':'Neb/Inhaled'},'prednisolone': {'dose_mgkg':1,'route':'PO'},'dexamethasone': {'dose_mgkg':0.15,'route':'PO/IV/IM'},'cetirizine': {'dose_text':'Age-banded pediatric dosing is preferred over mg/kg; use product-specific age schedule.','route':'PO'},'zinc': {'dose_text':'Use age-banded dosing, commonly 10 mg/day if <6 months and 20 mg/day if >=6 months in diarrhea protocols.','route':'PO'},'ors': {'dose_text':'Dose is fluid-plan based, not mg/kg drug dosing; use dehydration/rehydration tool.','route':'PO'}}
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
    try: st.query_params['dept']=name
    except Exception: pass
    if name in st.session_state.recent: st.session_state.recent.remove(name)
    st.session_state.recent=[name]+st.session_state.recent[:4]

def go_home():
    st.session_state.page='home'
    try:
        if 'dept' in st.query_params: del st.query_params['dept']
    except Exception:
        pass

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


def etat_triage_summary(emergency_flags, priority_flags):
    if emergency_flags:
        return 'Emergency', 'Immediate evaluation and stabilization needed.'
    if len(priority_flags)>=1:
        return 'Priority', 'Fast-track assessment is appropriate.'
    return 'Queue', 'No ETAT emergency or priority sign selected.'

def neonatal_jaundice_pathway(age_hours, bilirubin, preterm=False, risk=False):
    prompt, level = bilirubin_prompt(age_hours, bilirubin, preterm, risk)
    if age_hours < 24 and bilirubin > 0:
        return 'Urgent review', 'Jaundice in the first 24 hours needs urgent assessment.'
    if preterm or risk:
        return 'High-risk pathway', prompt
    return level, prompt

@st.cache_data(show_spinner=False)
def scenario_checklist(role):
    scenarios={
        'resident':['Can I reach emergency tools in 1 tap?','Are dose outputs readable under stress?','Is the next action obvious?'],
        'nurse':['Are volumes, feeds, and vitals quick to enter?','Can I go back easily on mobile?','Are warnings easy to spot?'],
        'consultant':['Are outputs framed as support not orders?','Are sources discoverable?','Do simplified tools declare limits?']
    }
    return scenarios.get(role,[])


def pediatric_bolus_ml(weight_kg):
    return round(weight_kg*20)

def pediatric_ibw_traub_kichen(age_years):
    if age_years < 1:
        return None
    return round((age_years*2)+8,1)

def sodium_deficit_meq(weight_kg, current_na, target_na=135):
    return max(0, round(0.6*weight_kg*(target_na-current_na),1))

def free_water_deficit_l(weight_kg, sex, current_na, target_na=140):
    tbw = 0.6*weight_kg if sex=='Male' else 0.5*weight_kg
    return max(0, round(tbw*((current_na/target_na)-1),2))

def corrected_sodium_hyperglycemia(na, glucose_mgdl):
    return round(na + 1.6*((max(glucose_mgdl,100)-100)/100),1)

def corrected_calcium_mgdl(total_ca, albumin):
    return round(total_ca + 0.8*(4-albumin),2)

def anion_gap(na, cl, hco3):
    return round(na-(cl+hco3),1)

def pediatric_map_floor(age_years):
    return 40 if age_years < 1 else 55 + age_years*1.5

def neonatal_map_target(ga_weeks):
    return ga_weeks

def infusion_rate_ml_hr(total_ml, hours):
    return round(total_ml/max(hours,0.1),1)

def glucose_infusion_advice(gir):
    if gir < 4:
        return 'Low GIR', 'Below common neonatal maintenance target; correlate with glucose trends and feeding tolerance.'
    if gir <= 8:
        return 'Usual GIR', 'Within common maintenance range for many neonates; interpret in full clinical context.'
    if gir <= 12:
        return 'High GIR', 'Higher glucose delivery; review indication, glucose values, and fluid balance.'
    return 'Very high GIR', 'Markedly high glucose delivery; recheck calculations and assess for hyperglycemia risk.'



@st.cache_data(show_spinner=False)
def indian_support_bundle(topic, **kwargs):
    if topic=='dehydration':
        severity=kwargs.get('severity','No dehydration')
        if severity=='Severe dehydration':
            return {
                'probable_causes':['Acute gastroenteritis with major fluid loss','Sepsis with poor perfusion','Profound vomiting or diarrhea','Adrenal/metabolic cause if atypical history'],
                'suggested_diagnosis':['Severe dehydration / possible shock','Need urgent reassessment for sepsis, electrolyte disorder, or hypoglycemia'],
                'management':['Urgent perfusion assessment','Use ORS/NG/IV strategy as clinically appropriate and per local protocol','Check glucose and electrolytes where available','Escalate if weak pulses, altered sensorium, anuria, or repeated emesis'],
                'alternatives':['If malnutrition or cardiac disease suspected, standard fluid assumptions may not apply']
            }
        if severity=='Some dehydration':
            return {
                'probable_causes':['Gastroenteritis with moderate fluid deficit','Fever with poor intake','Vomiting predominant illness'],
                'suggested_diagnosis':['Some dehydration without overt shock'],
                'management':['ORS is usually preferred if child can drink','Track ongoing stool and vomit losses','Reassess hydration after rehydration window'],
                'alternatives':['Consider sepsis, diabetic ketoacidosis, or surgical abdomen if symptoms do not fit simple diarrhea']
            }
    if topic=='anemia':
        return {
            'probable_causes':['Iron deficiency anemia','Thalassemia trait if microcytosis disproportionate','Chronic inflammation or blood loss'],
            'suggested_diagnosis':['Microcytic anemia pattern requiring CBC, ferritin or iron profile context, and dietary history'],
            'management':['Review diet, pallor severity, hemodynamic stability, and reticulocyte context','Use IAP/India anemia guidance for supplementation and workup'],
            'alternatives':['Lead exposure, hemolysis, or mixed deficiency if pattern is atypical']
        }
    if topic=='neonatal_sepsis':
        return {
            'probable_causes':['Early-onset neonatal sepsis','Late-onset sepsis','Pneumonia, meningitis, or line-related infection depending on context'],
            'suggested_diagnosis':['At-risk or probable neonatal sepsis based on symptoms and maternal or perinatal risk factors'],
            'management':['Admit/observe according to severity and unit policy','Obtain cultures before antibiotics when feasible','Start empiric antibiotics per local/NICU policy if probability high','Support temperature, glucose, perfusion, and feeding'],
            'alternatives':['Transient tachypnea, hypoglycemia, intracranial pathology, metabolic disease, or congenital heart disease can mimic sepsis']
        }
    if topic=='jaundice':
        return {
            'probable_causes':['Physiologic jaundice','Breastfeeding failure jaundice','Hemolysis or blood group incompatibility','Sepsis or prematurity-related vulnerability'],
            'suggested_diagnosis':['Neonatal jaundice requiring age-in-hours and risk-factor stratification'],
            'management':['Plot bilirubin on hour-specific nomogram','Assess feeding, weight loss, urine/stool transition, and hemolysis risk','Escalate sooner in preterm or sick infants'],
            'alternatives':['Conjugated jaundice, G6PD deficiency, cephalohematoma, hypothyroidism, or infection if course is atypical']
        }
    return {
        'probable_causes':['Use history, exam, and local epidemiology to build the differential'],
        'suggested_diagnosis':['Calculator output supports but does not replace diagnosis'],
        'management':['Follow local protocol and reassess if bedside findings conflict'],
        'alternatives':['Consider measurement error, mixed pathology, or nonstandard presentation']
    }

def render_bundle(bundle):
    st.markdown('**Probable causes**')
    for x in bundle['probable_causes']: st.markdown(f'- {x}')
    st.markdown('**Suggested diagnosis / frame**')
    for x in bundle['suggested_diagnosis']: st.markdown(f'- {x}')
    st.markdown('**Management suggestions**')
    for x in bundle['management']: st.markdown(f'- {x}')
    st.markdown('**Alternatives / cautions**')
    for x in bundle['alternatives']: st.markdown(f'- {x}')


def c_to_f(c):
    return round((c*9/5)+32,1)

@st.cache_data(show_spinner=False)
def protocol_detail_lines(topic):
    if topic=='pediatric_anemia':
        return [
            'Likely diagnostic frame: microcytic or nutritional anemia if history and hemogram fit.',
            'Probable causes include iron deficiency, dietary insufficiency, chronic blood loss, or thalassemia trait.',
            'Alternative diagnoses include mixed deficiency, chronic inflammation, hemolysis, or lead exposure.',
            'Check severity, hemodynamic stability, diet, pica, worm burden, blood loss history, and growth pattern.',
            'Mentzer index can support pattern recognition but does not diagnose iron deficiency by itself.',
            'IAP Standard Treatment Guideline 2022 on Iron Deficiency Anemia supports treatment based on compatible clinical and hemogram findings with targeted confirmation where needed.',
            'Indian pediatric anemia guidance also emphasizes prevention and iron-folic supplementation programs where relevant.',
            'Treatment direction commonly includes oral iron in stable likely IDA with counseling on adherence and diet.',
            'Alternative treatment path is further workup first when the pattern is atypical, severe, refractory, or associated with hemolysis or systemic disease.',
            'Reassess response, reticulocyte trend, hemoglobin rise, tolerance, and adherence rather than relying on one reading alone.'
        ]
    if topic=='neonatal_sepsis':
        return [
            'Likely diagnostic frame: at-risk, suspect, or high-probability neonatal sepsis depending on signs and maternal risk factors.',
            'Probable causes include early-onset bacterial sepsis, late-onset nosocomial infection, pneumonia, meningitis, or line-related infection.',
            'Alternative diagnoses include hypoglycemia, TTN, congenital heart disease, intracranial pathology, or metabolic illness.',
            'ICMR Standard Treatment Workflow for Sepsis in Neonates references observation for selected at-risk infants and escalation for worsening signs.',
            'The ICMR workflow available in 2024 states blood culture should be obtained before antibiotics when feasible and baby is being evaluated for sepsis.',
            'It also recommends empiric antibiotics as per local or unit policy rather than one universal regimen.',
            'Supportive care should include temperature stability, glucose support, perfusion review, respiratory support, and feeding decisions based on stability.',
            'Alternative management path is close observation without immediate prolonged antibiotics in lower-probability cases per workflow and response data.',
            'Lumbar puncture and broader investigations depend on hemodynamic stability and suspicion level.',
            'Definitive treatment must follow NICU/SNCU protocol, culture results, CRP trend, and the infant clinical course.'
        ]
    if topic=='pediatric_sepsis':
        return [
            'Likely diagnostic frame: sepsis or septic shock in a child with suspected infection and perfusion abnormality.',
            'Probable causes include bacterial sepsis, dengue with shock physiology, severe pneumonia, meningococcemia, or abdominal sepsis.',
            'Alternative diagnoses include dehydration, anaphylaxis, cardiogenic shock, toxic ingestion, or severe asthma with fatigue.',
            'ICMR pediatric workflow compendium includes sepsis and septic shock pathways for children.',
            'These workflows emphasize early recognition, rapid reassessment, hemodynamic support, antimicrobial timing, and source-focused evaluation.',
            'MAP and bedside perfusion markers should be interpreted together because a normal number does not exclude shock.',
            'Treatment direction usually includes airway and breathing review, vascular access, glucose check, fluid strategy, and early escalation.',
            'Alternative treatment path depends on shock phenotype, malnutrition, heart disease, or renal limitation where generic fluid assumptions may not hold.',
            'Use unit-specific antimicrobial and vasoactive protocols rather than calculator-only logic.',
            'Repeat clinical examination remains essential because pediatric shock can evolve rapidly despite an initially acceptable blood pressure.'
        ]
    if topic=='jaundice':
        return [
            'Likely diagnostic frame: neonatal unconjugated jaundice requiring hour-specific risk stratification.',
            'Probable causes include physiologic jaundice, breastfeeding failure jaundice, hemolysis, prematurity, bruising, or infection.',
            'Alternative diagnoses include conjugated jaundice, hypothyroidism, G6PD deficiency, biliary pathology, or metabolic disease.',
            'NICE neonatal jaundice guidance and Indian neonatal practice both depend on age in hours rather than day-of-life alone.',
            'IAP neonatal standards include jaundice-related topics within broader neonatal guidance resources and emphasize structured evaluation.',
            'Treatment direction includes plotting bilirubin on an accepted nomogram, checking gestation and neurotoxicity risk, and assessing feeding adequacy and weight loss.',
            'Alternative pathway is urgent evaluation when jaundice appears in the first 24 hours or the baby is preterm or clinically unwell.',
            'Phototherapy and exchange thresholds are not interchangeable across gestational ages and risk groups.',
            'Always review stool and urine transition, maternal blood group history, bruising, hemolysis clues, and sepsis red flags.',
            'Definitive treatment must follow local neonatal protocol and current hour-specific threshold charts.'
        ]
    return [
        'This output is a decision-support result, not a stand-alone diagnosis.',
        'Interpret the number together with history, examination, trend, and local epidemiology.',
        'Probable causes depend on the syndrome pattern and severity.',
        'Alternative diagnoses should be reviewed when the clinical picture is atypical.',
        'Indian standards generally support protocol-based, context-sensitive care rather than single-number decisions.',
        'Check for red flags, severity markers, and unstable physiology first.',
        'Review whether confirmatory laboratory or imaging data are required.',
        'Use local formulary and unit pathway for medication and escalation details.',
        'Reassess after the first intervention because pediatric and neonatal physiology changes quickly.',
        'Escalate when bedside findings and calculator output do not match.'
    ]

def render_protocol_lines(topic):
    for line in protocol_detail_lines(topic):
        st.markdown(f'- {line}')


@st.cache_data(show_spinner=False)
def detailed_calculator_guidance(calc, **kwargs):
    if calc=='pediatric_bmi':
        bmi=kwargs.get('bmi'); age=kwargs.get('age')
        lines=[
            f"Calculated BMI is {bmi:.2f} kg/mÃ‚Â².",
            "This number alone is not enough to diagnose normal nutrition, overweight, obesity, or wasting in a child.",
            "WHO and pediatric practice require age- and sex-specific growth interpretation; raw BMI is only the entry point.",
            "If the child is under 5 years, BMI-for-age z-score or weight-for-height style interpretation is more meaningful than adult BMI categories.",
            "If the child is older, BMI-for-age percentile or z-score should still be used rather than adult cutoffs.",
            "A low BMI may suggest thinness, undernutrition, chronic disease, malabsorption, high catabolic state, or simply constitutional build depending on growth trend.",
            "A high BMI may suggest overweight or obesity, but edema, endocrine disease, steroid exposure, or inaccurate height entry can distort interpretation.",
            "IAP standard treatment guidance includes childhood obesity and severe acute malnutrition related resources, while WHO growth standards remain central for anthropometric interpretation.",
            "Suggested next step is to correlate with growth velocity, diet history, pubertal stage, physical activity, family build, and any red flags such as weight loss or edema.",
            "Alternative explanations should be considered if BMI conflicts with the child visual build, MUAC, past records, or clinical examination.",
            "Treatment direction is not based on BMI alone; undernutrition needs nutritional and disease evaluation, while high BMI needs lifestyle, endocrine risk, and complication screening context.",
            "Protocol frame: use WHO growth charts or z-scores plus applicable IAP pediatric guidance rather than adult BMI labels."
        ]
        return lines
    if calc=='map':
        value=kwargs.get('value'); floor=kwargs.get('floor')
        return [
            f"MAP is {value:.1f} mmHg.",
            f"The simple bedside low-perfusion floor used here is approximately {floor:.1f} mmHg for age.",
            "A value below or near this threshold raises concern for circulatory compromise, especially if pulses are weak or mental status is altered.",
            "A normal MAP does not exclude compensated shock in children.",
            "WHO ETAT emphasizes early recognition of shock and impaired circulation using bedside signs, not blood pressure alone.",
            "Probable causes of low MAP include dehydration, sepsis, hemorrhage, myocarditis, anaphylaxis, and adrenal or metabolic illness.",
            "Alternative causes include wrong cuff size, motion artifact, or isolated measurement error.",
            "Suggested diagnosis frame is possible impaired perfusion if MAP is low and exam supports it.",
            "Treatment direction usually requires repeat vitals, perfusion check, glucose review, cause-focused resuscitation, and escalation when unstable.",
            "Protocol frame: integrate ETAT emergency signs with pediatric shock pathways and local unit policy."
        ]
    if calc=='bilirubin':
        prompt=kwargs.get('prompt')
        return [
            f"Current bilirubin interpretation prompt: {prompt}",
            "This output is only a risk flag and not the final treatment decision.",
            "Neonatal bilirubin must be interpreted by age in hours, gestational age, neurotoxicity risk factors, and clinical status.",
            "IAP neonatal guidance resources and standard neonatal practice support structured jaundice evaluation rather than isolated number-based decisions.",
            "NICE and related jaundice protocols also emphasize hour-specific thresholds and early escalation for jaundice in the first 24 hours.",
            "Probable causes include physiologic jaundice, breastfeeding failure jaundice, hemolysis, prematurity, bruising, or infection.",
            "Alternative diagnoses include conjugated jaundice, G6PD deficiency, hypothyroidism, cholestasis, or sepsis.",
            "Suggested next steps are to check feeding, weight loss, stool and urine transition, maternal blood group history, and illness signs.",
            "Treatment direction may include closer review, repeat bilirubin, phototherapy, or exchange consideration depending on formal threshold charts.",
            "Protocol frame: use local neonatal jaundice chart or accepted nomogram with unit-specific escalation policy."
        ]
    if calc=='gir':
        gir=kwargs.get('gir')
        return [
            f"Calculated glucose infusion rate is {gir:.2f} mg/kg/min.",
            "This should be interpreted with bedside glucose trends, feeding tolerance, gestational age, and fluid allowance.",
            "A low GIR may contribute to persistent or recurrent hypoglycemia, especially in preterm or growth-restricted infants.",
            "A high GIR may worsen hyperglycemia and complicate fluid planning.",
            "Probable causes of low glucose despite GIR include sepsis, hyperinsulinism, inadequate stores, delayed feeds, or incorrect infusion delivery.",
            "Alternative causes of apparent abnormal GIR include pump mismatch, wrong weight entry, or concentration error.",
            "IAP neonatal hypoglycemia guidance and unit protocols should drive threshold-based intervention, not this number alone.",
            "Suggested management direction is to verify glucose values, infusion accuracy, enteral strategy, and escalation thresholds.",
            "Treatment alternatives include feed optimization, dextrose concentration adjustment, or evaluation for persistent hypoglycemia disorders depending on the pattern.",
            "Protocol frame: use NICU hypoglycemia protocol with repeated glucose monitoring."
        ]
    return [
        "Interpret this calculator output together with history, examination, trend, and risk factors.",
        "One number is rarely diagnostic on its own in pediatrics or neonatology.",
        "Probable causes should be built from syndrome pattern and severity.",
        "Alternative diagnoses must be considered if bedside findings do not fit the number.",
        "Use IAP, ICMR, WHO, or local departmental protocols where applicable.",
        "Reassess after intervention and do not treat the calculator output in isolation.",
        "Escalate if the child is unstable, deteriorating, or has emergency signs.",
        "Use confirmatory investigations where clinically indicated.",
        "Check input quality if the result appears inconsistent.",
        "Document the interpretation and reassessment plan."
    ]

def render_guidance_block(calc, **kwargs):
    st.markdown('**Detailed interpretation and protocol frame**')
    for line in detailed_calculator_guidance(calc, **kwargs):
        st.markdown(f'- {line}')


@st.cache_data(show_spinner=False)
def universal_protocol_block(calc, value=None, unit='', min_ref=None, max_ref=None, protocol='Indian protocol context', year='Advisory', **kwargs):
    lines=[]
    lines.append(f"Result: {value} {unit}".strip())
    if min_ref is not None or max_ref is not None:
        lines.append(f"Reference frame used in app: minimum {min_ref if min_ref is not None else 'not fixed'}, maximum {max_ref if max_ref is not None else 'not fixed'}." )
    lines.append(f"Protocol label: {protocol} ({year}).")
    if calc=='bmi':
        bmi=float(value)
        lines += [
            'Raw BMI is a screening number and must not be interpreted using adult labels in children.',
            'Suggested diagnosis depends on age- and sex-specific BMI-for-age or growth chart interpretation.',
            'WHO growth standards and growth references remain the correct frame for anthropometric interpretation in children.',
            'IAP pediatric standards are relevant for obesity, severe acute malnutrition, and clinical nutrition decision pathways.',
            'Low values may represent wasting, chronic disease, malabsorption, constitutional thinness, or measurement error.',
            'High values may represent overweight, obesity, edema, endocrine disease, steroid exposure, or wrong height entry.',
            'Suggested next steps are growth chart review, diet history, activity review, family build, and search for red flags.',
            'Alternative diagnoses include chronic systemic disease, nephrotic state, endocrine disorders, or fluid retention.',
            'Treatment direction should be based on growth trend and clinical syndrome rather than BMI alone.',
            'Reassuring versus concerning status must be finalized only after plotting on appropriate growth standards.'
        ]
    elif calc=='map':
        lines += [
            'MAP is only one bedside perfusion marker and cannot exclude compensated shock.',
            'Values below the age-linked floor increase concern for circulatory compromise when exam findings also support hypoperfusion.',
            'WHO ETAT and ICMR pediatric sepsis guidance prioritize clinical recognition of shock over isolated pressure numbers.',
            'Probable causes include dehydration, sepsis, hemorrhage, myocarditis, anaphylaxis, and adrenal or metabolic causes.',
            'Alternative explanations include wrong cuff size, agitation, poor technique, or isolated device error.',
            'Suggested diagnosis is possible impaired perfusion if low MAP coexists with prolonged CRT, weak pulse, or altered sensorium.',
            'Treatment direction includes urgent reassessment, repeat vitals, glucose check, perfusion review, and cause-based management.',
            'Alternative management may be needed in SAM, cardiac disease, renal disease, or fluid-sensitive states.',
            'Protocol-based escalation is advised if bedside signs and blood pressure trend are worsening.',
            'A normal MAP should never delay escalation when the clinical picture is strongly concerning.'
        ]
    elif calc=='mentzer':
        lines += [
            'Mentzer index is a pattern-support tool, not a definitive diagnosis.',
            'Lower values may suggest thalassemia trait, while higher values may support iron deficiency pattern recognition.',
            'The result must be combined with Hb, RDW, RBC count, smear, ferritin if available, and family history.',
            'IAP and Indian pediatric anemia guidance favor syndrome-based interpretation rather than relying on one index alone.',
            'Probable diagnosis with higher index is iron deficiency anemia if the clinical context supports it.',
            'Alternative diagnoses include mixed deficiency, chronic inflammation, lead exposure, sideroblastic process, or hemoglobinopathy.',
            'Treatment direction for likely iron deficiency includes confirming severity, dietary review, and appropriate iron plan.',
            'Alternative treatment path is hematology workup when the pattern is atypical or nonresponsive.',
            'Do not use this result to rule out thalassemia trait without CBC pattern and family context.',
            'Protocol frame: interpret under IAP anemia guidance and local hematology policy.'
        ]
    elif calc=='anc':
        lines += [
            'ANC helps estimate neutropenia severity and infection risk context.',
            'Low values may indicate viral suppression, sepsis, marrow suppression, drug effect, autoimmune neutropenia, or nutritional deficiency.',
            'Very low ANC raises concern for invasive infection risk, especially with fever.',
            'Alternative explanations include lab timing, differential count error, or transient viral marrow suppression.',
            'Suggested diagnosis frame should distinguish febrile neutropenia from isolated asymptomatic neutropenia.',
            'Treatment direction depends on fever, hemodynamic stability, mucosal findings, and underlying disease context.',
            'Indian protocol framing should follow the relevant pediatric oncology or hematology unit pathway where applicable.',
            'Stable isolated neutropenia may permit observation and repeat counts, depending on severity and child condition.',
            'Febrile neutropenia or toxic appearance requires urgent escalation and antimicrobial protocol use.',
            'Interpretation should always include trend rather than one isolated ANC alone.'
        ]
    elif calc=='dehydration':
        lines += [
            'This output estimates fluid deficit or rehydration need but does not by itself diagnose the cause of illness.',
            'ICMR pediatric acute diarrhea workflow uses dehydration classification with Plan A, Plan B, and Plan C structure.',
            'Probable causes include acute gastroenteritis, fever with poor intake, vomiting illness, and sepsis-related poor perfusion.',
            'Alternative diagnoses include diabetic ketoacidosis, surgical abdomen, adrenal crisis, and severe sepsis.',
            'Mild or some dehydration generally supports enteral or ORS-led rehydration when the child can drink.',
            'Severe dehydration or poor perfusion requires urgent escalation and protocol-based fluid management.',
            'Reference range is clinical rather than numeric; concern rises when lethargy, poor drinking, sunken eyes, or slow skin pinch coexist.',
            'Treatment direction must consider sodium disorders, malnutrition, ongoing losses, and vomiting burden.',
            'Alternative treatment path is cautious fluid strategy if SAM, cardiac disease, or renal compromise is suspected.',
            'Protocol frame: ICMR pediatrics STW 2019 acute diarrhea and local pediatric emergency policy.'
        ]
    elif calc=='bilirubin':
        lines += [
            'This bilirubin result must be interpreted against age in hours, gestation, and neurotoxicity risk factors.',
            'Indian neonatal practice and international jaundice protocols use threshold charts, not isolated bilirubin values alone.',
            'Probable causes include physiologic jaundice, breastfeeding failure jaundice, prematurity, hemolysis, bruising, and infection.',
            'Alternative diagnoses include conjugated jaundice, G6PD deficiency, hypothyroidism, cholestasis, and sepsis.',
            'Concerning status rises if jaundice appears in the first 24 hours or the baby is unwell.',
            'Treatment direction may include repeat testing, feeding optimization, phototherapy, or exchange planning depending on formal thresholds.',
            'Alternative treatment path depends on gestation and local neonatal chart use.',
            'A reassuring number today may still require repeat review if the infant is early in the bilirubin trajectory.',
            'Protocol frame should cite local neonatal jaundice chart, unit policy, and neonatal society guidance where used.',
            'Use this block only as decision support and not as a replacement for the official threshold nomogram.'
        ]
    elif calc=='gir':
        lines += [
            'GIR should be interpreted with bedside glucose values and clinical response.',
            'Low GIR can contribute to hypoglycemia, especially in preterm, septic, or growth-restricted infants.',
            'High GIR can contribute to hyperglycemia or excessive fluid and glucose exposure.',
            'Probable causes of persistent low glucose despite GIR include hyperinsulinism, sepsis, inadequate stores, delayed feeding, or infusion error.',
            'Alternative explanations include wrong weight, wrong dextrose concentration, or pump mismatch.',
            'Suggested diagnosis depends on whether the baby is symptomatic, recurrently hypoglycemic, or persistently unstable.',
            'Treatment direction includes checking infusion accuracy, feed adequacy, repeat glucose, and protocol thresholds.',
            'Alternative treatment may involve concentration change, feed change, or persistent hypoglycemia workup.',
            'Indian neonatal protocol framing should follow NICU hypoglycemia policy and neonatal practice guidance.',
            'Trend over time is more meaningful than one GIR value alone.'
        ]
    elif calc=='bsa':
        lines += [
            'BSA is usually a dosing or physiological normalization tool rather than a diagnosis.',
            'The number can be useful for chemotherapy, burn, renal, or selected medication calculations depending on protocol.',
            'Probable error sources include inaccurate height or weight entry and unit mismatch.',
            'Alternative formulas exist, but Mosteller is commonly used for bedside simplicity.',
            'Suggested use is to verify whether the target drug or protocol actually requires BSA rather than weight-based dosing.',
            'Very unusual BSA for age should prompt review of anthropometry and nutritional status.',
            'Treatment direction should follow the target department protocol rather than the BSA value itself.',
            'Reference range varies strongly with age and body size, so there is no single normal number for all children.',
            'Indian protocol frame depends on the specialty using the BSA calculation.',
            'Document the source formula when BSA is used for medication decisions.'
        ]
    elif calc=='maintenance_fluid':
        lines += [
            'Maintenance fluid is a baseline estimate and not the total fluid prescription in every illness.',
            'The usual bedside frame is the Holliday-Segar style approach unless contraindicated by context.',
            'Probable reasons to modify the estimate include renal dysfunction, SIADH, cardiac disease, shock, sepsis, prematurity, or ongoing abnormal losses.',
            'Alternative fluid strategies may be needed in malnutrition or electrolyte disorders.',
            'Suggested diagnosis frame is hydration planning support rather than direct disease diagnosis.',
            'Treatment direction should integrate sodium status, glucose, urine output, perfusion, and ongoing loss replacement.',
            'Indian pediatric protocol context favors syndrome-based fluid adjustment rather than blind maintenance-only use.',
            'A child with pneumonia, CNS disease, edema, or renal disease may require restriction instead of standard maintenance.',
            'A child with diarrhea or high fever may need maintenance plus deficit plus ongoing loss replacement depending on severity.',
            'Reassess weight, urine output, perfusion, and electrolytes after starting fluids.'
        ]
    elif calc=='expected_weight':
        lines += [
            'Expected weight is a quick bedside estimate and not a substitute for plotting actual growth.',
            'The result is useful when the child weight is unknown or to sense whether measured weight looks discordant.',
            'A much lower actual weight can suggest undernutrition, chronic disease, malabsorption, constitutional small build, or wrong age input.',
            'A much higher actual weight can suggest overweight, obesity, endocrine issue, edema, or wrong age input.',
            'WHO growth charts remain the proper standard for confirming nutritional classification.',
            'IAP pediatric nutrition and obesity guidance should frame the next evaluation step when discrepancy is substantial.',
            'Treatment direction depends on the underlying cause of discordance, not the estimate alone.',
            'Alternative explanation always includes formula limitation because expected-weight equations are crude bedside tools.',
            'Reference range is broad and child-specific; trend across visits is more meaningful than one estimate.',
            'Use this result to trigger assessment, not to label the child definitively.'
        ]
    elif calc=='weight_loss':
        lines += [
            'Percent weight loss helps quantify nutritional or fluid change over time.',
            'In children, significant loss may suggest dehydration, poor intake, chronic disease, malabsorption, diabetes, TB, malignancy, or psychosocial feeding issue.',
            'In neonates, physiologic early weight loss has a different meaning than later pathological loss.',
            'Alternative explanations include scale variability, clothing difference, edema resolution, or wrong baseline entry.',
            'Suggested diagnosis frame depends on time course, feeding history, urine output, stool pattern, and illness signs.',
            'Treatment direction may include hydration review, feeding optimization, malnutrition workup, endocrine evaluation, or infection screening.',
            'Indian protocol context depends on age group and syndrome; SAM and neonatal feeding pathways are especially relevant.',
            'A rapid large loss is more concerning than a small gradual change without symptoms.',
            'Minimum and maximum acceptable change are age- and context-dependent rather than universal.',
            'Always correlate with MUAC, edema, appetite, and illness severity.'
        ]
    elif calc=='corrected_age':
        lines += [
            'Corrected age is important for developmental expectation, feeding assessment, and growth interpretation in preterm infants.',
            'Using chronological age alone can falsely label a preterm infant as delayed or undergrown.',
            'Probable error sources include wrong gestational age entry or wrong postnatal age calculation.',
            'Suggested diagnosis frame is developmental and growth adjustment rather than disease diagnosis.',
            'Treatment direction includes using corrected age for milestone assessment and selected nutrition decisions during infancy.',
            'Alternative interpretation may be needed if severe neonatal illness, brain injury, or syndromic disease affects development.',
            'Indian neonatal follow-up practice commonly uses corrected age in preterm assessment.',
            'Reference value is conceptual rather than a min-max normal range.',
            'If corrected age still shows significant developmental concern, structured developmental evaluation is needed.',
            'Document both chronological and corrected age during review.'
        ]
    elif calc=='qsofa':
        lines += [
            'qSOFA is a quick severity prompt, not a complete pediatric sepsis diagnostic tool.',
            'In children, age-adjusted pediatric assessment and full clinical examination remain more important than the score alone.',
            'Probable concern rises when high score coexists with infection suspicion, poor perfusion, altered sensorium, or respiratory distress.',
            'Alternative explanations include noninfectious altered mentation, seizure, intoxication, trauma, or dehydration.',
            'ICMR pediatric sepsis workflow should guide syndrome-level management more than a single score.',
            'Treatment direction includes urgent reassessment, sepsis screening, perfusion review, glucose check, and escalation where needed.',
            'A low score does not safely exclude sepsis in children.',
            'Reference frame is qualitative: higher score means higher concern, not a confirmed diagnosis.',
            'Use with ETAT emergency signs and local sepsis pathway.',
            'Trend and bedside deterioration matter more than a one-time score.'
        ]
    elif calc=='sodium_deficit':
        lines += [
            'Sodium deficit estimation supports structured correction planning in hyponatremia, but therapy must be individualized.',
            'Probable causes include gastroenteritis, SIADH, renal disease, adrenal insufficiency, diuretic use, or excess free water.',
            'Alternative explanations include lab artifact, hyperglycemia-related pseudolow sodium, or sampling error.',
            'Suggested diagnosis frame depends on symptoms, chronicity, volume status, and measured osmolality where available.',
            'Treatment direction must prioritize neurologic symptoms and safe rate of correction.',
            'Alternative treatment paths differ for hypovolemic, euvolemic, and hypervolemic hyponatremia.',
            'Indian protocol framing should follow pediatric electrolyte correction policy and intensive care standards.',
            'There is no single universal correction plan from this number alone.',
            'Overcorrection can be dangerous, so repeat sodium monitoring is essential.',
            'Always correct hyperglycemia effect and review seizure status before using the deficit mechanically.'
        ]
    elif calc=='free_water_deficit':
        lines += [
            'Free water deficit is an estimate used in hypernatremia planning and not a complete fluid prescription.',
            'Probable causes include diarrhea, inadequate intake, diabetes insipidus, fever, osmotic losses, or feeding error.',
            'Alternative explanations include wrong weight input or mixed electrolyte disorder.',
            'Suggested diagnosis frame depends on hydration state, neurologic status, urine output, and chronicity.',
            'Treatment direction requires slow controlled correction and close electrolyte monitoring.',
            'Alternative treatment paths may be needed in shock, renal disease, diabetes insipidus, or malnutrition.',
            'Indian pediatric fluid-electrolyte protocol should guide the actual correction rate.',
            'Rapid correction risks cerebral edema and neurologic deterioration.',
            'Use alongside ongoing losses and maintenance planning rather than as a stand-alone total.',
            'Repeat sodium checks are mandatory in clinically important hypernatremia.'
        ]
    elif calc=='corrected_sodium':
        lines += [
            'Corrected sodium helps estimate the effect of hyperglycemia on measured sodium.',
            'A low measured sodium may partly reflect osmotic water shift rather than true sodium depletion.',
            'Probable contexts include DKA, severe hyperglycemia, stress hyperglycemia, or diabetes-related dehydration.',
            'Alternative explanations include laboratory error or mixed electrolyte disorder.',
            'Suggested diagnosis frame is pseudohyponatremia adjustment support rather than a final sodium diagnosis.',
            'Treatment direction should follow DKA or hyperglycemia protocol rather than sodium correction alone.',
            'Indian protocol framing should align with pediatric hyperglycemia and DKA management standards.',
            'A corrected value that remains low suggests true concurrent hyponatremia may exist.',
            'Use serial glucose and sodium values to track response.',
            'Do not use corrected sodium in isolation when neurologic symptoms are present.'
        ]
    elif calc=='corrected_calcium':
        lines += [
            'Corrected calcium estimates the albumin-adjusted calcium status when albumin is abnormal.',
            'Probable causes of low corrected calcium include prematurity, sepsis, vitamin D deficiency, hypoparathyroidism, renal disease, or citrate exposure.',
            'Alternative explanations include acid-base effects and assay variation; ionized calcium is more definitive when available.',
            'Suggested diagnosis frame depends on symptoms such as jitteriness, seizures, apnea, or tetany.',
            'Treatment direction depends on severity, symptoms, ECG risk, and neonatal versus pediatric context.',
            'Alternative treatment path includes magnesium review and investigation of the underlying cause.',
            'Indian neonatal and pediatric protocols usually prioritize symptomatic status and repeat confirmation.',
            'A corrected value does not replace ionized calcium in critical care settings.',
            'Reference range depends on lab and age group, especially in neonates.',
            'Always correlate with phosphate, magnesium, albumin, and clinical signs.'
        ]
    elif calc=='anion_gap':
        lines += [
            'Anion gap helps frame acid-base differential diagnosis rather than giving a diagnosis by itself.',
            'A high gap may suggest ketoacidosis, lactic acidosis, renal failure, toxins, or sepsis-related metabolic stress.',
            'A normal gap acidosis may suggest diarrhea or renal tubular acidosis.',
            'Alternative explanations include low albumin effect or lab inconsistency.',
            'Suggested diagnosis frame must include bicarbonate, pH, perfusion, glucose, ketones, and renal context.',
            'Treatment direction is cause-specific and not based on the gap alone.',
            'Indian emergency and ICU practice would interpret this with the larger acid-base picture.',
            'Reference ranges vary somewhat by lab, but markedly elevated values increase concern for serious metabolic disease.',
            'Trend over time can show response to therapy.',
            'Always verify whether albumin correction is relevant in prolonged illness or critical care.'
        ]
    elif calc=='infusion_rate':
        lines += [
            'Infusion rate converts dose or volume planning into a practical pump setting and should always be double-checked.',
            'Probable risk from a wrong rate includes underdosing, fluid overload, electrolyte error, or dangerous medication exposure.',
            'Alternative error sources include wrong concentration, wrong weight, wrong time unit, or decimal placement mistake.',
            'Suggested diagnosis frame is medication-safety support rather than disease diagnosis.',
            'Treatment direction is to cross-check the calculation with the prescription, concentration, and pump settings.',
            'Indian medication-safety practice should include an independent double-check for high-risk drugs and neonatal infusions.',
            'Reference range depends entirely on the prescribed drug or fluid and not on the rate number itself.',
            'Any unusually high or low rate should trigger re-verification before administration.',
            'Alternative pathways include using standardized concentration charts where available.',
            'Document concentration, rate, weight, and reviewer before starting critical infusions.'
        ]
    elif calc=='neonatal_feed':
        lines += [
            'Daily feed volume in mL/kg/day supports neonatal nutrition planning but depends on maturity and tolerance.',
            'Probable need varies with gestational age, day of life, illness severity, respiratory support, and fluid restriction goals.',
            'Alternative explanations for poor tolerance include sepsis, NEC risk, reflux, delayed gut adaptation, or formula issues.',
            'Suggested diagnosis frame is nutrition and tolerance review rather than disease diagnosis.',
            'Treatment direction includes advancing feeds based on tolerance, abdominal exam, aspirates if monitored, stool pattern, and unit policy.',
            'Alternative treatment path is slower advancement or partial parenteral support in unstable babies.',
            'Indian NICU or SNCU feeding protocol should determine day-wise targets rather than this number alone.',
            'Minimum and maximum acceptable volume vary by gestation and day of life.',
            'Weight trend and urine output are critical companion indicators.',
            'Reassess if abdominal distension, bilious aspirate, apnea, or lethargy develops.'
        ]
    elif calc=='neonatal_fluid':
        lines += [
            'Neonatal fluid requirement in mL/kg/day is a structured starting estimate and not a fixed prescription.',
            'Probable modifiers include gestation, radiant warmer use, phototherapy, respiratory support, PDA, renal function, and sodium trend.',
            'Alternative risk is both underhydration and overhydration, especially in preterm babies.',
            'Suggested diagnosis frame is fluid planning support rather than direct disease diagnosis.',
            'Treatment direction should include daily weight, urine output, sodium, perfusion, and respiratory review.',
            'Alternative treatment path may require restriction or escalation depending on illness and insensible losses.',
            'Indian NICU practice relies on day-of-life and gestation-based fluid pathways.',
            'There is no universal single normal range across all neonates.',
            'Phototherapy and warmer care often increase fluid need, while cardiac or renal issues may reduce tolerance.',
            'Reassess fluid prescription every day and sooner if the infant status changes.'
        ]
    elif calc=='bolus':
        lines += [
            'Fluid bolus estimate supports emergency planning and should be used with a shock phenotype assessment.',
            'Probable indications include poor perfusion, dehydration shock, or sepsis depending on the clinical picture.',
            'Alternative diagnoses include cardiogenic shock, severe anemia, obstructive shock, or anaphylaxis where standard fluid strategy may differ.',
            'WHO ETAT and pediatric emergency guidance prioritize bedside recognition of shock signs before fluid escalation.',
            'Treatment direction includes reassessment after each bolus rather than repeated blind boluses.',
            'Alternative treatment path is cautious fluid strategy in SAM, myocarditis, renal failure, or dengue leakage states.',
            'Indian pediatric emergency protocol should guide dose, fluid choice, and escalation to vasoactive support.',
            'A calculated bolus does not confirm that fluid is the correct treatment.',
            'Monitor pulse volume, CRT, hepatomegaly, work of breathing, and urine output after intervention.',
            'Escalate quickly if perfusion remains poor or respiratory distress worsens.'
        ]
    else:
        lines += [
            'This result is a clinical support number and should be interpreted with history, examination, and trend.',
            'The app provides a protocol frame, not a stand-alone diagnosis.',
            'Probable causes depend on the syndrome under consideration and the patient context.',
            'Alternative diagnoses should be reviewed whenever bedside findings do not fit the number.',
            'Minimum and maximum reference values in this block are guidance anchors, not universal absolutes.',
            'Indian standard treatment workflows are advisory and allow physician judgment for individual variation.',
            'Treatment direction should focus on severity, red flags, and the likely syndrome rather than isolated numerics.',
            'Alternative management pathways may be required for malnutrition, prematurity, renal disease, or cardiac disease.',
            'Repeat assessment is recommended if the child or neonate is unstable or the value appears inconsistent.',
            'Escalate when protocol danger signs are present regardless of a borderline numeric result.'
        ]
    return lines

def render_universal_protocol(calc, value=None, unit='', min_ref=None, max_ref=None, protocol='Indian protocol context', year='Advisory', **kwargs):
    st.markdown('**Detailed under-result protocol block**')
    for line in universal_protocol_block(calc, value=value, unit=unit, min_ref=min_ref, max_ref=max_ref, protocol=protocol, year=year, **kwargs):
        st.markdown(f'- {line}')
def pediatric_clinical_interpretation(kind, value, **kwargs):
    if kind=='bmi':
        age=kwargs.get('age')
        return f"BMI is {value:.2f}. In children, BMI should not be interpreted alone; age- and sex-specific percentile or z-score review is needed. Consider nutritional history, chronic disease, edema, and pubertal stage before labeling undernutrition or obesity. If the child appears wasted, ill, or growth-faltering, correlate with weight trend, appetite, and red flags requiring in-person assessment."
    if kind=='map':
        floor=kwargs.get('floor')
        return f"Mean arterial pressure is {value:.1f} mmHg. Compare this with age-appropriate perfusion expectations; values near or below the estimated floor of {floor:.1f} mmHg may indicate compensated or overt circulatory compromise, especially if capillary refill is prolonged, pulses are weak, urine output is low, or mental status is altered. Consider sepsis, dehydration, hemorrhage, cardiac disease, and measurement error before acting."
    if kind=='dehydration':
        return f"Estimated dehydration support volume is {value} mL. This is a bedside planning cue, not a final order. Clinical severity should be judged alongside shock signs, ability to drink, ongoing stool or vomit losses, urine output, malnutrition, and serum electrolytes. Oral rehydration is preferred when feasible for mild to moderate dehydration; intravenous or nasogastric strategies are used when perfusion is impaired or enteral rehydration fails."
    if kind=='bilirubin':
        return f"This bilirubin prompt suggests: {value}. Interpretation depends strongly on age in hours, gestation, hemolysis risk, sepsis, weight loss, feeding adequacy, and neurotoxicity risk factors. Treatment decisions should follow hour-specific nomograms and local neonatal protocols rather than this prompt alone."
    if kind=='gir':
        return f"Calculated GIR is {value:.2f} mg/kg/min. Review this together with bedside glucose values, enteral feed tolerance, gestational age, sepsis risk, and fluid allowance. Low GIR may contribute to recurrent hypoglycemia, while high GIR can worsen hyperglycemia or fluid strategy complexity, especially in very preterm infants."
    return 'Interpret the result within the full clinical picture, repeating assessment if the child is unstable or the number conflicts with bedside findings.'


@st.cache_data(show_spinner=False)
def dept_link_card(name, info):
    slug = quote_plus(name)
    tags = ''.join([f"<span class='tag'>{t}</span>" for t in info['tags']])
    href = f"?dept={slug}"
    return f"<a href='{href}' style='text-decoration:none;color:inherit;display:block'><div class='card {info['cls']}'><div class='title'>{name}</div><div class='desc'>{info['desc']}</div><div style='margin-top:.38rem'>{tags}</div></div></a>"

def handle_query_nav():
    try:
        qp = st.query_params
        dept = qp.get('dept')
        if isinstance(dept, list):
            dept = dept[0] if dept else None
        if dept and dept in MODULES:
            st.session_state.dept = dept
            st.session_state.page = 'dept'
            if dept in st.session_state.recent:
                st.session_state.recent.remove(dept)
            st.session_state.recent = [dept] + st.session_state.recent[:4]
    except Exception:
        pass

def swipe_back_js():
    return """
<script>
(function(){
  if (window.__indimedSwipeBound) return;
  window.__indimedSwipeBound = true;
  let startX = 0, startY = 0, startT = 0;
  const edge = 36, minDx = 90, maxDy = 70, maxMs = 900;
  function touchStart(e){
    const t = e.changedTouches && e.changedTouches[0];
    if(!t) return;
    startX = t.clientX; startY = t.clientY; startT = Date.now();
  }
  function touchEnd(e){
    const t = e.changedTouches && e.changedTouches[0];
    if(!t) return;
    const dx = t.clientX - startX;
    const dy = Math.abs(t.clientY - startY);
    const dt = Date.now() - startT;
    const url = new URL(window.location.href);
    if(startX <= edge && dx >= minDx && dy <= maxDy && dt <= maxMs && url.searchParams.get('dept')){
      url.searchParams.delete('dept');
      window.location.href = url.toString();
    }
  }
  window.addEventListener('touchstart', touchStart, {passive:true});
  window.addEventListener('touchend', touchEnd, {passive:true});
})();
</script>
"""

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

st.markdown("<div class='hero'><h1>IndiMed X Elite</h1><p>Cross-platform, India-first bedside support with safer clinical framing, faster mobile use, ETAT-aware triage support, neonatal guidance prompts, and cleaner workflow design.</p></div>", unsafe_allow_html=True)
handle_query_nav()
components.html(swipe_back_js(), height=0)

if st.session_state.page=='home':
    st.text_input('Search modules, diseases, or tools', key='query', placeholder='Try: dengue, dose, vaccine, jaundice, sepsis')
    st.markdown("<div class='smallcap'>Search is instant across department names and descriptions.</div>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Departments</div>", unsafe_allow_html=True)
    ordered=[x for x in ['Pediatrics and Growth','Neonatology','AI Clinical Search','Medication Safety and Dose','Emergency Medicine','Metabolic and General Medicine','Hematology','HIV and ART Follow-up'] if x in search_modules(st.session_state.query)]
    for name in ordered:
        info=MODULES[name]
        st.markdown(dept_link_card(name, info), unsafe_allow_html=True)
else:
    dept=st.session_state.dept
    st.button('Back to Home', on_click=go_home)
    st.caption('Tip: swipe from the left edge to the right to go back on mobile.')
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
            st.markdown("<div class='box'><b>IAP quick topics</b><br>" + ' Ã¢â‚¬Â¢ '.join(IAP_TOPICS) + "</div>", unsafe_allow_html=True)
            for r in pubmed_search_cached(f'{symptom} {age_group} India guideline review'):
                st.markdown(f"<div class='box'><a href='{r['url']}' target='_blank'>{r['title']}</a><br><span class='desc'>{r['source']} | {r['pubdate']}</span></div>", unsafe_allow_html=True)

    elif dept=='Pediatrics and Growth':
        tabs=st.tabs(['Growth','Weight estimate','Vitals','Fever','Fluids','Vaccine','Catch-up','Dehydration','ETAT triage','Emergency'])
        with tabs[0]:
            with st.form('p1'):
                c1,c2,c3,c4=st.columns(4)
                age_m=c1.number_input('Age months',0,216,24)
                wt=c2.number_input('Weight kg',1.0,120.0,12.0)
                ht=c3.number_input('Height cm',30.0,220.0,85.0)
                sex=c4.selectbox('Sex',['Male','Female'])
                hc=st.number_input('Head circumference (cm)',0.0,80.0,45.0,0.1)
                s=st.form_submit_button('Calculate growth')
            if s:
                source_badges(indian='IAP', global_src='Standard bedside growth formula', method='BMI and quick expected-weight formula')
                c1,c2=st.columns(2); bmi=calc_bmi(wt,ht)
                c1.metric('BMI', f'{bmi:.2f}'); c2.metric('Expected weight', f'{expected_weight_kg(age_m):.1f} kg')
                hint = iap_percentile_hint('bmi', age_m/12, sex, bmi)
                st.markdown('**Growth chart interpretation**')
                st.caption(lms_method_note(age_m, 'bmi'))
                st.write(hint)
                percentile_num = infer_percentile_from_bmi(age_m/12, sex, bmi)
                zscore = percentile_to_zscore(percentile_num)
                c3,c4=st.columns(2)
                c3.metric('Approx percentile', f'{percentile_num}th' if percentile_num is not None else 'Unavailable')
                c4.metric('Approx z score', f'{zscore:+.2f}' if zscore is not None else 'Unavailable')
                st.markdown('**Growth percentile**')
                st.write(f"{simple_percentile_band(percentile_num)} | Approx z score: {zscore:+.2f}" if zscore is not None else simple_percentile_band(percentile_num))
                render_percentile_graph(percentile_num, sex, age_m)
                render_pictorial_percentile_projection('Male percentile lane', 'Male', percentile_num if sex=='Male' else None)
                render_pictorial_percentile_projection('Female percentile lane', 'Female', percentile_num if sex=='Female' else None)
                render_head_circumference_support(age_m, sex, hc)
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
                temp=c2.number_input('Temperature Ã‚Â°C',35.0,42.0,38.4)
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
                ped_drugs=sorted(set(['paracetamol','ibuprofen','ondansetron','amoxicillin','amoxicillin clavulanate','cefixime','ceftriaxone','cefotaxime','cephalexin','azithromycin','clindamycin','metronidazole','salbutamol','levosalbutamol','ipratropium','budesonide','hydrocortisone','prednisolone','dexamethasone','montelukast','cetirizine','levocetirizine','zinc','ors','vitamin d','iron','folic acid']) | set(DRUG_DATABASE.keys()) | set(LACTATION_EXTRA_DRUGS.keys()))
                drug=c1.selectbox('Drug', ped_drugs)
                wt=c2.number_input('Weight kg',1.0,200.0,20.0)
                s=st.form_submit_button('Calculate dose')
            if s:
                source_badges(indian='Drug-safety quick support', global_src='Weight-based dose estimate', method='mg/kg calculation')
                entry = pediatric_dose_entry(drug)
                if entry and 'dose_mgkg' in entry:
                    st.metric('Estimated single dose', f"{entry['dose_mgkg']*wt:.2f} mg")
                    if entry.get('route'):
                        st.caption(f"Route: {entry['route']} | Source: {entry.get('source','embedded')}")
                elif entry and 'dose_text' in entry:
                    st.markdown(f"<div class='box'><b>Dose guidance</b><br>{entry['dose_text']}</div>", unsafe_allow_html=True)
                    if entry.get('route'):
                        st.caption(f"Route: {entry['route']} | Source: {entry.get('source','embedded')}")
                else:
                    st.error('No embedded pediatric dose entry found for this drug. Add exact pediatric dosing data before using this calculator output clinically.')
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
                drug_names=sorted(DRUG_DATABASE.keys())
                d=st.selectbox('Drug for pregnancy/lactation note',drug_names,index=drug_names.index('paracetamol') if 'paracetamol' in drug_names else 0)
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
                render_universal_protocol('qsofa', value=score, unit='score', min_ref='0', max_ref='3', protocol='Sepsis screening support', year='Clinical standard')
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
            c1,c2,c3=st.columns(3); c1.metric('BMI', f'{bmi:.2f}'); c2.metric('BSA', f'{bsa:.2f} mÃ‚Â²'); c3.metric('MAP', f'{mapv:.1f} mmHg')
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


# Verification appendix added in this release
if __name__ == "__main__":
    pass


# Named-source validation summary injected in this release
NAMED_SOURCE_VALIDATION_SUMMARY = {
    "calculators_verified_or_mapped": {
        "growth_5_18": {"source": "Revised IAP growth charts for 5-18 years", "year": "2015", "status": "Partially verified"},
        "growth_under5": {"source": "WHO child growth standards", "year": "WHO standards / current standards page", "status": "Placeholder until full LMS embedding"},
        "bmi": {"source": "Standard BMI formula", "year": "current general standard", "status": "Verified-formula"},
        "bsa": {"source": "Mosteller formula", "year": "widely used clinical standard", "status": "Verified-formula"},
        "maintenance_fluids": {"source": "Holliday-Segar method", "year": "widely used pediatric standard", "status": "Verified-formula-with-cautions"},
        "map": {"source": "Standard MAP approximation", "year": "current general standard", "status": "Verified-formula"},
        "mentzer": {"source": "Mentzer index", "year": "standard hematology heuristic", "status": "Verified-formula-with-cautions"},
        "anc": {"source": "ANC definition", "year": "current standard", "status": "Verified-formula"},
        "corrected_age": {"source": "Prematurity corrected age convention", "year": "current neonatal standard", "status": "Verified-formula-with-cautions"},
        "qsofa": {"source": "Sepsis-3 qSOFA", "year": "2016", "status": "Verified-formula-with-cautions"}
    },
    "drug_validation": {
        "status": "Partial",
        "note": "Drug monographs require batch-by-batch named-source validation with dose basis, route, age cutoffs, max dose, renal/hepatic rules, contraindications, formulation assumptions, source and year."
    }
}


# --- Growth support demo panel helpers ---
def render_growth_support_panel(age_years=None, age_months=None, sex='Male', percentile=None, hc_cm=None):
    if percentile is not None:
        st.markdown('### Growth percentile projection')
        st.write(f'Estimated percentile: {percentile}')
        st.write(simple_percentile_band(percentile))
        render_pictorial_percentile_projection('Male percentile lane' if sex.lower().startswith('m') else 'Female percentile lane', sex, percentile)
    if age_months is not None and hc_cm is not None:
        render_head_circumference_support(age_months, sex, hc_cm)
