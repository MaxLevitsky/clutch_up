# ClutchUp Internal Dashboard - Implementation Specification

**Product:** ClutchUp - Beginner-Friendly Competitive Gaming Platform
**Dashboard Type:** Internal Control & Observability Layer
**Target Implementation:** Streamlit
**Version:** 1.0
**Date:** 2026-04-04

---

## 1. Feature Context

| Section | Fill In |
|---------|---------|
| **Feature** | Internal Operations Dashboard |
| **Description (Goal / Scope)** | Unified internal control layer providing real-time visibility into system health, product health, unit economics, and cost observability. Enables product owners, engineers, and operations teams to monitor platform health, track key product metrics, detect anomalies, and control operational costs. **Based on current repository structure:** ClutchUp v1.0 with tournament/team/player systems, FastAPI backend, React frontend, SQLite database. |
| **Client** | Internal stakeholders: Product owners, engineering team, operations team, business analysts |
| **Problem** | Lack of unified visibility into: (1) system uptime and errors, (2) user onboarding and retention funnels, (3) tournament/team creation and engagement patterns, (4) infrastructure costs and resource utilization. **Current state:** No telemetry, logging, or monitoring infrastructure exists in the repository. |
| **Solution** | Streamlit-based dashboard with four unified views: System Health (uptime, latency, error rates), Product Health (onboarding funnel, retention, North Star metric), AI Quality (not applicable - no AI in current product), Unit Economics / Cost Observability (database size, API throughput, infrastructure proxy metrics). Dashboard supports time filtering, segment filtering, release comparison, and anomaly alerting. |
| **Metrics** | Dashboard uptime >99%, data freshness <5 minutes, query response time <3 seconds, coverage of 100% critical product events, alert response time <1 minute |

---

## 2. User Stories and Use Cases

### User Story 1
**Role:** Engineering Team / DevOps

| Field | Fill In |
|-------|---------|
| **User Story ID** | US-DASH-1 |
| **User Story** | As an engineer, I want to monitor system health (uptime, latency, error rates, throughput) in real-time, so that I can detect and respond to production incidents quickly. |
| **UX / User Flow** | Open dashboard → navigate to System Health tab → view uptime status, API latency graphs, error rate charts, throughput metrics → filter by time range → drill down into specific API endpoints → view error logs → set up alert thresholds |

#### Use Case (+ Edges) BDD 1

| Field | Fill In |
|-------|---------|
| **Use Case ID** | UC-DASH-1.1 |
| **Given** | The backend FastAPI server is running and logging requests/responses; database is operational; dashboard Streamlit app is deployed and connected to backend database |
| **When** | Engineer opens System Health tab and views real-time metrics for the last 24 hours |
| **Then** | Dashboard displays: API uptime % (based on health check pings), P50/P95/P99 latency for all endpoints, error rate % by endpoint, requests per minute (throughput), active database connections, background job queue length (if applicable) |
| **Input** | Time range filter (last 1h, 24h, 7d, 30d), endpoint filter (all, /api/tournaments, /api/teams, /api/players) |
| **Output** | Line charts for latency/throughput over time, gauge for uptime %, error log table (timestamp, endpoint, status_code, error_message), alert indicators (red/yellow/green status) |
| **State** | Dashboard fetches metrics from: (1) structured logs stored in SQLite `system_logs` table (Missing - requires new instrumentation), (2) application-level metrics from FastAPI middleware (Missing), (3) database connection pool stats (Derivable from SQLAlchemy) |

**Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| FR-DASH-1 | The dashboard SHALL display API endpoint uptime % based on health check pings recorded every 1 minute |
| FR-DASH-2 | The dashboard SHALL display P50, P95, P99 latency for all API endpoints (/api/tournaments, /api/teams, /api/players, /api/tournaments/register) based on request duration logs |
| FR-DASH-3 | The dashboard SHALL display error rate % by endpoint, calculated as (error responses / total responses) * 100 |
| FR-DASH-4 | The dashboard SHALL support time range filtering: last 1 hour, 24 hours, 7 days, 30 days |
| FR-DASH-5 | The dashboard SHALL display recent error logs (last 100 errors) with timestamp, endpoint, status code, error message, player_id (if available) |

**Non-Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| NFR-DASH-1 | System Health metrics SHALL refresh every 60 seconds automatically |
| NFR-DASH-2 | Dashboard queries SHALL complete in <3 seconds for 95% of requests |
| NFR-DASH-3 | Dashboard SHALL handle up to 10 concurrent internal users without performance degradation |

#### Use Case (+ Edges) BDD 2

| Field | Fill In |
|-------|---------|
| **Use Case ID** | UC-DASH-1.2 |
| **Given** | Error rate for /api/tournaments/register endpoint exceeds 5% threshold |
| **When** | Engineer views System Health tab and error rate chart shows spike |
| **Then** | Dashboard displays alert banner (red), error rate chart highlights spike period, error log table shows recent failures with details (tournament_id, player_id, error_message: "Tournament full", "Rank mismatch", etc.) |
| **Input** | No user input required (automatic alert detection based on threshold rules) |
| **Output** | Alert banner with message "ALERT: /api/tournaments/register error rate is 12% (threshold: 5%)", clickable drill-down to filtered error logs |
| **State** | Alert rule stored in dashboard configuration; alert history logged to `dashboard_alerts` table (Missing) |

**Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| FR-DASH-6 | The dashboard SHALL display alert banners when error rate exceeds configurable thresholds (default: 5% for any endpoint) |
| FR-DASH-7 | The dashboard SHALL support drill-down from alert banner to filtered error logs for affected endpoint and time range |

**Non-Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| NFR-DASH-4 | Alert detection logic SHALL evaluate every 60 seconds and update UI within 5 seconds of threshold breach |
| NFR-DASH-5 | Alert configuration SHALL be editable via dashboard UI or config file without code changes |

---

### User Story 2
**Role:** Product Owner / Product Manager

| Field | Fill In |
|-------|---------|
| **User Story ID** | US-DASH-2 |
| **User Story** | As a product owner, I want to monitor product health (onboarding funnel, activation, retention, churn, North Star metric) in real-time, so that I can measure product-market fit and make data-driven decisions. |
| **UX / User Flow** | Open dashboard → navigate to Product Health tab → view onboarding funnel (account creation → first tournament join → first match completion), retention cohorts (7-day, 30-day), North Star metric (tournaments per active user), key user actions (tournament registrations, team creations) → filter by time range, cohort, region → compare releases/versions → export data |

#### Use Case BDD 1

