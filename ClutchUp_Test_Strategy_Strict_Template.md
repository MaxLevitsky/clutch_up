**Test Strategy**

**ClutchUp**

| Project Name | ClutchUp |
| :---- | :---- |
| **Document Version** | 1.1 |
| **Specification Version** | 1.1 |
| **Author** | Maksim Levitskii |
| **Date** | April 4, 2026 |
| **Change Summary** | Added tournament creation tests (FR-13 to FR-16, NFR-12 to NFR-14) |

# **1\. Document Information**

The table above identifies the document owner, version, and specification baseline used by this strategy.

# **2\. Purpose**

This document defines the overall testing approach for ClutchUp. It explains what will be tested, which test levels will be used, how requirements will be covered, what will be automated, and which quality gates must be satisfied before release. The strategy is based on the current SPEC for the beginner-friendly competitive gaming platform, especially the core areas of beginner tournaments, teams, and progression.

# **3\. Scope**

## **3.1 In Scope**

* User onboarding required to reach tournament eligibility.
* Rank-based beginner tournament discovery and registration.
* **Tournament creation through web interface (NEW - v1.1).**
* Tournament eligibility validation for rank, region, and account status.
* Team creation, invite generation, invite acceptance, and roster management.
* **Team creation UI enhancement and end-to-end validation (NEW - v1.1).**
* Team tournament registration and roster lock behavior.
* Player progression, badges, and tournament-tier unlock logic.
* Player profile updates related to tournament history and progression visibility.
* Notifications triggered by tournament registration and progression updates.
* Core UI and API flows for the features listed above.
* **API integration testing for new creation endpoints (NEW - v1.1).**
* Performance, reliability, security, and monitoring checks for critical workflows.

## **3.2 Out of Scope**

* Payment flows, subscriptions, and sponsored tournament monetization.  
* Full anti-cheat engine internals beyond interface-level validation and basic abuse checks.  
* Native mobile applications if they are not part of the current release scope.  
* Third-party partner integrations beyond interfaces required for core platform operation.  
* Experimental recommendation, matchmaking optimization, or personalization features outside the current SPEC.

# **4\. System Overview**

ClutchUp is a web-based competitive gaming platform designed for beginner and casual players. The platform lowers the barrier to competitive play by providing rank-based beginner tournaments, simple progression, social team play, and visible recognition through badges and profile milestones. A user can onboard quickly, receive a rank, discover eligible tournaments, create or join a team, register for individual or team events, and earn progression after event completion.

# **5\. Requirements Overview**

**Functional Requirements (FR):** Functional requirements describe what the system must do. For ClutchUp, this includes tournament discovery and join flows, eligibility validation, team creation and invites, team tournament registration, progression and badge updates, and notifications related to key user actions.

**Non-Functional Requirements (NFR):** Non-functional requirements describe how well the system must perform, how secure it must be, and how reliable and observable it must remain. For ClutchUp, this includes latency targets, invite-link security, stability under concurrent tournament load, and production monitoring.

# **6\. Test Objectives**

* Verify that functional requirements are correctly implemented.  
* Validate critical player workflows for beginner tournaments, teams, and progression.  
* Ensure system behavior is stable under expected conditions and realistic concurrency.  
* Verify performance, reliability, and security constraints for core workflows.  
* Confirm that beginner-facing UX remains understandable and low-friction.  
* Provide confidence for safe changes, releases, and post-release monitoring.

# **7\. Test Levels and Test Types**

## **7.1 Unit Testing**

**Purpose:** Validate isolated business logic, calculations, transformations, validation rules, and edge cases.

**Typical Coverage:**

* Rank eligibility rules and region checks.
* Tournament registration validation.
* **Tournament creation business logic and validation (NEW - v1.1).**
* **Tournament parameter validation: capacity, start time, team size (NEW - v1.1).**
* Team roster validation and roster-lock rules.
* Progression point calculations and badge assignment logic.
* Invite token generation and validation.
* Error mapping and user-facing validation messages.

## **7.2 Integration Testing**

**Purpose:** Validate interaction between components, services, databases, and APIs.

**Typical Coverage:**

* UI/API to tournament service integration.
* **Tournament creation API endpoint validation and response schema (NEW - v1.1).**
* **Created tournament immediate visibility in tournament lists (NEW - v1.1).**
* Service and repository interaction for teams and invites.
* Serialization and deserialization of tournament and team payloads.
* Progression updates after match-result processing.
* Notification dispatch after tournament join or progression event.
* Profile updates after tournament completion.

## **7.3 End-to-End Testing**

**Purpose:** Validate critical user workflows from the user perspective.

**Typical Coverage:**

* Onboarding to first eligible tournament join.
* Ineligible player blocked from joining the wrong tournament.
* **Tournament creation flow from UI form to database persistence and immediate visibility (NEW - v1.1).**
* Team creation and friend invite acceptance.
* **Team creation UI validation and end-to-end workflow verification (NEW - v1.1).**
* Team joins a team tournament and roster is locked.
* Tournament completion leads to visible progression update.
* Badge visibility in profile after reward processing.

## **7.4 Non-Functional Testing**

