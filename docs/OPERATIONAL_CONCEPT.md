# Digital Twin Operational Concept

## Project Summary
A digital twin AI assistant that represents a professional on their personal website. The system allows visitors to interact with an AI-powered chatbot that has knowledge of the person's career, background, skills, and experience. The digital twin answers professional questions on behalf of the owner while maintaining authenticity and staying within defined boundaries.

## System Overview

### Purpose
Provide an intelligent, always-available representative of a professional that can:
- Answer career-related questions from website visitors
- Represent the person's professional brand and expertise
- Engage potential clients, employers, and collaborators
- Filter out non-professional inquiries with grace

### Key Value Propositions
1. **24/7 Availability** — Professional representation without manual intervention
2. **Scalable Engagement** — Handle multiple visitor conversations simultaneously
3. **Consistent Brand** — Deliver on-brand responses aligned with the owner's profile
4. **Professional Boundary** — Automatically redirect off-topic conversations

---

## Actors & Roles

### Owner
- Creates and maintains their profile by uploading a CV/resume
- Configures what information the digital twin should know
- Receives notifications of visitor interactions
- Can update profile information to keep the digital twin current

### Visitor
- Discovers the owner's website
- Engages with the digital twin chatbot
- Asks professional or non-professional questions
- Learns about the owner's career, skills, and experience

### Digital Twin (AI Assistant)
- LLM-based conversational agent
- Represents the owner with knowledge of their background
- Enforces professional boundaries
- Acknowledges its nature as an AI digital twin when relevant

### App System
- Manages user authentication and profile storage
- Handles chat sessions and message routing
- Provides the interface for owner and visitor interactions
- Manages notifications and logging

### Notification System
- Alerts owner of visitor interactions
- Logs conversation summaries
- Provides analytics on engagement

---

## Use Cases

### Use Case 1: Owner Sets Up Digital Twin Profile
**Actor:** Owner

**Flow:**
1. Owner navigates to profile setup
2. Uploads CV/resume file
3. System extracts and summarizes professional information
4. Owner reviews extracted information and makes corrections
5. Owner confirms profile is ready
6. Digital twin is now active and ready to chat

**Outcome:** Digital twin has accurate knowledge of owner's background and can begin answering visitor questions

---

### Use Case 2: Visitor Asks Professional Question
**Actor:** Visitor, Digital Twin (AI), Owner (receives notification)

**Flow:**
1. Visitor arrives at owner's website
2. Visitor initiates chat with digital twin
3. Visitor asks a professional question (e.g., "What's your experience with Python?", "Do you work with startups?")
4. Digital twin accesses owner's profile data
5. Digital twin generates contextual, accurate response
6. Owner receives notification of the interaction
7. Conversation continues naturally

**Outcome:** Visitor gets answer; Owner gains a qualified lead or networking opportunity

---

### Use Case 3: Visitor Asks Non-Professional Question
**Actor:** Visitor, Digital Twin (AI)

**Flow:**
1. Visitor asks off-topic question (e.g., personal life, politics, unrelated topics)
2. Digital twin recognizes the question is outside professional scope
3. Digital twin politely declines and redirects to professional topics
4. Digital twin maintains professional tone and engagement
5. Conversation can continue on appropriate topics or naturally conclude

**Outcome:** Conversation boundaries maintained; professionalism preserved

---

## Authentication & User Differentiation

### Architecture: Hybrid Model (Public Visitor Chat + Protected Owner Dashboard)

```
┌─────────────────────────────────────────────────────────────┐
│                        Website                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐              ┌──────────────────────┐ │
│  │  Public Pages    │              │  Protected Routes    │ │
│  │  (No Auth)       │              │  (Auth Required)     │ │
│  ├──────────────────┤              ├──────────────────────┤ │
│  │ • Homepage       │              │ • /dashboard         │ │
│  │ • Chat Widget    │              │ • /profile           │ │
│  │ • About Page     │              │ • /notifications     │ │
│  │ • Services       │              │ • /analytics         │ │
│  │ (Visitor Access) │              │ (Owner Access Only)  │ │
│  └──────────────────┘              └──────────────────────┘ │
│         ↕                                    ↕               │
│  Anonymous Sessions                  Authenticated Sessions  │
│  (No Login Required)                 (Login Required)        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Access Control Levels

#### Level 1: Public/Visitor Access
**Routes:** `/`, `/about`, `/chat`, `/services`, etc.
**Authentication:** None required
**Capabilities:**
- View public profile information
- Chat with digital twin
- Browse website content
- No account creation needed

**User Identification:**
- Anonymous (session-based, no user ID)
- Optional: Tracked via session ID or device ID
- Can be anonymous or provide email optionally

#### Level 2: Owner Access (Protected)
**Routes:** `/dashboard`, `/profile`, `/settings`, `/notifications`, `/analytics`
**Authentication:** Required (Email + Password / OAuth)
**Capabilities:**
- Upload and manage CV/profile
- View all visitor conversations
- Configure digital twin behavior
- Access notifications and analytics
- Update profile information

**User Identification:**
- Authenticated user (user ID in session/JWT)
- Role-based access control (RBAC) with "owner" role
- Session token/JWT verifies identity

### Authentication Flow

#### Owner Registration & Login
```
1. Owner navigates to /login or /register
2. Creates account (email/password) or uses OAuth (Google/GitHub)
3. Email verification (if applicable)
4. System stores owner credentials in database
5. Owner logs in successfully
6. Session/JWT token created and stored
7. Owner redirected to /dashboard
8. Token included in subsequent requests
```

#### Visitor Interaction Flow
```
1. Visitor arrives at homepage (public, no login)
2. Initiates chat with digital twin
3. System creates anonymous session (session ID)
4. Messages sent with session ID, no user authentication
5. Visitor can continue chatting without logging in
6. No persistent account needed
```

### User Differentiation in Code

**Middleware/Guard:**
```
Request → Check Authentication → Verify Role → Grant/Deny Access
                                      ↓
                          "owner" → Allow
                          "visitor" → Redirect to login or deny
                          "anonymous" → Allow public routes only
