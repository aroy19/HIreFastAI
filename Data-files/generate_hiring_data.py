#!/usr/bin/env python3
"""
Generate joinable hiring mock datasets for multi-agent insight workflows.
Run: python generate_hiring_data.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent
TODAY = datetime(2026, 8, 23)

JOB_TYPES = ["BE", "FE", "DS"]
ROLE_LEVELS = {
    "BE": ["SWE1", "SWE2", "SWE3", "Staff SWE", "Principal", "Eng Manager"],
    "FE": ["SWE1", "SWE2", "SWE3", "Staff SWE", "Eng Manager"],
    "DS": ["SWE1", "SWE2", "SWE3", "Staff SWE", "Eng Manager"],
}

STAGE_TEMPLATES = [
    ("Resume screening", 2, "1=Unqualified resume, 3=Meets bar, 5=Strong pedigree"),
    ("Recruiter screening", 3, "1=Poor communication, 3=Clear and engaged, 5=Exceptional advocate"),
    ("Tech Screening", 5, "1=Fundamental gaps, 3=Solid fundamentals, 5=Deep technical breadth"),
    ("Coding interview", 5, "1=Could not solve, 3=Working solution with hints, 5=Optimal clean code"),
    ("System design", 7, "1=No scalable thinking, 3=Adequate design, 5=Production-grade architecture"),
    ("HM - Org fit", 5, "1=Misaligned values, 3=Good collaborator, 5=Strong leadership potential"),
    ("Recruiter debrief", 2, "1=Process concerns, 3=Standard pass, 5=Expedite offer"),
    ("Offer stage", 10, "1=Declined immediately, 3=Negotiating, 5=Accepted"),
    ("Hired or Not Hired", 1, "1=Not hired, 3=N/A, 5=Hired"),
]

SENIOR_PLUS = {"SWE3", "Staff SWE", "Principal", "Eng Manager"}
JUNIOR_LEVELS = {"SWE1", "SWE2"}

SOURCES = [
    ("Employee Referral", 0.38),
    ("LinkedIn", 0.28),
    ("Indeed", 0.14),
    ("GitHub", 0.08),
    ("Company Website", 0.07),
    ("Recruiter Agency", 0.05),
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Sam", "Jamie", "Drew", "Blake", "Cameron", "Reese", "Skyler", "Logan",
    "Priya", "Arjun", "Mei", "Carlos", "Sofia", "Ethan", "Nina", "Omar",
    "Hannah", "Raj", "Yuki", "Marcus", "Elena", "David", "Fatima", "Noah",
]
LAST_NAMES = [
    "Chen", "Patel", "Kim", "Nguyen", "Garcia", "Williams", "Johnson", "Singh",
    "Brown", "Martinez", "Lee", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Clark", "Lewis", "Robinson", "Walker", "Young", "King", "Wright", "Scott",
]

LOCATIONS = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Remote - US"]

OTHER_MANAGERS = ["Raj Patel", "Maria Chen", "James Okonkwo"]

REJECTION_REASONS = {
    "general": [
        "Missing required skill",
        "Not good team fit",
        "Too junior for role level",
        "Insufficient years of experience",
        "Location mismatch",
        "Commute concerns",
        "Salary expectations misaligned",
        "Failed coding bar",
    ],
    "fe_system_design": [
        "Missing system design skills for frontend architecture",
        "Weak frontend system design - state management at scale",
        "Could not articulate component architecture patterns",
        "Insufficient experience designing large SPA systems",
    ],
    "be_linkedin": [
        "Resume inflation - skills not validated in tech screen",
        "LinkedIn profile overstated distributed systems experience",
        "Could not demonstrate claimed backend expertise",
    ],
    "offer_decline": [
        "Declined - competing offer 18% higher base salary",
        "Declined - competing offer with better equity package",
        "Declined - offer timeline too slow, accepted elsewhere",
        "Declined - total comp below market for Staff level",
        "Declined - preferred hybrid, we require onsite 4 days",
        "Declined - accepted FAANG competing offer",
    ],
}

PROFILES = [
    "{yoe} YOE {stack} engineer at {company}. Built {project}.",
    "Former {company} {title}. Expertise in {stack}. {yoe} years experience.",
    "{level} developer specializing in {stack}. Open to {location}.",
    "Full-stack leaning {stack}. Led team of {team_size} at {company}.",
]

COMPANIES = ["Stripe", "Meta", "StartupXYZ", "Datadog", "Airbnb", "Uber", "Square", "Plaid"]
STACKS = {
    "BE": ["Java/Kotlin", "Python/Django", "Go microservices", "Node.js", "Ruby on Rails"],
    "FE": ["React/TypeScript", "Vue.js", "Angular", "Next.js", "React Native"],
    "DS": ["Python/ML", "Spark/Airflow", "TensorFlow", "dbt/Snowflake", "R/statistics"],
}


def weighted_choice(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]


def gen_stages():
    rows = []
    stage_id = 1
    for job_type in JOB_TYPES:
        for role_level in ROLE_LEVELS[job_type]:
            order = 1
            for stage_name, duration, rubric in STAGE_TEMPLATES:
                if stage_name == "System design" and role_level not in SENIOR_PLUS:
                    continue
                if role_level == "Eng Manager" and stage_name == "Coding interview":
                    stage_name = "Leadership case study"
                rows.append({
                    "stage_id": f"STG-{stage_id:04d}",
                    "job_type": job_type,
                    "role_level": role_level,
                    "stage_name": stage_name,
                    "stage_order": order,
                    "expected_duration_days": duration,
                    "grading_rubric_1_to_5": rubric,
                })
                stage_id += 1
                order += 1
    return rows


def stage_lookup(stages):
    lookup = {}
    for s in stages:
        key = (s["job_type"], s["role_level"])
        lookup.setdefault(key, []).append(s)
    for key in lookup:
        lookup[key].sort(key=lambda x: x["stage_order"])
    return lookup


def gen_jobs():
    rows = []
    job_id = 1
    specs = [
        # Open roles with intentional pipeline health issues
        ("BE", "Staff SWE", "Open", TODAY - timedelta(days=94), None, None, "San Francisco, CA", True),
        ("FE", "SWE2", "Open", TODAY - timedelta(days=78), None, None, "New York, NY", True),
        ("BE", "SWE3", "Open", TODAY - timedelta(days=65), None, None, "Seattle, WA", True),
        ("DS", "Staff SWE", "Open", TODAY - timedelta(days=88), None, None, "Remote - US", True),
        ("FE", "Staff SWE", "Open", TODAY - timedelta(days=52), None, None, "San Francisco, CA", True),
        ("BE", "SWE1", "Open", TODAY - timedelta(days=45), None, None, "Austin, TX", True),
        ("FE", "SWE1", "Open", TODAY - timedelta(days=40), None, None, "Remote - US", True),
        ("DS", "SWE2", "Open", TODAY - timedelta(days=38), None, None, "Seattle, WA", True),
        ("BE", "Principal", "Open", TODAY - timedelta(days=71), None, None, "San Francisco, CA", True),
        ("FE", "SWE3", "Open", TODAY - timedelta(days=55), None, None, "New York, NY", True),
        ("BE", "SWE2", "Open", TODAY - timedelta(days=32), None, None, "Austin, TX", True),
        ("DS", "SWE1", "Open", TODAY - timedelta(days=28), None, None, "Remote - US", True),
        ("BE", "Eng Manager", "Open", TODAY - timedelta(days=60), None, None, "San Francisco, CA", True),
        ("FE", "Eng Manager", "Open", TODAY - timedelta(days=48), None, None, "Seattle, WA", True),
        ("BE", "SWE3", "Open", TODAY - timedelta(days=25), None, None, "New York, NY", True),
        ("DS", "SWE3", "Open", TODAY - timedelta(days=22), None, None, "Austin, TX", True),
        ("FE", "SWE2", "Open", TODAY - timedelta(days=35), None, None, "San Francisco, CA", True),
        ("BE", "Staff SWE", "Open", TODAY - timedelta(days=42), None, None, "Seattle, WA", True),
        ("DS", "Eng Manager", "Open", TODAY - timedelta(days=30), None, None, "Remote - US", True),
        ("BE", "SWE2", "Open", TODAY - timedelta(days=18), None, None, "Austin, TX", True),
        ("FE", "SWE3", "Open", TODAY - timedelta(days=15), None, None, "New York, NY", True),
        # Closed historic roles (30%)
        ("BE", "SWE2", "Closed", TODAY - timedelta(days=120), TODAY - timedelta(days=45), "CAND-0042", "San Francisco, CA", False),
        ("FE", "SWE1", "Closed", TODAY - timedelta(days=110), TODAY - timedelta(days=50), "CAND-0088", "Remote - US", False),
        ("BE", "Staff SWE", "Closed", TODAY - timedelta(days=150), TODAY - timedelta(days=60), "CAND-0120", "Seattle, WA", False),
        ("DS", "SWE2", "Closed", TODAY - timedelta(days=100), TODAY - timedelta(days=40), "CAND-0155", "Austin, TX", False),
        ("FE", "SWE3", "Closed", TODAY - timedelta(days=130), TODAY - timedelta(days=55), "CAND-0198", "New York, NY", False),
        ("BE", "SWE1", "Closed", TODAY - timedelta(days=95), TODAY - timedelta(days=35), "CAND-0230", "Austin, TX", False),
        ("DS", "SWE3", "Closed", TODAY - timedelta(days=140), TODAY - timedelta(days=70), "CAND-0265", "Remote - US", False),
        ("FE", "Staff SWE", "Closed", TODAY - timedelta(days=160), TODAY - timedelta(days=80), "CAND-0298", "San Francisco, CA", False),
        ("BE", "SWE3", "Closed", TODAY - timedelta(days=105), TODAY - timedelta(days=42), "CAND-0335", "Seattle, WA", True),
    ]
    # Exactly 3 jobs (10%) under other managers; rest under Aparna G.
    non_aparna_indices = {27, 28, 29}  # 0-based indices into specs
    for idx, (job_type, role_level, status, open_date, close_date, hired, location, _) in enumerate(specs):
        manager = random.choice(OTHER_MANAGERS) if idx in non_aparna_indices else "Aparna G."
        days_open = (close_date or TODAY).toordinal() - open_date.toordinal()
        rows.append({
            "job_id": f"JOB-{job_id:04d}",
            "job_type": job_type,
            "role_level": role_level,
            "hiring_manager": manager,
            "job_status": status,
            "job_open_date": open_date.strftime("%Y-%m-%d"),
            "days_open": days_open,
            "job_closed_date": close_date.strftime("%Y-%m-%d") if close_date else "",
            "candidate_hired": hired or "",
            "job_location": location,
        })
        job_id += 1
    return rows


def gen_candidates(n=220):
    rows = []
    for i in range(1, n + 1):
        source = weighted_choice(SOURCES)
        job_type = random.choice(JOB_TYPES)
        yoe = random.randint(1, 15)
        stack = random.choice(STACKS[job_type])
        company = random.choice(COMPANIES)
        template = random.choice(PROFILES)
        profile = template.format(
            yoe=yoe,
            stack=stack,
            company=company,
            title=random.choice(["SWE", "Senior SWE", "Staff Engineer", "Tech Lead"]),
            level=random.choice(["Junior", "Mid", "Senior", "Staff"]),
            location=random.choice(LOCATIONS),
            team_size=random.randint(2, 12),
            project=random.choice(["payments API", "search infra", "ML pipeline", "design system"]),
        )
        rows.append({
            "candidate_id": f"CAND-{i:04d}",
            "sourced_from": source,
            "profile_summary": profile,
        })
    return rows


def pass_rate(source, job_type, role_level, stage_name):
    """Intentional patterns for sourcing quality agent."""
    base = 0.55
    if source == "Employee Referral":
        base = 0.72
    elif source == "GitHub" and job_type == "BE":
        base = 0.68
    elif source == "LinkedIn":
        base = 0.35
        if job_type == "BE" and role_level in {"Staff SWE", "Principal"}:
            base = 0.18
        if job_type == "FE":
            base = 0.28
    elif source == "Indeed":
        base = 0.42
    elif source == "Recruiter Agency":
        base = 0.48

    if stage_name in ("Resume screening", "Recruiter screening"):
        base += 0.1
    elif stage_name in ("System design", "Coding interview"):
        base -= 0.08
    return max(0.08, min(0.92, base + random.uniform(-0.05, 0.05)))


def rejection_reason(source, job_type, role_level, stage_name, decision):
    if decision == "Yes":
        return ""
    if stage_name == "Offer stage":
        return random.choice(REJECTION_REASONS["offer_decline"])
    if job_type == "FE" and stage_name == "System design":
        return random.choice(REJECTION_REASONS["fe_system_design"])
    if source == "LinkedIn" and job_type == "BE" and stage_name == "Tech Screening":
        return random.choice(REJECTION_REASONS["be_linkedin"])
    return random.choice(REJECTION_REASONS["general"])


def gen_applications_and_feedback(jobs, candidates, stages, interviewers):
    stage_map = stage_lookup(stages)
    interviewer_by_type = {}
    for iv in interviewers:
        interviewer_by_type.setdefault(iv["job_type"], []).append(iv["interviewer_id"])

    # Track load per interviewer this month (Aug 2026)
    interviewer_load = {iv["interviewer_id"]: 0 for iv in interviewers}

    applications = []
    feedback = []
    app_id = 1
    fb_id = 1

    open_jobs = [j for j in jobs if j["job_status"] == "Open"]
    closed_jobs = [j for j in jobs if j["job_status"] == "Closed"]

    def simulate_pipeline(job, n_apps, force_stuck=False, fe_pattern=False, offer_declines=False):
        nonlocal app_id, fb_id
        key = (job["job_type"], job["role_level"])
        pipeline = stage_map[key]
        open_dt = datetime.strptime(job["job_open_date"], "%Y-%m-%d")

        for _ in range(n_apps):
            cand = random.choice(candidates)
            app_date = open_dt + timedelta(days=random.randint(0, max(5, job["days_open"] - 5)))
            if app_date > TODAY:
                app_date = TODAY - timedelta(days=random.randint(1, 14))

            applications.append({
                "application_id": f"APP-{app_id:04d}",
                "job_id": job["job_id"],
                "candidate_id": cand["candidate_id"],
                "application_date": app_date.strftime("%Y-%m-%d"),
            })

            current_date = app_date
            stuck_at_hm = force_stuck and random.random() < 0.4

            for stage in pipeline:
                if stage["stage_name"] == "Hired or Not Hired":
                    break

                # SLA breach: stuck at HM screen
                if stuck_at_hm and stage["stage_name"] == "HM - Org fit":
                    extra_days = random.randint(14, 28)
                else:
                    extra_days = random.randint(0, max(1, stage["expected_duration_days"]))

                current_date += timedelta(days=extra_days)
                if current_date > TODAY and job["job_status"] == "Closed":
                    current_date = datetime.strptime(job["job_closed_date"], "%Y-%m-%d") - timedelta(days=1)

                iv_pool = interviewer_by_type.get(job["job_type"], [])
                iv_id = random.choice(iv_pool) if iv_pool else ""

                # Bias load: Sarah Chen overloaded, Mike/Priya underutilized
                if random.random() < 0.45:
                    iv_id = "IV-001"  # Sarah Chen - drowning
                elif random.random() < 0.3:
                    iv_id = random.choice(["IV-008", "IV-009"])  # Mike Torres, Priya Sharma - underloaded

                if current_date.month == 8 and current_date.year == 2026:
                    interviewer_load[iv_id] = interviewer_load.get(iv_id, 0) + 1

                rate = pass_rate(cand["sourced_from"], job["job_type"], job["role_level"], stage["stage_name"])

                # FE system design rejection pattern
                if fe_pattern and stage["stage_name"] == "System design" and job["job_type"] == "FE":
                    rate = 0.15

                # Offer decline pattern
                if offer_declines and stage["stage_name"] == "Offer stage":
                    rate = 0.25

                decision = "Yes" if random.random() < rate else "No"
                reason = rejection_reason(
                    cand["sourced_from"], job["job_type"], job["role_level"],
                    stage["stage_name"], decision,
                )

                feedback.append({
                    "feedback_id": f"FB-{fb_id:05d}",
                    "application_id": f"APP-{app_id:04d}",
                    "stage_id": stage["stage_id"],
                    "interviewer_id": iv_id,
                    "date_of_interview": current_date.strftime("%Y-%m-%d"),
                    "decision": decision,
                    "decision_reason": reason,
                })
                fb_id += 1

                if decision == "No":
                    break
                if stuck_at_hm and stage["stage_name"] == "HM - Org fit":
                    break  # still in pipeline

            app_id += 1

    # Open jobs - more applications
    for job in open_jobs:
        n = random.randint(8, 18)
        force_stuck = job["job_id"] in ("JOB-0001", "JOB-0002", "JOB-0004")  # Platform/FE stuck
        fe_pattern = job["job_type"] == "FE" and job["role_level"] in ("SWE2", "SWE3", "Staff SWE")
        offer_declines = job["role_level"] in ("Staff SWE", "Principal", "SWE3")
        simulate_pipeline(job, n, force_stuck=force_stuck, fe_pattern=fe_pattern, offer_declines=offer_declines)

    # Closed jobs - historic
    for job in closed_jobs:
        n = random.randint(5, 12)
        simulate_pipeline(job, n, force_stuck=False, fe_pattern=False, offer_declines=False)

    return applications, feedback, interviewer_load


def gen_interviewers():
    names = [
        ("Sarah", "Chen", "BE"),
        ("David", "Kim", "BE"),
        ("Lisa", "Wang", "BE"),
        ("Tom", "Bradley", "BE"),
        ("Anita", "Desai", "BE"),
        ("Mike", "Torres", "BE"),
        ("Priya", "Sharma", "BE"),
        ("Emily", "Foster", "FE"),
        ("Jason", "Reed", "FE"),
        ("Nina", "Patel", "FE"),
        ("Chris", "Liu", "FE"),
        ("Rachel", "Green", "FE"),
        ("Mike", "Torres", "FE"),
        ("Priya", "Sharma", "FE"),
        ("Kevin", "Brooks", "DS"),
        ("Amy", "Zhang", "DS"),
        ("Daniel", "Ruiz", "DS"),
        ("Sophia", "Martin", "DS"),
    ]
    rows = []
    for i, (first, last, jt) in enumerate(names, 1):
        rows.append({
            "interviewer_id": f"IV-{i:03d}",
            "interviewer_name": f"{first} {last}",
            "job_type": jt,
        })
    return rows


def gen_availability(interviewers, interviewer_load):
    rows = []
    avail_id = 1

    # Load bias: Sarah (IV-001) few slots, Mike (IV-006/013) and Priya (IV-007/014) many
    load_factor = {
        "IV-001": 0.15,   # drowning - almost no availability
        "IV-006": 0.95,
        "IV-007": 0.92,
        "IV-013": 0.93,
        "IV-014": 0.90,
    }

    for iv in interviewers:
        iv_id = iv["interviewer_id"]
        factor = load_factor.get(iv_id, 0.55)

        # 10% past, 90% future
        for day_offset in list(range(-30, 0)) + list(range(1, 91)):
            if random.random() > factor:
                continue
            day = TODAY + timedelta(days=day_offset)
            if day.weekday() >= 5:
                continue
            for hour in [9, 10, 11, 13, 14, 15, 16]:
                slot = day.replace(hour=hour, minute=0, second=0)
                is_future = day_offset > 0
                if is_future and random.random() > 0.9:
                    continue
                if not is_future and random.random() > 0.3:
                    continue
                rows.append({
                    "availability_id": f"AVAIL-{avail_id:05d}",
                    "interviewer_id": iv_id,
                    "available_slot": slot.strftime("%Y-%m-%d %H:%M"),
                    "slot_period": "future" if is_future else "past",
                })
                avail_id += 1

    return rows


def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows):>5} rows -> {path.name}")


def main():
    print("Generating hiring mock datasets...\n")

    stages = gen_stages()
    write_csv("interview_stages.csv", stages, [
        "stage_id", "job_type", "role_level", "stage_name", "stage_order",
        "expected_duration_days", "grading_rubric_1_to_5",
    ])

    jobs = gen_jobs()
    write_csv("jobs.csv", jobs, [
        "job_id", "job_type", "role_level", "hiring_manager", "job_status",
        "job_open_date", "days_open", "job_closed_date", "candidate_hired", "job_location",
    ])

    candidates = gen_candidates(220)
    write_csv("candidates.csv", candidates, [
        "candidate_id", "sourced_from", "profile_summary",
    ])

    interviewers = gen_interviewers()
    write_csv("interviewer_pool.csv", interviewers, [
        "interviewer_id", "interviewer_name", "job_type",
    ])

    applications, feedback, interviewer_load = gen_applications_and_feedback(
        jobs, candidates, stages, interviewers,
    )
    write_csv("applications.csv", applications, [
        "application_id", "job_id", "candidate_id", "application_date",
    ])
    write_csv("interview_feedback.csv", feedback, [
        "feedback_id", "application_id", "stage_id", "interviewer_id",
        "date_of_interview", "decision", "decision_reason",
    ])

    availability = gen_availability(interviewers, interviewer_load)
    write_csv("interviewer_availability.csv", availability, [
        "availability_id", "interviewer_id", "available_slot", "slot_period",
    ])

    # Summary stats
    open_jobs = sum(1 for j in jobs if j["job_status"] == "Open")
    aparna_jobs = sum(1 for j in jobs if j["hiring_manager"] == "Aparna G.")
    future_slots = sum(1 for a in availability if a["slot_period"] == "future")

    print("\n--- Summary ---")
    print(f"Jobs: {len(jobs)} total | {open_jobs} open ({100*open_jobs/len(jobs):.0f}%) | {len(jobs)-open_jobs} closed")
    print(f"Aparna G. manages {aparna_jobs}/{len(jobs)} jobs ({100*aparna_jobs/len(jobs):.0f}%)")
    print(f"Candidates: {len(candidates)} | Applications: {len(applications)} | Feedback rows: {len(feedback)}")
    print(f"Availability slots: {len(availability)} | Future: {future_slots} ({100*future_slots/len(availability):.0f}%)")
    print(f"\nJoin keys:")
    print("  applications.job_id -> jobs.job_id")
    print("  applications.candidate_id -> candidates.candidate_id")
    print("  interview_feedback.application_id -> applications.application_id")
    print("  interview_feedback.stage_id -> interview_stages.stage_id")
    print("  interview_feedback.interviewer_id -> interviewer_pool.interviewer_id")
    print("  interviewer_availability.interviewer_id -> interviewer_pool.interviewer_id")
    print("  interview_stages.(job_type, role_level) -> jobs.(job_type, role_level)")


if __name__ == "__main__":
    main()