**Purpose:** Validate system qualities beyond functional correctness.

**Typical Coverage:** 

* Performance testing.  
* Load testing.  
* Security testing.  
* Reliability and resilience testing.  
* Usability evaluation.  
* Availability monitoring.

# **8\. Requirement-to-Test-Level Mapping**

| Requirement ID | Requirement Summary | Unit | Integration | E2E | Performance | Security | Monitoring |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| FR-001 | User can join an eligible beginner tournament | Yes | Yes | Yes | No | No | Yes |
| FR-002 | System blocks ineligible tournament registration | Yes | Yes | Yes | No | Yes | Yes |
| FR-003 | User can create a team and invite friends | Yes | Yes | Yes | No | Yes | Yes |
| FR-004 | Eligible team can join a team tournament | Yes | Yes | Yes | No | No | Yes |
| FR-005 | Tournament completion updates progression and badges | Yes | Yes | Yes | No | No | Yes |
| FR-006 | Notifications are sent for registration and progression events | No | Yes | Yes | No | No | Yes |
| **FR-013** | **Create tournament with valid parameters (NEW - v1.1)** | **Yes** | **Yes** | **Yes** | **No** | **No** | **Yes** |
| **FR-014** | **Validate tournament parameters (capacity, start time) (NEW - v1.1)** | **Yes** | **Yes** | **Yes** | **No** | **Yes** | **Yes** |
| **FR-015** | **Initialize tournament status as UPCOMING (NEW - v1.1)** | **Yes** | **Yes** | **Yes** | **No** | **No** | **Yes** |
| **FR-016** | **Validate team size requirement for team tournaments (NEW - v1.1)** | **Yes** | **Yes** | **Yes** | **No** | **No** | **Yes** |
| NFR-001 | Tournament eligibility and join flow meet latency targets | No | Yes | Yes | Yes | No | Yes |
| NFR-002 | Team invite links are secure and resistant to abuse | Yes | Yes | No | No | Yes | Yes |
| NFR-003 | Platform remains stable under expected concurrent tournament load | No | Yes | No | Yes | No | Yes |
| NFR-004 | Core workflows remain observable in production | No | No | No | No | No | Yes |
| **NFR-012** | **Tournament creation completes within 2 seconds (NEW - v1.1)** | **No** | **Yes** | **Yes** | **Yes** | **No** | **Yes** |
| **NFR-013** | **Validation errors return 400 with clear messages (NEW - v1.1)** | **No** | **Yes** | **Yes** | **No** | **No** | **Yes** |
| **NFR-014** | **Created tournament immediately visible in lists (NEW - v1.1)** | **No** | **Yes** | **Yes** | **No** | **No** | **Yes** |

# **9\. Test Priorities**

| Priority | Meaning |
| :---- | :---- |
| High | Critical for business value, fairness, safety, or a core workflow. |
| Medium | Important but not release-blocking. |
| Low | Useful but not critical. |

Priorities are assigned according to impact on the core competitive loop and user trust. Tournament join, eligibility validation, team registration, and progression updates are High priority because they directly define the product promise. Notifications and secondary profile behavior are Medium priority. Cosmetic-only behavior and non-critical UI polish are Low priority unless they block usability.

# **10\. Test Environment**

Tests will run in the following environments:

* Local developer environment.  
* CI pipeline.  
* Test environment / staging.  
* Production monitoring.

Environment configuration includes:

* Relational database with realistic tournament, player, and team data.  
* Background job processing for notifications and progression.  
* Mocked external services where full integration is unnecessary or unstable.  
* Desktop browsers: Chrome, Firefox, and Edge.  
* Responsive testing for major mobile viewport sizes in web UI.

# **11\. Test Data Strategy**

Testing will use representative data sets that cover both expected and problematic behavior:

* Valid beginner player accounts.
* Valid and invalid ranks.
* Allowed and disallowed regions.
* Teams with valid and invalid roster sizes.
* Valid inputs, invalid inputs, and empty inputs.
* Boundary values for rank tiers, invite expiry, and tournament capacity.
* **Boundary values for tournament capacity (8-64 players) and team size (2-5 players) (NEW - v1.1).**
* **Valid and invalid tournament start times (future vs past) (NEW - v1.1).**
* Duplicate registration attempts.
* Expired, malformed, and tampered invite links.
* Large tournament datasets for performance scenarios.
* Security-related malicious inputs such as forged requests and invalid payloads.
* Performance datasets with concurrent registration attempts.
* **Tournament creation payloads with missing or invalid required fields (NEW - v1.1).**

# **12\. Automation Strategy**

The project will prioritize automation of:

* Unit tests for core business logic and validation rules.  
* Integration tests for tournament registration, team flows, notifications, and progression updates.  
* A focused set of end-to-end tests for business-critical user journeys.  
* Selected performance smoke checks for tournament join and team registration.  
* Monitoring-based validation for production-critical failure paths.

Manual testing will remain for:

* Exploratory testing.  
* Beginner usability review.  
* Visual checks and responsive review.  
* Rare edge scenarios not worth automating yet.  
* Cross-browser exploratory testing beyond the critical matrix.

# **13\. Entry and Exit Criteria**

