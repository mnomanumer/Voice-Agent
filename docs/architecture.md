# System Architecture

## Architecture Diagram

```
┌─────────┐     ┌─────────────┐     ┌────────────────────────┐     ┌──────────────────┐
│ Caller  │────▶│ US Phone    │────▶│ Vapi (STT + LLM + TTS) │────▶│ FastAPI REST API │
└─────────┘     │ Number      │     │                        │     │                  │
                └─────────────┘     │ - Deepgram STT         │     │ - Validation     │
                                    │ - Groq LLM (llama-3.3) │     │ - Normalization  │
                                    │ - TTS Voice            │     │ - Persistence    │
                                    │ - create_patient tool  │     └────────┬─────────┘
                                    └────────────────────────┘              │
                                                                           ▼
                                    ┌─────────────────────────────────────────────┐
                                    │ Supabase PostgreSQL                          │
                                    │ - patients table (soft delete)              │
                                    │ - Indexes: last_name, dob, phone_number     │
                                    └─────────────────────────────────────────────┘
                                                                           ▲
                                    ┌─────────────────────────────────────────────┐
                                    │ Dashboard (HTML + Vanilla JS)               │
                                    │ - Fetches /patients via REST API            │
                                    │ - Search, View, Delete                      │
                                    │ - Tailwind CSS via CDN                      │
                                    └─────────────────────────────────────────────┘
```

## Component Descriptions

### 1. Voice Layer (Vapi)
- **Provider**: Vapi.ai
- **STT**: Deepgram Nova-2
- **LLM**: Groq `llama-3.3-70b-versatile` (BYOK)
- **TTS**: Vapi default voices
- **Phone**: Free US number from Vapi
- **Function Calling**: `create_patient` tool calls FastAPI `/patients`

### 2. API Layer (FastAPI)
- **Framework**: FastAPI 0.115
- **Validation**: Pydantic v2 models with field validators
- **Database**: SQLAlchemy 2.0 async ORM
- **Response Format**: Envelope `{"data": ..., "error": null}`
- **Error Handling**: Centralized exception handlers
- **Documentation**: Auto-generated OpenAPI at `/docs`

### 3. Data Layer (Supabase PostgreSQL)
- **Database**: PostgreSQL 15+ (Supabase free tier)
- **ORM**: SQLAlchemy with declarative models
- **Connection**: psycopg3 driver
- **Migrations**: Auto-create on startup (dev), manual for prod

### 4. Dashboard (Server-Rendered HTML)
- **Template**: Jinja2
- **Frontend**: Vanilla JavaScript + Tailwind CSS (CDN)
- **Data Fetching**: Client-side `fetch()` to REST API
- **No Build Step**: Single self-contained HTML file

## Data Flow Explanation

### Voice Call Flow
1. Caller dials Vapi phone number
2. Vapi answers, plays first message: "Hi, thanks for calling! What's your first name?"
3. LLM (Groq) processes speech → text → intent
4. LLM asks for missing required fields one at a time
5. When all required fields collected, LLM offers optional fields
6. LLM reads back all collected data, asks "Is all of that correct?"
7. On explicit confirmation ("yes"), LLM calls `create_patient` tool
8. Tool POSTs JSON to FastAPI `/patients`
9. FastAPI validates, normalizes, inserts into PostgreSQL
10. FastAPI returns created patient with `patient_id`
11. LLM informs caller: "Registration completed!" and ends call

### API Request Flow
1. Client (Vapi tool / Dashboard JS / curl) sends HTTP request
2. FastAPI routes to endpoint
3. Pydantic validates request body/query params
4. On validation error: returns 422 with error envelope
5. Service layer calls repository
6. Repository executes SQLAlchemy query
7. Database returns result
8. Service maps to Pydantic response model
9. FastAPI returns 200/201 with data envelope

### Dashboard Flow
1. Browser loads `/dashboard` (Jinja2 template)
2. On page load, JavaScript fetches `GET /patients`
3. Response data populates HTML table
4. User searches → JS fetches with query params
5. User clicks View → JS fetches `GET /patients/{id}` → shows modal
6. User clicks Delete → confirmation modal → `DELETE /patients/{id}` → refresh

## Technology Choice Rationale

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Native async, auto OpenAPI, type hints, fast |
| **Pydantic v2** | 10x faster than v1, robust validation, generic models |
| **SQLAlchemy 2.0** | Modern async ORM, type-safe, no session management issues |
| **Supabase** | Managed PostgreSQL, free tier, no credit card, instant setup |
| **Vapi** | Purpose-built for voice agents, handles STT/LLM/TTS/phone |
| **Groq** | Free tier, llama-3.3-70b, sub-second latency |
| **Render** | Free tier, auto-deploy from GitHub, custom domains |
| **Tailwind CDN** | No build step, utility-first, professional look |
| **Vanilla JS** | Zero dependencies, runs everywhere, simple |

## Why Validation is Duplicated (LLM + API)

| Layer | Purpose |
|-------|---------|
| **LLM (Vapi)** | Conversational validation — guides user naturally, handles "I meant..." corrections, asks clarifying questions |
| **API (FastAPI)** | Authoritative validation — enforces schema, normalizes data, prevents bad data at rest, security boundary |

The LLM is probabilistic and can hallucinate. The API is deterministic and is the source of truth.

## Why Soft Delete

1. **Audit Trail**: Preserves registration history for compliance/demo
2. **Recovery**: Accidental deletes can be recovered by clearing `deleted_at`
3. **Referential Integrity**: Future features (appointments, calls) can reference patients
4. **Simple Implementation**: Single `deleted_at` timestamp, filtered by default

## Why Confirmation Before Save

1. **User Trust**: Caller hears their data read back, catches errors
2. **Legal**: Explicit consent for data collection
3. **Quality**: Reduces duplicate/incorrect records
4. **Voice UX**: Natural conversation pattern ("Let me read that back...")

## Data Model

### Patient Table
| Column | Type | Constraints |
|--------|------|-------------|
| patient_id | UUID | PK, default gen_random_uuid() |
| first_name | VARCHAR(50) | NOT NULL |
| last_name | VARCHAR(50) | NOT NULL |
| date_of_birth | DATE | NOT NULL |
| sex | VARCHAR(20) | NOT NULL, enum |
| phone_number | VARCHAR(10) | NOT NULL, 10 digits |
| email | VARCHAR(255) | NULL |
| address_line_1 | VARCHAR(255) | NOT NULL |
| address_line_2 | VARCHAR(255) | NULL |
| city | VARCHAR(100) | NOT NULL |
| state | VARCHAR(2) | NOT NULL, US state code |
| zip_code | VARCHAR(10) | NOT NULL, 5 or 9 digits |
| insurance_provider | VARCHAR(255) | NULL |
| insurance_member_id | VARCHAR(100) | NULL |
| preferred_language | VARCHAR(100) | DEFAULT 'English' |
| emergency_contact_name | VARCHAR(255) | NULL |
| emergency_contact_phone | VARCHAR(10) | NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now(), onupdate |
| deleted_at | TIMESTAMPTZ | NULL |

### Indexes
- `ix_patients_last_name` — for search by last name
- `ix_patients_date_of_birth` — for DOB filtering
- `ix_patients_phone_number` — for phone lookup