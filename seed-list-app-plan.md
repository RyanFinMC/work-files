# Seed List App — Product + Technical Plan

## 1) Goal and Success Criteria
A seed list app helps teams monitor inbox placement by sending campaigns to controlled seed mailboxes across major ESPs and measuring where each message lands.

### Primary outcomes
- Detect inbox placement regressions quickly (within minutes, not days).
- Break down deliverability by ESP, campaign, and time window.
- Provide enough raw evidence (headers, folders/labels, timestamps) to investigate root causes.

### MVP success metrics
- Inbox placement computed for at least Gmail, Microsoft, Yahoo/AOL, and iCloud.
- End-to-end processing latency under 5 minutes for 95% of checks.
- Campaign-level dashboard with placement rates and missing counts.

---

## 2) Scope

### In-scope (MVP)
- Seed mailbox inventory + grouping.
- Campaign registration with matching identifiers.
- Polling-based mailbox checks.
- Placement classification: `inbox`, `spam`, `promotions`, `missing`.
- Dashboard cards + ESP/campaign tables.
- Basic threshold alerts.

### Out-of-scope (MVP)
- Fully automated remediation recommendations.
- Domain warmup orchestration.
- Dedicated sender reputation scoring model.

---

## 3) Core Features

### A. Seed Account Management
- CRUD seed addresses and metadata.
- Grouping by ESP, region, provider type (consumer/business), and campaign set.
- Credential method per seed: OAuth2 or app-password/IMAP secret reference.
- Health state: active, paused, auth_expired, connection_error.

### B. Campaign Tracking
- Register campaign with one or more identifiers:
  - subject token (required)
  - custom header (recommended, e.g. `X-Campaign-ID`)
  - optional tracking pixel ID
- Track per-seed detection:
  - placement bucket
  - detected timestamp
  - latency from `sent_at`
  - auth signal extraction (SPF/DKIM/DMARC from headers)

### C. Dashboard + Reporting
- Live summary: inbox %, spam %, missing %.
- ESP breakdown table with trend deltas.
- Campaign comparison over date ranges.
- CSV export for campaign + seed-level outcomes.

### D. Alerting
- Rule examples:
  - inbox placement drop by >15% vs trailing 7-day baseline
  - missing rate above threshold (e.g., 20%)
- Notification channels for MVP: email + webhook.

---

## 4) Retrieval and Classification Strategy

### Provider integrations
- **IMAP (default path):** broad compatibility for Yahoo/AOL/iCloud/other providers.
- **Gmail API:** preferred for accurate label/tab detection (`INBOX`, `CATEGORY_PROMOTIONS`, `SPAM`).
- **Microsoft Graph:** preferred for M365/Outlook mailbox access.

### Placement rules
- `inbox`: message in inbox folder/label and not junk.
- `spam`: message found in junk/spam folder/label.
- `promotions`: Gmail promotions label present.
- `missing`: not found after retry window expires.

### Polling cadence
- First check at T+1 min, then T+3, T+5, T+10 (configurable).
- Mark `missing` only after final retry.

---

## 5) Architecture

```text
Client (Next.js)
    |
    v
API Service (FastAPI/Express)
    |-- PostgreSQL (metadata + results)
    |-- Redis (job queue + dedupe locks)
    |
    v
Worker(s)
    |-- IMAP connector
    |-- Gmail API connector
    |-- Microsoft Graph connector
    |
    v
Classifier + Result Writer
```

### Service responsibilities
- **API service:** CRUD, campaign registration, query/report endpoints, authn/authz.
- **Worker service:** mailbox polling, provider API calls, retries/backoff, normalization.
- **Classifier:** maps provider-specific folder/label states to unified placement buckets.

---

## 6) Data Model (Implementation-Oriented)

### `seed_accounts`
- `id` (uuid)
- `email` (unique)
- `esp_name` (enum/text)
- `auth_method` (`oauth2` | `imap_secret`)
- `credential_ref` (secret manager key)
- `region`, `tags` (jsonb)
- `status` (`active` | `paused` | `auth_expired` | `error`)
- `created_at`, `updated_at`

### `campaigns`
- `id` (uuid)
- `name`
- `subject_identifier`
- `header_identifier` (nullable)
- `tracking_id` (nullable)
- `sent_at`
- `created_at`

### `delivery_results`
- `id` (uuid)
- `campaign_id` (fk)
- `seed_account_id` (fk)
- `placement` (`inbox` | `spam` | `promotions` | `missing`)
- `detected_at` (nullable when missing)
- `latency_ms` (nullable)
- `source_provider` (`imap` | `gmail_api` | `ms_graph`)
- `folder_or_label` (raw normalized source)
- `spf_result`, `dkim_result`, `dmarc_result` (nullable)
- `raw_headers` (jsonb, optional/truncated)

### `alert_events`
- `id` (uuid)
- `campaign_id` (nullable)
- `scope` (`global` | `esp` | `campaign`)
- `severity` (`info` | `warning` | `critical`)
- `message`
- `created_at`

### Recommended indexes
- `delivery_results (campaign_id, placement)`
- `delivery_results (seed_account_id, detected_at desc)`
- `delivery_results (detected_at desc)`
- `campaigns (sent_at desc)`

---

## 7) API Surface (MVP)

- `POST /seed-accounts`
- `GET /seed-accounts`
- `PATCH /seed-accounts/:id`
- `POST /campaigns`
- `GET /campaigns`
- `POST /campaigns/:id/checks/run`
- `GET /campaigns/:id/results`
- `GET /dashboard/summary?from=&to=`
- `GET /dashboard/esp-breakdown?campaign_id=`
- `GET /alerts`

---

## 8) Delivery Roadmap

### Phase 1 — MVP foundation (2–4 weeks)
- Seed CRUD + secret references
- IMAP connector + worker queue
- Campaign registration + basic result table
- Simple dashboard summary + ESP table

### Phase 2 — Provider depth (2–3 weeks)
- Gmail API label-based placement
- Microsoft Graph integration
- Better retry logic + dedupe

### Phase 3 — Reliability + analytics (2–3 weeks)
- Header parsing and auth outcomes
- Historical trend charts
- CSV export + alert thresholds

### Phase 4 — Scale hardening
- Partition/archival strategy for `delivery_results`
- Queue throughput tuning + backpressure
- SLO monitoring and on-call runbooks

---

## 9) Security and Operations
- Store mailbox secrets in managed secret storage (not plaintext DB).
- Encrypt at rest and in transit.
- Prefer OAuth2 scopes with least privilege.
- Audit logging for credential updates and access attempts.
- Respect provider quotas with exponential backoff and jitter.

---

## 10) Known Risks and Mitigations
- **Provider API quota/rate limits** → batching, caching, adaptive polling.
- **Mailbox auth churn** → seed health checks + proactive re-auth reminders.
- **False missing classifications** → multi-pass polling before final missing state.
- **High write volume** → time-based partitioning + retention policy.