## **13.1 Entry Criteria**

* Requirements are available and reviewed.  
* Test environment is ready.  
* Build is deployable.  
* Database schema and seed data are available.  
* Required services are accessible.  
* Test accounts and roles are prepared.

## **13.2 Exit Criteria**

* All critical test cases executed.  
* No open critical defects.  
* Required automated tests pass.  
* Performance thresholds met.  
* Security blockers resolved.  
* Core monitoring and alerting enabled for release.

# **14\. Quality Gates**

* All unit tests pass.  
* All critical integration tests pass.  
* Critical end-to-end scenarios pass.  
* No critical security findings remain open.  
* Performance thresholds are within limits.  
* Production monitoring is configured for tournament registration, team registration, progression failures, and notification failures.

# **15\. Risks and Limitations**

* Some external integrations are mocked in lower environments.  
* Performance testing is limited to staging capacity and may not perfectly represent production.  
* UI testing does not cover every browser/device combination.  
* Some non-functional checks rely on monitoring after release.  
* Low player-pool volume in pre-production may hide match-density issues.  
* Anti-cheat validation is only partially covered by this strategy.

# **16\. Deliverables**

* Requirements list with IDs.  
* Test strategy.  
* Test cases.  
* Traceability matrix.  
* Automated test implementation.  
* Test execution results.  
* Defect reports.  
* Release quality summary.

# **Requirements List**

| Requirement ID | Requirement Summary |
| :---- | :---- |
| FR-001 | The system must allow a user to join a beginner tournament if the user satisfies all eligibility rules. |
| FR-002 | The system must block users from joining tournaments for which they are not eligible. |
| FR-003 | The system must allow a user to create a team and invite friends. |
| FR-004 | The system must allow an eligible team to register for a team tournament. |
| FR-005 | The system must update player progression, badges, and unlocked tiers after tournament completion. |
| FR-006 | The system must notify users about successful tournament registration and progression updates. |
| **FR-013** | **The system must allow tournament organizers to create tournaments with valid parameters (NEW - v1.1).** |
| **FR-014** | **The system must validate tournament capacity (8-64) and start time (future only) (NEW - v1.1).** |
| **FR-015** | **The system must initialize newly created tournaments with status UPCOMING and registered_count 0 (NEW - v1.1).** |
| **FR-016** | **The system must require team_size (2-5) for team tournaments and prohibit it for solo tournaments (NEW - v1.1).** |
| NFR-001 | Tournament eligibility and join actions must meet defined latency targets. |
| NFR-002 | Team invite links must be secure, revocable, and resistant to tampering. |
| NFR-003 | Core tournament and team workflows must remain stable under expected concurrent load. |
| NFR-004 | Core workflows must be observable through logs, metrics, and alerts. |
| **NFR-012** | **Tournament creation API response must complete within 2 seconds (NEW - v1.1).** |
| **NFR-013** | **Tournament creation validation errors must return HTTP 400 with clear error messages (NEW - v1.1).** |
| **NFR-014** | **Created tournaments must be immediately visible in tournament lists (NEW - v1.1).** |

# **Test Cases**

### **TC-FR-001-01 — Eligible beginner player joins beginner tournament**

**Requirement ID:** FR-001

**Title:** Eligible beginner player joins beginner tournament

**Type:** Functional

**Level:** E2E

**Priority:** High

**Preconditions:** User is onboarded, authenticated, and has a beginner rank. An eligible tournament exists and is open for registration.

**Test Data:** Beginner-ranked player account; eligible tournament in the same region with available capacity.

**Steps:** Log in as the eligible beginner player.

1. Open the tournaments page.  
2. Select an eligible beginner tournament.  
3. Click Join.

**Expected Result:** The user is successfully registered and sees confirmation, tournament timing, and event details.

**Automation Status:** Automated

**Automation ID:** AT-FR-001-E2E-01

**Notes:** Core release-blocking flow.

### **TC-FR-001-02 — Eligible tournament list shows only available beginner events**

**Requirement ID:** FR-001

**Title:** Eligible tournament list shows only available beginner events

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** Tournament service is populated with mixed eligible and ineligible tournaments.

**Test Data:** Player with beginner rank; tournament dataset containing multiple ranks, regions, and capacity states.

**Steps:** Request tournament list for the beginner player.

4. Inspect the returned list.

**Expected Result:** Only tournaments that match eligibility rules and are open for registration are returned.

**Automation Status:** Automated

**Automation ID:** AT-FR-001-INT-02

### **TC-FR-001-03 — Tournament registration closes when capacity is reached**

**Requirement ID:** FR-001

**Title:** Tournament registration closes when capacity is reached

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** Tournament is one slot away from full capacity.

**Test Data:** Two eligible users attempting to join the last available slot.

**Steps:** Submit registration for user A.

5. Submit registration for user B immediately after or concurrently.

**Expected Result:** Only one user receives successful registration. The other receives a clear capacity-related message.

**Automation Status:** Planned

**Automation ID:** AT-FR-001-INT-03

### **TC-FR-002-01 — Ineligible player cannot join higher-rank tournament**

**Requirement ID:** FR-002