| Field | Fill In |
|-------|---------|
| **Use Case ID** | UC-DASH-2.1 |
| **Given** | Product events are instrumented and logged to `product_events` table (Missing); players, tournaments, teams data exists in database |
| **When** | Product owner opens Product Health tab and views metrics for last 30 days |
| **Then** | Dashboard displays: Onboarding funnel (total accounts created → % completed onboarding → % joined first tournament → % completed first match), Activation rate (% of users who joined first tournament within 7 days), 7-day retention (% of D0 users who returned on D7), 30-day retention, Churn rate, North Star metric (tournaments per active user), Team creation rate (% of users who created a team within 30 days), Top 5 most popular tournaments (by registration count) |
| **Input** | Time range filter (last 7d, 30d, 90d), region filter (NA, EU, ALL), rank filter (BEGINNER, INTERMEDIATE, ADVANCED, EXPERT, ALL) |
| **Output** | Funnel chart (Sankey diagram), retention cohort table, line charts for trends, KPI cards with current values and % change vs previous period |
| **State** | Metrics derived from: (1) `players` table (account creation timestamps), (2) `tournament_registrations` table (first tournament join), (3) `product_events` table for match completion (Missing), (4) daily aggregated metrics stored in `product_metrics_daily` table (Missing) |

**Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| FR-DASH-8 | The dashboard SHALL display onboarding funnel with stages: (1) Account created, (2) First tournament joined, (3) First match completed (proxy: first tournament with status=COMPLETED) |
| FR-DASH-9 | The dashboard SHALL calculate and display activation rate as % of users who joined first tournament within 7 days of account creation |
| FR-DASH-10 | The dashboard SHALL calculate and display 7-day retention as % of users created on day D who have activity (tournament join or match) on day D+7 |
| FR-DASH-11 | The dashboard SHALL calculate and display 30-day retention as % of users created on day D who have activity on day D+30 |
| FR-DASH-12 | The dashboard SHALL calculate and display North Star metric as average number of tournaments joined per active user (active = had activity in last 30 days) |
| FR-DASH-13 | The dashboard SHALL support filtering by time range (last 7/30/90 days), region (NA/EU/ALL), and rank tier (BEGINNER/INTERMEDIATE/ADVANCED/EXPERT/ALL) |

**Non-Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| NFR-DASH-6 | Product Health metrics SHALL refresh every 5 minutes (acceptable latency for business metrics) |
| NFR-DASH-7 | Retention cohort calculations SHALL use pre-aggregated daily tables to ensure query performance <3 seconds |

#### Use Case (+ Edges) BDD 2

| Field | Fill In |
|-------|---------|
| **Use Case ID** | UC-DASH-2.2 |
| **Given** | Multiple app versions or releases are deployed (tracked via `app_version` field in product_events table - Missing); release comparison feature is enabled |
| **When** | Product owner selects "Compare Releases" mode and selects two versions (e.g., v1.0 vs v1.1) |
| **Then** | Dashboard displays side-by-side comparison: Onboarding funnel completion rates, Activation rates, Retention rates, North Star metric, with % difference highlighted (green for improvement, red for regression) |
| **Input** | Version selector (dropdown), comparison mode toggle |
| **Output** | Comparison table with metrics for each version and delta %, visual indicators for improvement/regression |
| **State** | Metrics filtered by `app_version` field in product_events and derived tables |

**Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| FR-DASH-14 | The dashboard SHALL support release comparison mode where two app versions can be selected for side-by-side metric comparison |
| FR-DASH-15 | The dashboard SHALL highlight metric deltas with color coding (green: >5% improvement, red: >5% regression, gray: <5% change) |

**Non-Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| NFR-DASH-8 | Release comparison queries SHALL complete in <5 seconds even for 90-day time ranges |
| NFR-DASH-9 | Dashboard SHALL support at least 10 historical app versions for comparison |

---

### User Story 3
**Role:** Operations / Business Analyst

| Field | Fill In |
|-------|---------|
| **User Story ID** | US-DASH-3 |
| **User Story** | As an operations team member, I want to monitor unit economics and cost observability (database size, API request volume, infrastructure proxy metrics) in real-time, so that I can optimize resource usage and forecast costs. |
| **UX / User Flow** | Open dashboard → navigate to Unit Economics tab → view database size growth, API request volume trends, cost per active user (proxy), expensive flows (API endpoints with highest latency/volume), resource utilization trends → filter by time range → set up cost alert thresholds → export data for forecasting |

#### Use Case (+ Edges) BDD 1

| Field | Fill In |
|-------|---------|
| **Use Case ID** | UC-DASH-3.1 |
| **Given** | Infrastructure metrics are collected: database size (from SQLite file size or query), API request counts (from system logs), active user counts (from product metrics) |
| **When** | Operations team member opens Unit Economics tab and views metrics for last 30 days |
| **Then** | Dashboard displays: Database size (MB) trend over time, Total API requests per day, Requests per active user per day, Top 5 most-called API endpoints (by volume), Top 5 slowest API endpoints (by P95 latency), Database growth rate (MB per day), Estimated monthly database size (linear projection) |
| **Input** | Time range filter (last 7d, 30d, 90d) |
| **Output** | Line charts for database size and request volume trends, table of top endpoints with volume and latency stats, projection chart for database growth |
| **State** | Metrics derived from: (1) Database file size (Derivable - SQLite file size check), (2) `system_logs` table request counts (Missing), (3) `product_metrics_daily` table for active users (Missing) |

**Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| FR-DASH-16 | The dashboard SHALL display database size (MB) as a line chart showing growth over selected time range |
| FR-DASH-17 | The dashboard SHALL display total API requests per day as a line chart |
| FR-DASH-18 | The dashboard SHALL calculate and display requests per active user per day as (total requests / active users) |
| FR-DASH-19 | The dashboard SHALL display top 5 API endpoints by request volume with counts and % of total |
| FR-DASH-20 | The dashboard SHALL display top 5 API endpoints by P95 latency with values in milliseconds |
| FR-DASH-21 | The dashboard SHALL calculate and display database growth rate (MB per day) based on linear regression over last 30 days |

**Non-Functional Requirements**

| Req ID | Requirement |
|--------|-------------|
| NFR-DASH-10 | Database size checks SHALL not block production database operations (use separate read connection) |
| NFR-DASH-11 | Unit Economics metrics SHALL refresh every 10 minutes (lower frequency acceptable for cost metrics) |

---

## 3. Architecture / Solution

### 3.1 Client Side