```

**Database User Model:**
```
User {
  id: UUID
  email: string (unique)
  password: hashed
  role: "owner" | "visitor"  # Determined at registration
  profile: {
    cv_path: string
    summary: string
    linkedin_data: object
  }
  created_at: timestamp
  updated_at: timestamp
}
```

**Session/Chat Model:**
```
ChatSession {
  id: UUID
  owner_id: UUID        # Owner whose profile is being queried
  user_id: UUID | null  # If visitor is logged in (optional)
  session_id: string    # Anonymous session ID
  messages: [
    {
      sender: "visitor" | "ai"
      content: string
      timestamp: timestamp
    }
  ]
}
```

### Differentiation Checkpoints

| Action | Owner | Visitor |
|--------|-------|---------|
| Access dashboard | ✅ Authenticated required | ❌ Redirected to login |
| Chat with digital twin | ✅ Can test/manage | ✅ Full access |
| Upload CV | ✅ Full access | ❌ Denied |
| View own conversations | ✅ Full access | ✅ Only active session |
| View analytics | ✅ Full access | ❌ Denied |
| Receive notifications | ✅ Yes | ❌ No |
| Update profile | ✅ Full access | ❌ Denied |

### Session Management

**Owner Session:**
- Duration: 24 hours or user logout
- Stored in database (persistent)
- JWT token or session cookie
- Refreshable tokens for long sessions

**Visitor Session:**
- Duration: 30 minutes of inactivity or browser close
- Stored in memory or short-lived storage
- Session ID only (no authentication)
- No persistent tracking (privacy-friendly)

### Security Considerations
- Owner passwords hashed (bcrypt/Argon2)
- Protected routes require valid authentication
- CSRF protection on state-changing operations
- Rate limiting on login attempts
- Visitor data isolation (no cross-conversation leakage)
- HTTPS enforced for all authenticated routes

---

## Digital Twin AI Behavior

### System Prompt Foundation
The digital twin operates under these core principles:

**Role:** Represent the owner as an AI digital twin on their website, answering questions about:
- Career history and background
- Technical and professional skills
- Experience and achievements
- Expertise and specializations

**Scope:** Professional and career-related topics only

**Key Behaviors:**
- **Transparency:** Clearly acknowledges being an AI digital twin when relevant
- **Authenticity:** Speaks on behalf of the owner, not making assumptions
- **Honesty:** Admits when lacking information rather than fabricating answers
- **Professionalism:** Maintains professional tone suitable for potential clients/employers
- **Boundary Setting:** Gracefully redirects non-professional conversations
- **Engagement:** Conversational and welcoming while staying professional

### Context Provided to AI
The digital twin receives:
1. Owner's profile summary (extracted from CV)
2. LinkedIn profile data (if available)
3. Key skills, experience, and achievements
4. Professional background and history

### Decision Rules
- **If question is career-related:** Answer based on owner's context
- **If question is not in provided context:** Say "I don't know" rather than guess
- **If question is non-professional:** Politely decline and redirect
- **If asked about AI nature:** Confirm being a digital twin while staying in character

---

## Technical Interactions

### Data Flow
```
Owner Profile Upload
         ↓
    [CV Processing]
         ↓
   Profile Summary + LinkedIn Data
         ↓
    [Stored in System]
         ↓
   Digital Twin Ready
         ↓
Visitor Question → [LLM with System Prompt + Context] → Response
         ↓
  [Notification to Owner]
```

### Notification Events
- New visitor interaction started
- Conversation ended/summary
- Visitor expressed interest (qualitative signals)
- System errors or anomalies

---

## Success Metrics
- Number of visitor interactions
- Conversation quality/satisfaction
- Professional lead generation
- Engagement duration and depth
- Owner satisfaction with representation

---

## Future Enhancements
- Multi-language support
- Integration with calendar for scheduling
- Email forwarding to owner
- Visitor information capture
- Conversation sentiment analysis
- A/B testing different response styles