**Title:** Ineligible player cannot join higher-rank tournament

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** Eligibility rules are configured and tournament service is available.

**Test Data:** Beginner-ranked player; advanced tournament.

**Steps:** Send a join request for a tournament above the player’s allowed rank.

6. Validate the service response and persistence state.

**Expected Result:** Registration is rejected with a clear reason and no bracket entry is created.

**Automation Status:** Automated

**Automation ID:** AT-FR-002-INT-01

**Notes:** Also verify error response structure.

### **TC-FR-002-02 — Player from unsupported region is blocked from registration**

**Requirement ID:** FR-002

**Title:** Player from unsupported region is blocked from registration

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** Tournament has a region restriction.

**Test Data:** Eligible rank but unsupported region.

**Steps:** Attempt to join a tournament from an unsupported region.

**Expected Result:** The system blocks registration and shows a region-related eligibility message.

**Automation Status:** Automated

**Automation ID:** AT-FR-002-INT-02

### **TC-FR-002-03 — Duplicate registration attempt is rejected**

**Requirement ID:** FR-002

**Title:** Duplicate registration attempt is rejected

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** User is already registered in the tournament.

**Test Data:** Existing tournament registration for the same user.

**Steps:** Attempt to join the same tournament again.

**Expected Result:** The system prevents duplicate registration and returns a friendly duplicate message.

**Automation Status:** Automated

**Automation ID:** AT-FR-002-INT-03

### **TC-FR-003-01 — User creates a team and sends invite**

**Requirement ID:** FR-003

**Title:** User creates a team and sends invite

**Type:** Functional

**Level:** E2E

**Priority:** High

**Preconditions:** Authenticated player account with access to team features.

**Test Data:** Team name, badge, invite recipient.

**Steps:** Open the team hub.

7. Create a new team.  
8. Generate an invite link.  
9. Send the invite link.

**Expected Result:** The team is created and an invite is generated and visible in roster management.

**Automation Status:** Automated

**Automation ID:** AT-FR-003-E2E-01

**Notes:** Validate owner role assignment.

### **TC-FR-003-02 — Invited friend joins team successfully**

**Requirement ID:** FR-003

**Title:** Invited friend joins team successfully

**Type:** Functional

**Level:** E2E

**Priority:** High

**Preconditions:** A valid team invite link exists.

**Test Data:** Invited user account; active team invite.

**Steps:** Open the invite link as the invited user.

10. Accept the invite.

**Expected Result:** The invited user becomes part of the team roster and invite status changes to accepted.

**Automation Status:** Automated

**Automation ID:** AT-FR-003-E2E-02

### **TC-FR-003-03 — Team name must be unique according to system rules**

**Requirement ID:** FR-003

**Title:** Team name must be unique according to system rules

**Type:** Functional

**Level:** Unit

**Priority:** Medium

**Preconditions:** Name validation rules are available.

**Test Data:** Existing team name and duplicate proposed name.

**Steps:** Run team-creation validation with a duplicate team name.

**Expected Result:** Validation fails according to naming rules and prevents team creation.

**Automation Status:** Automated

**Automation ID:** AT-FR-003-UNIT-03

### **TC-FR-004-01 — Eligible team joins team tournament**

**Requirement ID:** FR-004

**Title:** Eligible team joins team tournament

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** Team exists, required members are eligible, and team tournament is open.

**Test Data:** Valid team roster and team tournament.

**Steps:** Submit team tournament registration.

11. Validate team size and eligibility.  
12. Confirm registration.

**Expected Result:** The team is registered and the roster is locked according to event rules.

**Automation Status:** Automated

**Automation ID:** AT-FR-004-INT-01

**Notes:** Check roster-lock state transition.

### **TC-FR-004-02 — Team with insufficient roster cannot join tournament**

**Requirement ID:** FR-004

**Title:** Team with insufficient roster cannot join tournament

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** Tournament requires more members than the team currently has.

**Test Data:** Incomplete team roster.

**Steps:** Attempt team tournament registration with an incomplete roster.

**Expected Result:** Registration is rejected and the user sees the missing-roster requirement.

**Automation Status:** Automated

**Automation ID:** AT-FR-004-INT-02

### **TC-FR-004-03 — Roster cannot be changed after lock is applied**

**Requirement ID:** FR-004

**Title:** Roster cannot be changed after lock is applied

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** Team is already registered and roster lock is active.

**Test Data:** Registered team; pending roster update action.

**Steps:** Attempt to remove or add a player after roster lock.

**Expected Result:** The system blocks the change according to lock rules and preserves event roster consistency.

**Automation Status:** Planned

**Automation ID:** AT-FR-004-INT-03

### **TC-FR-005-01 — Tournament completion updates progression**

**Requirement ID:** FR-005

**Title:** Tournament completion updates progression

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** Tournament results are finalized and progression rules are configured.

**Test Data:** Player participation and result dataset.

**Steps:** Process tournament results.

13. Trigger progression update.  
14. Read the updated player profile.

**Expected Result:** Points, badges, and unlocked tier state are updated correctly.

**Automation Status:** Automated

**Automation ID:** AT-FR-005-INT-01

**Notes:** Include repeatability and idempotency checks.