| Area | Fill In |
|------|---------|
| **Client Type** | Streamlit web application (Python-based, internal-only deployment) |
| **User Entry Points** | Single URL: `http://internal-dashboard.clutchup.local:8501/` (or localhost during development). Login: Basic HTTP auth (username/password) - no OAuth required for v1.0 internal tool. |
| **Main Screens / Commands** | (1) **System Health Tab**: Uptime, latency, error rates, throughput, error logs, alerts. (2) **Product Health Tab**: Onboarding funnel, activation, retention, churn, North Star metric, top tournaments. (3) **Unit Economics Tab**: Database size, API volume, cost proxies, expensive flows. (4) **Settings Tab**: Alert thresholds, metric refresh intervals, export data. Navigation via Streamlit sidebar with tab selection. |
| **Input / Output Format** | **Inputs:** Time range selector (dropdown: 1h/24h/7d/30d/90d), endpoint filter (multiselect: all endpoints or specific), region filter (dropdown: NA/EU/ALL), rank filter (dropdown: BEGINNER/.../ALL), version comparison selectors (dropdown). **Outputs:** Charts (line, bar, Sankey funnel, gauge), KPI cards (metric value + trend), tables (error logs, top endpoints), alert banners (colored status messages), CSV export buttons. |

### 3.2 Backend Services

| Area | Fill In |
|------|---------|
| **Service Name** | DashboardDataService (new Python module) |
| **Responsibility** | Aggregate and serve dashboard metrics from backend database and logs. Expose Python functions consumed directly by Streamlit app. No REST API required (Streamlit and backend run in same environment). Responsibilities: (1) Query system_logs table for API metrics, (2) Query product_events table for product metrics, (3) Query players/tournaments/teams tables for funnel and engagement metrics, (4) Calculate aggregated metrics (retention cohorts, North Star), (5) Evaluate alert rules and return alert status. |
| **Business Logic** | *System Health:* Calculate uptime % = (successful health checks / total health checks) * 100. Calculate error rate % per endpoint = (5xx + 4xx responses / total responses) * 100. Calculate P50/P95/P99 latency from request duration logs using numpy.percentile. *Product Health:* Calculate activation rate = (users with first tournament join within 7 days / total users created in period) * 100. Calculate 7-day retention = (users with activity on D+7 / users created on D) * 100. Calculate North Star = total tournaments joined in period / active users in period. *Unit Economics:* Database size = os.path.getsize(clutchup.db) / (1024*1024) MB. Requests per active user = total requests / active users. |
| **API / Contract** | Python functions (no HTTP API): `get_system_health_metrics(time_range, endpoint_filter) -> dict`, `get_product_health_metrics(time_range, region_filter, rank_filter) -> dict`, `get_unit_economics_metrics(time_range) -> dict`, `get_alerts() -> list[Alert]`, `get_error_logs(limit, endpoint_filter) -> list[ErrorLog]`. All functions return dictionaries/dataclasses suitable for Streamlit display. |
| **Request Schema** | Function parameters: `time_range: str` (enum: "1h", "24h", "7d", "30d", "90d"), `endpoint_filter: list[str]` (e.g., ["/api/tournaments", "/api/teams"]), `region_filter: str` (enum: "NA", "EU", "ALL"), `rank_filter: str` (enum: "BEGINNER", "ALL"). |
| **Response Schema** | Example for `get_system_health_metrics`: `{"uptime_pct": 99.8, "latency_p50_ms": 45, "latency_p95_ms": 120, "latency_p99_ms": 250, "error_rate_pct": 2.3, "throughput_rpm": 150, "active_connections": 5}`. Example for `get_product_health_metrics`: `{"funnel": {"accounts_created": 1000, "first_tournament_joined": 650, "first_match_completed": 400}, "activation_rate_pct": 65, "retention_7d_pct": 45, "retention_30d_pct": 28, "north_star": 3.2, "team_creation_rate_pct": 15}`. |
| **Error Handling** | If required telemetry tables (system_logs, product_events) are missing: Return placeholder metrics with warning flag `{"status": "warning", "message": "Telemetry not instrumented yet. Showing mock data.", "metrics": {...}}`. If database connection fails: Return error dict `{"status": "error", "message": "Database unreachable"}` and display error message in Streamlit. Log all errors to stderr for debugging. |

### 3.3 Data Architecture and Flows

| Area | Fill In |
|------|---------|
| **Main Entities (ER)** | **Existing entities (already in repository):** Player (id, username, email, rank, region, account_status, created_at), Tournament (id, name, rank_tier, region, capacity, registered_count, status, start_time, format, is_team_tournament, team_size, created_at), Team (id, name, badge, owner_id, created_at), TournamentRegistration (id, tournament_id, player_id, team_id, registered_at), TeamMembership (id, team_id, player_id, role, joined_at), TeamInvite (id, team_id, token, invited_by, status, created_at, expires_at). **NEW entities required for dashboard (Missing):** SystemLog (id, timestamp, endpoint, method, status_code, duration_ms, player_id, error_message), ProductEvent (id, event_name, event_timestamp, user_id, session_id, app_version, feature_name, flow_name, step_name, success_flag, error_code, metadata_json), ProductMetricsDaily (id, date, active_users_count, new_users_count, tournaments_joined_count, teams_created_count, total_api_requests), DashboardAlert (id, alert_type, metric_name, threshold_value, actual_value, triggered_at, resolved_at, status). |
| **Relationships (ER)** | SystemLog.player_id → Player.id (nullable, for authenticated requests). ProductEvent.user_id → Player.id. ProductMetricsDaily: standalone aggregation table, no FK. DashboardAlert: standalone, references metric names as strings. All new tables have 1:N relationship to Player where applicable. |
| **Data Flow (DFD)** | **System Health Flow:** (1) FastAPI middleware logs each request to SystemLog table (timestamp, endpoint, method, status_code, duration_ms, player_id if authenticated, error_message if error). (2) Background job (cron or FastAPI BackgroundTask) runs health check ping every 1 minute, logs result to SystemLog. (3) DashboardDataService queries SystemLog table with time_range filter, calculates metrics (uptime, latency percentiles, error rates). (4) Streamlit app calls DashboardDataService functions, renders charts. **Product Health Flow:** (1) Frontend and backend log product events to ProductEvent table (event_name, timestamp, user_id, metadata). Key events: "account_created", "tournament_joined", "match_completed", "team_created". (2) Background job runs daily aggregation (cron job at 00:00 UTC) to populate ProductMetricsDaily table. (3) DashboardDataService queries ProductEvent and ProductMetricsDaily with filters, calculates funnel, retention, North Star. (4) Streamlit renders metrics. **Unit Economics Flow:** (1) DashboardDataService queries database file size using os.path.getsize. (2) Queries SystemLog for request counts per day. (3) Queries ProductMetricsDaily for active user counts. (4) Calculates derived metrics (requests per user, growth rate). (5) Streamlit renders charts and projections. |
| **Input Sources** | (1) Production database `clutchup.db` (SQLite) - contains players, tournaments, teams, registrations. (2) New telemetry tables: SystemLog, ProductEvent, ProductMetricsDaily (all stored in same clutchup.db). (3) Dashboard configuration file `dashboard_config.yaml` (alert thresholds, refresh intervals). (4) System resources: database file size, server timestamp (datetime.now()). |

