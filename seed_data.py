from __future__ import annotations
from database import Database

PROFILE = {
    "full_name": "Detective James 'Shannon' Padilla",
    "preferred_name": "Shannon",
    "title": "Digital Forensic Detective / Examiner",
    "email": "James.Padilla@JaxSheriff.org",
    "phone": "(904) 327-6444",
    "agency": "Jacksonville Sheriff's Office",
    "summary": "Law enforcement professional with over 31 years of experience, including extensive expertise in digital forensics, complex investigations, and courtroom testimony. Ten years of specialized experience examining computers, mobile devices, vehicles, and emerging technologies. Proven ability to conduct detailed forensic analysis, prepare expert reports, teach forensic concepts, and testify effectively in court. Holds a Master of Science in Digital Forensics and serves as an instructor for the International Association of Computer Investigative Specialists (IACIS).",
}

EMPLOYMENT = [
    ("Jacksonville Sheriff's Office", "Digital Forensic Detective / Examiner", "2016-11", "Present", "Jacksonville, Florida", "Extract and analyze data from computers, mobile devices, drones, digital media, vehicles, and emerging technologies. Assigned as a Task Force Officer to the U.S. Secret Service Jacksonville Field Office. Perform advanced acquisition methods, document findings in standardized forensic reports, testify in criminal proceedings, conduct training, author agency best-practice manuals, and evaluate forensic equipment and vendors."),
    ("Jacksonville Sheriff's Office", "Bailiff, Patrol Officer, and Detective", "2002-11", "2016-11", "Jacksonville, Florida", "Investigated firearms-related crimes; authored search warrants, court orders, arrest warrants, and subpoenas; obtained ISP records; evaluated digital evidence; prepared investigative reports; worked with prosecutors; and frequently testified in criminal proceedings. Also performed courtroom security, inmate movement, patrol, and community response duties."),
    ("Palm Beach County Sheriff's Office", "Deputy Sheriff", "2000-03", "2002-11", "Palm Beach County, Florida", "Patrolled assigned areas, deterred criminal activity, provided community-policing and crime-prevention services, enforced laws, investigated crimes, made arrests, and prepared detailed reports."),
    ("Guarantec, LLC", "Business / Systems Analyst", "1990-03", "2000-03", "", "Designed a company-wide financial software plan, collaborated with software engineers, evaluated and tested code, and performed basic development in COBOL, FORTRAN, C, C++, C#, and FoxPro."),
]

EDUCATION = [
    ("Master of Science in Digital Forensics", "University of Central Florida", "2023", "", ""),
    ("Bachelor of Applied Science in Public Safety Management", "Florida State College at Jacksonville", "2020", "Magna Cum Laude", ""),
    ("Certified Ethical Hacker Program", "Edmonds Community College", "2016", "", ""),
    ("Associate in Arts, General Studies", "Florida State College at Jacksonville", "2011", "", ""),
    ("Associate in Science, Criminal Justice", "Florida State College at Jacksonville", "2002", "", ""),
]

CERTIFICATIONS = [
    ("Certified Mobile Device Forensic Examiner (CMDE)", "IACIS", "2025-12-03", "2028-12-31"),
    ("Cellebrite Advanced Smartphone Analysis (CASA)", "Cellebrite", "2021-03-12", ""),
    ("Certified Forensic Examiner (CFE)", "IACIS", "2019-09-18", "2028-12-31"),
    ("Cellebrite Certified Operator (CCO)", "Cellebrite", "2018-02-06", ""),
    ("Cellebrite Certified Physical Analyst (CCPA)", "Cellebrite", "2018-02-06", ""),
    ("AccessData Certified Examiner v5 (ACE)", "AccessData / Exterro", "2017-07-27", ""),
    ("DVR Examiner Certified User", "DME Forensics", "2017-08-15", ""),
    ("Digital Forensic Examiner", "CyberSecurity Institute", "2015-10-19", ""),
]

