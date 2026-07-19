# Technical Design Document
## Digital Twin AI Assistant Platform

**Version:** 1.0  
**Date:** 2026-07-19  
**Status:** Draft  

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [System Design](#system-design)
4. [Database Design](#database-design)
5. [API Specifications](#api-specifications)
6. [Security Architecture](#security-architecture)
7. [Deployment & Infrastructure](#deployment--infrastructure)
8. [Development Guidelines](#development-guidelines)

---

## Architecture Overview

### Architectural Pattern: Microservices with Monolithic Database

The system follows a microservices architecture with independent services communicating via REST APIs and message queues, backed by a single normalized database.

```
┌────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                     │
│  (React Frontend / Next.js - Single Page Application)     │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTP/HTTPS
                       ↓
┌────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
│  (Express.js / FastAPI - Rate Limiting, Auth, Routing)    │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │          │
       ↓          ↓          ↓          ↓          ↓
┌────────────┐ ┌────────┐ ┌───────┐ ┌──────────┐ ┌──────┐
│    AUTH    │ │PROFILE │ │ CHAT  │ │ANALYTICS │ │CONFIG│
│  SERVICE   │ │SERVICE │ │SERVICE│ │ SERVICE  │ │SERV. │
│(Port 3001) │ │(3002)  │ │(3003) │ │ (3004)   │ │(3005)│
└─────┬──────┘ └────┬───┘ └───┬───┘ └────┬─────┘ └──┬───┘
      │             │         │          │          │
      └─────────────┼─────────┼──────────┼──────────┘
                    │         │          │
                    ↓         ↓          ↓
             ┌──────────────────────────────┐
             │   MESSAGE QUEUE (Redis)      │
             │  (Event Publishing/Consume)  │
             └─────────────┬────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ↓                 ↓                  ↓
    ┌────────────┐  ┌─────────────┐  ┌────────────────┐
    │ POSTGRESQL │  │   REDIS     │  │  S3 (FILE ST.) │
    │  DATABASE  │  │   CACHE     │  │   (Encrypted)  │
    └────────────┘  └─────────────┘  └────────────────┘
         │
         ├─────┬──────┬────────┬──────┬─────────┐
         │     │      │        │      │         │
         ↓     ↓      ↓        ↓      ↓         ↓
       users chat  profiles  sessions config analytics
```

### Key Design Principles

1. **Separation of Concerns** — Each service has a single responsibility
2. **Stateless Services** — Services can be scaled horizontally
3. **Database Normalization** — Single source of truth in database
4. **Event-Driven** — Services communicate via message queue
5. **API-First** — All interactions through well-defined APIs
6. **Security by Default** — Encryption, authentication, authorization at every layer

---

## Technology Stack

### Backend
| Layer | Technology | Reason |
|-------|-----------|--------|
| **Language** | Python 3.11+ | AI/ML ecosystem, rapid development, readability |
| **Web Framework** | FastAPI | Async support, auto-generated docs, type hints |
| **ORM** | SQLAlchemy | Database abstraction, migration management |
| **Task Queue** | Celery + Redis | Async job processing, event handling |
| **Authentication** | JWT + bcrypt | Stateless auth, password security |
| **API Docs** | OpenAPI/Swagger | Auto-generated, standards-compliant |

### Database
| Component | Technology | Reason |
|-----------|-----------|--------|
| **Primary DB** | PostgreSQL 14+ | ACID compliance, JSON support, scalability |
| **Cache** | Redis 7+ | Session storage, rate limiting, real-time data |
| **File Storage** | AWS S3 | Scalability, encryption, backup, CDN integration |

### Frontend
| Component | Technology | Reason |
|-----------|-----------|--------|
| **Framework** | React 18+ | Component-based, large ecosystem, performance |
| **Build Tool** | Vite or Next.js | Fast development, SSR optional, modern tooling |
| **State Mgmt** | React Query + Zustand | Server/client state management, simplicity |
| **Styling** | Tailwind CSS | Utility-first, responsive, maintainable |
| **Chat UI** | Custom Component | Real-time messaging, typing indicators |

### AI/ML
| Component | Technology | Reason |
|-----------|-----------|--------|
| **LLM Provider** | Claude API | High-quality outputs, cost-effective, safety features |
| **Embeddings** | Sentence Transformers | Local embeddings for relevance scoring |
| **Document Processing** | PyPDF2 + python-docx | CV parsing and text extraction |

### Notifications
| Component | Technology | Reason |
|-----------|-----------|--------|
| **Push Notifications** | Pushover API | Reliable, simple, cross-platform (iOS/Android/Desktop) |
| **Notification Client** | httpx | Async HTTP client for Pushover API calls |

### DevOps & Infrastructure
| Component | Technology | Reason |
|-----------|-----------|--------|
| **Container** | Docker | Consistent environments, deployment simplicity |
| **Orchestration** | Docker Compose (dev), Kubernetes (prod) | Scalability, reliability |
| **CI/CD** | GitHub Actions | GitHub-native, free, feature-rich |
| **Monitoring** | Prometheus + Grafana | Open-source, comprehensive metrics |
| **Logging** | ELK Stack (Elasticsearch) | Centralized logging, searchability |
| **Cloud Hosting** | AWS / GCP / DigitalOcean | Scalability, managed services |

---

## System Design

### 1. Authentication Service (E1)

**Purpose:** Handle user registration, login, session management, and OAuth

**Responsibilities:**
- Register new owners with email/password
- OAuth integration (Google, GitHub)
- JWT token generation and validation
- Session management
- Password reset workflow
- Rate limiting on login attempts

**Key Endpoints:**
```
POST   /auth/register          # Register new owner
POST   /auth/login             # Email/password login
POST   /auth/oauth/google      # Google OAuth callback
POST   /auth/oauth/github      # GitHub OAuth callback
POST   /auth/refresh-token     # Refresh JWT
POST   /auth/logout            # Logout (invalidate token)
POST   /auth/forgot-password   # Request password reset
POST   /auth/reset-password    # Reset password via token
GET    /auth/me                # Get current user info
```

**Database Models:**
```python
class Owners(Base):
    id: UUID
    email: str (unique, indexed)
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool
    email_verified: bool
    oauth_provider: str (nullable)
    oauth_id: str (nullable)
    created_at: DateTime
    updated_at: DateTime
    
class OwnerSessions(Base):
    id: UUID
    owner_id: UUID (foreign key)
    token: str (unique, indexed)
    expires_at: DateTime
    created_at: DateTime
```

**Environment Variables:**
```
AUTH_JWT_SECRET=<secret>
AUTH_JWT_EXPIRY=86400  # 24 hours
AUTH_PASSWORD_MIN_LENGTH=8
AUTH_LOGIN_MAX_ATTEMPTS=5
AUTH_LOGIN_LOCKOUT_DURATION=900  # 15 minutes
GOOGLE_OAUTH_CLIENT_ID=<id>
GOOGLE_OAUTH_CLIENT_SECRET=<secret>
GITHUB_OAUTH_CLIENT_ID=<id>
GITHUB_OAUTH_CLIENT_SECRET=<secret>
```

---

### 2. Profile Service (E2)

**Purpose:** Handle CV uploads, text extraction, profile processing, and management

**Responsibilities:**
- Handle CV file uploads
- Extract text from PDF/DOCX
- Generate profile summary via LLM
- Store and manage profile data
- LinkedIn integration
- Profile validation

**Key Endpoints:**
```
POST   /profiles/cv/upload      # Upload CV file
GET    /profiles/{owner_id}/cv  # Download CV
POST   /profiles/{owner_id}/process-cv  # Process uploaded CV
GET    /profiles/{owner_id}/summary     # Get profile summary
PUT    /profiles/{owner_id}/summary     # Update summary
GET    /profiles/{owner_id}     # Get full profile
PUT    /profiles/{owner_id}     # Update profile
POST   /profiles/{owner_id}/linkedin/auth  # Link LinkedIn
GET    /profiles/{owner_id}/linkedin      # Get LinkedIn data
DELETE /profiles/{owner_id}/linkedin      # Unlink LinkedIn
```

**Database Models:**
```python
class Profiles(Base):
    id: UUID
    owner_id: UUID (foreign key, unique)
    bio: str
    headline: str
    cv_file_path: str
    cv_extracted_text: str
    profile_summary: dict  # JSON
    skills: list[str]
    experience_years: int
    linkedin_profile_url: str (nullable)
    linkedin_data: dict (nullable, JSON)
    created_at: DateTime
    updated_at: DateTime
    
class CVProcessingJobs(Base):
    id: UUID
    user_id: UUID (foreign key)
    cv_file_path: str
    status: Enum["pending", "processing", "completed", "failed"]
    extracted_text: str (nullable)
    error_message: str (nullable)
    created_at: DateTime
    updated_at: DateTime
```

**File Storage:**
```
S3 Structure:
s3://digital-twin-files/
├── cv-uploads/{user_id}/{filename}  (encrypted)
├── cv-extracted/{user_id}/text.txt  (encrypted)
└── temp/{job_id}/                   (cleanup after 24h)
```

**Async Processing:**
```python
# CV processing job via Celery
@celery_app.task
def process_cv(cv_file_path: str, user_id: str):
    # 1. Extract text
    # 2. Clean text
    # 3. Generate summary via LLM
    # 4. Update database
    # 5. Publish event: "profile_summary_generated"
```

---

### 3. Chat Service (E3)

**Purpose:** Handle chat messages, LLM integration, response generation

**Responsibilities:**
- Create/manage chat sessions
- Store and retrieve messages
- Integrate with LLM API
- Enforce professional boundaries
- Stream responses to frontend
- Maintain conversation context

**Key Endpoints:**
```
POST   /chat/sessions           # Create new chat session
GET    /chat/sessions/{session_id}/messages  # Get messages
POST   /chat/sessions/{session_id}/messages  # Send message
GET    /chat/sessions/{session_id}           # Get session info
DELETE /chat/sessions/{session_id}           # Delete session
```

**WebSocket/SSE Support:**
```
WS /chat/ws/{session_id}  # WebSocket for real-time chat
GET /chat/sse/{session_id}/message-stream  # Server-sent events
```

**Database Models:**
```python
class ChatSessions(Base):
    id: UUID
    owner_id: UUID (foreign key, indexed)
    session_id: str (unique, indexed)  # Anonymous session ID
    visitor_ip: str (nullable, hashed for privacy)
    visitor_email: str (nullable, encrypted)
    created_at: DateTime
    updated_at: DateTime
    expires_at: DateTime
    
class Messages(Base):
    id: UUID
    session_id: UUID (foreign key, indexed)
    sender: Enum["visitor", "ai"]
    content: str
    tokens_used: int (nullable)
    created_at: DateTime
    
class ConversationContexts(Base):
    id: UUID
    session_id: UUID (foreign key, unique)
    messages_summary: str
    key_topics: list[str]
    sentiment: str
    flagged: bool
    flag_reason: str (nullable)
    updated_at: DateTime
```

**LLM Integration:**
```python
async def generate_response(session_id: str, message: str, profile_context: dict):
    # 1. Retrieve profile
    # 2. Build system prompt
    # 3. Retrieve conversation history
    # 4. Call LLM API
    # 5. Stream response
    # 6. Save message to DB
    # 7. Update conversation context
    # 8. Publish event: "message_processed"
    
system_prompt = f"""
### Your role
You are a digital twin representing {profile.headline}.
You answer questions about their career, background, skills, and experience.

### Context
{profile.profile_summary}

LinkedIn: {profile.linkedin_profile_url}

### Rules
1. Stay professional and engaging
2. Only answer career-related questions
3. If you don't know, say so
4. Redirect non-professional questions
5. Be concise (max 500 words per response)

### Important
Always acknowledge being an AI digital twin if asked.
"""
```

**Message Processing Pipeline:**
```
Visitor Message → Validation → Boundary Check → LLM Call → Response Stream → Save DB
        ↓
    - Max 10K chars
    - No SQL injection
    - Rate limit check
```

---

### 4. Analytics Service (E7)

**Purpose:** Track metrics, generate reports, identify leads

**Responsibilities:**
- Aggregate conversation metrics
- Calculate engagement statistics
- Identify high-intent conversations
- Generate reports
- Track visitor patterns

**Key Endpoints:**
```
GET /analytics/dashboard          # Main dashboard metrics
GET /analytics/conversations      # Conversation list with filters
GET /analytics/trends             # Engagement trends (chart data)
GET /analytics/topics             # Most common topics
GET /analytics/leads              # Identified leads
GET /analytics/export             # Export data (CSV/JSON)
```

**Database Models:**
```python
class ConversationMetrics(Base):
    id: UUID
    session_id: UUID (foreign key)
    owner_id: UUID (foreign key)
    conversation_length: int  # number of message pairs
    duration_seconds: int
    visitor_country: str (nullable)
    visitor_device: str (nullable)  # mobile, desktop
    high_intent_score: float  # 0-1
    flagged_as_lead: bool
    created_at: DateTime
    
class AnalyticsEvents(Base):
    id: UUID
    owner_id: UUID (foreign key)
    event_type: str  # conversation_started, message_sent, conversation_ended
    event_data: dict (JSON)
    created_at: DateTime
```

**Analytics Queries (Redis Cache):**
```python
# Cached for 1 hour
def get_dashboard_metrics(owner_id: str, days: int = 30):
    return {
        "total_conversations": int,
        "conversations_today": int,
        "active_conversations": int,
        "avg_conversation_length": float,
        "avg_response_time": float,  # seconds
        "high_intent_conversations": int,
        "visitor_retention": float,  # 0-1
    }

def get_conversation_list(owner_id: str, limit: int = 50, offset: int = 0):
    return [
        {
            "id": str,
            "timestamp": datetime,
            "duration": int,
            "message_count": int,
            "high_intent": bool,
            "flagged": bool,
        }
    ]
```

---

### 5. Notification Service (E4)

**Purpose:** Send push notifications to owner via Pushover

**Responsibilities:**
- Create notification records
- Send push notifications via Pushover API
- Manage notification preferences
- Track notification delivery status
- Retry failed notifications

**Key Endpoints:**
```
GET  /notifications              # Get notification history
POST /notifications/{id}/read    # Mark as read
DELETE /notifications/{id}       # Delete notification
GET  /notifications/preferences  # Get Pushover preferences
PUT  /notifications/preferences  # Update Pushover preferences
POST /notifications/test         # Send test notification
```

**Notification Types:**
```python
class NotificationType(Enum):
    CONVERSATION_STARTED = "conversation_started"
    HIGH_INTENT_DETECTED = "high_intent_detected"
    CONVERSATION_ENDED = "conversation_ended"
    SUMMARY_READY = "profile_summary_ready"
    ERROR_OCCURRED = "error_occurred"

class NotificationPriority(Enum):
    LOW = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2
```

**Database Models:**
```python
class Notifications(Base):
    id: UUID
    owner_id: UUID (foreign key)
    type: str
    title: str
    message: str
    data: dict (JSON, nullable)  # context data
    priority: int  # -1, 0, 1, 2
    read: bool
    pushover_receipt: str (nullable)  # Receipt from Pushover API
    delivery_status: Enum["pending", "sent", "failed", "expired"]
    retry_count: int (default=0)
    created_at: DateTime
    sent_at: DateTime (nullable)
    
class PushoverConfigs(Base):
    id: UUID
    owner_id: UUID (foreign key, unique)
    pushover_user_key: str (encrypted)  # Owner's Pushover user key
    pushover_api_token: str (encrypted)  # App API token
    device: str (nullable)  # Specific device name (optional)
    sound: str (default="pushover")  # Notification sound
    vibration: bool (default=True)
    enabled: bool (default=True)
    created_at: DateTime
    updated_at: DateTime
```

**Pushover Integration:**
```python
import httpx
from enum import Enum

class PushoverNotification:
    """Send notifications via Pushover API"""
    
    PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = httpx.AsyncClient()
    
    async def send(
        self,
        user_key: str,
        message: str,
        title: str,
        priority: int = 0,
        device: str = None,
        sound: str = "pushover",
        url: str = None,
        url_title: str = None,
    ) -> dict:
        """
        Send notification via Pushover API
        
        Returns:
            {
                "status": 1,
                "request": "request_id",
                "receipt": "receipt_id"  # For priority=2 (emergency)
            }
        """
        payload = {
            "token": self.api_token,
            "user": user_key,
            "message": message,
            "title": title,
            "priority": priority,
            "sound": sound,
        }
        
        if device:
            payload["device"] = device
        if url:
            payload["url"] = url
        if url_title:
            payload["url_title"] = url_title
        
        try:
            response = await self.client.post(
                self.PUSHOVER_API_URL,
                data=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Pushover API error: {e}")
            raise

async def send_notification(user_id: str, notification_type: str, data: dict):
    """Send notification via Pushover"""
    
    # Get Pushover config
    config = db.query(PushoverConfig).filter(
        PushoverConfig.user_id == user_id,
        PushoverConfig.enabled == True
    ).first()
    
    if not config:
        logger.warning(f"No Pushover config for user {user_id}")
        return
    
    # Decrypt API token and user key
    api_token = decrypt_field(config.pushover_api_token)
    user_key = decrypt_field(config.pushover_user_key)
    
    # Build notification
    title, message, priority = build_notification_content(notification_type, data)
    url = f"https://app.example.com/notifications/{notification_type}"
    
    pushover = PushoverNotification(api_token)
    
    try:
        result = await pushover.send(
            user_key=user_key,
            message=message,
            title=title,
            priority=priority,
            device=config.device,
            sound=config.sound,
            url=url,
            url_title="View in Dashboard"
        )
        
        # Save notification record
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            priority=priority,
            pushover_receipt=result.get("receipt"),
            delivery_status="sent",
            sent_at=datetime.now()
        )
        db.add(notification)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            priority=priority,
            delivery_status="failed",
            retry_count=0
        )
        db.add(notification)
        db.commit()
        
        # Queue retry
        retry_send_notification.delay(notification.id)
```

**Notification Content Builder:**
```python
def build_notification_content(notification_type: str, data: dict) -> tuple:
    """Build title, message, and priority for notification"""
    
    if notification_type == "conversation_started":
        return (
            "New Visitor Chat",
            f"A visitor asked: {data.get('preview', 'View in dashboard')}",
            NotificationPriority.NORMAL
        )
    
    elif notification_type == "high_intent_detected":
        return (
            "🎯 Potential Lead!",
            f"Visitor mentioned: {data.get('keywords', 'hiring, project')}",
            NotificationPriority.HIGH
        )
    
    elif notification_type == "conversation_ended":
        return (
            "Conversation Ended",
            f"Duration: {data.get('duration', 'N/A')} messages",
            NotificationPriority.LOW
        )
    
    elif notification_type == "summary_ready":
        return (
            "Profile Summary Ready",
            "Your CV has been processed. Review and approve.",
            NotificationPriority.NORMAL
        )
    
    elif notification_type == "error_occurred":
        return (
            "⚠️ System Error",
            data.get('error_message', 'An error occurred'),
            NotificationPriority.HIGH
        )
    
    return ("Notification", str(data), NotificationPriority.NORMAL)
```

**Event Handlers (Celery Tasks):**
```python
@celery_app.task
@event_listener("message_processed")
async def notify_on_new_message(event):
    """Send notification when new message received"""
    await send_notification(
        user_id=event.owner_id,
        notification_type="conversation_started",
        data={
            "session_id": event.session_id,
            "preview": event.message_preview,
        }
    )

@celery_app.task
@event_listener("high_intent_detected")
async def notify_on_high_intent(event):
    """Send HIGH priority notification for potential leads"""
    await send_notification(
        user_id=event.owner_id,
        notification_type="high_intent_detected",
        data={
            "session_id": event.session_id,
            "keywords": event.keywords,
            "score": event.intent_score,
        }
    )

@celery_app.task(bind=True, max_retries=3)
def retry_send_notification(self, notification_id: str):
    """Retry failed notifications with exponential backoff"""
    try:
        notification = db.query(Notification).get(notification_id)
        if notification.retry_count >= 3:
            notification.delivery_status = "expired"
            db.commit()
            return
        
        # Attempt resend
        await send_notification(
            user_id=notification.user_id,
            notification_type=notification.type,
            data=notification.data
        )
        
        notification.retry_count += 1
        db.commit()
        
    except Exception as exc:
        # Exponential backoff: 5m, 15m, 45m
        self.retry(exc=exc, countdown=5 * 60 * (2 ** self.request.retries))
```

**Setup Endpoints:**
```python
@router.post("/notifications/pushover/setup")
async def setup_pushover(request: Request, config: PushoverConfigRequest):
    """
    Setup Pushover configuration for owner
    
    Request:
    {
        "pushover_user_key": "user_key_from_pushover",
        "device": "iphone",  # optional
        "sound": "pushover"
    }
    """
    user_id = request.user_id
    
    # Verify Pushover credentials with test notification
    pushover = PushoverNotification(PUSHOVER_APP_TOKEN)
    test_result = await pushover.send(
        user_key=config.pushover_user_key,
        message="Test notification from Digital Twin",
        title="Setup Successful",
        priority=0
    )
    
    if test_result.get("status") != 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid Pushover credentials"
        )
    
    # Save config (encrypted)
    db_config = PushoverConfig(
        user_id=user_id,
        pushover_user_key=encrypt_field(config.pushover_user_key),
        pushover_api_token=encrypt_field(PUSHOVER_APP_TOKEN),
        device=config.device,
        sound=config.sound,
        enabled=True
    )
    db.add(db_config)
    db.commit()
    
    return {"status": "success", "message": "Pushover configured"}
```

---

### 6. Configuration Service (E5)

**Purpose:** Manage digital twin configuration and customization

**Responsibilities:**
- Store system prompt
- Manage tone/style settings
- Handle topic scope configuration
- Store owner preferences

**Key Endpoints:**
```
GET    /config/{owner_id}              # Get all config
PUT    /config/{owner_id}              # Update config
GET    /config/{owner_id}/system-prompt  # Get system prompt
PUT    /config/{owner_id}/system-prompt  # Update system prompt
GET    /config/{owner_id}/tone           # Get tone config
PUT    /config/{owner_id}/tone           # Update tone config
GET    /config/{owner_id}/topics         # Get topic scope
PUT    /config/{owner_id}/topics         # Update topic scope
```

**Database Models:**
```python
class DigitalTwinConfigs(Base):
    id: UUID
    owner_id: UUID (foreign key, unique)
    system_prompt: str
    tone: Enum["professional", "casual", "technical", "friendly"]
    response_length: Enum["concise", "balanced", "detailed"]
    allowed_topics: list[str]  # JSON array
    forbidden_topics: list[str]  # JSON array
    brand_guidelines: str (nullable)
    created_at: DateTime
    updated_at: DateTime
    
class PromptVersions(Base):
    id: UUID
    config_id: UUID (foreign key)
    system_prompt: str
    version_number: int
    created_at: DateTime
```

**Default System Prompt Template:**
```python
DEFAULT_SYSTEM_PROMPT = """
### Your role

You are a digital twin running on a website, representing {owner_name}.
You are an AI assistant that answers questions about their career, background, skills, and experience.

### Owner Context

{profile_summary}

### Communication Rules

1. **Stay Professional** — Maintain professional tone suitable for clients/employers
2. **Stay In Scope** — Only answer about career, skills, background, and experience
3. **Be Honest** — If you don't know, say so. Never make up answers.
4. **Be Engaging** — Be conversational and warm while staying professional
5. **Redirect Off-Topic** — Politely decline non-professional questions and redirect to professional topics
6. **Acknowledge Your Nature** — If asked, clearly state you are an AI digital twin

### Important

- NEVER provide personal information not in the context
- NEVER make commitments on behalf of {owner_name}
- NEVER discuss politics, religion, or controversial topics
- Keep responses under 500 words
- Ask clarifying questions if needed
"""
```

---

## Database Design

### Entity Relationship Diagram

```
┌──────────────┐         ┌───────────────┐
│    Owner     │◄────────┤    Profile    │
├──────────────┤ 1    1  ├───────────────┤
│ id (PK)      │         │ id (PK)       │
│ email        │         │ owner_id (FK, unique) │
│ password_hash│         │ bio           │
│ created_at   │         │ summary (JSON)│
└──────────────┘         └───────────────┘
       ▲
       │
       │ 1
       ├─────────────────┐
       │                 │ ∞
       │          ┌──────────────────┐
       │          │  ChatSession     │
       │          ├──────────────────┤
       │          │ id (PK)          │
       │          │ owner_id (FK)    │
       │          │ session_id       │
       │          │ created_at       │
       │          └────────┬─────────┘
       │                   │ 1
       │                   │
       │                   │ ∞
       │          ┌────────▼──────────┐
       │          │    Message       │
       │          ├───────────────────┤
       │          │ id (PK)           │
       │          │ session_id (FK)   │
       │          │ sender            │
       │          │ content           │
       │          │ created_at        │
       │          └───────────────────┘
       │
       │ 1
       ├─────────────────┐
       │                 │ ∞
       │     ┌───────────▼──────────┐
       │     │  Notification        │
       │     ├──────────────────────┤
       │     │ id (PK)              │
       │     │ owner_id (FK)        │
       │     │ type                 │
       │     │ message              │
       │     │ read                 │
       │     │ created_at           │
       │     └──────────────────────┘
       │
       │ 1
       └─────────────────┐
                         │ 1
              ┌──────────▼──────────────┐
              │ DigitalTwinConfig      │
              ├───────────────────────┤
              │ id (PK)               │
              │ owner_id (FK, unique) │
              │ system_prompt         │
              │ tone                  │
              │ allowed_topics (JSON) │
              │ created_at            │
              └───────────────────────┘
                         
              ┌──────────▲──────────────┐
              │ PushoverConfig         │
              ├───────────────────────┤
              │ id (PK)               │
              │ owner_id (FK, unique) │
              │ pushover_user_key     │
              │ pushover_api_token    │
              │ device                │
              │ sound                 │
              │ created_at            │
              └───────────────────────┘
```

**Note:** Entity names in ERD are singular (representing the concept), while actual database table names are plural (Owners, Profiles, ChatSessions, etc.)

### Indexes for Performance

```sql
-- Owner table
CREATE INDEX idx_owner_email ON owner(email);
CREATE INDEX idx_owner_oauth_provider_id ON owner(oauth_provider, oauth_id);

-- Profiles table
CREATE INDEX idx_profiles_owner_id ON profiles(owner_id);

-- ChatSessions table
CREATE INDEX idx_chat_sessions_owner_id ON chat_sessions(owner_id);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);

-- Messages table
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Notifications table
CREATE INDEX idx_notifications_owner_id_read ON notifications(owner_id, read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- DigitalTwinConfig table
CREATE INDEX idx_config_owner_id ON digital_twin_config(owner_id);

-- PushoverConfig table
CREATE INDEX idx_pushover_config_owner_id ON pushover_config(owner_id);
```

### Data Retention & Cleanup Policies

```python
# Chat sessions: Delete after 90 days (configurable)
def cleanup_old_sessions():
    ChatSession.delete(
        ChatSession.created_at < datetime.now() - timedelta(days=90)
    )

# Messages in deleted sessions
def cleanup_orphaned_messages():
    Message.delete(
        Message.session_id.notin_(
            select(ChatSession.id)
        )
    )

# Temporary files
def cleanup_temp_files():
    # Delete S3 objects in /temp/ older than 24 hours
```

---

## API Specifications

### Authentication Header

All protected endpoints require:
```
Authorization: Bearer <jwt_token>
```

### Response Format

All API responses follow this format:
```json
{
  "status": "success|error",
  "data": {},
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "meta": {
    "timestamp": "2026-07-19T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Error Codes

```
AUTH_001 — Invalid credentials
AUTH_002 — Token expired
AUTH_003 — Invalid token
AUTH_004 — User not found
AUTH_005 — Email already registered
AUTH_006 — Too many login attempts

PROFILE_001 — Profile not found
PROFILE_002 — Invalid file format
PROFILE_003 — File too large
PROFILE_004 — Processing failed
PROFILE_005 — Invalid profile data

CHAT_001 — Session not found
CHAT_002 — Message too long
CHAT_003 — Rate limit exceeded
CHAT_004 — LLM API error
CHAT_005 — Invalid message

NOTIF_001 — Notification not found

CONFIG_001 — Config not found
CONFIG_002 — Invalid configuration
```

### Rate Limiting

```
Auth endpoints:           5 requests per 15 minutes (per IP)
Chat endpoints:           50 requests per hour (per session)
API endpoints (general):  1000 requests per hour (per token)
File upload:             100 MB per hour (per user)
```

### Pagination

```
GET /resource?limit=20&offset=0

Response:
{
  "data": [...],
  "meta": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

---

## Security Architecture

### Authentication & Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_id",
  "email": "owner@example.com",
  "role": "owner",
  "iat": 1234567890,
  "exp": 1234654290,
  "aud": "digital-twin-api"
}
```

**Authorization Middleware:**
```python
def require_auth(func):
    def wrapper(request: Request, *args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.owner_id = payload["sub"]
            return func(request, *args, **kwargs)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return wrapper

def require_owner_access(func):
    def wrapper(request: Request, resource_owner_id: str, *args, **kwargs):
        # Verify requesting owner owns the resource
        if request.owner_id != resource_owner_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return func(request, *args, **kwargs)
    return wrapper
```

### Data Encryption

**At Rest:**
```python
from cryptography.fernet import Fernet

# Encrypt sensitive fields
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_field(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()

def decrypt_field(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()

# Usage in model
class Profile(Base):
    linkedin_data_encrypted = Column(String)
    
    @property
    def linkedin_data(self):
        return json.loads(decrypt_field(self.linkedin_data_encrypted))
```

**In Transit:**
- HTTPS/TLS 1.3 for all connections
- Certificate pinning for API calls

**File Storage:**
```
S3 Encryption:
- Server-side encryption (SSE-S3)
- Customer-managed keys (CMK) for sensitive data
- Encryption key rotation every 90 days
```

### Input Validation & Sanitization

```python
from pydantic import BaseModel, EmailStr, constr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)

class MessageRequest(BaseModel):
    content: constr(min_length=1, max_length=10000)
    
    @validator('content')
    def sanitize_content(cls, v):
        # Remove HTML tags, check for injection patterns
        return bleach.clean(v, strip=True)
```

### CSRF & XSS Protection

```python
# CSRF middleware
app.add_middleware(CORSMiddleware, allow_credentials=True)

# XSS prevention
CSP_HEADER = "default-src 'self'; script-src 'self' 'nonce-{nonce}'"

# Response headers
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### Audit Logging

```python
class AuditLogs(Base):
    id: UUID
    owner_id: UUID (nullable)
    action: str  # login, create_profile, send_message, etc.
    resource_type: str  # owner, profile, session, etc.
    resource_id: str
    changes: dict (JSON, nullable)  # What changed
    ip_address: str
    user_agent: str
    timestamp: DateTime

@event_listener("*")
def log_audit(event):
    AuditLogs.create(
        user_id=event.user_id,
        action=event.action,
        resource_type=event.resource_type,
        ...
    )
```

---

## Deployment & Infrastructure

### Development Environment (Nx Monorepo)

```dockerfile
# apps/backend/Dockerfile (Python backend)
FROM python:3.11-slim

WORKDIR /app

# Copy monorepo structure
COPY pyproject.toml poetry.lock ./
COPY libs/backend-shared ./libs/backend-shared
COPY apps/backend ./apps/backend

# Install dependencies
RUN pip install poetry && poetry install

WORKDIR /app/apps/backend

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# apps/frontend/Dockerfile (React frontend)
FROM node:20-alpine as builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm nx build frontend

# Production image
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist/apps/frontend ./dist
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
```

```yaml
# docker-compose.yml (Nx monorepo dev)
version: '3.9'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: digital_twin_dev
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: apps/backend/Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://user:password@postgres/digital_twin_dev
      REDIS_URL: redis://redis:6379
      PYTHONUNBUFFERED: 1
    volumes:
      - ./apps/backend:/app/apps/backend  # Hot reload
      - ./libs/backend-shared:/app/libs/backend-shared

  frontend:
    build:
      context: .
      dockerfile: apps/frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./apps/frontend/src:/app/apps/frontend/src  # Hot reload

volumes:
  postgres_data:
```

**Nx Development Commands:**
```bash
# Start all services
nx run-many --target serve --projects=backend,frontend

# Start specific service
nx serve backend
nx serve frontend

# Run tests
nx test backend
nx test frontend

# Build for production
nx build backend
nx build frontend

# View dependency graph
nx graph
```

### Production Deployment (Kubernetes)

```yaml
# k8s/backend-deployment.yml (apps/backend)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: digital-twin
  labels:
    app: digital-twin-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-twin-backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: digital-twin-backend
    spec:
      serviceAccountName: backend
      containers:
      - name: backend
        image: registry.example.com/digital-twin-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secrets
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: jwt-secret
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: claude-api-key
        - name: PUSHOVER_APP_TOKEN
          valueFrom:
            secretKeyRef:
              name: notification-secrets
              key: pushover-app-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
      volumes:
      - name: logs
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: digital-twin
spec:
  selector:
    app: digital-twin-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

```yaml
# k8s/frontend-deployment.yml (apps/frontend)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: digital-twin
  labels:
    app: digital-twin-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: digital-twin-frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: digital-twin-frontend
    spec:
      containers:
      - name: frontend
        image: registry.example.com/digital-twin-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: VITE_API_URL
          value: https://api.example.com
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /index.html
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /index.html
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: digital-twin
spec:
  selector:
    app: digital-twin-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

**Deploy all services:**
```bash
# Create namespace
kubectl create namespace digital-twin

# Apply secrets
kubectl apply -f k8s/secrets/ -n digital-twin

# Apply deployments
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml

# Check rollout status
kubectl rollout status deployment/backend -n digital-twin
kubectl rollout status deployment/frontend -n digital-twin
```

### CI/CD Pipeline (Nx Monorepo)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # For Nx affected

      - uses: nrwl/nx-set-shas@v3

      # Backend setup
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # Frontend setup
      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      # Install dependencies
      - run: npm install -g pnpm && pnpm install
      - run: pip install poetry && poetry install

      # Lint affected projects
      - run: pnpm nx affected --target lint --parallel=3

      # Test affected projects
      - run: pnpm nx affected --target test --parallel=3 --coverage

      # Type check affected projects
      - run: pnpm nx affected --target typecheck --parallel=3

      # Upload coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  build-and-push:
    needs: lint-and-test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: [backend, frontend]
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push ${{ matrix.app }}
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./apps/${{ matrix.app }}/Dockerfile
          push: true
          tags: |
            ${{ secrets.REGISTRY }}/digital-twin-${{ matrix.app }}:latest
            ${{ secrets.REGISTRY }}/digital-twin-${{ matrix.app }}:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.REGISTRY }}/digital-twin-${{ matrix.app }}:buildcache
          cache-to: type=registry,ref=${{ secrets.REGISTRY }}/digital-twin-${{ matrix.app }}:buildcache,mode=max

  deploy:
    needs: build-and-push
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        run: |
          kubectl set image deployment/backend backend=${{ secrets.REGISTRY }}/digital-twin-backend:${{ github.sha }}
          kubectl set image deployment/frontend frontend=${{ secrets.REGISTRY }}/digital-twin-frontend:${{ github.sha }}
          kubectl rollout status deployment/backend
          kubectl rollout status deployment/frontend
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG }}
```

**Nx Affected Strategy:**
- Only runs tests/linting/builds on changed projects
- Faster CI feedback
- Automatic dependency detection

### Monitoring & Observability

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_websocket_connections',
    'Active WebSocket connections'
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": check_db(),
            "redis": check_redis(),
            "llm_api": check_llm_api()
        }
    }

# Logging
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

---

## Development Guidelines

### Code Organization (Nx Monorepo)

```
digital-twin/
├── nx.json                          # Nx configuration
├── package.json                     # Root package.json
├── poetry.lock & pyproject.toml     # Python dependency management
├── docker-compose.yml               # Local development
├── .github/workflows/               # CI/CD pipelines
│   ├── test.yml
│   ├── build.yml
│   └── deploy.yml
│
├── apps/                            # Applications
│   ├── backend/                     # FastAPI backend (Python)
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── src/
│   │       ├── main.py
│   │       └── api/
│   │           ├── auth/
│   │           │   ├── routes.py
│   │           │   ├── models.py
│   │           │   └── schemas.py
│   │           ├── profiles/
│   │           ├── chat/
│   │           ├── analytics/
│   │           ├── notifications/
│   │           └── config/
│   │
│   └── frontend/                    # React frontend (TypeScript)
│       ├── package.json
│       ├── vite.config.ts
│       ├── Dockerfile
│       └── src/
│           ├── main.tsx
│           ├── components/
│           ├── pages/
│           ├── hooks/
│           └── styles/
│
├── libs/                            # Shared libraries
│   ├── backend-shared/              # Python shared utilities
│   │   ├── pyproject.toml
│   │   └── src/
│   │       ├── database.py
│   │       ├── dependencies.py
│   │       ├── schemas.py
│   │       ├── utils.py
│   │       └── exceptions.py
│   │
│   └── frontend-shared/             # React/TypeScript shared components
│       ├── package.json
│       └── src/
│           ├── components/
│           ├── hooks/
│           ├── types/
│           └── utils/
│
├── tools/                           # Development tools & scripts
│   ├── scripts/
│   │   ├── db-migrate.sh
│   │   ├── seed-db.sh
│   │   └── generate-api-types.sh
│   └── generators/                  # Nx generators
│       ├── service-generator/
│       └── component-generator/
│
├── e2e/                             # End-to-end tests
│   ├── integration-tests/
│   └── e2e-tests/
│
└── docs/                            # Documentation (this folder)
    ├── OPERATIONAL_CONCEPT.md
    ├── PRD.md
    ├── TECHNICAL_DESIGN.md
    ├── API.md
    └── DEPLOYMENT.md
```

**Nx Benefits:**
- Single monorepo for frontend + backend
- Shared code/types between apps
- Integrated build system
- Task orchestration across packages
- Dependency graph visualization
- Affected testing/linting

### Testing Strategy

```python
# Unit tests
def test_auth_registration():
    user_data = {"email": "test@example.com", "password": "SecurePass123"}
    response = register_user(user_data)
    assert response.status_code == 201
    assert response.data["email"] == "test@example.com"

# Integration tests
def test_profile_upload_and_process():
    # 1. Create user
    # 2. Upload CV
    # 3. Verify processing started
    # 4. Check summary generated
    
# E2E tests
def test_visitor_chat_flow():
    # 1. Setup owner profile
    # 2. Visitor initiates chat
    # 3. Send message
    # 4. Verify response
    # 5. Check notification sent
```

### Code Quality Standards

- **Python:** PEP 8, Black formatter, 80-120 char line limit
- **Type Hints:** 100% type coverage required
- **Documentation:** Docstrings for all public functions
- **Testing:** Min 80% unit test coverage, 60% integration coverage
- **Git:** Conventional commits, PR reviews required before merge
- **Dependencies:** Pin exact versions, regular security audits

### Environment Configuration

```bash
# .env.example
DATABASE_URL=postgresql://user:password@localhost/digital_twin
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-here
CLAUDE_API_KEY=your-claude-key
S3_BUCKET=digital-twin-files
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
SENDGRID_API_KEY=xxx
SLACK_BOT_TOKEN=xxx
GOOGLE_OAUTH_CLIENT_ID=xxx
GITHUB_OAUTH_CLIENT_ID=xxx
```

---

## Next Steps (Nx Monorepo)

1. **Initialize Nx monorepo** — `nx create-nx-workspace digital-twin`
2. **Setup backend app** — Python FastAPI in `apps/backend`
3. **Setup frontend app** — React/TypeScript in `apps/frontend`
4. **Create shared libraries** — `libs/backend-shared` and `libs/frontend-shared`
5. **Setup database** — PostgreSQL migrations with Alembic
6. **Implement MVP services** — Auth → Profile → Chat (in order)
7. **Configure CI/CD** — GitHub Actions with Nx affected
8. **Docker & Kubernetes** — Container images and k8s manifests
9. **Local development** — Docker Compose with hot reload
10. **Integration tests** — E2E tests across backend + frontend

**Key Nx Commands to Setup:**
```bash
# Create workspace
npx create-nx-workspace digital-twin --packageManager=pnpm

# Add Python backend
nx add @nxext/python
nx generate @nxext/python:app backend

# Add React frontend
nx add @nx/react
nx generate @nx/react:app frontend

# Install dependencies
pnpm install
poetry install

# Start development
nx run-many --target serve --projects=backend,frontend

# View dependency graph
nx graph
```