### 3.4 Infrastructure

| Area | Fill In |
|------|---------|
| **Required Hardware / Resources** | **Development:** Single machine (laptop or desktop) running Windows/Mac/Linux with Python 3.10+, 8GB RAM, 20GB disk space. **Production (internal deployment):** Cloud VM or on-premise server with 2 vCPU, 4GB RAM, 50GB SSD. OS: Linux (Ubuntu 22.04 recommended). **Network:** Internal network only (no public internet access). Dashboard accessible via VPN or internal IP. **Dependencies:** Python 3.10+, Streamlit 1.28+, SQLAlchemy 2.0+, pandas 2.0+, numpy, plotly (for charts). No separate database server required (uses existing clutchup.db SQLite file). **Background jobs:** Cron (Linux) or Task Scheduler (Windows) for daily aggregation job and health check ping. **Monitoring:** Dashboard monitors itself - no external monitoring required for v1.0. **Backup:** Dashboard reads from production database but does not write to core tables (only to telemetry tables) - backup strategy follows existing database backup plan. |

---

## 4. Work Plan

### Mapping: Use Case → Tasks

| Use Case | Task ID | Task | Dependencies | DoD | Subtasks |
|----------|---------|------|--------------|-----|----------|
| UC-DASH-1.1 | T-DASH-1 | Implement System Health telemetry and metrics | None | System logs captured for all API requests; health check job running; metrics queryable | ST-DASH-1, ST-DASH-2, ST-DASH-3 |
| UC-DASH-1.2 | T-DASH-2 | Implement System Health dashboard UI and alerting | T-DASH-1 | Streamlit tab displays uptime, latency, errors; alerts trigger correctly | ST-DASH-4, ST-DASH-5 |
| UC-DASH-2.1 | T-DASH-3 | Implement Product Health telemetry and metrics | None | Product events logged; daily aggregation job running; funnel/retention calculable | ST-DASH-6, ST-DASH-7, ST-DASH-8 |
| UC-DASH-2.2 | T-DASH-4 | Implement Product Health dashboard UI and release comparison | T-DASH-3 | Streamlit tab displays funnel, retention, North Star; release comparison works | ST-DASH-9, ST-DASH-10 |
| UC-DASH-3.1 | T-DASH-5 | Implement Unit Economics metrics and dashboard UI | T-DASH-1 | Streamlit tab displays database size, API volume, cost proxies | ST-DASH-11, ST-DASH-12 |

---

## 5. Detailed Task Breakdown

### Task 1

| Field | Fill In |
|-------|---------|
| **Task ID** | T-DASH-1 |
| **Related Use Case** | UC-DASH-1.1 |
| **Task Description** | Implement System Health telemetry: Create SystemLog table, add FastAPI middleware to log all requests, create health check background job, create DashboardDataService functions for system health metrics |
| **Dependencies** | None (can start immediately) |
| **DoD** | (1) SystemLog table created in clutchup.db with schema: id, timestamp, endpoint, method, status_code, duration_ms, player_id, error_message. (2) FastAPI middleware logs every request to SystemLog. (3) Health check job runs every 1 minute and logs result. (4) DashboardDataService.get_system_health_metrics() returns correct uptime, latency, error rate. (5) Unit tests pass for all functions. |

**Subtasks**

| Subtask ID | Description | Dependencies | Acceptance Criteria |
|------------|-------------|--------------|---------------------|
| ST-DASH-1 | Create SystemLog database model and migration | None | SystemLog model defined in backend/app/models/system_log.py with fields: id, timestamp, endpoint, method, status_code, duration_ms, player_id (FK nullable), error_message (nullable). Migration script creates table in clutchup.db. Table creation verified via SQLite CLI. |
| ST-DASH-2 | Implement FastAPI middleware for request logging | ST-DASH-1 | Middleware class `RequestLoggingMiddleware` added to backend/app/middleware/logging.py. Middleware logs to SystemLog table: timestamp (UTC), endpoint (request.url.path), method (request.method), status_code (response.status_code), duration_ms (end_time - start_time in ms), player_id (extracted from auth header if present, else NULL), error_message (extracted from exception if status >=400, else NULL). Middleware registered in backend/app/main.py. Verified: 10 test requests logged correctly to SystemLog. |
| ST-DASH-3 | Create health check background job and DashboardDataService | ST-DASH-1, ST-DASH-2 | Health check script `backend/jobs/health_check.py` created: pings FastAPI /health endpoint every 1 minute, logs result to SystemLog (endpoint="/health", status_code=200 or 500). Cron job configured to run script. DashboardDataService class created in `backend/dashboard/data_service.py` with method `get_system_health_metrics(time_range, endpoint_filter)` that queries SystemLog and returns: uptime_pct (% of /health logs with status 200), latency_p50/p95/p99_ms (numpy percentiles of duration_ms), error_rate_pct (% logs with status >=400), throughput_rpm (count logs per minute avg). Unit test `test_get_system_health_metrics()` passes with mock data. |

### Task 2

| Field | Fill In |
|-------|---------|
| **Task ID** | T-DASH-2 |
| **Related Use Case** | UC-DASH-1.2 |
| **Task Description** | Implement System Health dashboard UI in Streamlit with metrics charts, error log table, and alerting logic |
| **Dependencies** | T-DASH-1 (telemetry must be working) |
| **DoD** | (1) Streamlit app created at `backend/dashboard/streamlit_app.py` with System Health tab. (2) Tab displays: uptime gauge, latency line charts (P50/P95/P99), error rate line chart, throughput line chart, error log table (last 100 rows). (3) Time range and endpoint filters work correctly. (4) Alert logic evaluates error_rate_pct > threshold and displays red banner. (5) Manual testing: Open dashboard, view metrics, trigger alert by creating test errors, confirm banner appears. |

**Subtasks**

