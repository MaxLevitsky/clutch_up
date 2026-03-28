# Instruction for the AI Agent: Code Generation by Architecture (Web App — Final Combined Version)

You are an AI agent that generates production-ready code for a **web-based competitive gaming platform (ClutchUp)**.

This document combines:
- strict architectural rules
- detailed implementation guidance
- PRD-driven development
- full traceability
- testing discipline

---

# 1. Architectural Principle

Frontend (Web UI) → HTTP → Backend → DB

## Rules

- Frontend NEVER connects to DB
- Backend ALWAYS owns business logic
- Frontend = UI + orchestration
- Backend = source of truth

---

# 2. PRD — Source of Truth

All development MUST be based on `prd.json`.

AI MUST:
- validate PRD
- extend if incomplete
- use PRD as single source of truth

Includes:
- features
- BDD scenarios
- business rules
- test cases

---

# 3. Development Process (STRICT)

1. PRD validation
2. Identify layers
3. Gap analysis
4. Backend implementation
5. Backend tests
6. Frontend implementation
7. Frontend tests

---

# 4. Gap Analysis (MANDATORY)

| Scenario | Model | Repo | Service | API | FE API | Hook | Component | BE Test | FE Test |
|----------|------|------|--------|-----|--------|------|-----------|--------|--------|
| SC001    | ?    | ?    | ?      | ?   | ?      | ?    | ?         | ?      | ?      |

---

# 5. Backend Architecture (FastAPI)

Layers:
API → Service → Repository → Model

## Entities
- Player
- Tournament
- Team
- Match
- Badge
- Progression

## Rules
- no layer skipping
- all logic in service layer
- validation must be backend

---

# 6. Frontend Architecture

Structure:
- pages/
- components/
- features/{FeatureID}
- services/api
- hooks

Flow:
UI → Hook → API → Backend → Response → UI

## Rules
- no business logic in UI
- no direct fetch in components
- API calls only via clients

---

# 7. Feature Implementation Order

Backend first:
1. Model
2. Schema
3. Repository
4. Service
5. API
6. Backend tests

Then frontend:
7. API client
8. Hook
9. Component
10. UI states
11. Frontend tests

---

# 8. Testing Strategy

## Backend
- business logic validation
- DB correctness
- API correctness

## Frontend
- UI rendering
- interaction flows
- API call correctness

---

# 9. Traceability (MANDATORY)

Every file must include:

Feature: F001  
Scenario: SC001  

---

# 10. ClutchUp Domain Rules

- rank eligibility → backend only
- tournament join validation → backend
- progression → backend
- teams → backend integrity

---

# 11. Checklist

- PRD complete
- backend implemented first
- frontend uses API only
- tests exist
- traceability present
- no logic in UI
- tests pass

---

# 12. Output Expectations

AI MUST:
1. Update PRD
2. Perform gap analysis
3. Generate backend
4. Generate frontend
5. Generate tests

AI MUST NOT:
- skip layers
- ignore PRD
- skip tests
- break architecture
