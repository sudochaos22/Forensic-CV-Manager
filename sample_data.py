from __future__ import annotations

from database import Database

SAMPLE_PROFILE = {
    "full_name": "Alex Morgan",
    "preferred_name": "Alex",
    "title": "Digital Forensic Examiner",
    "email": "alex.morgan@example.org",
    "phone": "(555) 010-2048",
    "agency": "Metro Regional Public Safety Laboratory",
    "summary": (
        "Digital forensic examiner with experience examining computers, mobile devices, vehicles, "
        "cloud data, and other digital evidence. Skilled in evidence preservation, forensic analysis, "
        "technical reporting, instruction, and courtroom testimony."
    ),
}

EMPLOYMENT = [
    {"employer":"Metro Regional Public Safety Laboratory","title":"Digital Forensic Examiner","start_date":"2018-06","end_date":"Present","location":"Metro City, USA","description":"Acquire, preserve, examine, and report on digital evidence from computers, mobile devices, removable media, vehicles, and internet-connected devices.\nPrepare technical reports and provide courtroom testimony."},
    {"employer":"County Sheriff's Office","title":"Detective","start_date":"2012-01","end_date":"2018-05","location":"Example County, USA","description":"Conducted complex criminal investigations, prepared legal process, reviewed digital evidence, coordinated with prosecutors, and testified in court."},
    {"employer":"City Police Department","title":"Police Officer","start_date":"2008-03","end_date":"2011-12","location":"Example City, USA","description":"Responded to calls for service, conducted preliminary investigations, made arrests, collected evidence, and prepared detailed reports."},
]

EDUCATION = [
    {"degree":"Master of Science in Digital Forensics","institution":"State University","graduation_date":"2022-05","honors":"","notes":"Graduate study in computer, mobile-device, network, and file-system forensics."},
    {"degree":"Bachelor of Science in Criminal Justice","institution":"Regional College","graduation_date":"2010-05","honors":"Magna Cum Laude","notes":""},
]

TRAINING = [
    ("2026-02-13","Vehicle Forensics","National Cyber Forensics Institute",36,1),
    ("2025-10-17","Mobile Device Examiner","National Cyber Forensics Institute",80,1),
    ("2025-07-25","Linux for Law Enforcement","National Cyber Forensics Institute",36,1),
    ("2025-04-11","Advanced Smartphone Analysis","Mobile Forensics Academy",40,1),
    ("2024-09-20","Network Intrusion Response","National Cyber Forensics Institute",80,1),
    ("2024-05-03","Memory Capture and Analysis","International Forensic Training Association",24,1),
    ("2023-11-17","Windows Forensic Analysis","Regional Cybercrime Center",32,1),
    ("2023-03-10","Basic Computer Forensic Examiner","International Forensic Training Association",80,1),
]

CERTIFICATIONS = [
    {"certification":"Certified Digital Forensic Examiner","issuing_organization":"International Forensic Training Association","earned_date":"2023-06","expiration_date":"2028-06","status":"Active"},
    {"certification":"Certified Mobile Device Examiner","issuing_organization":"International Forensic Training Association","earned_date":"2025-12","expiration_date":"2028-12","status":"Active"},
    {"certification":"Mobile Forensics Certified Operator","issuing_organization":"Mobile Forensics Academy","earned_date":"2024-04","expiration_date":"2027-04","status":"Active"},
]

TESTIMONY = [
    {"testimony_date":"2026-04-22","case_number":"26-CF-001234","court":"Example County Circuit Court","jurisdiction":"State of Example","witness_type":"Expert Witness","party":"Prosecution","subject":"Mobile-device forensics"},
    {"testimony_date":"2025-08-14","case_number":"25-CF-004321","court":"Example County Circuit Court","jurisdiction":"State of Example","witness_type":"Fact Witness","party":"Prosecution","subject":"Digital evidence collection"},
    {"testimony_date":"2024-02-09","case_number":"24-CF-000987","court":"Example County Circuit Court","jurisdiction":"State of Example","witness_type":"Expert Witness","party":"Prosecution","subject":"Computer forensics"},
]

TEACHING = [
    {"organization":"International Forensic Training Association","role":"Block Instructor","course_name":"Memory Capture and Analysis","start_date":"2024","end_date":"Present","description":"Teach memory acquisition, validation, triage, and analysis concepts.","hours":24},
    {"organization":"Regional Cybercrime Center","role":"Guest Instructor","course_name":"Digital Evidence First Responder","start_date":"2022","end_date":"2025","description":"Provided instruction on identifying, documenting, collecting, and preserving digital evidence.","hours":16},
]

ORGANIZATIONS = [
    {"organization":"International Forensic Training Association","role":"Member / Instructor","start_year":"2022","end_year":"Present"},
    {"organization":"Regional Digital Forensics Working Group","role":"Member","start_year":"2019","end_year":"Present"},
]

SKILLS = [
    ("Mobile-device acquisition and analysis","Forensic Disciplines"),
    ("Computer and file-system forensics","Forensic Disciplines"),
    ("Memory acquisition and analysis","Forensic Disciplines"),
    ("Vehicle and IoT forensics","Forensic Disciplines"),
    ("Cellebrite UFED and Physical Analyzer","Forensic Tools"),
    ("Magnet AXIOM","Forensic Tools"),
    ("X-Ways Forensics","Forensic Tools"),
    ("Forensic Explorer","Forensic Tools"),
    ("Volatility Framework","Forensic Tools"),
    ("Python and SQLite","Technical"),
    ("Technical reports and courtroom testimony","Professional"),
]

ACHIEVEMENTS = [
    {"achievement":"Developed a standardized digital-evidence examination workflow","achievement_date":"2025-01","organization":"Metro Regional Public Safety Laboratory","description":"Created documentation and quality-control checkpoints for consistent examinations.","category":"Professional"},
]


def load_sample_profile(db: Database, *, clear: bool = True) -> None:
    if clear:
        db.clear_current_profile_data()
    db.save_profile(SAMPLE_PROFILE)
    for row in EMPLOYMENT: db.insert_row("employment", row)
    for row in EDUCATION: db.insert_row("education", row)
    for date, name, provider, hours, core in TRAINING:
        db.insert_row("training", {"attended_date":date,"course_name":name,"provider":provider,"hours":hours,"core_training":core,"category":"Digital Forensics"})
    for row in CERTIFICATIONS: db.insert_row("certifications", row)
    for row in TESTIMONY: db.insert_row("testimony", row)
    for row in TEACHING: db.insert_row("teaching", row)
    for row in ORGANIZATIONS: db.insert_row("organizations", row)
    for skill, category in SKILLS: db.insert_row("skills", {"skill":skill,"category":category})
    for row in ACHIEVEMENTS: db.insert_row("achievements", row)