| Subtask ID | Description | Dependencies | Acceptance Criteria |
|------------|-------------|--------------|---------------------|
| ST-DASH-4 | Create Streamlit System Health tab UI | ST-DASH-3 | Streamlit app file `backend/dashboard/streamlit_app.py` created with tab "System Health". UI components: (1) Sidebar filters: time_range selectbox (1h/24h/7d/30d), endpoint_filter multiselect. (2) Main area: KPI cards (uptime %, error rate %), line chart (Plotly) for latency (3 lines: P50/P95/P99), line chart for throughput (requests per minute), error log table (Streamlit dataframe) with columns: timestamp, endpoint, status_code, error_message. Data fetched via `DashboardDataService.get_system_health_metrics()` and `get_error_logs()`. Chart updates when filters change. Manual test: Filters work, charts render correctly with mock data. |
| ST-DASH-5 | Implement alert logic and banner | ST-DASH-4 | Alert rule: If error_rate_pct > 5% for any endpoint in selected time range, display alert banner. Alert logic in DashboardDataService.get_alerts() function: Query SystemLog grouped by endpoint, calculate error_rate_pct, check against threshold (loaded from dashboard_config.yaml), return list of Alert objects (alert_type="error_rate", metric_name="error_rate_pct", threshold_value=5.0, actual_value=12.3, endpoint="/api/tournaments/register"). Streamlit UI: If alerts list not empty, display st.error() banner at top with message "ALERT: {endpoint} error rate is {actual_value}% (threshold: {threshold_value}%)". Clickable link filters error log table to affected endpoint. Manual test: Create >5% errors in test DB, confirm banner appears. |

### Task 3

| Field | Fill In |
|-------|---------|
| **Task ID** | T-DASH-3 |
| **Related Use Case** | UC-DASH-2.1 |
| **Task Description** | Implement Product Health telemetry: Create ProductEvent and ProductMetricsDaily tables, add event logging to backend/frontend, create daily aggregation job, create DashboardDataService functions for product metrics |
| **Dependencies** | None |
| **DoD** | (1) ProductEvent table created with schema: id, event_name, event_timestamp, user_id (FK), session_id, app_version, feature_name, flow_name, step_name, success_flag, error_code, metadata_json. (2) ProductMetricsDaily table created with schema: id, date, active_users_count, new_users_count, tournaments_joined_count, teams_created_count, total_api_requests. (3) Backend logs events for: account_created, tournament_joined, team_created. (4) Daily aggregation job populates ProductMetricsDaily. (5) DashboardDataService.get_product_health_metrics() returns funnel, activation, retention, North Star. (6) Unit tests pass. |

**Subtasks**

| Subtask ID | Description | Dependencies | Acceptance Criteria |
|------------|-------------|--------------|---------------------|
| ST-DASH-6 | Create ProductEvent and ProductMetricsDaily tables | None | ProductEvent model in `backend/app/models/product_event.py` with fields: id, event_name (str), event_timestamp (datetime), user_id (FK to Player, nullable for anonymous events), session_id (str, nullable), app_version (str, default "1.0"), feature_name (str, nullable), flow_name (str, nullable), step_name (str, nullable), success_flag (bool, default True), error_code (str, nullable), metadata_json (str, nullable). ProductMetricsDaily model in `backend/app/models/product_metrics_daily.py` with fields: id, date (date, unique), active_users_count (int), new_users_count (int), tournaments_joined_count (int), teams_created_count (int), total_api_requests (int). Migration script creates both tables. Verified via SQLite CLI. |
| ST-DASH-7 | Add product event logging to backend | ST-DASH-6 | ProductEventRepository class created in `backend/app/repositories/product_event_repository.py` with method `log_event(event_name, user_id, metadata)`. Integration points: (1) PlayerRepository.create() logs event "account_created" with metadata {"rank": rank, "region": region}. (2) TournamentRepository.register_player() logs event "tournament_joined" with metadata {"tournament_id": X, "tournament_name": Y}. (3) TeamRepository.create() logs event "team_created" with metadata {"team_id": X, "team_name": Y}. All events include user_id (player_id), app_version (hardcoded "1.0" for now), timestamp (UTC). Unit tests verify events are logged correctly. Integration test: Create player, register for tournament, create team → verify 3 events in ProductEvent table. |
| ST-DASH-8 | Create daily aggregation job and product metrics functions | ST-DASH-6, ST-DASH-7 | Aggregation script `backend/jobs/daily_aggregation.py` created: Runs at 00:00 UTC daily (cron job). Queries: (1) active_users_count = count distinct user_id in ProductEvent where event_timestamp in [yesterday 00:00, yesterday 23:59]. (2) new_users_count = count Player.created_at in [yesterday]. (3) tournaments_joined_count = count ProductEvent where event_name="tournament_joined" in [yesterday]. (4) teams_created_count = count ProductEvent where event_name="team_created". (5) total_api_requests = count SystemLog in [yesterday]. Inserts row into ProductMetricsDaily. DashboardDataService.get_product_health_metrics(time_range, region_filter, rank_filter) function: Queries ProductEvent and Player tables to calculate: (1) Funnel: accounts_created = count Player.created_at in time_range, first_tournament_joined = count distinct user_id in ProductEvent where event_name="tournament_joined" and user_id in (players created in time_range), first_match_completed = proxy using tournaments with status=COMPLETED (Missing real match events). (2) Activation rate = (first_tournament_joined within 7 days / accounts_created) * 100. (3) 7-day retention = for each cohort date D in time_range, calculate (users with event on D+7 / users created on D) * 100, average across cohorts. (4) North Star = (total tournament_joined events in time_range / active_users_count in time_range). Unit test passes with mock data. |

### Task 4

| Field | Fill In |
|-------|---------|
| **Task ID** | T-DASH-4 |
| **Related Use Case** | UC-DASH-2.2 |
| **Task Description** | Implement Product Health dashboard UI in Streamlit with funnel chart, retention cohort table, North Star KPI, and release comparison feature |
| **Dependencies** | T-DASH-3 (product telemetry must be working) |
| **DoD** | (1) Streamlit Product Health tab created with: funnel chart (Sankey), retention cohort table, North Star KPI card, top 5 tournaments table. (2) Filters work: time_range, region, rank. (3) Release comparison mode: Select two app_versions, display side-by-side metrics, highlight deltas. (4) Manual testing confirms all features work correctly. |

**Subtasks**