### **TC-FR-005-02 — Badge is visible in player profile after award**

**Requirement ID:** FR-005

**Title:** Badge is visible in player profile after award

**Type:** Functional

**Level:** E2E

**Priority:** Medium

**Preconditions:** Player has just earned a badge through tournament progression.

**Test Data:** Player with a newly awarded badge.

**Steps:** Open the player profile after progression update.

**Expected Result:** The new badge appears in the profile with correct label and history state.

**Automation Status:** Automated

**Automation ID:** AT-FR-005-E2E-02

### **TC-FR-005-03 — Progression is not applied twice for the same result set**

**Requirement ID:** FR-005

**Title:** Progression is not applied twice for the same result set

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Progression processor supports idempotent execution.

**Test Data:** Same finalized result set submitted twice.

**Steps:** Run progression update once.

15. Run progression update again with the same result set.

**Expected Result:** The second execution does not duplicate points, badges, or unlocks.

**Automation Status:** Automated

**Automation ID:** AT-FR-005-UNIT-03

### **TC-FR-006-01 — Registration notification is sent after successful tournament join**

**Requirement ID:** FR-006

**Title:** Registration notification is sent after successful tournament join

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** Notification service is connected or mocked.

**Test Data:** Successful tournament registration event.

**Steps:** Register the user to a tournament.

16. Observe the notification event.

**Expected Result:** The user receives a registration confirmation notification with correct event details.

**Automation Status:** Automated

**Automation ID:** AT-FR-006-INT-01

### **TC-FR-006-02 — Progression notification is sent after reward update**

**Requirement ID:** FR-006

**Title:** Progression notification is sent after reward update

**Type:** Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** Progression update completes successfully.

**Test Data:** Player with a progression event that awards points or a badge.

**Steps:** Finalize tournament results.

17. Observe generated notification payload.

**Expected Result:** The user receives a progression update notification with accurate reward information.

**Automation Status:** Planned

**Automation ID:** AT-FR-006-INT-02

### **TC-NFR-001-01 — Tournament join latency meets threshold under expected load**

**Requirement ID:** NFR-001

**Title:** Tournament join latency meets threshold under expected load

**Type:** Non-Functional

**Level:** Performance

**Priority:** High

**Preconditions:** Staging environment is available with representative infrastructure.

**Test Data:** At least 200 valid join attempts under expected concurrency.

**Steps:** Execute join requests under expected concurrency.

18. Measure latency distribution and error rate.

**Expected Result:** p95 response time stays within the agreed threshold and error rate stays below the allowed limit.

**Automation Status:** Planned

**Automation ID:** AT-NFR-001-PERF-01

### **TC-NFR-001-02 — Tournament list endpoint remains responsive for large dataset**

**Requirement ID:** NFR-001

**Title:** Tournament list endpoint remains responsive for large dataset

**Type:** Non-Functional

**Level:** Performance

**Priority:** Medium

**Preconditions:** Tournament service contains a large realistic dataset.

**Test Data:** Large list of tournaments across multiple ranks and regions.

**Steps:** Request tournament list repeatedly under realistic read load.

19. Measure response time and payload stability.

**Expected Result:** The endpoint remains within target latency and returns stable filtered results.

**Automation Status:** Planned

**Automation ID:** AT-NFR-001-PERF-02

### **TC-NFR-002-01 — Invite links reject tampered tokens**

**Requirement ID:** NFR-002

**Title:** Invite links reject tampered tokens

**Type:** Non-Functional

**Level:** Security

**Priority:** High

**Preconditions:** Invite generation is enabled.

**Test Data:** Valid invite link and modified invite token.

**Steps:** Create a valid invite.

20. Tamper with the token.  
21. Attempt invite acceptance.

**Expected Result:** The system rejects the request safely and records a security-relevant event.

**Automation Status:** Planned

**Automation ID:** AT-NFR-002-SEC-01

**Notes:** No sensitive details should be exposed in the response.

### **TC-NFR-002-02 — Revoked invite link cannot be used**

**Requirement ID:** NFR-002

**Title:** Revoked invite link cannot be used

**Type:** Non-Functional

**Level:** Security

**Priority:** Medium

**Preconditions:** Team owner can revoke invite links.

**Test Data:** Invite link revoked before acceptance.

**Steps:** Create invite.

22. Revoke invite.  
23. Attempt acceptance using the revoked link.

**Expected Result:** The revoked link is rejected and cannot add the user to the team.

**Automation Status:** Planned

**Automation ID:** AT-NFR-002-SEC-02

### **TC-NFR-003-01 — Team registration remains stable under expected tournament load**

**Requirement ID:** NFR-003

**Title:** Team registration remains stable under expected tournament load

**Type:** Non-Functional

**Level:** Performance

**Priority:** Medium

**Preconditions:** Staging environment has realistic team and tournament data.

**Test Data:** Concurrent team registration requests.

**Steps:** Submit concurrent team registration requests.

24. Measure failure rate and consistency.

**Expected Result:** The system remains stable and no duplicate or corrupted registrations are created.

**Automation Status:** Planned

**Automation ID:** AT-NFR-003-PERF-01

**Notes:** Focus on concurrency safety.