TESTIMONY = [
    ("2014-03-05", "14CF023654AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2019-06-20", "16CF047922AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2020-02-12", "17CF029772AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2023-03-08", "21CF042578AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2023-09-07", "21CF042578AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2025-06-25", "24CF045022AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2025-07-09", "23CF080598AD", "4th Judicial Circuit", "Florida", "Fact Witness"),
    ("2025-01-28", "21CF000566AD", "4th Judicial Circuit", "Florida", "Expert Witness"),
    ("2023-05-09", "21CF000558AD", "4th Judicial Circuit", "Florida", "Expert Witness"),
    ("2026-04-22", "21CF044394AD", "4th Judicial Circuit", "Florida", "Expert Witness"),
]

TEACHING = [
    ("IACIS", "Class Instructor", "RAM Capture & Analysis", "2026", "2026", "Instruction focused on capture and analysis of random-access memory."),
    ("IACIS", "Block Instructor", "RAM Capture & Analysis", "2024", "2026", "Instruction focused on capture of random-access memory."),
    ("IACIS", "Peer Coach", "Computer Forensic Examiner Certification", "2021", "2025", "One-on-one coaching for candidates completing the certification process."),
    ("IACIS", "Block Instructor", "First Responder", "2021", "2022", "Instruction focused on collection of digital evidence at crime scenes."),
    ("IACIS", "Block Instructor", "Digital Soup", "2021", "2023", "Instruction covering evidence from non-traditional and internet-connected devices."),
    ("University of Central Florida", "Graduate Teaching Assistant", "OS and File System Forensics (CIS 6386)", "2023", "2023", "Assisted with course preparation, discussion sessions, grading, student records, and mentoring."),
    ("University of Central Florida", "Graduate Teaching Assistant", "Practice of Digital Forensics (CIS 6207)", "2023", "2023", "Assisted with course preparation, discussion sessions, grading, student records, and mentoring."),
]

ORGANIZATIONS = [
    ("International Association of Computer Investigative Specialists", "Member / Instructor", "2019", "Present"),
    ("Jacksonville Exchange Club", "President", "2016", "2017"),
    ("School Advisory Council", "Chairman", "2002", "2016"),
    ("Jacksonville Junior Chamber of Commerce", "Vice President", "1994", "1999"),
]

SKILLS = [
    ("Cellebrite Inseyets (UFED, Physical Analyzer, Premium)", "Forensic Tools"),
    ("Magnet GrayKey", "Forensic Tools"),
    ("Exterro Forensic Tool Kit", "Forensic Tools"),
    ("Magnet AXIOM", "Forensic Tools"),
    ("GetData Forensic Explorer", "Forensic Tools"),
    ("Computer and file-system forensics", "Forensic Disciplines"),
    ("Mobile-device forensics", "Forensic Disciplines"),
    ("Vehicle and IoT forensics", "Forensic Disciplines"),
    ("Memory acquisition and analysis", "Forensic Disciplines"),
    ("System analysis and development", "Technical"),
    ("Python, C, and C# scripting", "Technical"),
    ("Expert reports and courtroom testimony", "Professional"),
]