| Subtask ID | Description | Dependencies | Acceptance Criteria |
|------------|-------------|--------------|---------------------|
| ST-DASH-9 | Create Streamlit Product Health tab UI | ST-DASH-8 | Streamlit tab "Product Health" added to `backend/dashboard/streamlit_app.py`. UI components: (1) Sidebar filters: time_range, region, rank. (2) Main area: Funnel chart (Plotly Sankey diagram) with 3 nodes: Accounts Created → First Tournament Joined → First Match Completed, width proportional to conversion counts. (3) KPI cards: Activation Rate %, 7-day Retention %, 30-day Retention %, North Star (tournaments per user). (4) Line chart: North Star trend over time (daily values). (5) Table: Top 5 tournaments by registration count (name, region, rank, registrations). Data fetched via DashboardDataService.get_product_health_metrics(). Manual test: Filters update charts correctly. |
| ST-DASH-10 | Implement release comparison feature | ST-DASH-9 | Comparison mode toggle added to sidebar (checkbox "Enable Release Comparison"). When enabled: Two selectboxes appear for version selection (version_a, version_b), populated from distinct app_version values in ProductEvent table. When two versions selected: Display two-column layout with metrics for each version side-by-side. Metrics displayed: Funnel completion %, Activation %, 7-day Retention %, 30-day Retention %, North Star. Delta column shows (version_b - version_a) / version_a * 100 as percentage, color-coded: green if delta > +5%, red if delta < -5%, gray otherwise. Data fetched via DashboardDataService.get_product_health_metrics(filters + app_version filter). Manual test: Select two versions, confirm metrics and deltas display correctly. |

### Task 5

| Field | Fill In |
|-------|---------|
| **Task ID** | T-DASH-5 |
| **Related Use Case** | UC-DASH-3.1 |
| **Task Description** | Implement Unit Economics metrics and dashboard UI: Database size tracking, API volume metrics, cost proxies, dashboard tab |
| **Dependencies** | T-DASH-1 (system logs needed for API volume) |
| **DoD** | (1) DashboardDataService.get_unit_economics_metrics() returns: database_size_mb, database_growth_mb_per_day, api_requests_per_day, requests_per_active_user, top_endpoints_by_volume, top_endpoints_by_latency. (2) Streamlit Unit Economics tab displays: DB size trend chart, API volume trend chart, requests per user KPI, top endpoints tables. (3) Database growth projection chart (linear extrapolation). (4) Manual testing confirms accuracy of metrics. |

**Subtasks**

| Subtask ID | Description | Dependencies | Acceptance Criteria |
|------------|-------------|--------------|---------------------|
| ST-DASH-11 | Implement unit economics metrics functions | ST-DASH-3, ST-DASH-8 | DashboardDataService.get_unit_economics_metrics(time_range) function implemented: (1) database_size_mb = os.path.getsize("backend/clutchup.db") / (1024*1024). (2) Query ProductMetricsDaily for date range to get daily database size snapshots (Missing - need to add db_size_mb field to ProductMetricsDaily). Workaround for v1.0: Query SystemLog table size as proxy, or record daily db size in aggregation job. (3) database_growth_mb_per_day = linear regression slope of db size over time (using numpy.polyfit). (4) api_requests_per_day = sum(total_api_requests) from ProductMetricsDaily grouped by date. (5) requests_per_active_user = total_api_requests / active_users_count per day, averaged. (6) top_endpoints_by_volume = query SystemLog grouped by endpoint, order by count desc, limit 5. (7) top_endpoints_by_latency = query SystemLog grouped by endpoint, order by percentile(duration_ms, 0.95) desc, limit 5. Unit test verifies calculations with mock data. |
| ST-DASH-12 | Create Streamlit Unit Economics tab UI | ST-DASH-11 | Streamlit tab "Unit Economics" added. UI components: (1) Sidebar filters: time_range. (2) Main area: KPI cards: Current DB Size (MB), DB Growth Rate (MB/day), Total API Requests (selected period), Requests per Active User. (3) Line chart: Database size over time (daily snapshots). (4) Line chart: API requests per day. (5) Projection chart: Database size projection for next 30/90 days (linear extrapolation from growth rate, with disclaimer "Projection assumes linear growth"). (6) Table: Top 5 Endpoints by Volume (endpoint, request_count, % of total). (7) Table: Top 5 Endpoints by Latency (endpoint, P95 latency ms). Data fetched via DashboardDataService.get_unit_economics_metrics(). Manual test: Metrics and charts display correctly, projection calculation verified manually. |

---

## Implementation Notes

### Repository-Aware Implementation Details

**Based on current repository structure:**

1. **Backend:** FastAPI application at `backend/app/main.py`. Services at `backend/app/services/`. Repositories at `backend/app/repositories/`. Models at `backend/app/models/`. Database: SQLite at `backend/clutchup.db`.

2. **Existing Services:** TournamentService (register_player, get_eligible_tournaments, create_tournament), TeamService (create_team, create_invite, register_team_for_tournament), PlayerService (create_player, get_by_id).

3. **Dashboard Integration Points:**
   - **System Health telemetry:** Add middleware in `backend/app/middleware/logging.py` (new file), register in `backend/app/main.py`.
   - **Product Events:** Integrate into existing repositories (PlayerRepository, TournamentRepository, TeamRepository) by adding event logging calls after DB operations.
   - **Dashboard Service:** Create new module `backend/dashboard/data_service.py` (separate from API services - dashboard is internal tool).
   - **Streamlit App:** Create `backend/dashboard/streamlit_app.py` (separate entry point from FastAPI app).

4. **Data Conflicts and Assumptions:**
   - **Conflict:** Product spec mentions "match completion" as a key metric, but current repository has Match model defined but not used (no match creation or result processing logic). **Current state:** Matches table exists but empty. **Target state:** Use match results to track "first value" event. **Dashboard implication:** For v1.0, proxy "match completion" with "tournament with status=COMPLETED" participation. Add note in dashboard that this is a proxy metric. Real match event logging to be added in future sprint.
   - **Assumption:** No authentication system exists in current repository (player_id passed as query param). Dashboard will use basic HTTP auth (Streamlit built-in) for v1.0. Real user auth integration in future.
   - **Assumption:** No app versioning or release tracking in current repository. For release comparison feature, add `app_version` field to ProductEvent table. Default to "1.0" for all current events. Future: Extract version from API request headers or deployment metadata.
   - **Assumption:** No background job infrastructure in current repository. Use simple cron jobs (Linux) or Python scripts run via scheduler for health checks and daily aggregation. Future: Migrate to Celery or similar task queue if needed.