### **TC-NFR-003-02 — Progression processing recovers from transient worker failure**

**Requirement ID:** NFR-003

**Title:** Progression processing recovers from transient worker failure

**Type:** Non-Functional

**Level:** Reliability

**Priority:** Medium

**Preconditions:** Background job processing is enabled.

**Test Data:** Progression event with injected transient worker failure.

**Steps:** Trigger progression event.

25. Interrupt worker once.  
26. Allow retry logic to execute.

**Expected Result:** The event is eventually processed once and profile state remains correct.

**Automation Status:** Planned

**Automation ID:** AT-NFR-003-REL-02

### **TC-NFR-004-01 — Failed tournament registration is observable in monitoring**

**Requirement ID:** NFR-004

**Title:** Failed tournament registration is observable in monitoring

**Type:** Non-Functional

**Level:** Monitoring

**Priority:** Medium

**Preconditions:** Monitoring and alerting are configured in staging or production-like environment.

**Test Data:** Forced registration failure.

**Steps:** Trigger a controlled registration failure.

27. Verify logs, metrics, and alerting signal.

**Expected Result:** The failure is observable with actionable context for support and engineering.

**Automation Status:** Planned

**Automation ID:** AT-NFR-004-MON-01

### **TC-FR-013-01 — Create tournament with valid parameters (NEW - v1.1)**

**Requirement ID:** FR-013

**Title:** Create tournament with valid parameters

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament repository is available and tournament service is initialized.

**Test Data:** Valid tournament creation parameters (name, rank_tier, region, capacity, format, future start_time, is_team_tournament=False).

**Steps:** Call service.create_tournament() with valid parameters.

**Expected Result:** Tournament is created with status UPCOMING, registered_count 0, and all fields correctly populated.

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_success

### **TC-FR-013-02 — Create tournament via API endpoint (NEW - v1.1)**

**Requirement ID:** FR-013

**Title:** Create tournament via API endpoint

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** API server is running with test database.

**Test Data:** Valid HTTP POST request payload with all required tournament fields.

**Steps:** POST /api/tournaments/ with valid JSON payload.

**Expected Result:** Response returns 201 Created with tournament data including status UPCOMING and registered_count 0.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_success

### **TC-FR-014-01 — Reject tournament with invalid capacity (NEW - v1.1)**

**Requirement ID:** FR-014

**Title:** Reject tournament with invalid capacity

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament service is initialized.

**Test Data:** Tournament parameters with capacity=4 (below minimum of 8).

**Steps:** Call service.create_tournament() with capacity < 8.

**Expected Result:** Returns error status with message "Capacity must be between 8 and 64".

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_invalid_capacity

### **TC-FR-014-02 — Reject tournament with past start time (NEW - v1.1)**

**Requirement ID:** FR-014

**Title:** Reject tournament with past start time

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament service is initialized.

**Test Data:** Tournament parameters with start_time in the past.

**Steps:** Call service.create_tournament() with start_time < current time.

**Expected Result:** Returns error status with message "Start time must be in the future".

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_past_start_time

### **TC-FR-014-03 — API returns 400 for invalid capacity (NEW - v1.1)**

**Requirement ID:** FR-014

**Title:** API returns 400 for invalid capacity

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** API server is running with test database.

**Test Data:** HTTP POST payload with capacity=100 (exceeds maximum of 64).

**Steps:** POST /api/tournaments/ with invalid capacity.

**Expected Result:** Response returns 400 Bad Request with clear error message.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_invalid_capacity

### **TC-FR-014-04 — API returns 400 for past start time (NEW - v1.1)**

**Requirement ID:** FR-014

**Title:** API returns 400 for past start time

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** API server is running with test database.

**Test Data:** HTTP POST payload with past start_time.

**Steps:** POST /api/tournaments/ with past start_time.

**Expected Result:** Response returns 400 Bad Request with clear error message.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_past_start_time

### **TC-FR-015-01 — New tournament has UPCOMING status (NEW - v1.1)**

**Requirement ID:** FR-015

**Title:** New tournament has UPCOMING status

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament service is initialized.

**Test Data:** Valid tournament creation parameters.

**Steps:** Call service.create_tournament() and inspect returned tournament object.

**Expected Result:** Tournament status is TournamentStatus.UPCOMING and registered_count is 0.

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_initial_status

### **TC-FR-016-01 — Team tournament requires team_size (NEW - v1.1)**

**Requirement ID:** FR-016

**Title:** Team tournament requires team_size

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament service is initialized.

**Test Data:** Tournament parameters with is_team_tournament=True and team_size=None.

**Steps:** Call service.create_tournament() with missing team_size for team tournament.

**Expected Result:** Returns error status with message "Team tournaments must specify team_size".

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_team_missing_size

### **TC-FR-016-02 — Solo tournament prohibits team_size (NEW - v1.1)**

**Requirement ID:** FR-016

**Title:** Solo tournament prohibits team_size

**Type:** Functional

**Level:** Unit

**Priority:** High

**Preconditions:** Tournament service is initialized.

**Test Data:** Tournament parameters with is_team_tournament=False and team_size=3.