# Core CV training plus the detailed entries visible in the supplied CV.
TRAINING = [
    ("2026-04-02", "Webinar: Reconstructing User Activities from a Memory Dump", "NW3C", 1, 0),
    ("2026-04-01", "Webinar: iCatch - Mapping Forensic Artifacts from iOS Devices", "NW3C", 1, 0),
    ("2026-01-23", "Vehicle Forensic Course (VFC)", "NCFI", 36, 1),
    ("2026-01-15", "Review of Forensics Principles (RFP - BCERT)", "NCFI", 6, 0),
    ("2025-11-13", "Mobile Device Forensics Course", "IACIS", 36, 1),
    ("2025-09-11", "Mobile Device Examiner Program (MDE)", "NCFI", 116, 1),
    ("2025-07-25", "Internet of Things (IOT)", "NCFI", 36, 1),
    ("2025-07-18", "Linux for Law Enforcement (LLE)", "NCFI", 36, 1),
    ("2025-06-12", "Virtual Advanced Mobile Extraction Techniques (AMET)", "NCFI", 6, 1),
    ("2025-02-06", "Advanced Forensic Training (AFT)", "NCFI", 96, 1),
    ("2024-09-13", "Skimmer Forensics Course (SFC)", "NCFI", 40, 1),
    ("2024-07-27", "Network Intrusion Response Program (NITRO)", "NCFI", 116, 1),
    ("2023-11-10", "Introduction to Phone Repair (IPR)", "NCFI", 36, 1),
    ("2023-08-03", "Advanced Digital Forensic Analysis: macOS", "NW3C", 28, 1),
    ("2023-01-20", "Network Intrusion Response Program (NITRO)", "NCFI", 116, 0),
    ("2022-03-04", "X-Ways Forensics", "H-11", 24, 1),
    ("2021-08-20", "Basic Computer Evidence Recovery Training (BCERT)", "NCFI", 176, 1),
    ("2021-08-10", "Forensic Explorer Introduction Training", "GetData", 16, 1),
    ("2021-06-09", "Basic Cyber Investigations: Dark Web & OSINT", "NW3C", 24, 0),
    ("2021-05-07", "Basic Computer Forensic Examiner (Staff)", "IACIS", 76, 0),
    ("2021-04-24", "Train the Trainer Course", "IACIS", 8, 0),
    ("2021-03-12", "Cellebrite Advanced Smartphone Analysis (CASA)", "Cellebrite", 28, 1),
    ("2020-12-04", "Advanced Digital Forensic Analysis: macOS", "NW3C", 32, 1),
    ("2020-11-06", "Advanced Digital Forensic Analysis: iOS & Android", "NW3C", 32, 1),
    ("2020-07-20", "In-Service Training: Memory Forensics", "NCFI", 24, 0),
    ("2019-05-10", "Basic Computer Forensic Examiner", "IACIS", 76, 1),
    ("2018-11-09", "Vehicle Systems Forensics (iVe)", "Berla", 40, 1),
    ("2018-08-31", "JTAG Chip-Off for Smartphones", "FLETC", 80, 1),
    ("2018-06-08", "Basic Network Intrusion Investigations", "NW3C", 32, 0),
    ("2018-02-06", "Cellebrite Certified Operator / Physical Analyst", "Cellebrite", 35, 0),
    ("2017-07-28", "Seized Computer Evidence Recovery Specialist", "FLETC", 80, 1),
    ("2017-07-14", "Introduction to Digital Evidence Analysis", "FLETC", 40, 1),
    ("2017-05-12", "Digital Evidence Acquisition Specialist Training Program", "FLETC", 80, 1),
    ("2017-02-17", "Mobile Device Investigations Program", "FLETC", 40, 1),
    ("2014-09-18", "Case Preparation / Court Presentation", "St. Johns River State College", 40, 0),
    ("2002-01-01", "Interview and Interrogations", "Law Enforcement Training", None, 1),
    ("2001-01-01", "Field Training Officer", "Law Enforcement Training", None, 1),
    ("2001-01-01", "Instructor Techniques", "Law Enforcement Training", None, 1),
]


def seed(db: Database) -> None:
    if db.count("employment") or db.get_profile().get("full_name"):
        return
    db.save_profile(PROFILE)
    for item in EMPLOYMENT:
        db.insert_row("employment", dict(zip(["employer", "title", "start_date", "end_date", "location", "description"], item)))
    for item in EDUCATION:
        db.insert_row("education", dict(zip(["degree", "institution", "graduation_date", "honors", "notes"], item)))
    for cert, org, earned, expires in CERTIFICATIONS:
        db.insert_row("certifications", {"certification": cert, "issuing_organization": org, "earned_date": earned, "expiration_date": expires})
    for date, case, court, jurisdiction, kind in TESTIMONY:
        db.insert_row("testimony", {"testimony_date": date, "case_number": case, "court": court, "jurisdiction": jurisdiction, "witness_type": kind})
    for org, role, course, start, end, desc in TEACHING:
        db.insert_row("teaching", {"organization": org, "role": role, "course_name": course, "start_date": start, "end_date": end, "description": desc})
    for org, role, start, end in ORGANIZATIONS:
        db.insert_row("organizations", {"organization": org, "role": role, "start_year": start, "end_year": end})
    for skill, category in SKILLS:
        db.insert_row("skills", {"skill": skill, "category": category})
    for date, name, provider, hours, core in TRAINING:
        db.insert_row("training", {"attended_date": date, "course_name": name, "provider": provider, "hours": hours, "core_training": core})