5. **AI Quality Section:** **Not applicable** - ClutchUp v1.0 has no AI/ML features. No LLM prompts, no inference endpoints, no AI telemetry needed. AI Quality dashboard view can be omitted or show "N/A - No AI features in product" message. If future product iterations add AI matchmaking or chat moderation, add AI telemetry schema and dashboard section in future sprint.

6. **Unit Economics - Cost Observability:** Current repository uses SQLite (free, no API costs). No cloud infrastructure costs visible in code. For v1.0, unit economics focuses on **resource utilization proxies:** database size (storage cost proxy), API request volume (compute cost proxy), requests per active user (efficiency metric). Real cost tracking (cloud bills, server costs) requires external integration with billing systems - out of scope for v1.0 dashboard. Dashboard will include placeholder "Cost per Active User" calculated as (assumed_monthly_server_cost / active_users) - configurable in dashboard_config.yaml.

### Missing Telemetry and Instrumentation Requirements

**Existing Metrics (Available Now):**
- Player count, creation dates (from `players` table)
- Tournament count, registrations, capacity (from `tournaments`, `tournament_registrations` tables)
- Team count, membership count (from `teams`, `team_memberships` tables)
- Database file size (derivable via os.path.getsize)

**Derivable Metrics (Computable from Existing Data):**
- Onboarding funnel stage 1 (account creation): Use Player.created_at
- Onboarding funnel stage 2 (first tournament join): Use min(TournamentRegistration.registered_at) per player
- Activation rate: Calculate from Player.created_at and TournamentRegistration timestamps
- Tournament popularity: Count TournamentRegistration per tournament
- Team creation rate: Count Team.created_at per player

**Missing Metrics (Require New Instrumentation):**

*System Health (Missing):*
- API request logs (endpoint, method, status_code, duration_ms, timestamp, player_id, error_message) → **Requires:** SystemLog table + FastAPI middleware
- Health check logs (uptime tracking) → **Requires:** Health check job + SystemLog entries
- Database connection pool stats → **Derivable** from SQLAlchemy engine.pool but not persisted
- Background job queue length → **Not applicable** (no queue system in current repository; cron jobs used instead)

*Product Health (Missing):*
- Match completion events → **Requires:** ProductEvent logging when match results recorded (Match model exists but unused)
- Session tracking (session_id, session duration) → **Requires:** Frontend session ID generation + ProductEvent logging
- Retention activity tracking (which users returned on D+7?) → **Derivable** from ProductEvent table once event logging is added
- North Star metric components (tournaments per active user) → **Derivable** from ProductEvent once tournament_joined events logged
- Churn detection (users who stopped activity) → **Derivable** from ProductEvent + last_activity_timestamp calculation
- App version / release tracking → **Requires:** app_version field in ProductEvent + version injection in API middleware

*Unit Economics (Missing):*
- Historical database size snapshots → **Requires:** Daily aggregation job to record db size in ProductMetricsDaily.db_size_mb field
- Token usage, LLM costs → **Not applicable** (no AI in product)
- Infrastructure costs → **Requires:** External integration with cloud billing API (out of scope for v1.0)

**Minimum Telemetry Schemas (to be implemented):**

**SystemLog Table:**
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    duration_ms REAL NOT NULL,
    player_id INTEGER NULL,
    error_message TEXT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id)
);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_endpoint ON system_logs(endpoint);
```

**ProductEvent Table:**
```sql
CREATE TABLE product_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    event_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NULL,
    session_id TEXT NULL,
    app_version TEXT NOT NULL DEFAULT '1.0',
    feature_name TEXT NULL,
    flow_name TEXT NULL,
    step_name TEXT NULL,
    success_flag INTEGER NOT NULL DEFAULT 1,
    error_code TEXT NULL,
    metadata_json TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES players(id)
);
CREATE INDEX idx_product_events_timestamp ON product_events(event_timestamp);
CREATE INDEX idx_product_events_event_name ON product_events(event_name);
CREATE INDEX idx_product_events_user_id ON product_events(user_id);
```

**ProductMetricsDaily Table:**
```sql
CREATE TABLE product_metrics_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    active_users_count INTEGER NOT NULL DEFAULT 0,
    new_users_count INTEGER NOT NULL DEFAULT 0,
    tournaments_joined_count INTEGER NOT NULL DEFAULT 0,
    teams_created_count INTEGER NOT NULL DEFAULT 0,
    total_api_requests INTEGER NOT NULL DEFAULT 0,
    db_size_mb REAL NOT NULL DEFAULT 0
);
CREATE INDEX idx_product_metrics_daily_date ON product_metrics_daily(date);
```

**DashboardAlert Table (optional for v1.0, can start with in-memory alerts):**
```sql
CREATE TABLE dashboard_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    threshold_value REAL NOT NULL,
    actual_value REAL NOT NULL,
    triggered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    status TEXT NOT NULL DEFAULT 'active'
);
```

### Backend Contracts Required by Dashboard

**DashboardDataService Python Module (`backend/dashboard/data_service.py`):**

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SystemHealthMetrics:
    uptime_pct: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    error_rate_pct: float
    throughput_rpm: float
    active_db_connections: int

@dataclass
class ProductHealthMetrics:
    funnel: Dict[str, int]  # {"accounts_created": X, "first_tournament": Y, "first_match": Z}
    activation_rate_pct: float
    retention_7d_pct: float
    retention_30d_pct: float
    north_star: float  # tournaments per active user
    team_creation_rate_pct: float

@dataclass
class UnitEconomicsMetrics:
    database_size_mb: float
    database_growth_mb_per_day: float
    api_requests_per_day: float
    requests_per_active_user: float
    top_endpoints_by_volume: List[Dict]  # [{"endpoint": "/api/...", "count": X, "pct": Y}]
    top_endpoints_by_latency: List[Dict]  # [{"endpoint": "/api/...", "p95_ms": X}]

@dataclass
class Alert:
    alert_type: str
    metric_name: str
    threshold_value: float
    actual_value: float
    endpoint: Optional[str]
    triggered_at: datetime

class DashboardDataService:
    def __init__(self, db_session):
        self.db = db_session

    def get_system_health_metrics(
        self,
        time_range: str,  # "1h", "24h", "7d", "30d", "90d"
        endpoint_filter: Optional[List[str]] = None
    ) -> SystemHealthMetrics:
        """Query SystemLog table and calculate system health metrics."""
        pass

    def get_product_health_metrics(
        self,
        time_range: str,
        region_filter: str = "ALL",
        rank_filter: str = "ALL"
    ) -> ProductHealthMetrics:
        """Query ProductEvent and Player tables to calculate product metrics."""
        pass

    def get_unit_economics_metrics(
        self,
        time_range: str
    ) -> UnitEconomicsMetrics:
        """Calculate cost and resource utilization metrics."""
        pass

    def get_alerts(self) -> List[Alert]:
        """Evaluate alert rules and return active alerts."""
        pass

    def get_error_logs(
        self,
        limit: int = 100,
        endpoint_filter: Optional[List[str]] = None
    ) -> List[Dict]:
        """Query SystemLog for recent errors."""
        pass
```

