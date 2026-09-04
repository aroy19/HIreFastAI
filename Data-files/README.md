# Hiring Mock Data — Multi-Agent Insight Workflows

Seven joinable CSV files for building sourcing, rejection, panel load, offer, and pipeline health agents.

## Files

| File | Rows | Description |
|------|------|-------------|
| `interview_stages.csv` | 138 | Master framework: stages per job type + role level |
| `jobs.csv` | 30 | Open and closed roles (70% open) |
| `candidates.csv` | 220 | Candidate profiles and sourcing channel |
| `applications.csv` | 352 | Links candidates to jobs |
| `interview_feedback.csv` | 931 | Per-stage decisions, reasons, interviewer |
| `interviewer_pool.csv` | 18 | Interviewers by job type |
| `interviewer_availability.csv` | 5074 | Past (10%) and future (90%) slots, 9am–5pm |

## Import to Google Sheets

1. Create a new Google Sheet.
2. **File → Import → Upload** each CSV as a separate tab (or use **File → Import → Upload** once per file).
3. Name tabs: `interview_stages`, `jobs`, `candidates`, `applications`, `interview_feedback`, `interviewer_pool`, `interviewer_availability`.

Regenerate anytime:

```bash
python3 generate_hiring_data.py
```

## Join Diagram

```
jobs ──────────────────────────────────────────────┐
  │ job_id                                           │
  ▼                                                  │
applications ◄── candidates.candidate_id             │
  │ application_id                                   │
  ▼                                                  │
interview_feedback                                   │
  │ stage_id ──────► interview_stages                │
  │ interviewer_id ► interviewer_pool ◄── jobs.job_type
  └────────────────► interviewer_availability
```

### SQL-style joins (examples)

```sql
-- Pipeline health: days in stage vs SLA
SELECT j.job_id, j.role_level, s.stage_name, s.expected_duration_days,
       f.date_of_interview, f.decision
FROM interview_feedback f
JOIN applications a ON f.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
JOIN interview_stages s ON f.stage_id = s.stage_id;

-- Sourcing quality: pass rate by channel and role
SELECT c.sourced_from, j.job_type, j.role_level,
       COUNT(*) AS interviews,
       SUM(CASE WHEN f.decision = 'Yes' THEN 1 ELSE 0 END) AS passes
FROM interview_feedback f
JOIN applications a ON f.application_id = a.application_id
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN jobs j ON a.job_id = j.job_id
GROUP BY 1, 2, 3;
```

## Embedded Patterns (for agent demos)

| Agent | Pattern baked into data |
|-------|------------------------|
| **Sourcing Quality** | LinkedIn ~18–35% pass rate for BE Staff/Principal; Referrals ~72%; GitHub strong for BE |
| **Rejection Pattern** | FE SWE2/SWE3/Staff: ~85% reject at System design with frontend architecture reasons |
| **Panel Load Balancer** | Sarah Chen (IV-001) overloaded; Mike Torres & Priya Sharma underutilized |
| **Offer Insights** | Staff/Principal/SWE3 roles: ~75% offer declines — comp, timing, competing offers |
| **Pipeline Health** | JOB-0001 BE Staff open 94 days; HM screen SLA breaches on stuck roles |

## Notes

- **90% of jobs** are owned by hiring manager **Aparna G.** (27 of 30).
- **70% of jobs are Open**; 30% Closed with historic hire data.
- `interview_feedback.interviewer_id` is included to power the Panel Load Balancer (join to `interviewer_pool`).
- `interviewer_availability.slot_period` is `past` or `future` (~91% future slots).
- Reference date for "today": **2026-08-23**.
