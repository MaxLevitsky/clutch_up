# ClutchUp - Beginner-Friendly Competitive Gaming Platform

Version 1.0

## Project Overview

ClutchUp is a community-first competitive gaming platform designed for beginner and casual players. It combines rank-based tournaments, simple progression, and social play to help users enter competition without fear, improve over time, and stay engaged through teams and events.

## Features

### F001: Beginner Tournament Discovery and Registration
- Players can discover tournaments that match their rank and region
- Simple one-action registration flow
- Eligibility validation with clear error messages
- Tournament details display (timing, format, capacity)

### F002: Team Creation and Management
- Create teams with unique names and badges
- Generate shareable invite links for friends
- View team roster and pending invites
- Register teams for team tournaments with automatic roster lock

### F003: Player Progression and Badges
- Earn progression points through tournament participation
- Unlock badges and new tournament tiers
- Visible profile progression history

## Architecture

The project follows a strict **Frontend → Backend → Database** architecture:

```
Frontend (React/TypeScript) → HTTP → Backend (FastAPI) → Database (SQLite)
```

### Backend Structure (FastAPI)
```
backend/
├── app/
│   ├── models/          # SQLAlchemy models (Player, Tournament, Team, etc.)
│   ├── schemas/         # Pydantic schemas for API validation
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic layer
│   ├── api/            # FastAPI endpoints
│   ├── database.py     # Database configuration
│   └── main.py         # Application entry point
└── tests/              # Backend unit tests
```

### Frontend Structure (React/TypeScript)
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page-level components
│   ├── services/      # API clients
│   ├── hooks/         # Custom React hooks
│   ├── App.tsx        # Main application
│   └── main.tsx       # Entry point
└── public/            # Static assets
```

## Key Architectural Principles

1. **No Direct Database Access from Frontend**: All data operations go through the backend API
2. **Layered Backend**: API → Service → Repository → Model
3. **Business Logic in Backend**: All validation and business rules are enforced server-side
4. **Frontend as Orchestration**: UI components use hooks to call API clients
5. **Traceability**: Every file includes Feature/Scenario comments linking to PRD

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Quick Start

#### 1. Run Backend (in first terminal)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

#### 2. Run Frontend (in second terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Verify Installation

1. Open `http://localhost:5173` in your browser
2. Navigate to "Tournaments" page
3. You should see a list of tournaments

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### Running Tests

#### Backend Tests
```bash
cd backend
pytest
```

#### Frontend Tests
```bash
cd frontend
npm test
```

## API Endpoints

### Tournaments
- `GET /api/tournaments/eligible/{player_id}` - Get eligible tournaments for player
- `GET /api/tournaments/` - Get all tournaments
- `POST /api/tournaments/register` - Register player for tournament
- `GET /api/tournaments/validate-eligibility/{player_id}/{tournament_id}` - Validate eligibility

### Teams
- `POST /api/teams/` - Create a new team
- `POST /api/teams/invites` - Create team invite
- `POST /api/teams/invites/{token}/accept` - Accept invite
- `GET /api/teams/{team_id}/roster` - Get team roster
- `POST /api/teams/{team_id}/register-tournament/{tournament_id}` - Register team for tournament
- `DELETE /api/teams/invites/{token}/revoke` - Revoke invite

### Players
- `POST /api/players/` - Create new player
- `GET /api/players/{player_id}` - Get player by ID

## Requirements Coverage

### Functional Requirements (FR)
- FR-1: Show only eligible tournaments ✅
- FR-2: One-action tournament registration ✅
- FR-3: Registration confirmation with details ✅
- FR-4: Eligibility validation (rank, region, account) ✅
- FR-5: Clear error messages for ineligible players ✅
- FR-6: Create team with unique name ✅
- FR-7: Generate shareable invites ✅
- FR-8: Display roster status ✅
- FR-9: Validate team size for tournaments ✅
- FR-10: Lock roster at registration ✅
- FR-11: Award progression points ⏳ (Backend ready)
- FR-12: Display badges and progression ⏳ (Backend ready)

### Non-Functional Requirements (NFR)
- NFR-1: Tournament eligibility < 2s ✅ (Architecture supports)
- NFR-2: Responsive layouts ✅ (CSS responsive)
- NFR-3: Prevent duplicate registrations ✅ (Database constraint)
- NFR-4: Secure validation logic ✅ (Backend only)
- NFR-5: User-friendly error messages ✅
- NFR-6: Team creation < 3s ✅ (Architecture supports)
- NFR-7: Secure, revocable invite links ✅
- NFR-8: Roster lock consistency ✅
- NFR-9: Concurrent update safety ✅ (Database transactions)
- NFR-10: Reliable progression updates ⏳ (Backend ready)
- NFR-11: Fast profile data loading ✅

## Test Coverage

### Backend Tests (Unit)
- Tournament eligibility validation
- Rank mismatch detection
- Region mismatch detection
- Duplicate registration prevention
- Team creation with unique names
- Team invite acceptance
- Team tournament eligibility validation
- Roster size validation

### Test Cases Implemented
- TC-FR-001-01: Eligible player joins tournament ✅
- TC-FR-001-02: Eligible tournament list filtering ✅
- TC-FR-002-01: Ineligible rank rejection ✅
- TC-FR-002-02: Region mismatch rejection ✅
- TC-FR-002-03: Duplicate registration rejection ✅
- TC-FR-003-01: Team creation ✅
- TC-FR-003-02: Invite acceptance ✅
- TC-FR-003-03: Unique team name validation ✅
- TC-FR-004-01: Team tournament registration ✅
- TC-FR-004-02: Insufficient roster rejection ✅

## Database Schema

### Main Entities
- **Player**: User accounts with rank and region
- **Tournament**: Events with rank/region restrictions
- **Team**: Player groups with ownership
- **TournamentRegistration**: Player/team tournament entries
- **TeamMembership**: Player-team relationships
- **TeamInvite**: Invite links with expiration
- **Match**: Tournament matches
- **Badge**: Achievement badges
- **Progression**: Player progression tracking

## Future Enhancements
- Authentication and authorization
- Progression calculation service
- Badge award system
- Match result processing
- Notifications service
- Admin dashboard
- Payment integration
- Mobile native apps

## License
Proprietary

## Authors
- Maksim Levitskii

## Documentation
- `prd.json` - Product Requirements Document
- `SPEC ClutchUp project - Лист1.csv` - Detailed specification
- `ClutchUp_Test_Strategy_Strict_Template.md` - Test strategy
- `web_arch_prompt_FINAL.md` - Architecture guidelines
