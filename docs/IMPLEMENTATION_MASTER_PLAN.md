# Implementation Master Plan
## Digital Twin AI Assistant Platform

**Version:** 1.0  
**Date:** 2026-07-19  
**Status:** Draft  

---

## Table of Contents
1. [Overview](#overview)
2. [Phase Timeline](#phase-timeline)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Development Environment](#development-environment)
5. [Backend Services Implementation Order](#backend-services-implementation-order)
6. [Frontend Implementation Order](#frontend-implementation-order)
7. [Integration & Deployment](#integration--deployment)
8. [Risk & Mitigation](#risk--mitigation)
9. [Pull Request Management Guidelines](#pull-request-management-guidelines)
10. [GitHub Command Line Workflow](#github-command-line-gh-workflow)

---

## Overview

This master plan outlines the high-level sequence of work to build the Digital Twin platform from infrastructure through MVP launch.

### Implementation Principles
1. **Infrastructure First** — Establish foundations before coding
2. **Backend-Driven** — Build API contracts before frontend
3. **Layered Approach** — Each service depends on previous ones
4. **MVP Focus** — Deliver E1-E4 services first (core functionality)
5. **Iterative Validation** — Test integration at each phase

### Success Definition
- **MVP Launch:** End of Q3 2026
- **Core Users:** 10-20 alpha testers
- **Core Flows:** Owner registration → Profile upload → Chat → Notifications
- **Uptime:** 95%+ during testing
- **Quality:** Zero data loss, basic security in place

---

## Phase Timeline

### Phase 0: Foundation (Week 1-2)
**Output:** Ready-to-code infrastructure

```
Week 1:
├── Nx monorepo setup
├── Database schema design & setup
├── Docker Compose configuration
├── CI/CD pipeline scaffold
└── Development guidelines

Week 2:
├── Shared libraries structure
├── API contract definitions (OpenAPI)
├── Authentication framework
└── Logging & monitoring setup
```

### Phase 1: Core Services (Week 3-8)
**Output:** MVP backend services operational

```
Week 3-4: Auth Service (E1)
├── Owner registration/login
├── JWT token management
├── OAuth integration skeleton
└── Integration tests

Week 5-6: Profile Service (E2)
├── CV upload & storage
├── Text extraction pipeline
├── LLM summary generation
└── Profile management API

Week 7-8: Chat Service (E3)
├── Chat session management
├── LLM integration
├── Message persistence
└── Response generation
```

### Phase 2: Supporting Services (Week 9-10)
**Output:** Complete backend system

```
Week 9: Notification Service (E4)
├── Pushover integration
├── Notification events
├── In-app notification storage
└── Notification preferences

Week 10: Config Service (E5)
├── System prompt management
├── Tone/style configuration
├── Topic scope management
└── Configuration API
```

### Phase 3: Frontend (Week 11-14)
**Output:** Web interface operational

```
Week 11: Core Pages (Public + Auth)
├── Homepage & navigation
├── Login/Register flows
├── Owner dashboard shell
└── Public chat widget

Week 12: Profile Management
├── CV upload UI
├── Profile summary review
├── Settings pages
└── Edit functionality

Week 13: Chat Interface
├── Chat widget refinement
├── Message display
├── Real-time messaging
└── Visitor experience polish

Week 14: Dashboard & Analytics
├── Notification center
├── Conversation browser
├── Basic analytics view
└── Configuration UI
```

### Phase 4: Integration & Launch (Week 15-16)
**Output:** MVP ready for testing

```
Week 15: Integration Testing
├── End-to-end flows
├── Cross-service communication
├── Data consistency checks
└── Performance testing

Week 16: Launch Preparation
├── Documentation
├── Deployment to staging
├── Security audit
├── Onboarding for alpha users
```

---

## Infrastructure Setup

### Phase 0.1: Repository & Local Development

```
┌─────────────────────────────────────────┐
│  Nx Monorepo Initialization              │
├─────────────────────────────────────────┤
│                                         │
│  1. Create Nx workspace                 │
│     └─ monorepo structure                │
│                                         │
│  2. Add Python backend support          │
│     └─ apps/backend app                  │
│     └─ libs/backend-shared library       │
│                                         │
│  3. Add React frontend support          │
│     └─ apps/frontend app                 │
│     └─ libs/frontend-shared library      │
│                                         │
│  4. Configure build tools               │
│     └─ Nx configuration (nx.json)        │
│     └─ TypeScript config                 │
│     └─ Python poetry (pyproject.toml)    │
│                                         │
│  5. Add Git & CI/CD scaffold            │
│     └─ .github/workflows/                │
│     └─ .gitignore & .gitattributes       │
│                                         │
└─────────────────────────────────────────┘
```

**Deliverable:** Ready-to-develop local environment

---

### Phase 0.2: Database Infrastructure

```
┌─────────────────────────────────────────┐
│  PostgreSQL & Schema Setup              │
├─────────────────────────────────────────┤
│                                         │
│  1. PostgreSQL container (Docker)       │
│     └─ Version 14+                       │
│     └─ Dev database: digital_twin_dev   │
│                                         │
│  2. Alembic migrations setup            │
│     └─ Migration scripts folder          │
│     └─ Base migration template           │
│     └─ Environment configuration         │
│                                         │
│  3. Database schema (phased)            │
│     └─ Phase 0: Owners, OwnerSessions   │
│     └─ Phase 1: Profiles, CVProcessing  │
│     └─ Phase 1: ChatSessions, Messages  │
│     └─ Phase 2: Notifications, Config   │
│                                         │
│  4. Redis setup                         │
│     └─ Session store                     │
│     └─ Cache layer                       │
│     └─ Rate limiting                     │
│                                         │
│  5. S3 (or local storage alternative)   │
│     └─ Development bucket/folder         │
│     └─ CV file storage                   │
│     └─ Encryption at rest configuration  │
│                                         │
└─────────────────────────────────────────┘
```

**Deliverable:** Persistent data layer ready

---

### Phase 0.3: Development Tooling

```
┌─────────────────────────────────────────┐
│  Docker Compose & Local Stack           │
├─────────────────────────────────────────┤
│                                         │
│  1. docker-compose.yml                  │
│     ├─ PostgreSQL service                │
│     ├─ Redis service                     │
│     ├─ Backend service (hot reload)      │
│     └─ Frontend service (hot reload)     │
│                                         │
│  2. Environment configuration           │
│     └─ .env.example (template)           │
│     └─ .env.local (development)          │
│     └─ Config validation script          │
│                                         │
│  3. Development scripts                 │
│     ├─ start-dev.sh (Docker Compose up)  │
│     ├─ db-migrate.sh (Run migrations)    │
│     ├─ seed-db.sh (Test data)            │
│     └─ reset-db.sh (Clean slate)         │
│                                         │
│  4. Code quality tools                  │
│     ├─ Black (Python formatter)          │
│     ├─ Flake8 (Python linter)            │
│     ├─ MyPy (Python type checker)        │
│     ├─ ESLint (TypeScript linter)        │
│     ├─ Prettier (Code formatter)         │
│     └─ Pre-commit hooks                  │
│                                         │
│  5. Logging setup                       │
│     └─ Structured JSON logging           │
│     └─ Console output (dev)              │
│     └─ Log level configuration           │
│                                         │
└─────────────────────────────────────────┘
```

**Deliverable:** One-command local development environment

---

## Development Environment

### Local Development Stack

```
Developer Machine
│
├── Nx Workspace (monorepo root)
│   ├── apps/backend (FastAPI + Uvicorn on :8000)
│   ├── apps/frontend (React Vite on :3000)
│   ├── libs/backend-shared
│   └── libs/frontend-shared
│
└── Docker Compose Stack (via docker-compose up)
    ├── PostgreSQL 14 (:5432)
    ├── Redis 7 (:6379)
    └── LocalStack (S3 simulation, :4566)

API Communication:
Frontend (:3000) ←→ Backend (:8000)

Browser Access:
http://localhost:3000 (Frontend)
http://localhost:8000/docs (API Docs)
http://localhost:5432 (DB available for admin tools)
```

### Development Workflow

```
1. Initial Setup
   $ git clone ...
   $ cd digital-twin
   $ pnpm install
   $ poetry install
   $ cp .env.example .env.local
   
2. Start Stack
   $ docker-compose up -d
   $ pnpm nx run-many --target serve --projects=backend,frontend
   
3. View Running Services
   Frontend: http://localhost:3000
   Backend API: http://localhost:8000
   Swagger Docs: http://localhost:8000/docs
   
4. Development (hot reload active)
   Edit code in apps/backend or apps/frontend
   Changes auto-reload in running services
   
5. Database Migrations
   $ pnpm nx run backend:migrate
   
6. Run Tests
   $ pnpm nx test backend
   $ pnpm nx test frontend
```

### Environment Variables

**Backend (.env.local):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/digital_twin_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key-change-in-production
JWT_EXPIRY=86400
CLAUDE_API_KEY=sk-...  # From Anthropic
PUSHOVER_APP_TOKEN=...  # From Pushover
S3_BUCKET=digital-twin-dev
AWS_ENDPOINT_URL=http://localhost:4566  # LocalStack
DEBUG=True
LOG_LEVEL=DEBUG
```

**Frontend (.env.local):**
```
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

---

## Backend Services Implementation Order

### Dependency Graph

```
Phase 0 (Foundation)
│
├─→ Shared Libraries & Database
│   ├─ Database models & migrations
│   ├─ Schemas (Pydantic models)
│   ├─ Exceptions & error handling
│   ├─ Dependencies (auth, db sessions)
│   ├─ Utils (encryption, validation)
│   └─ Logging configuration
│
Phase 1 (Core Services)
│
├─→ Auth Service (E1) — Foundation for all
│   ├─ Owner model & database
│   ├─ Registration endpoint
│   ├─ Login endpoint & JWT
│   ├─ OAuth skeleton (Google/GitHub)
│   ├─ Password reset flow
│   └─ Session management
│
├─→ Profile Service (E2) — Feeds Chat & Config
│   ├─ Profiles model & database
│   ├─ CV upload & storage (S3)
│   ├─ Text extraction pipeline
│   ├─ LLM summary generation (Claude API)
│   ├─ Profile CRUD endpoints
│   └─ LinkedIn integration skeleton
│
├─→ Chat Service (E3) — Core business logic
│   ├─ ChatSessions model & database
│   ├─ Messages model & database
│   ├─ Session creation & retrieval
│   ├─ Message persistence
│   ├─ LLM integration (Claude API)
│   ├─ Response generation
│   ├─ Boundary enforcement
│   └─ Conversation context tracking
│
Phase 2 (Supporting Services)
│
├─→ Config Service (E5) — Configures Twin
│   ├─ DigitalTwinConfigs model
│   ├─ System prompt management
│   ├─ Tone/style configuration
│   ├─ Topic scope management
│   └─ Configuration endpoints
│
├─→ Notification Service (E4) — Async notifications
│   ├─ Notifications model & database
│   ├─ PushoverConfigs model
│   ├─ Pushover API integration
│   ├─ Event handlers (Celery)
│   ├─ Notification preferences
│   └─ Retry logic
│
├─→ Analytics Service (E7) — Optional MVP
│   ├─ ConversationMetrics model
│   ├─ AnalyticsEvents model
│   ├─ Metrics aggregation
│   ├─ Dashboard endpoints
│   └─ Report generation

Cross-Service Dependencies:
- Chat Service requires Config Service (for prompts)
- Chat Service triggers Notification Service (events)
- All services require Auth Service (protected routes)
- All services may access Profile Service (owner context)
```

### Service Implementation Sequence

**Week 3-4: Auth Service (E1)**
```
Output: Owners can register & login

├─ Core functionality
│  ├─ Owner registration (email/password)
│  ├─ Email verification
│  ├─ Login with JWT
│  ├─ Token refresh
│  └─ Logout
│
├─ Security
│  ├─ Password hashing (bcrypt)
│  ├─ Rate limiting on login (5 attempts/15min)
│  ├─ Token expiry (24 hours)
│  └─ CORS configuration
│
├─ Endpoints
│  ├─ POST /auth/register
│  ├─ POST /auth/login
│  ├─ POST /auth/refresh-token
│  ├─ POST /auth/logout
│  ├─ GET /auth/me
│  └─ POST /auth/forgot-password
│
└─ Testing
   ├─ Unit tests for auth logic
   ├─ Integration tests with database
   └─ API endpoint tests
```

**Week 5-6: Profile Service (E2)**
```
Output: Owners can upload CV & AI generates profile summary

├─ CV Processing Pipeline
│  ├─ File upload validation (PDF/DOCX, max 10MB)
│  ├─ Async text extraction
│  ├─ Text cleaning & normalization
│  ├─ LLM summary generation via Claude
│  └─ Owner review & approval
│
├─ Profile Management
│  ├─ Profile CRUD operations
│  ├─ CV storage (S3 encrypted)
│  ├─ Profile summary storage & retrieval
│  ├─ Skills & experience extraction
│  └─ Headline & bio fields
│
├─ Endpoints
│  ├─ POST /profiles/cv/upload
│  ├─ GET /profiles/{owner_id}
│  ├─ PUT /profiles/{owner_id}
│  ├─ GET /profiles/{owner_id}/summary
│  ├─ PUT /profiles/{owner_id}/summary
│  └─ POST /profiles/{owner_id}/process-cv
│
└─ Testing
   ├─ File upload tests
   ├─ Text extraction tests
   ├─ LLM integration tests (mocked)
   └─ Profile persistence tests
```

**Week 7-8: Chat Service (E3)**
```
Output: Visitors can chat with digital twin

├─ Chat Session Management
│  ├─ Create anonymous sessions
│  ├─ Session persistence (30min expiry)
│  ├─ Conversation history
│  └─ Session cleanup
│
├─ Message Processing
│  ├─ Message validation (max 10K chars)
│  ├─ Message persistence
│  ├─ LLM response generation
│  ├─ Streaming responses (SSE or WebSocket)
│  └─ Token usage tracking
│
├─ Response Generation
│  ├─ Load owner profile context
│  ├─ Build system prompt (default)
│  ├─ Call Claude API with context
│  ├─ Stream response to visitor
│  └─ Save message to database
│
├─ Boundary Enforcement
│  ├─ Detect off-topic questions
│  ├─ Professional boundary rules
│  ├─ Redirect to relevant topics
│  └─ Log boundary violations
│
├─ Endpoints
│  ├─ POST /chat/sessions
│  ├─ GET /chat/sessions/{session_id}/messages
│  ├─ POST /chat/sessions/{session_id}/messages
│  ├─ WS /chat/ws/{session_id} (WebSocket option)
│  └─ GET /chat/sse/{session_id}/stream (SSE option)
│
└─ Testing
   ├─ Session lifecycle tests
   ├─ Message persistence tests
   ├─ LLM integration tests (mocked)
   ├─ Boundary detection tests
   └─ Load testing (concurrent sessions)
```

**Week 9: Notification Service (E4)**
```
Output: Owners receive Pushover notifications

├─ Notification Infrastructure
│  ├─ Notification models & database
│  ├─ PushoverConfigs storage
│  ├─ Notification event handlers (Celery)
│  └─ Retry logic (exponential backoff)
│
├─ Pushover Integration
│  ├─ Pushover API client
│  ├─ User key validation
│  ├─ Priority levels (low, normal, high, emergency)
│  ├─ Device targeting
│  └─ Notification sounds
│
├─ Event Handlers
│  ├─ New message event → notify
│  ├─ High-intent detection → high priority notify
│  ├─ Summary ready event → notify
│  ├─ Error events → high priority notify
│  └─ Retry failed notifications
│
├─ Endpoints
│  ├─ POST /notifications/pushover/setup
│  ├─ GET /notifications/preferences
│  ├─ PUT /notifications/preferences
│  ├─ POST /notifications/test
│  └─ GET /notifications/history
│
└─ Testing
   ├─ Pushover API mock tests
   ├─ Event handler tests
   ├─ Notification storage tests
   └─ Retry logic tests
```

**Week 10: Config Service (E5)**
```
Output: Owners can customize digital twin behavior

├─ Configuration Management
│  ├─ System prompt storage & versioning
│  ├─ Tone/style settings
│  ├─ Topic scope (allowed/forbidden)
│  ├─ Brand guidelines (optional)
│  └─ Config validation
│
├─ Endpoints
│  ├─ GET /config/{owner_id}
│  ├─ PUT /config/{owner_id}
│  ├─ GET /config/{owner_id}/system-prompt
│  ├─ PUT /config/{owner_id}/system-prompt
│  ├─ POST /config/{owner_id}/system-prompt/preview
│  └─ GET /config/{owner_id}/system-prompt/versions
│
└─ Testing
   ├─ Config CRUD tests
   ├─ Validation tests
   ├─ Integration with chat service
   └─ Preview generation tests
```

---

## Frontend Implementation Order

### Dependency Graph

```
Phase 0 (Foundation)
│
├─→ Build System & Routing
│   ├─ Vite configuration
│   ├─ React Router setup
│   ├─ Environment variables
│   └─ TypeScript configuration
│
├─→ Shared Components & Hooks
│   ├─ API client (axios/fetch wrapper)
│   ├─ Auth context & hooks
│   ├─ Form components
│   ├─ Button, Input, Modal components
│   ├─ Layout wrapper
│   └─ Error boundaries
│
Phase 1 (Public & Auth Pages)
│
├─→ Public Pages
│   ├─ Homepage
│   ├─ Chat widget (public)
│   ├─ About/Services pages
│   └─ Chat bubble toggle
│
├─→ Auth Pages
│   ├─ Login page
│   ├─ Register page
│   ├─ Password reset flow
│   └─ Email verification page
│
Phase 2 (Owner Dashboard)
│
├─→ Dashboard Shell
│   ├─ Main navigation
│   ├─ Sidebar menu
│   ├─ Dashboard layout
│   └─ Protected routes
│
├─→ Profile Management
│   ├─ Profile display
│   ├─ CV upload form
│   ├─ Summary review & edit
│   ├─ Profile settings
│   └─ LinkedIn setup (skeleton)
│
├─→ Chat Interface
│   ├─ Chat widget refinement
│   ├─ Message display
│   ├─ Message input
│   ├─ Typing indicators
│   └─ Real-time streaming
│
Phase 3 (Analytics & Notifications)
│
├─→ Notification Center
│   ├─ Unread notifications badge
│   ├─ Notification dropdown
│   ├─ Notification preferences
│   └─ Pushover setup page
│
├─→ Conversation Browser
│   ├─ Conversations list
│   ├─ Conversation detail view
│   ├─ Conversation search
│   ├─ Flag/unflag conversations
│   └─ Conversation export (PDF)
│
└─→ Analytics Dashboard (Optional MVP)
    ├─ Engagement metrics
    ├─ Chart visualizations
    ├─ Time period selection
    └─ Export data
```

### Frontend Implementation Sequence

**Week 11: Core Pages & Auth**
```
Output: Owners can register & login, homepage visible

├─ Public Pages
│  ├─ Homepage (marketing)
│  ├─ Navigation bar
│  ├─ Public chat widget (visitors only)
│  └─ About/Services pages
│
├─ Auth Pages
│  ├─ Register form (email/password)
│  ├─ Login form
│  ├─ OAuth buttons (Google/GitHub skeleton)
│  ├─ Password reset flow
│  └─ Email verification message
│
├─ Shared Infrastructure
│  ├─ API client wrapper
│  ├─ Auth context (JWT storage)
│  ├─ Protected route wrapper
│  ├─ Form validation utilities
│  └─ Error handling
│
└─ Testing
   ├─ Auth flow tests
   ├─ Form validation tests
   └─ Public page rendering tests
```

**Week 12: Profile Management**
```
Output: Owners can upload CV & review profile

├─ Dashboard Shell
│  ├─ Sidebar navigation
│  ├─ Dashboard layout
│  ├─ User menu (logout, settings)
│  └─ Breadcrumbs
│
├─ Profile Page
│  ├─ Profile display
│  ├─ CV upload form (drag & drop)
│  ├─ Upload progress indicator
│  ├─ Summary display (read-only after review)
│  ├─ Summary edit form (text editor)
│  └─ Save/cancel buttons
│
├─ Settings Page
│  ├─ Email management
│  ├─ Password change
│  ├─ Account preferences
│  └─ Data export/delete
│
└─ Testing
   ├─ File upload tests
   ├─ Form submission tests
   ├─ Data persistence tests
   └─ Error handling tests
```

**Week 13: Chat Interface**
```
Output: Full chat interface on dashboard

├─ Chat Widget Polish
│  ├─ Message display (left/right bubbles)
│  ├─ Message input textarea
│  ├─ Send button (Enter or click)
│  ├─ Typing indicator (while waiting)
│  ├─ Loading spinner
│  ├─ Timestamp on messages
│  └─ Scroll to latest message
│
├─ Real-Time Features
│  ├─ WebSocket or SSE for streaming responses
│  ├─ Live message delivery
│  ├─ Error state handling
│  └─ Reconnection logic
│
├─ Visitor Experience
│  ├─ Responsive design (mobile/desktop)
│  ├─ Touch-friendly on mobile
│  ├─ Dark mode support (optional)
│  └─ Accessibility (WCAG AA)
│
└─ Testing
   ├─ Message rendering tests
   ├─ WebSocket connection tests
   ├─ Error handling tests
   └─ Mobile responsiveness tests
```

**Week 14: Dashboard & Notifications**
```
Output: Owners can see conversations & receive notifications

├─ Notification Center
│  ├─ Bell icon with unread badge
│  ├─ Notification dropdown
│  ├─ Notification list
│  ├─ Mark as read
│  ├─ Delete notification
│  └─ Pushover setup wizard
│
├─ Conversation Browser
│  ├─ Conversations list (paginated)
│  ├─ List columns: timestamp, duration, preview
│  ├─ Conversation detail view
│  ├─ Full conversation transcript
│  ├─ Flag conversation button
│  ├─ Search/filter conversations
│  └─ Export as PDF
│
├─ Analytics Dashboard (MVP minimal)
│  ├─ Total conversations (all-time, today, week)
│  ├─ Chart: conversations over time
│  ├─ Most common topics
│  ├─ Average conversation length
│  └─ Date range selector
│
└─ Testing
   ├─ Notification display tests
   ├─ Conversation list tests
   ├─ Search/filter tests
   └─ Chart rendering tests
```

---

## Integration & Deployment

### Phase 15: Integration Testing

```
┌──────────────────────────────────────────┐
│  End-to-End User Flows                   │
├──────────────────────────────────────────┤
│                                          │
│  Flow 1: Owner Onboarding                │
│  ├─ Register account                      │
│  ├─ Verify email                          │
│  ├─ Login successfully                    │
│  ├─ Upload CV file                        │
│  ├─ Review generated summary              │
│  ├─ Approve & activate profile            │
│  └─ Verify profile stored                 │
│                                          │
│  Flow 2: Visitor Chat                    │
│  ├─ Access homepage                       │
│  ├─ Open chat widget                      │
│  ├─ Ask professional question             │
│  ├─ Receive AI response                   │
│  ├─ Continue conversation                 │
│  └─ Chat stored in database               │
│                                          │
│  Flow 3: Owner Receives Notification      │
│  ├─ Visitor starts chat                   │
│  ├─ Chat Service triggers event           │
│  ├─ Notification Service sends Pushover   │
│  ├─ Owner receives mobile notification    │
│  ├─ Owner clicks notification             │
│  └─ Views conversation in dashboard       │
│                                          │
│  Flow 4: Owner Customizes Twin            │
│  ├─ Login to dashboard                    │
│  ├─ Go to Settings → Digital Twin Config  │
│  ├─ Edit system prompt                    │
│  ├─ Change tone to "casual"               │
│  ├─ Save configuration                    │
│  ├─ Test with sample question             │
│  └─ Verify response uses new config       │
│                                          │
└──────────────────────────────────────────┘
```

### Phase 16: Deployment Preparation

```
Staging Deployment
│
├─ Database
│  ├─ Production PostgreSQL (managed service)
│  ├─ Production Redis (managed service)
│  ├─ S3 bucket for file storage
│  └─ Database backups configured
│
├─ Backend (Kubernetes)
│  ├─ 3 replicas for backend
│  ├─ Health checks configured
│  ├─ Resource limits set
│  ├─ Logging to CloudWatch/ELK
│  └─ Monitoring with Prometheus
│
├─ Frontend (Kubernetes or CDN)
│  ├─ 2 replicas for frontend
│  ├─ Static assets on CDN
│  ├─ SSL/TLS certificates
│  └─ Gzip compression
│
├─ External Services
│  ├─ Claude API key provisioned
│  ├─ Pushover app token obtained
│  └─ OAuth providers configured (Google, GitHub)
│
├─ Security & Compliance
│  ├─ SSL/TLS for all endpoints
│  ├─ Database encryption at rest
│  ├─ Secrets management (sealed secrets)
│  ├─ API rate limiting configured
│  ├─ CORS policy set
│  └─ Security audit performed
│
├─ CI/CD Pipeline
│  ├─ GitHub Actions configured
│  ├─ Automated tests on PR
│  ├─ Automated build on merge
│  ├─ Automated deployment to staging
│  └─ Manual promotion to production
│
└─ Documentation
   ├─ API documentation (Swagger)
   ├─ User guide for owners
   ├─ Deployment runbook
   └─ Troubleshooting guide
```

---

## Risk & Mitigation

### High Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| **LLM API Rate Limit** | Chat doesn't work | Medium | Implement queue, rate limiting, fallback response |
| **Data Loss** | User data corrupted | Low | Daily backups, encrypted storage, transaction logging |
| **Deployment Failure** | Can't launch MVP | Medium | Staging environment, rollback procedures, health checks |
| **Security Breach** | Data compromise | Low | HTTPS only, secrets management, regular audits |
| **Performance Issues** | Users leave | Medium | Load testing, caching strategy, database optimization |
| **Database Schema Mismatch** | API failures | Medium | Migration testing, backwards compatibility checks |

### Medium Risks

| Risk | Mitigation |
|------|-----------|
| Nx/Python integration issues | Early spike week 1, test both stacks |
| Claude API changes | Use semantic versioning, monitor deprecations |
| Pushover service downtime | Graceful degradation, in-app notification fallback |
| Storage/upload failures | Retry logic, user feedback, logging |

### Mitigation Strategy Timeline

```
Week 1-2: Infrastructure spike
├─ Test Nx + Python + Docker integration
├─ Verify all external service credentials work
└─ Load test database with sample data

Week 3-8: Service development
├─ Unit test every service endpoint
├─ Mock external APIs (Claude, Pushover)
└─ Weekly integration checkpoints

Week 9-10: Integration phase
├─ Test cross-service communication
├─ Staging environment testing
└─ Performance profiling

Week 11-14: Frontend phase
├─ Browser compatibility testing
├─ Mobile responsiveness testing
└─ Accessibility audit

Week 15-16: Pre-launch
├─ Security penetration testing
├─ Data backup & recovery drill
├─ Rollback procedure testing
└─ Alpha user onboarding
```

---

## Success Metrics

### MVP Completion Criteria

**Functional:**
- ✅ Owner can register & verify email
- ✅ Owner can upload CV & review AI summary
- ✅ Visitor can ask questions via chat widget
- ✅ Digital twin responds with contextual answers
- ✅ Owner receives Pushover notification on new chat
- ✅ Owner can see conversations in dashboard
- ✅ Owner can customize system prompt & tone

**Technical:**
- ✅ Backend API 95%+ uptime during testing
- ✅ Chat responses < 5 seconds (p95)
- ✅ Database backups automated daily
- ✅ All secrets encrypted & secured
- ✅ Code coverage > 80% (unit tests)
- ✅ Zero data loss incidents

**User Experience:**
- ✅ Registration flow < 2 minutes
- ✅ CV upload & processing < 5 minutes
- ✅ Chat loads < 2 seconds
- ✅ Mobile responsive (tested on 3+ devices)
- ✅ No console errors on main flows

**Launch Readiness:**
- ✅ Alpha users onboarded (10-20 testers)
- ✅ Documentation complete
- ✅ Deployment runbook tested
- ✅ Incident response procedures documented
- ✅ Monitoring & alerting configured

---

---

## Pull Request Management Guidelines

### Strategy & Philosophy

Pull Requests are the unit of work for the project. Each PR should:
- Represent a **logical, reviewable chunk of work** (not too large, not too small)
- Have a **clear scope** tied to a specific feature/fix
- Be **independently testable** (unit tests included)
- Include **documentation** of changes and rationale
- Enable **code review** and knowledge sharing

### PR Sizing Guidelines

| PR Size | Scope | Examples | Review Time |
|---------|-------|----------|------------|
| **Small (50-200 lines)** | Single focused task | Add endpoint, fix bug, refactor utility | 15-30 min |
| **Medium (200-500 lines)** | Feature component | API service layer, UI component, migration | 30-60 min |
| **Large (500-1000 lines)** | Complete feature | Full service with tests, complex flow | 60-120 min |
| **Too Large (>1000 lines)** | ❌ Split into multiple PRs | Multiple services, major refactor | N/A |
| **Too Small (<50 lines)** | ❌ Combine or reconsider | Single variable rename, comment fix | N/A |

**Exception:** Infrastructure setup (docker-compose, CI/CD) may be larger but should be reviewed carefully.

---

### PR Lifecycle & Structure

### Stage 1: Pre-Development Planning

**Before creating branch:**

```
1. Identify the feature/task
   ├─ What's being built?
   ├─ Which service/component?
   └─ Estimated scope (small/medium/large)

2. Create PR tracking folder
   Location: ./pr-work/{issue-number}-{feature-name}/
   
   Structure:
   pr-work/
   └── E1-001-auth-registration/          # Branch name: e1/001-auth-registration
       ├── PR_DESCRIPTION.md               # PR description (NOT committed)
       ├── CHECKLIST.md                    # Development checklist
       ├── FINDINGS.md                     # Code review findings log
       ├── DESIGN_NOTES.md                 # Architecture/design decisions
       ├── TEST_PLAN.md                    # Testing approach & results
       └── ARTIFACTS/                      # Related diagrams, API specs, etc.
           ├── api-schema.json
           ├── sequence-diagram.md
           └── test-results.txt

3. Create feature branch
   Naming convention: {service}/{issue}-{feature}
   Examples:
   - e1/001-auth-registration
   - e2/003-cv-upload
   - e3/005-chat-session
   - frontend/012-chat-widget
```

**PR_DESCRIPTION.md (template, not committed):**

```markdown
# PR Description: {Feature Name}

## Objective
{Clear 2-3 sentence description of what this PR delivers}

## Changes
- {Change 1}
- {Change 2}
- {Change 3}

## Type
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Test
- [ ] Docs
- [ ] Infrastructure

## Scope
- Services affected: {Service names}
- Files changed: ~{number} files
- Lines added: ~{number} +, ~{number} -

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done
- [ ] No regressions found

## Checklist
- [ ] Code follows project conventions
- [ ] No console warnings/errors
- [ ] Secrets not committed
- [ ] Database migrations included (if applicable)
- [ ] API docs updated
- [ ] Tests pass locally
- [ ] CI/CD passing

## Reviewers
@reviewer1 @reviewer2

## Related Issues
Fixes #123
Relates to #124
```

---

### Stage 2: Development

**Workflow:**

```bash
# 1. Create feature branch (locally)
git checkout -b e1/001-auth-registration

# 2. Work on feature
# - Write code
# - Add unit tests
# - Add integration tests
# - Update documentation

# 3. Keep branch updated
git fetch origin main
git rebase origin/main  # Keep history clean

# 4. Commit regularly with clear messages
git commit -m "E1-001: Add registration endpoint

- Implements POST /auth/register
- Validates email format & password strength
- Sends verification email via SendGrid
- Tests: 8 unit tests, 2 integration tests
- Refs #001"

# 5. Run local tests
nx test backend --projects=auth

# 6. Run linting & formatting
nx lint backend
nx format:write

# 7. Push when ready for review
git push origin e1/001-auth-registration
```

**Commit Message Convention:**

```
{Service}-{Issue}: {Brief description}

{Detailed explanation}
- What changed
- Why it changed
- Any important notes

Tests: {number} unit, {number} integration
Refs #{issue-number}
```

---

### Stage 3: Create Pull Request

**Before pushing to GitHub:**

```
1. Finalize PR_DESCRIPTION.md
   ├─ Objective is clear
   ├─ All changes documented
   ├─ Testing section complete
   └─ Checklist items verified

2. Verify branch is clean
   ├─ No uncommitted changes
   ├─ All tests passing locally
   ├─ No merge conflicts
   └─ Branch up-to-date with main

3. Create PR in GitHub
   ├─ Title: {Service}-{Issue}: {Feature}
   ├─ Description: Copy from PR_DESCRIPTION.md
   ├─ Labels: type/feature, service/auth, size/medium
   ├─ Assignee: self
   ├─ Reviewers: 1-2 team members
   └─ Link issues: Fixes #001
```

**PR Title Format:**

```
[{Service}] {Feature Name} (#{issue})

Examples:
[E1] Add owner registration flow (#001)
[E2] Implement CV text extraction (#003)
[E3] Add chat session management (#005)
[Frontend] Create chat widget component (#012)
```

**PR Description (in GitHub):**

Use the same content from PR_DESCRIPTION.md

---

### Stage 4: Code Review

**Reviewer Responsibilities:**

```
1. Understand the change
   ├─ Read PR description
   ├─ Review DESIGN_NOTES.md if provided
   └─ Ask for clarification if needed

2. Review code quality
   ├─ Follows project conventions
   ├─ No code duplication
   ├─ Error handling present
   ├─ Proper logging
   └─ Security implications checked

3. Review test coverage
   ├─ Unit tests adequate (>80% coverage)
   ├─ Integration tests for new endpoints
   ├─ Edge cases covered
   └─ No test skips (`.skip`, `.only`)

4. Review documentation
   ├─ Code comments where needed (why, not what)
   ├─ API docs updated
   ├─ Database migrations documented
   └─ Breaking changes noted

5. Log findings
   Location: pr-work/{pr-folder}/FINDINGS.md
   Format:
   ```
   ## Code Review Findings

   ### [CRITICAL] Issue Name
   Location: file.py:123
   - Description of issue
   - Suggested fix
   - Impact if not fixed

   ### [MEDIUM] Issue Name
   - ...

   ### [LOW] Issue Name
   - ...

   ### Approved Items
   - ✅ Test coverage adequate
   - ✅ No security issues
   - ✅ Performance acceptable
   ```

6. Approve or request changes
   ├─ Approve (if all good)
   ├─ Comment (for discussion)
   └─ Request changes (for blocking issues)
```

**Review Priorities:**

1. **Critical** (block merge):
   - Data loss risk
   - Security vulnerability
   - Breaking API change
   - Missing tests
   - Database corruption risk

2. **Medium** (should fix):
   - Performance concern
   - Code duplication
   - Incomplete error handling
   - Poor naming

3. **Low** (nice to have):
   - Style improvements
   - Documentation clarity
   - Code organization suggestions

---

### Stage 5: Addressing Feedback

**Author Workflow:**

```
1. Review all comments
   ├─ Understand feedback
   ├─ Ask for clarification if needed
   └─ Agree/disagree with changes

2. Make required changes
   ├─ Fix critical issues
   ├─ Fix medium issues
   ├─ Consider low suggestions
   └─ Write new tests if needed

3. Commit changes clearly
   git commit -m "E1-001: Address review feedback

   - Extracted validation logic to utils
   - Added edge case tests for email validation
   - Improved error messages per review
   
   Refs #001"

4. Push changes
   git push origin e1/001-auth-registration

5. Reply to comments
   ├─ Explain what was changed
   ├─ Link to relevant commit
   ├─ Mark resolved comments
   └─ Ask for re-review if substantial changes

6. Repeat until approved
```

**Don't:**
- ❌ Force push (rewrite history) during review
- ❌ Merge with unresolved comments
- ❌ Ignore feedback
- ❌ Create new commits for minor fixes (squash if needed)

---

### Stage 6: Merge & Cleanup

**Merge Checklist:**

```
Before merging:
├─ [ ] All reviewers approved (min 1-2)
├─ [ ] All CI/CD checks passing
├─ [ ] No merge conflicts
├─ [ ] Commit history is clean
├─ [ ] No debug code left
├─ [ ] Database migrations tested
└─ [ ] Tests passing on CI

Merge strategy:
├─ Use "Squash and merge" for small PRs (<300 lines)
├─ Use "Create a merge commit" for larger PRs
└─ NEVER use "Rebase and merge" (maintains commit history)

Commit message after merge:
{PR-Title} ({PR-Number})

{PR description summary}
```

**After Merge:**

```bash
# 1. Delete branch locally
git branch -d e1/001-auth-registration

# 2. Delete branch on GitHub
git push origin --delete e1/001-auth-registration

# 3. Update local main
git checkout main
git pull origin main

# 4. Archive PR folder (locally)
mv pr-work/E1-001-auth-registration pr-archive/2026-07-20-E1-001/

# 5. Link archived folder in PR
Comment on closed PR:
"PR artifacts archived at: pr-archive/2026-07-20-E1-001/"
```

---

### PR Folder Structure (Complete Example)

```
pr-work/
└── E1-001-auth-registration/
    ├── PR_DESCRIPTION.md                 # Pre-commit (main doc)
    ├── CHECKLIST.md                      # Progress tracking
    ├── DESIGN_NOTES.md                   # Architecture decisions
    ├── FINDINGS.md                       # Code review log
    ├── TEST_PLAN.md                      # Testing strategy
    │
    ├── ARTIFACTS/
    │   ├── api-schema.json               # OpenAPI spec
    │   ├── database-schema.sql           # New tables/columns
    │   ├── sequence-diagram.md           # Flow diagram
    │   ├── test-results.txt              # Local test output
    │   └── performance-analysis.md       # If applicable
    │
    └── REVIEW_COMMENTS/
        └── round-1.md                    # Reviewer comments log
```

**Files NOT committed to git:**
```
.gitignore additions:
pr-work/
pr-archive/
```

---

### Metrics & Standards

**Quality Gates (required for merge):**

| Metric | Target | Checked By |
|--------|--------|-----------|
| Test Coverage | > 80% | CI (coverage report) |
| Lint Passing | 0 errors | CI (flake8, ESLint) |
| Type Check | 0 errors | CI (mypy, TypeScript) |
| Performance | No regression | Manual testing |
| Security Scan | 0 critical | CI (bandit, npm audit) |
| Code Review | ≥1 approval | GitHub |
| Documentation | Updated | Manual review |

**Expected PR Metrics (across project):**

```
Small PRs (50-200 lines):     60% of PRs
Medium PRs (200-500 lines):   35% of PRs
Large PRs (500-1000 lines):    5% of PRs

Average review time: 45 minutes
Average merge time: 24-48 hours from creation
Approval rate: 85%+ (low rejection rate)
```

---

### Common Patterns & Anti-Patterns

**✅ Good PR Patterns:**

```
1. Single service feature
   Title: [E1] Add password reset endpoint
   Scope: Only Auth Service changes
   
2. Focused refactor
   Title: [Shared] Extract email validation utils
   Scope: Affects 2 files, no behavior change
   
3. Bug fix
   Title: [E3] Fix chat message timestamp encoding
   Scope: One-liner fix + test
   
4. Test coverage
   Title: [E2] Add tests for CV text extraction
   Scope: Test file only, 200 lines
```

**❌ Anti-Patterns to Avoid:**

```
1. Mega PR
   Title: Complete Auth Service Implementation
   Problem: 2000+ lines, 15 files, hard to review
   Solution: Split into: Registration → Login → Password Reset → OAuth
   
2. Mixed concerns
   Title: Fix chat bug + Refactor database layer + Update docs
   Problem: Changes in 5 services, unclear scope
   Solution: One PR per concern
   
3. WIP branch
   Title: Work in progress - dont merge yet
   Problem: Merged anyway, breaks CI
   Solution: Use Draft PR until ready
   
4. Undocumented changes
   Title: Fix stuff
   Problem: No description, unclear what changed
   Solution: Clear PR description required
```

---

### GitHub Command Line (`gh`) Workflow

**Why `gh`?**
- Faster than web UI
- Scriptable & automatable
- Consistent workflow across team
- Integrates with local git
- Reduces context switching

**Installation & Setup:**

```bash
# Install gh (macOS)
brew install gh

# Authenticate
gh auth login
# Follow prompts to authenticate with GitHub

# Verify setup
gh auth status
```

**Common Commands:**

```bash
# ========== PR Creation ==========

# Create PR (interactive)
gh pr create

# Create PR with details (preferred)
gh pr create --title "[E1] Add auth registration (#001)" \
             --body "$(cat pr-work/E1-001-auth-registration/PR_DESCRIPTION.md)" \
             --reviewer @reviewer1,@reviewer2 \
             --label type/feature,service/auth,size/medium

# Create as draft (not ready yet)
gh pr create --draft

# ========== PR Management ==========

# List PRs (current branch)
gh pr view

# List all open PRs
gh pr list --state open

# List PRs for review
gh pr list --state open --search "review-requested:@me"

# View specific PR
gh pr view {number}

# View PR in browser
gh pr view {number} --web

# ========== PR Workflow ==========

# Check PR status
gh pr status

# Add reviewer
gh pr edit {number} --add-reviewer @reviewer1,@reviewer2

# Add labels
gh pr edit {number} --add-label type/feature,size/medium

# Link issue
gh pr edit {number} --add-label fixes-{issue-number}

# Set title
gh pr edit {number} --title "New title"

# Set body/description
gh pr edit {number} --body "New description"

# ========== Code Review ==========

# Review PR (interactive)
gh pr review {number}

# Approve PR
gh pr review {number} --approve

# Request changes
gh pr review {number} --request-changes --body "Please address feedback"

# Comment on PR
gh pr comment {number} --body "Great work! Just one thing..."

# View PR comments
gh pr view {number} --comments

# ========== Issue Management ==========

# Create issue
gh issue create --title "E1-001: Fix auth bug" \
                --body "Description..." \
                --label bug,service/auth

# List issues
gh issue list --state open

# View issue
gh issue view {number}

# Add comment to issue
gh issue comment {number} --body "Addressed in PR #456"

# Close issue
gh issue close {number}

# ========== Merging ==========

# Merge PR (auto-detect squash/merge)
gh pr merge {number}

# Merge with squash (for small PRs)
gh pr merge {number} --squash

# Merge with merge commit (for larger PRs)
gh pr merge {number} --merge

# Merge and delete branch
gh pr merge {number} --delete-branch

# Merge and close related issue
gh pr merge {number} --squash --delete-branch
```

**Workflow Scripts (Create as shell functions):**

```bash
# Add to ~/.zshrc or ~/.bashrc

# Create new feature branch with PR folder
pr_start() {
    local service=$1
    local issue=$2
    local feature=$3
    
    if [ -z "$service" ] || [ -z "$issue" ] || [ -z "$feature" ]; then
        echo "Usage: pr_start {service} {issue} {feature}"
        echo "Example: pr_start e1 001 auth-registration"
        return 1
    fi
    
    local branch="${service}/${issue}-${feature}"
    local folder="pr-work/${service^^}-${issue}-${feature}"
    
    # Create folder structure
    mkdir -p "${folder}/ARTIFACTS"
    
    # Create templates
    cat > "${folder}/PR_DESCRIPTION.md" << 'EOF'
# PR Description: {Feature}

## Objective
{Description}

## Changes
- {Change 1}

## Type
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Test
- [ ] Docs

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Code follows conventions
- [ ] No console warnings/errors
- [ ] Tests pass locally
- [ ] CI/CD passing
EOF

    cat > "${folder}/CHECKLIST.md" << 'EOF'
# Development Checklist

- [ ] Code implemented
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Local tests passing
- [ ] Linting passing
- [ ] Type checking passing
- [ ] PR description complete
- [ ] Reviewers assigned
EOF

    # Create branch
    git checkout -b "${branch}"
    
    echo "✅ PR setup complete!"
    echo "   Branch: ${branch}"
    echo "   Folder: ${folder}"
    echo "   Next: Make changes and push"
}

# Create PR from command line
pr_create() {
    local issue=$1
    local description_file="pr-work/*/PR_DESCRIPTION.md"
    
    if [ ! -f "$description_file" ]; then
        echo "❌ PR_DESCRIPTION.md not found"
        return 1
    fi
    
    gh pr create --title "[$(git branch --show-current | cut -d/ -f1 | tr a-z A-Z)] $(git branch --show-current | cut -d/ -f2-) (#${issue})" \
                 --body "$(cat $description_file)" \
                 --draft
    
    echo "✅ PR created (draft mode)"
    echo "   Review and mark as ready when complete"
}

# Review PR locally
pr_review() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        echo "Usage: pr_review {pr_number}"
        return 1
    fi
    
    # Checkout PR branch locally
    gh pr checkout "${pr_number}"
    
    echo "✅ PR #${pr_number} checked out"
    echo "   Run tests locally, review code"
}

# Merge PR and cleanup
pr_merge() {
    local pr_number=$1
    local squash=${2:-true}
    
    if [ "$squash" = "true" ]; then
        gh pr merge "${pr_number}" --squash --delete-branch
    else
        gh pr merge "${pr_number}" --merge --delete-branch
    fi
    
    git checkout main
    git pull origin main
    
    echo "✅ PR #${pr_number} merged and cleaned up"
}
```

**Typical PR Workflow (using `gh`):**

```bash
# 1. Start feature
pr_start e1 001 auth-registration

# 2. Do work...
# - Implement feature
# - Write tests
# - Update docs

# 3. Commit regularly
git commit -m "E1-001: Add registration endpoint..."

# 4. Push and create PR
git push origin e1/001-auth-registration
pr_create 001

# 5. Mark as ready (from web or CLI)
gh pr ready --number {pr_number}

# 6. Link issues
gh pr edit {pr_number} --add-label fixes-001

# 7. Wait for review
gh pr status

# 8. Address feedback
# - Make changes
# - Push updates
git push origin e1/001-auth-registration

# 9. Get approval
gh pr view {pr_number}

# 10. Merge
pr_merge {pr_number}
```

---

### Tools & Automation

**GitHub PR Templates:**

Create: `.github/pull_request_template.md`

```markdown
## Description
{Clear summary of changes}

## Type
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Test
- [ ] Docs

## Related Issues
Fixes #123
Relates to #456

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Code follows conventions
- [ ] No console warnings/errors
- [ ] Tests passing
- [ ] Documentation updated

## Screenshots (if applicable)
{UI changes should include screenshots}
```

**Branch Protection Rules:**

```
GitHub Settings → Branches → main

Required:
✅ Require pull request reviews (min 1)
✅ Dismiss stale pull request approvals
✅ Require status checks to pass (CI/CD)
✅ Require branches to be up to date
✅ Restrict who can push to main
```

**CI/CD Checks (GitHub Actions):**

```yaml
on pull_request:
  - Run linting (flake8, ESLint)
  - Run type checking (mypy, TypeScript)
  - Run tests with coverage
  - Security scan (bandit, npm audit)
  - Check for secrets (detect-secrets)
  - Build Docker image
```

---

### Training & Onboarding

**For New Team Members:**

1. Read this guideline document
2. Review 3-5 existing PRs (merged)
3. Create first PR (small, simple task)
4. Get code review feedback
5. Refine process with team

**PR Review Template for First Time:**

```markdown
First PR Checklist:
- [ ] Branch naming correct? (service/issue-name)
- [ ] PR description complete?
- [ ] Commit messages clear?
- [ ] Code style consistent?
- [ ] Tests passing?
- [ ] No merge conflicts?
- [ ] Reviewed by >1 person?
- [ ] All feedback addressed?
```

---

### Summary: PR Workflow Diagram

```
┌─────────────────────┐
│  Plan & Scope PR    │  Create pr-work/ folder
│  (Before branch)    │  Write PR_DESCRIPTION.md
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Create Branch      │  Branch: service/issue-name
│  (Start work)       │  Push initial commit
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Develop Feature    │  Commit regularly
│  (Week 1-2)         │  Run tests locally
│                     │  Update documentation
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Create PR          │  Copy description to GitHub
│  (Push to GitHub)   │  Add reviewers
│                     │  Link related issues
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Code Review        │  Reviewer checks quality
│  (1-2 days)         │  Log findings in FINDINGS.md
│                     │  Approve or request changes
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Address Feedback   │  Make requested changes
│  (As needed)        │  Push updates
│                     │  Reply to comments
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Merge PR           │  All checks passing
│  (After approval)   │  Squash or merge commit
│                     │  Close related issues
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Cleanup            │  Delete branch
│  (Post-merge)       │  Archive pr-work/ folder
│                     │  Update project board
└─────────────────────┘
```

---

## Next Steps

1. **Approve Master Plan** — Confirm timeline & approach
2. **Allocate Resources** — Assign team members to phases
3. **Create Detailed Phase 0 Plan** — Break down infrastructure setup
4. **Setup CI/CD** — GitHub Actions initial configuration
5. **Provision Cloud Resources** — AWS/GCP/DigitalOcean accounts
6. **Configure Branch Protection** — Set up GitHub PR requirements
7. **Begin Phase 0 (Week 1)** — Infrastructure sprint
