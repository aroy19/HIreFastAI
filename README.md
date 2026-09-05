# HireFast AI

**Use the Github Repo** to access all files

 [https://github.com/aroy19/HIreFastAI](https://github.com/aroy19/HIreFastAI)

HireFast AI is an AI-powered hiring intelligence system for Engineering Managers and Talent teams. It turns scattered pipeline data—roles, candidates, interviews, and interviewer load—into **grounded, scored recommendations** you can act on in minutes.

Ask a question in chat. An orchestrator routes it to the right specialist agents. Each agent returns the same contract: **recommendation, evidence, confidence, cost, and a cheaper alternative**. An Evaluation Agent scores every insight before it is logged and shown on the dashboard.

**Stack:** n8n Cloud · OpenAI · Pinecone · Google Drive / Sheets · Looker Studio

---

## How it works

1. Load live hiring CSVs from Google Drive.
2. Route the question to one primary agent (and up to two secondary).
3. Ground answers in historic hiring knowledge via RAG (Pinecone).
4. Evaluate insights against a golden dataset (actionability, grounding, hallucination risk).
5. Append results to Google Sheets and surface them in Looker Studio.

**Five insight agents**


| Agent                   | Answers                                           |
| ----------------------- | ------------------------------------------------- |
| **Sourcing Quality**    | Which channels convert best by role type?         |
| **Rejection Pattern**   | Where and why candidates fail interview stages    |
| **Panel Load Balancer** | Who is overloaded vs. underused on the panel      |
| **Offer Insights**      | Why offers are declined; acceptance rate by level |
| **Pipeline Health**     | Stale roles, SLA breaches, funnel bottlenecks     |


---

## Files in this repo

```
HIreFastAI/
├── README.md                          ← this file
├── Artifacts/
│   ├── Final - Hiring-Insights-Multi-Agent-Architecture.md
│   ├── HireFast AI-Press-Release-and-FAQ.md
│   └── HireFast Multi-Agent.json
└── Data-files/
    ├── README.md
    ├── generate_hiring_data.py
    ├── interview_stages.csv
    ├── jobs.csv
    ├── candidates.csv
    ├── applications.csv
    ├── interview_feedback.csv
    ├── interviewer_pool.csv
    └── interviewer_availability.csv
```

### `Artifacts/`


| File                                                                                                                     | What it is                                                                         |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [Final - Hiring-Insights-Multi-Agent-Architecture.md](Artifacts/Final%20-%20Hiring-Insights-Multi-Agent-Architecture.md) | Strategy and technical architecture: agents, data flow, eval gate, cost, dashboard |
| [HireFast AI-Press-Release-and-FAQ.md](Artifacts/HireFast%20AI-Press-Release-and-FAQ.md)                                 | Product overview, FAQ, value, privacy, and operating cost                          |
| [HireFast Multi-Agent.json](Artifacts/HireFast%20Multi-Agent.json)                                                       | Export of the n8n multi-agent workflow (import into n8n)                           |


### `Data-files/`

Synthetic hiring dataset used by the agents. Schema and join diagram: [Data-files/README.md](Data-files/README.md). Regenerate with `python3 Data-files/generate_hiring_data.py`.


| File                           | Rows (excl. header) | Contents                                                   |
| ------------------------------ | ------------------- | ---------------------------------------------------------- |
| `interview_stages.csv`         | 138                 | Stages, SLA days, and grading rubric by job type and level |
| `jobs.csv`                     | 30                  | Open and closed roles, hiring manager, days open, location |
| `candidates.csv`               | 220                 | Candidate profiles and sourcing channel                    |
| `applications.csv`             | 337                 | Links candidates to jobs                                   |
| `interview_feedback.csv`       | 875                 | Stage decisions, rejection reasons, interviewer            |
| `interviewer_pool.csv`         | 18                  | Interviewer roster by job type                             |
| `interviewer_availability.csv` | 4,930               | Past and future interview slots                            |


Reference date for “today” in the mock data: **2026-08-23**.

---

## Google Drive — input and output files

Operational data, eval fixtures, and run logs live in Google Drive / Sheets. The n8n workflow reads inputs from Drive and appends outputs to a spreadsheet that Looker Studio uses as its source.

**Source folder (inputs):** [HireFast hiring data](https://drive.google.com/drive/folders/1op-OsDrVPmx61-ke_sy0SJCcC63l4x5z)

**Output workbook:** [Output file](https://docs.google.com/spreadsheets/d/1loADiQ_MfcfeyEiI7p75QwOKfYacWV2dPhDwo7cp_2U/edit?usp=drivesdk)

**Historic RAG file:** [hiring knowledge (Drive file)](https://drive.google.com/file/d/1ln6OrT9iTfjgDfrIfa3Fk3gogkaDWMDw/view?usp=sharing)

### Input files

Loaded on each routed chat run from the source folder (all CSVs except `golden_dataset.csv`).


| File                                                 | Role                                                       | Used by                                                        |
| ---------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------- |
| `jobs.csv`                                           | Open/closed roles, days open, hiring manager               | Pipeline Health, Offer Insights                                |
| `candidates.csv`                                     | Profiles and sourcing channel                              | Sourcing Quality                                               |
| `applications.csv`                                   | Candidate ↔ job links                                      | All agents                                                     |
| `interview_feedback.csv`                             | Stage decisions and reasons                                | Rejection Pattern, Panel Load, Offer Insights, Pipeline Health |
| `interview_stages.csv`                               | Stage order and SLA days                                   | Pipeline Health, Rejection Pattern                             |
| `interviewer_pool.csv`                               | Interviewer roster                                         | Panel Load Balancer                                            |
| `interviewer_availability.csv`                       | Slot capacity (past / future)                              | Panel Load Balancer                                            |
| `golden_dataset.csv`                                 | Eval fixtures (same folder; **not** fed to insight agents) | Evaluation Agent (24h cache)                                   |
| Historic knowledge file (`hiring_rag_knowledge.csv`) | Aggregated historical patterns                             | One-time Pinecone ingest; query-time RAG for all five agents   |


`Data-files/` in this repo is the checked-in copy of the seven operational CSVs. Keep Drive in sync when you regenerate the mock data.

### Output files

Each routed run appends rows to the **Output file** spreadsheet. Looker Studio reads both tabs, joined on `execution_id`.


| Destination                                                                                                          | Tab             | Written by                              | What gets logged                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------- | --------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Output file](https://docs.google.com/spreadsheets/d/1loADiQ_MfcfeyEiI7p75QwOKfYacWV2dPhDwo7cp_2U/edit?usp=drivesdk) | **Insights**    | Format Rows → Append to Sheet           | One row per specialist agent: recommendation, evidence, confidence, cost (tokens / model / USD), alternative, agent-specific payload               |
| Same spreadsheet                                                                                                     | **Evaluations** | Format Eval Rows → Append Eval to Sheet | One row per scored agent: PASS / PARTIAL / FAIL, quality gate (RELEASE / RELEASE_WITH_FLAGS / BLOCK), actionability, grounding, hallucination risk |


Dashboard: Looker Studio connected to this sheet (Google sign-in with sheet access; no API key).