**Steps:** Call service.create_tournament() with team_size for solo tournament.

**Expected Result:** Returns error status with message "Solo tournaments must not specify team_size".

**Automation Status:** Not Started

**Automation ID:** test_create_tournament_solo_with_team_size

### **TC-FR-016-03 — API validates team_size requirement (NEW - v1.1)**

**Requirement ID:** FR-016

**Title:** API validates team_size requirement

**Type:** Functional

**Level:** Integration

**Priority:** High

**Preconditions:** API server is running with test database.

**Test Data:** HTTP POST payload with is_team_tournament=True and missing team_size.

**Steps:** POST /api/tournaments/ with invalid team_size configuration.

**Expected Result:** Response returns 400 Bad Request with clear error message.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_team_size_validation

### **TC-NFR-012-01 — Tournament creation completes within 2 seconds (NEW - v1.1)**

**Requirement ID:** NFR-012

**Title:** Tournament creation completes within 2 seconds

**Type:** Non-Functional

**Level:** Performance

**Priority:** Medium

**Preconditions:** API server running in test environment.

**Test Data:** Valid tournament creation request.

**Steps:** POST /api/tournaments/ and measure response time.

**Expected Result:** Response completes in < 2000ms with successful creation.

**Automation Status:** Planned

**Automation ID:** test_api_create_tournament_performance

### **TC-NFR-013-01 — Validation errors return clear messages (NEW - v1.1)**

**Requirement ID:** NFR-013

**Title:** Validation errors return clear messages

**Type:** Non-Functional

**Level:** Integration

**Priority:** Medium

**Preconditions:** API server running with test database.

**Test Data:** Multiple invalid tournament creation requests (invalid capacity, past time, missing fields).

**Steps:** POST /api/tournaments/ with each invalid payload and inspect error messages.

**Expected Result:** All validation errors return HTTP 400 with clear, actionable error messages.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_validation_messages

### **TC-NFR-014-01 — Created tournament immediately visible (NEW - v1.1)**

**Requirement ID:** NFR-014

**Title:** Created tournament immediately visible

**Type:** Non-Functional

**Level:** Integration

**Priority:** High

**Preconditions:** API server running with test database.

**Test Data:** Valid tournament creation request.

**Steps:** POST /api/tournaments/ to create tournament, then GET /api/tournaments/ to list all tournaments.

**Expected Result:** Newly created tournament appears in the list response immediately.

**Automation Status:** Not Started

**Automation ID:** test_api_create_tournament_immediate_visibility

**Notes:** Alert fatigue should be avoided.

### **TC-NFR-004-02 — Notification delivery failure is visible in logs and metrics**

**Requirement ID:** NFR-004

**Title:** Notification delivery failure is visible in logs and metrics

**Type:** Non-Functional

**Level:** Monitoring

**Priority:** Low

**Preconditions:** Notification worker and monitoring are enabled.

**Test Data:** Injected downstream notification failure.

**Steps:** Trigger notification event.

28. Force the notification send to fail.  
29. Inspect monitoring outputs.

**Expected Result:** Failure is recorded in logs and metrics with enough detail to diagnose the issue.

**Automation Status:** Planned

**Automation ID:** AT-NFR-004-MON-02

# **Traceability Matrix**

