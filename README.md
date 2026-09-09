# CareCloud Voice AI Patient Registration

## Live Demo
- Phone: +1 XXX XXX XXXX (placeholder — fill after Vapi setup)
- API: https://YOUR-SERVICE.onrender.com (placeholder)
- Dashboard: https://YOUR-SERVICE.onrender.com/dashboard (placeholder)
- API Docs: https://YOUR-SERVICE.onrender.com/docs (placeholder)

## What This Is
Voice-based AI patient registration agent for a technical assessment.
Uses synthetic/demo data only. Not a production healthcare system.

## Architecture
```
Caller → Phone → Vapi (STT+LLM+TTS) → FastAPI REST API → Supabase PostgreSQL
```

**Data Flow:**
1. Caller dials the Vapi-provided US phone number
2. Vapi handles Speech-to-Text (STT), LLM processing, and Text-to-Speech (TTS)
3. The LLM (Groq) converses with the caller using the system prompt from `docs/voice-agent-prompt.md`
4. When all required fields are collected and confirmed, the LLM calls the `create_patient` tool
5. The tool POSTs to the FastAPI `/patients` endpoint
6. FastAPI validates, normalizes, and stores the patient in Supabase PostgreSQL
7. Dashboard at `/dashboard` displays all active patients via the same REST API

## Features
- **Voice Conversation**: Natural language patient intake via Vapi + Groq LLM
- **Server-Side Validation**: All data validated by FastAPI before persistence
- **Phone Normalization**: Accepts "(415) 555-1234", "+1 415 555 1234", "4155551234" → stores as "4155551234"
- **State Normalization**: Accepts "ca", "Ca", "CA" → stores as "CA"
- **Date Flexibility**: Accepts "MM/DD/YYYY" and "YYYY-MM-DD"
- **Soft Delete**: Patients marked with `deleted_at` timestamp, never hard-deleted
- **Search & Filter**: By last name, phone number, or date of birth
- **Dashboard**: Real-time patient table with view modal and delete confirmation
- **Response Envelope**: All API responses follow `{"data": ..., "error": null}` format
- **Comprehensive Tests**: 39 test cases covering all endpoints and validation rules

## Tech Stack

| Technology | Purpose | Reason |
|------------|---------|--------|
| Python 3.12 | Backend runtime | Mature, great ecosystem |
| FastAPI | Web framework | Fast, async, auto OpenAPI docs |
| SQLAlchemy 2.0 | ORM | Modern, type-safe database access |
| PostgreSQL (Supabase) | Database | Free tier, managed, persistent |
| Pydantic v2 | Validation | Fast, robust data validation |
| Vapi | Voice platform | STT + LLM + TTS + phone numbers |
| Groq | LLM inference | Free tier, fast llama-3.3-70b |
| Render | Hosting | Free tier, auto-deploy from GitHub |
| Tailwind CSS | Dashboard styling | CDN-based, no build step |
| pytest | Testing | Industry standard, async support |

## Project Structure
```
g:\Voice AI Agent\
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── patients.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── patient.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── patient_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── patient_repository.py
│   └── web/
│       ├── __init__.py
│       ├── dashboard.py
│       └── templates/
│           └── dashboard.html
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_patients.py
│   └── test_validation.py
│
├── docs/
│   ├── architecture.md
│   └── voice-agent-prompt.md
│
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── README.md
└── LICENSE
```

## Setup & Installation

### Windows PowerShell
```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/carecloud-voice-agent.git
cd carecloud-voice-agent

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your DATABASE_URL and other settings

# Run the development server
uvicorn app.main:app --reload
```

### Verify
- Health: `GET http://localhost:8000/health` → `{"data":{"status":"ok"},"error":null}`
- API Docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/dashboard`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (or sqlite for local) | `sqlite:///./demo.db` |
| `API_BASE_URL` | Base URL for the API (used by dashboard) | `http://localhost:8000` |
| `ENVIRONMENT` | `development` or `production` | `development` |

## API Endpoints