### Separation of Responsibilities

**Dashboard UI Responsibilities (Streamlit):**
- User input: time range selection, filters, toggles
- Data visualization: charts, tables, KPI cards
- User interactions: drill-downs, exports
- Alert display: banners, notifications

**Backend Aggregation Responsibilities (DashboardDataService):**
- SQL queries to telemetry tables (SystemLog, ProductEvent, ProductMetricsDaily)
- Metric calculations (percentiles, rates, averages, cohorts)
- Alert rule evaluation (threshold comparisons)
- Data transformations for dashboard consumption

**Source-of-Truth Data Sources:**
- **System Health:** SystemLog table (request logs), health check job logs
- **Product Health:** ProductEvent table (user actions), ProductMetricsDaily table (aggregated daily metrics), Player/Tournament/Team tables (core entities)
- **Unit Economics:** ProductMetricsDaily table (aggregated counts), database file size (os.path.getsize), SystemLog table (API volume)

---

## Testing and QA Considerations

**Unit Tests:**
- Test DashboardDataService metric calculation functions with mock data
- Test alert rule evaluation logic
- Test data aggregation job correctness

**Integration Tests:**
- Test end-to-end flow: Log event → Aggregation job → Query metric → Dashboard display
- Test dashboard with realistic data volumes (10k players, 100k events)
- Test filter combinations and edge cases (empty data, single data point)

**Manual E2E Tests:**
- Create test data: 100 players, 50 tournaments, 20 teams, 500 registrations, 1000 product events
- Verify dashboard displays correct metrics
- Test alert triggering: Simulate high error rate, confirm alert appears
- Test release comparison: Tag events with v1.0 and v1.1, confirm comparison works

**Performance Tests:**
- Dashboard query response time <3 seconds for 30-day time range with 100k events
- Streamlit app handles 10 concurrent users without errors
- Daily aggregation job completes in <5 minutes

---

## Open Questions and Future Enhancements

**Open Questions (to be resolved during implementation):**
1. **Database Growth Tracking:** Should db size be tracked daily in aggregation job, or queried on-demand? (Recommendation: Track daily to enable historical trend charts)
2. **Alert Persistence:** Should alerts be stored in DashboardAlert table, or kept in-memory only? (Recommendation: Store for v1.0 to enable alert history view)
3. **Session Tracking:** How to generate session_id in frontend? (Recommendation: Generate UUID in React on app load, store in sessionStorage, send with API requests)
4. **Cost Assumptions:** What monthly server cost to assume for "cost per active user" calculation? (Recommendation: Make configurable in dashboard_config.yaml, default $50/month)

**Future Enhancements (out of scope for v1.0):**
- **Automated Alerting:** Email/Slack notifications when alerts trigger (currently only visual dashboard alerts)
- **Advanced Anomaly Detection:** Use statistical methods (Z-score, moving averages) to auto-detect anomalies beyond simple thresholds
- **User-Level Drill-Down:** Click on funnel stage to see list of specific users in that cohort
- **Geolocation Map:** Visualize player distribution by region on world map
- **Real-Time Streaming:** WebSocket or SSE for live metric updates (currently 60-second refresh)
- **Multi-Tenant Support:** If ClutchUp becomes white-label platform, add tenant_id filtering
- **Integration with External Tools:** Export to Grafana, DataDog, or other observability platforms
- **Match-Level Metrics:** Once Match system is fully implemented, add match duration, outcomes, rating changes to Product Health
- **AI Metrics (if AI added to product):** Prompt version comparison, model performance, refusal rates, structured output validation

---

## Deployment Plan

**Development Environment:**
1. Run Streamlit locally: `streamlit run backend/dashboard/streamlit_app.py`
2. FastAPI backend runs on localhost:8000
3. Dashboard connects to local clutchup.db

**Production Environment (Internal):**
1. Deploy Streamlit app on internal VM (Linux)
2. Configure systemd service to run Streamlit on boot
3. Set up cron jobs for health check and daily aggregation
4. Expose dashboard on internal IP with basic HTTP auth
5. VPN access required for remote team members
6. No public internet exposure

**Configuration Management:**
- `backend/dashboard/dashboard_config.yaml`:
  ```yaml
  alerts:
    error_rate_threshold_pct: 5.0
    latency_p95_threshold_ms: 500
  metrics:
    system_health_refresh_interval_sec: 60
    product_health_refresh_interval_sec: 300
    unit_economics_refresh_interval_sec: 600
  cost_assumptions:
    monthly_server_cost_usd: 50
  ```

**Monitoring:**
- Dashboard monitors itself (uptime, query times logged to SystemLog)
- Manual check daily by ops team
- Alert if dashboard app crashes (systemd restart configured)

---

**End of Specification**

---

## Summary

This specification provides an **implementation-ready blueprint** for a Streamlit-based internal dashboard for ClutchUp v1.0. It is grounded in the **current repository reality** (FastAPI backend, SQLite database, tournament/team/player systems) and the **existing product spec** (beginner-friendly competitive gaming platform).

**Key Implementation Dependencies:**
1. **New Database Tables:** SystemLog, ProductEvent, ProductMetricsDaily (3 tables)
2. **New Backend Components:** RequestLoggingMiddleware, ProductEventRepository, DashboardDataService (3 modules)
3. **New Background Jobs:** Health check job, daily aggregation job (2 cron jobs)
4. **New Frontend:** Streamlit app with 3 tabs (1 Python file)

**Implementation Priority:**
- **Phase 1 (MVP):** System Health tab (T-DASH-1, T-DASH-2) - provides immediate operational visibility
- **Phase 2:** Product Health tab (T-DASH-3, T-DASH-4) - enables product decisions
- **Phase 3:** Unit Economics tab (T-DASH-5) - supports cost optimization

**Estimated Effort:**
- Backend telemetry + middleware: 3 days
- Dashboard UI (all tabs): 3 days
- Background jobs + testing: 2 days
- **Total:** ~8 days (1-2 week sprint)

This dashboard will provide **unified visibility** into system health, product health, and unit economics, enabling data-driven decisions and rapid incident response for the ClutchUp internal team.