| Requirement ID | Requirement Summary | Test Case ID | Test Level | Automation ID | Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-001 | The system must allow a user to join a beginner tournament if the user satisfies all eligibility rules | TC-FR-001-01 | E2E | AT-FR-001-E2E-01 | Automated |
| FR-001 | The system must allow a user to join a beginner tournament if the user satisfies all eligibility rules | TC-FR-001-02 | Integration | AT-FR-001-INT-02 | Automated |
| FR-001 | The system must allow a user to join a beginner tournament if the user satisfies all eligibility rules | TC-FR-001-03 | Integration | AT-FR-001-INT-03 | Planned |
| FR-002 | The system must block users from joining tournaments for which they are not eligible | TC-FR-002-01 | Integration | AT-FR-002-INT-01 | Automated |
| FR-002 | The system must block users from joining tournaments for which they are not eligible | TC-FR-002-02 | Integration | AT-FR-002-INT-02 | Automated |
| FR-002 | The system must block users from joining tournaments for which they are not eligible | TC-FR-002-03 | Integration | AT-FR-002-INT-03 | Automated |
| FR-003 | The system must allow a user to create a team and invite friends | TC-FR-003-01 | E2E | AT-FR-003-E2E-01 | Automated |
| FR-003 | The system must allow a user to create a team and invite friends | TC-FR-003-02 | E2E | AT-FR-003-E2E-02 | Automated |
| FR-003 | The system must allow a user to create a team and invite friends | TC-FR-003-03 | Unit | AT-FR-003-UNIT-03 | Automated |
| FR-004 | The system must allow an eligible team to register for a team tournament | TC-FR-004-01 | Integration | AT-FR-004-INT-01 | Automated |
| FR-004 | The system must allow an eligible team to register for a team tournament | TC-FR-004-02 | Integration | AT-FR-004-INT-02 | Automated |
| FR-004 | The system must allow an eligible team to register for a team tournament | TC-FR-004-03 | Integration | AT-FR-004-INT-03 | Planned |
| FR-005 | The system must update player progression, badges, and unlocked tiers after tournament completion | TC-FR-005-01 | Integration | AT-FR-005-INT-01 | Automated |
| FR-005 | The system must update player progression, badges, and unlocked tiers after tournament completion | TC-FR-005-02 | E2E | AT-FR-005-E2E-02 | Automated |
| FR-005 | The system must update player progression, badges, and unlocked tiers after tournament completion | TC-FR-005-03 | Unit | AT-FR-005-UNIT-03 | Automated |
| FR-006 | The system must notify users about successful tournament registration and progression updates | TC-FR-006-01 | Integration | AT-FR-006-INT-01 | Automated |
| FR-006 | The system must notify users about successful tournament registration and progression updates | TC-FR-006-02 | Integration | AT-FR-006-INT-02 | Planned |
| NFR-001 | Tournament eligibility and join actions must meet defined latency targets | TC-NFR-001-01 | Performance | AT-NFR-001-PERF-01 | Planned |
| NFR-001 | Tournament eligibility and join actions must meet defined latency targets | TC-NFR-001-02 | Performance | AT-NFR-001-PERF-02 | Planned |
| NFR-002 | Team invite links must be secure, revocable, and resistant to tampering | TC-NFR-002-01 | Security | AT-NFR-002-SEC-01 | Planned |
| NFR-002 | Team invite links must be secure, revocable, and resistant to tampering | TC-NFR-002-02 | Security | AT-NFR-002-SEC-02 | Planned |
| NFR-003 | Core tournament and team workflows must remain stable under expected concurrent load | TC-NFR-003-01 | Performance | AT-NFR-003-PERF-01 | Planned |
| NFR-003 | Core tournament and team workflows must remain stable under expected concurrent load | TC-NFR-003-02 | Reliability | AT-NFR-003-REL-02 | Planned |
| NFR-004 | Core workflows must be observable through logs, metrics, and alerts | TC-NFR-004-01 | Monitoring | AT-NFR-004-MON-01 | Planned |
| NFR-004 | Core workflows must be observable through logs, metrics, and alerts | TC-NFR-004-02 | Monitoring | AT-NFR-004-MON-02 | Planned |
| **FR-013** | **The system must allow tournament organizers to create tournaments with valid parameters (NEW - v1.1)** | **TC-FR-013-01** | **Unit** | **test_create_tournament_success** | **Not Started** |
| **FR-013** | **The system must allow tournament organizers to create tournaments with valid parameters (NEW - v1.1)** | **TC-FR-013-02** | **Integration** | **test_api_create_tournament_success** | **Not Started** |
| **FR-014** | **The system must validate tournament capacity (8-64) and start time (future only) (NEW - v1.1)** | **TC-FR-014-01** | **Unit** | **test_create_tournament_invalid_capacity** | **Not Started** |
| **FR-014** | **The system must validate tournament capacity (8-64) and start time (future only) (NEW - v1.1)** | **TC-FR-014-02** | **Unit** | **test_create_tournament_past_start_time** | **Not Started** |
| **FR-014** | **The system must validate tournament capacity (8-64) and start time (future only) (NEW - v1.1)** | **TC-FR-014-03** | **Integration** | **test_api_create_tournament_invalid_capacity** | **Not Started** |
| **FR-014** | **The system must validate tournament capacity (8-64) and start time (future only) (NEW - v1.1)** | **TC-FR-014-04** | **Integration** | **test_api_create_tournament_past_start_time** | **Not Started** |
| **FR-015** | **The system must initialize newly created tournaments with status UPCOMING and registered_count 0 (NEW - v1.1)** | **TC-FR-015-01** | **Unit** | **test_create_tournament_initial_status** | **Not Started** |
| **FR-016** | **The system must require team_size (2-5) for team tournaments and prohibit it for solo tournaments (NEW - v1.1)** | **TC-FR-016-01** | **Unit** | **test_create_tournament_team_missing_size** | **Not Started** |
| **FR-016** | **The system must require team_size (2-5) for team tournaments and prohibit it for solo tournaments (NEW - v1.1)** | **TC-FR-016-02** | **Unit** | **test_create_tournament_solo_with_team_size** | **Not Started** |
| **FR-016** | **The system must require team_size (2-5) for team tournaments and prohibit it for solo tournaments (NEW - v1.1)** | **TC-FR-016-03** | **Integration** | **test_api_create_tournament_team_size_validation** | **Not Started** |
| **NFR-012** | **Tournament creation API response must complete within 2 seconds (NEW - v1.1)** | **TC-NFR-012-01** | **Performance** | **test_api_create_tournament_performance** | **Planned** |
| **NFR-013** | **Tournament creation validation errors must return HTTP 400 with clear error messages (NEW - v1.1)** | **TC-NFR-013-01** | **Integration** | **test_api_create_tournament_validation_messages** | **Not Started** |
| **NFR-014** | **Created tournaments must be immediately visible in tournament lists (NEW - v1.1)** | **TC-NFR-014-01** | **Integration** | **test_api_create_tournament_immediate_visibility** | **Not Started** |