| Method | Path | Description | Success | Error |
|--------|------|-------------|---------|-------|
| GET | `/health` | Health check | 200 | - |
| POST | `/patients` | Create patient | 201 | 422 |
| GET | `/patients` | List patients (with optional filters) | 200 | - |
| GET | `/patients/{id}` | Get patient by ID | 200 | 404 |
| PUT | `/patients/{id}` | Partial update patient | 200 | 404, 422 |
| DELETE | `/patients/{id}` | Soft delete patient | 200 | 404 |

**Query Parameters for GET /patients:**
- `last_name` (optional) - case-insensitive partial match
- `date_of_birth` (optional) - exact match, format YYYY-MM-DD
- `phone_number` (optional) - exact match, 10 digits

## API Response Format

### Success
```json
{
  "data": { ... },
  "error": null
}
```

### Error
```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "body -> date_of_birth: Value error, Date of birth cannot be in the future"
  }
}
```

**Error Codes:** `VALIDATION_ERROR`, `PATIENT_NOT_FOUND`, `INTERNAL_ERROR`, `BAD_REQUEST`, `CONFLICT`

## Voice Agent
The voice agent is configured in Vapi with:
- **Model**: Groq `llama-3.3-70b-versatile`
- **System Prompt**: See `docs/voice-agent-prompt.md`
- **Tool**: `create_patient` — POSTs to `/patients` with all collected fields
- **Flow**: Collect required fields → Offer optional fields → Review → Confirm → Save

The LLM is probabilistic, so the API performs authoritative validation as a safety net.

## Validation Rules

| Field | Rules |
|-------|-------|
| `first_name`, `last_name` | 1-50 chars, letters/spaces/hyphens/apostrophes only |
| `date_of_birth` | Valid date, not in future, MM/DD/YYYY or YYYY-MM-DD |
| `sex` | One of: Male, Female, Other, Decline to Answer |
| `phone_number` | 10 digits after normalization (strips formatting, removes leading +1) |
| `email` | Valid email format (optional) |
| `address_line_1` | Non-empty, max 255 chars |
| `address_line_2` | Optional, max 255 chars |
| `city` | Non-empty, max 100 chars |
| `state` | Valid 2-letter US state/territory code (auto-uppercased) |
| `zip_code` | 5 digits or ZIP+4 (#####-####) |
| `insurance_provider` | Optional, max 255 chars |
| `insurance_member_id` | Optional, alphanumeric only |
| `preferred_language` | Optional, defaults to "English" |
| `emergency_contact_name` | Optional, max 255 chars |
| `emergency_contact_phone` | Optional, normalized to 10 digits |

## Testing
```powershell
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

## Deployment

### Render + Supabase (Free Tier, $0)

1. **Supabase**: Create project → Get connection string → Add `+psycopg` → Set as `DATABASE_URL`
2. **GitHub**: Push repo (ensure `.env` is not committed)
3. **Render**: New Web Service → Connect GitHub → Add `DATABASE_URL` and `API_BASE_URL` env vars
4. **Groq**: Get API key → Add to Vapi Provider Keys
5. **Vapi**: Add Groq key → Get free US number → Create Assistant with system prompt → Add `create_patient` tool → Assign to phone number

See `AGENT_PLAYBOOK.md` Phase 7 for detailed steps.

## Security
- No real patient data — synthetic/demo only
- All secrets via environment variables
- Server-side validation on every request
- HTTPS enforced in production (Render)
- No secrets committed to repository
- Soft delete preserves audit trail

## Known Limitations
- Render free tier sleeps after 15 min inactivity (30-60s cold start)
- Supabase free tier pauses after 7 days inactivity
- Vapi calls consume credits ($10 free on signup, ~200 min with BYOK Groq)
- Not a production HIPAA-compliant system
- Demo data only

## Next Steps (If More Time)
- Authentication/API keys for API access
- Rate limiting
- Appointment scheduling integration
- Multi-language support (Spanish, etc.)
- Call transcripts and analytics
- HIPAA compliance (BAA, encryption, audit logs)
- Patient matching/deduplication
- Webhook callbacks for real-time updates

## Test Data
Use this synthetic patient for voice testing:
- **Name**: Jane Doe
- **DOB**: March 5, 1990
- **Sex**: Female
- **Phone**: 415-555-1234
- **Address**: 100 Main Street, San Francisco, CA 94105

