# LearnZo - Project Context and Engineering Specification

**Status:** Initial architecture approved; implementation has not started beyond repository/folder creation.

**Purpose of this document:** This file is the canonical context handoff for any AI coding agent working on LearnZo. Read this document before proposing architecture, creating files, adding dependencies, or implementing features. Preserve the decisions and scope below unless the human explicitly changes them.

---

## 1. Project Summary

LearnZo is a prototype AI-native learning platform inspired by the product direction described for Scaler 3.0.

The goal is **not** to build a traditional LMS with an AI chatbot bolted on. The core product idea is a continuous adaptive learning loop:

```text
Observe learner behavior and answers
        ->
Evaluate what the evidence proves
        ->
Update the learner's skill profile
        ->
Choose the next best learning action
        ->
Teach / practice / mentor
        ->
Observe again
```

The prototype should demonstrate that the platform:

1. understands a learner's current skill level,
2. selects what the learner should study next,
3. provides learning content for that topic,
4. offers context-aware AI assistance,
5. evaluates the learner using multiple signals,
6. updates the learner model from evidence, and
7. changes subsequent learning recommendations based on that updated model.

The adaptive loop is the product. Individual AI features exist to support it.

---

## 2. Repository Context

Repository name:

```text
LearnZo
```

Current repository structure created by the human:

```text
LearnZo/
├── backend/
└── frontend/
```

The repository is intentionally a **single monorepo**.

Implementation should begin with the backend.

Python is already installed on the developer's machine.

No assumption should be made that backend or frontend scaffolding beyond these folders already exists unless the repository contents show otherwise.

---

## 3. Product Vision

The long-term product mental model is:

```text
                        LEARNER EXPERIENCES
                  ┌─────────────────────────┐
                  │ Onboarding              │
                  │ Daily Learning          │
                  │ AI Teaching Assistant   │
                  │ AI Mentor               │
                  │ Assignments             │
                  │ Live Class Intelligence │
                  │ Career Journey          │
                  │ Support                 │
                  └────────────┬────────────┘
                               │
                  ┌────────────▼────────────┐
                  │ Learning Orchestration  │
                  └────────────┬────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    Learner Model         Skill Graph          Judge Platform
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                  ┌────────────▼────────────┐
                  │ Shared AI Platform      │
                  │ Model Gateway           │
                  │ Retrieval / embeddings  │
                  │ Tool calling            │
                  │ AI observability        │
                  └─────────────────────────┘
```

The central primitives are:

1. **Skill Graph / Curriculum**
2. **Learner Model**
3. **Judge / Evaluation Platform**
4. **Learning Planner**
5. **AI assistance layered on top of these primitives**

Do not make "agent" the core domain abstraction.

---

## 4. Prototype Scope

The prototype should implement one coherent vertical learning journey.

### In scope

* Hardcoded curriculum / topics
* Hardcoded skill relationships and prerequisites
* Curated video resource for each topic, initially using YouTube
* Onboarding diagnostic
* Initial learner skill profile
* Daily topic / learning-plan selection
* Lesson experience around the selected video
* Context-aware AI Teaching Assistant
* Broader AI Mentor
* Practice / assessment after learning
* At least one realistic engineering-style assignment
* Multi-signal judge
* Skill evidence generation
* Learner mastery updates
* Next-topic recommendation based on updated mastery
* Basic AI tracing / observability once AI calls are introduced

### Explicitly out of scope for v1

Do **not** implement the following unless the human explicitly expands scope:

* Live classes
* Cohort planner
* Career matching
* Placement workflows
* Support automation
* True multi-agent classrooms
* Production-grade code execution sandbox infrastructure
* Kubernetes
* Kafka
* Microservices
* Temporal
* Dedicated vector database
* Complex recommendation ML models
* Mobile apps
* Real payment flows
* Real Scaler integrations

These may be represented in architecture documentation as future extensions but should not consume prototype implementation time.

---

## 5. Intended User Experience

A simplified end-to-end learner journey:

### Step 1 - Onboarding

The learner provides a target such as:

```text
I want to become a strong Backend SDE2.
```

The platform may collect basic self-reported background information, but self-report is not treated as mastery evidence.

### Step 2 - Diagnostic

The learner answers a short adaptive or semi-adaptive set of questions across the supported skill graph.

Example supported skill dimensions for the prototype may include:

```text
Backend Engineering
├── SQL Fundamentals
├── Database Indexing
├── Transactions
├── Caching
├── Distributed Systems Fundamentals
├── Messaging / Queues
└── System Design Fundamentals
```

The diagnostic produces initial skill evidence and an initial learner profile.

### Step 3 - Skill Profile

The learner sees something like:

```text
SQL                      88%
Database Indexing        52%
Transactions             61%
Caching                  73%
Distributed Systems      43%
System Design            48%
```

Internally, mastery should also track confidence and evidence rather than storing only a naked percentage.

### Step 4 - Daily Planner

The system chooses a suitable next topic based primarily on deterministic rules:

* learner mastery gap,
* prerequisite satisfaction,
* target-role importance,
* confidence in current estimate,
* optionally recency / need for review.

An LLM may explain the decision in natural language, but the LLM should not freely invent the curriculum order.

Example:

```text
Today's focus: Database Indexing

Why today?
Your SQL fundamentals are strong, but your diagnostic showed a gap in
query-performance reasoning. Indexing is also a prerequisite for later
database-scaling topics.
```

### Step 5 - Lesson

The learner gets:

* the topic,
* a curated YouTube video,
* supporting topic information,
* an AI TA alongside the lesson.

### Step 6 - Teaching Assistant

The TA answers questions about what the learner is studying **right now**.

TA context should eventually include:

* current topic,
* video transcript chunks,
* current video timestamp if available,
* learner skill profile,
* recent conversation.

TA should be implemented as a context-aware RAG / generation pipeline before considering it a sophisticated autonomous agent.

### Step 7 - Practice / Assignment

After the lesson, the learner should produce evidence.

The prototype should support simple assessments such as:

* MCQ / objective questions,
* free-text conceptual reasoning,
* one realistic engineering scenario.

Example realistic assignment:

```text
An /orders API became slow after a large tenant was onboarded.
You are given the SQL query, schema, current indexes, and EXPLAIN output.
Diagnose the problem, propose a fix, and explain the trade-offs.
```

### Step 8 - Multi-Signal Judge

The judge evaluates more than the final answer.

Signals may include:

1. Objective signals

   * MCQ correctness
   * deterministic checks
   * expected output / known facts

2. Semantic signals

   * quality of reasoning
   * diagnosis
   * tradeoff awareness
   * explanation quality

3. Behavioral / assistance signals

   * number of attempts
   * hints requested
   * whether the learner solved independently

The judge should produce structured evidence, not merely a single percentage.

### Step 9 - Learner Model Update

The evaluation generates skill evidence that updates mastery and confidence.

Example:

```text
Database Indexing
0.52 -> 0.68

Evidence:
- 4/5 conceptual answers correct
- correctly identified the need for a composite index
- required one hint on selectivity
- did not explain write-amplification trade-offs
```

### Step 10 - Adaptation

The planner runs again using the updated state.

The next experience may:

* move forward,
* reinforce the same skill,
* assign a more advanced version,
* revisit a prerequisite,
* choose a different high-value gap.

This closed loop must remain visible in both the architecture and the demo.

---

## 6. TA vs Mentor Boundary

Do not collapse these into one generic chatbot.

### AI Teaching Assistant

Purpose:

```text
Help me understand what I am learning right now.
```

Responsibilities:

* lesson-specific questions,
* explanations grounded in lesson material,
* contextual hints,
* clarification of current concepts.

Typical context:

* current topic,
* current resource,
* transcript retrieval,
* immediate learner state,
* recent TA conversation.

### AI Mentor

Purpose:

```text
Help me understand where I am going overall and how I am progressing.
```

Responsibilities:

* explain why a topic was selected,
* discuss skill gaps,
* review learning history,
* recommend next actions,
* explain patterns in learner performance,
* give broad learning guidance.

Potential tools later:

```text
get_learner_profile
get_skill_mastery
get_learning_history
get_recent_evaluations
get_current_learning_plan
get_curriculum_topic
recommend_next_activity
```

The mentor is a better candidate for tool calling / agentic behavior than the TA.

---

## 7. Curriculum and Skill Graph

For the prototype, curriculum data should be controlled and deterministic.

Do not start with a general-purpose curriculum-generation system.

A possible initial graph:

```text
Backend Engineering
│
├── SQL Fundamentals
│       ↓
├── Database Indexing
│       ↓
├── Transactions
│
├── Caching
│       ↓
├── Distributed Systems Fundamentals
│       ↓
├── Messaging / Queues
│
└── System Design Fundamentals
```

The actual graph may be refined during implementation, but keep the first version small: roughly **8-12 topics** is sufficient.

Each topic should conceptually support:

```text
Topic
- id
- slug
- title
- description
- skill(s) assessed
- prerequisite topic / skill ids
- target mastery
- importance for target role
- curated learning resources
- diagnostic questions
- practice questions / assignments
```

For v1, curriculum can be seeded into Postgres or defined as seed data. Avoid dynamic curriculum generation.

---

## 8. Video / Learning Resource Strategy

Use curated YouTube resources for the prototype.

Do not dynamically search YouTube every time the planner selects a topic.

Preferred model:

```text
Topic
  -> curated resource mapping
      -> YouTube URL
      -> transcript / text representation
      -> metadata
```

Example conceptual resource fields:

```text
id
topic_id
type = youtube
url
title
author
duration_seconds
transcript_status
```

Transcript chunks can later be embedded and stored for TA retrieval.

The prototype only needs approximately one high-quality video per topic.

---

## 9. Learner Model

The learner profile should represent competence as evidence-backed state.

Conceptual structure:

```text
LearnerSkillState
- learner_id
- skill_id
- mastery_score        # normalized, e.g. 0.0-1.0
- confidence_score     # confidence in mastery estimate
- last_assessed_at
- evidence_count
```

Evidence is stored separately so mastery can be explained and recalculated.

Conceptual evidence:

```text
SkillEvidence
- id
- learner_id
- skill_id
- source_type
- source_id
- score
- confidence
- weight
- evidence_summary
- metadata_json
- created_at
```

Possible source types:

```text
diagnostic
quiz
free_text
assignment
judge
mentor_observation   # probably not v1
```

A core product rule:

> Merely watching or completing content should not automatically imply mastery. Mastery should primarily move because the learner produced evidence.

---

## 10. Daily Planner

The daily planner should initially be a deterministic service rather than a free-form LLM agent.

Conceptual eligibility:

```text
eligible(topic) =
    prerequisites_satisfied
    AND mastery(topic_skill) < desired_mastery
```

Conceptual ranking:

```text
priority(topic) =
    skill_gap
    * target_role_importance
    * confidence_factor
    * optional_review_factor
```

The exact formula can evolve. Keep v1 understandable and testable.

The planner returns:

```text
DailyLearningPlan
- learner_id
- date
- selected_topic_id
- reason codes / scores
- human-readable explanation
```

If an LLM generates the explanation, persist the underlying deterministic reason data separately.

---

## 11. Multi-Signal Judge

The judge is one of the most important architectural pieces and should be treated as a first-class domain module.

Conceptual components:

```text
JudgeEngine
├── ObjectiveJudge
├── ReasoningJudge
├── AssistanceSignalCollector
├── RubricEngine
├── ScoreAggregator
└── SkillEvidenceGenerator
```

Each judge should output a common structured signal rather than arbitrary prose.

Example:

```json
{
  "skill_id": "database_indexing",
  "criterion": "tradeoff_reasoning",
  "score": 0.6,
  "confidence": 0.82,
  "evidence": [
    "Learner selected the correct composite index",
    "Learner did not identify write-amplification cost"
  ],
  "feedback": "The fix is correct, but explain the read/write trade-off."
}
```

### Judge design principles

* Prefer deterministic evidence where deterministic evidence exists.
* LLM judges handle semantic / open-ended dimensions.
* Do not ask an LLM to infer facts that can be computed.
* Persist judge version, rubric version, model version, and relevant prompt version once these concepts exist.
* Judge output must be structured and parseable.
* Evaluation should eventually be reproducible and traceable.

The prototype does not need a full human-calibrated golden evaluation dataset, but the architecture should not prevent adding one later.

---

## 12. Backend Architecture

Use a **modular monolith**.

Do not build microservices for the prototype.

Desired direction:

```text
backend/
├── pyproject.toml
├── .env.example
├── alembic.ini
├── Dockerfile
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   │
│   ├── api/
│   │   └── router.py
│   │
│   ├── modules/
│   │   ├── curriculum/
│   │   ├── diagnostics/
│   │   ├── learner/
│   │   ├── planner/
│   │   ├── learning/
│   │   ├── ta/
│   │   ├── mentor/
│   │   ├── assignments/
│   │   └── judge/
│   │
│   ├── ai/
│   │   ├── gateway.py
│   │   ├── models.py
│   │   └── providers/
│   │
│   └── workers/
│       └── celery_app.py       # add only when Celery is introduced
│
└── tests/
    ├── conftest.py
    └── test_health.py
```

Not every directory above needs to be created immediately. Create structure incrementally as features are implemented.

### Domain module pattern

A feature may eventually look like:

```text
modules/
└── learner/
    ├── router.py
    ├── schemas.py
    ├── models.py
    ├── service.py
    └── repository.py
```

Use this pragmatically; do not create empty layers solely for architectural symmetry.

The goal is feature ownership and discoverability, not ceremony.

---

## 13. Backend Tech Stack

Use the following unless the human explicitly changes it.

### Language and framework

```text
Python 3.12
FastAPI
Uvicorn
```

### Dependency / environment management

```text
uv
pyproject.toml
```

### Validation / configuration

```text
Pydantic
pydantic-settings
```

### Database

```text
PostgreSQL
SQLAlchemy 2.x
Alembic
```

Use normal synchronous database access initially unless a concrete need justifies async SQLAlchemy.

### Vector retrieval

Later:

```text
pgvector
```

Do not introduce Pinecone, Chroma, Weaviate, Milvus, etc. for v1.

### Cache / ephemeral state / job broker

Later:

```text
Redis
```

### Background jobs

Later, when needed:

```text
Celery + Redis
```

Use background jobs for tasks such as:

* transcript processing,
* embedding generation,
* long-running judge pipelines,
* profile recalculation if necessary.

Do not use Celery for token streaming to the browser.

### Testing and quality

```text
pytest
httpx
Ruff
```

Add type checking only if it improves development rather than becoming setup overhead.

---

## 14. AI Stack

Use direct model provider SDKs behind LearnZo-owned abstractions.

Possible providers:

```text
OpenAI
Anthropic
```

Do not tightly couple domain logic to a provider.

### Model Gateway

Introduce a small internal abstraction once the first real LLM feature is implemented.

Conceptual API:

```text
generate(...)
generate_structured(...)
stream(...)
embed(...)
```

Responsibilities may eventually include:

* provider routing,
* model selection,
* structured-output validation,
* retries,
* timeouts,
* tracing,
* token/cost metadata,
* fallback logic.

Do not overbuild a production-grade gateway before it is needed.

### LangChain / LangGraph

Do **not** start with LangChain everywhere.

Prefer direct SDKs and normal Python composition.

LangGraph may be considered later for genuinely stateful, branching workflows such as a more sophisticated judge pipeline or agent workflow.

Use a framework because the workflow requires it, not because the project contains AI.

---

## 15. Retrieval / RAG

RAG is mainly needed for lesson-specific TA grounding.

Expected flow:

```text
Learner question
        ->
Embed / retrieve relevant transcript chunks
        ->
Combine with current topic + learner context + conversation
        ->
LLM
        ->
Stream response
```

Transcript chunk data may conceptually store:

```text
resource_id
chunk_index
text
start_timestamp
end_timestamp
embedding
```

Use Postgres + pgvector for this once retrieval is introduced.

Do not add vector infrastructure during the first backend scaffold milestone.

---

## 16. Frontend Direction

Frontend implementation begins after sufficient backend foundation exists.

Recommended stack:

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
```

Expected initial pages / experiences:

```text
/onboarding
/diagnostic
/dashboard
/learn/[topic]
/assignment/[id]
/mentor
/profile
```

Important UX principle:

The dashboard should visually communicate adaptation, e.g.:

```text
Backend SDE2 readiness: 68%

Today's focus:
Database Indexing

Why today?
Your diagnostic showed a gap in query-performance reasoning.

Skill profile:
SQL                      91%
Indexing                 52%
Transactions             61%
Distributed Systems      43%
```

The UI should make the learner model and adaptive decision feel tangible.

---

## 17. API Style

Use versioned REST APIs initially.

Example prefix:

```text
/api/v1
```

Potential future routes include:

```text
GET  /api/v1/health

GET  /api/v1/curriculum/topics
GET  /api/v1/curriculum/topics/{topic_id}

POST /api/v1/diagnostics
POST /api/v1/diagnostics/{id}/answers
POST /api/v1/diagnostics/{id}/complete

GET  /api/v1/learners/{id}/profile
GET  /api/v1/learners/{id}/skills

GET  /api/v1/learners/{id}/daily-plan

POST /api/v1/ta/chat
POST /api/v1/mentor/chat

POST /api/v1/assignments/{id}/submissions
GET  /api/v1/submissions/{id}/evaluation
```

These are directional, not a frozen API contract.

Use Server-Sent Events for simple LLM response streaming unless bidirectional realtime behavior creates a concrete need for WebSockets.

---

## 18. Data Model - Directional Entities

The exact schema should be designed feature-by-feature, but likely core entities include:

```text
User
LearnerProfile

Skill
Topic
TopicPrerequisite
LearningResource
ResourceChunk

Diagnostic
DiagnosticQuestion
DiagnosticAttempt
DiagnosticAnswer

LearnerSkillState
SkillEvidence

DailyLearningPlan
LearningSession

Assignment
Submission

JudgeRun
JudgeSignal / JudgeResult
Evaluation

ChatSession
ChatMessage
```

Use relational columns for stable, queryable domain fields.

Use PostgreSQL JSONB for flexible model/judge metadata where strict relational modeling adds little value.

Do not default every AI-related payload to JSONB.

---

## 19. Infrastructure Direction

### Local development

Eventually use Docker Compose for supporting infrastructure:

```text
frontend
api
worker          # once needed
postgres
redis           # once needed
```

The developer should still be able to run backend processes directly on the host during normal development if convenient.

### Deployment direction

If deployed on AWS:

```text
Frontend      -> Vercel or suitable web hosting
FastAPI       -> ECS Fargate
Postgres      -> RDS PostgreSQL
Redis         -> ElastiCache
Object files  -> S3
```

AWS deployment is not the first milestone.

Do not add Kubernetes to the prototype.

---

## 20. AI Observability

Once LLM calls are introduced, capture enough information to debug and compare behavior.

For model calls, aim to record:

```text
trace_id
feature
learner_id if applicable
provider
model
prompt/version identifier when introduced
input/output token counts
latency
cost if available
retrieval context identifiers
tool calls
success/failure
```

For judge runs, additionally preserve:

```text
judge version
rubric version
model version
structured signals
confidence
final aggregation
```

Langfuse or OpenTelemetry-style tracing may be introduced later.

Do not make observability tooling a blocker for the first foundation milestone.

---

## 21. Security / Safety Baseline

This is a prototype, but follow basic engineering hygiene:

* secrets only through environment variables,
* never commit API keys,
* provide `.env.example`,
* validate API inputs,
* do not execute arbitrary learner code directly on the host,
* do not expose raw internal prompts or secrets to clients,
* sanitize / constrain tool execution when agent tools are added.

A production-grade secure code sandbox is outside v1 scope.

---

## 22. Initial Backend Scaffold Milestone

Before implementing any learning-domain behavior, create a small, reliable backend foundation.

The first milestone is complete only when all of the following work:

```text
[ ] Python project initialized with uv
[ ] pyproject.toml created
[ ] FastAPI application boots
[ ] environment settings load from .env
[ ] PostgreSQL connection configured
[ ] SQLAlchemy 2.x configured
[ ] Alembic configured and can run migrations
[ ] central API router exists
[ ] GET /api/v1/health works
[ ] tests run with pytest
[ ] health endpoint has a test
[ ] Ruff linting / formatting works
[ ] .env.example exists
[ ] sensible .gitignore exists
```

Initial dependencies should remain small:

```text
fastapi
uvicorn
pydantic
pydantic-settings
sqlalchemy
postgresql driver
alembic
pytest
httpx
ruff
```

Do **not** install Redis, Celery, pgvector, OpenAI, Anthropic, LangGraph, Langfuse, etc. during this milestone unless a concrete implemented feature needs them.

---

## 23. Recommended Implementation Order

After the backend scaffold is healthy, implement vertical capabilities in this order.

### Phase 1 - Foundation

* FastAPI scaffold
* config
* Postgres
* migrations
* tests
* health endpoint

### Phase 2 - Curriculum / Skill Graph

* Skill entity
* Topic entity
* prerequisites
* learning resources
* seed 8-12 backend-engineering topics
* curriculum read APIs

### Phase 3 - Learner + Diagnostic

* learner profile
* diagnostic questions
* diagnostic attempt flow
* deterministic / simple scoring
* skill evidence from diagnostic
* initial learner skill states

At the end of this phase, the system should be able to create a learner profile from onboarding evidence.

### Phase 4 - Daily Planner

* prerequisite checks
* mastery gap calculation
* topic ranking
* create daily plan
* explain why a topic was selected

Prefer deterministic explanation templates first. Add LLM-generated natural-language explanation only if useful.

### Phase 5 - Learning Resource Experience Backend

* topic resource API
* curated YouTube metadata
* transcript storage / ingestion strategy
* learning-session tracking

### Phase 6 - TA

Only now introduce:

* first LLM provider SDK,
* ModelGateway,
* transcript chunking,
* embeddings,
* pgvector,
* retrieval,
* TA chat with streaming.

### Phase 7 - Practice + Judge

* questions / assignment schema
* submissions
* objective judge
* LLM reasoning judge
* common JudgeSignal schema
* aggregation
* feedback
* SkillEvidence generation

### Phase 8 - Mastery Update Loop

* consume new evidence
* update LearnerSkillState
* rerun planner
* demonstrate that tomorrow's learning choice changes

This closes the core LearnZo loop.

### Phase 9 - Mentor

* mentor chat
* learner-state tools
* history / evaluation tools
* explanations about progress and future learning

### Phase 10 - Background Processing / Operational Polish

Introduce Redis / Celery only for workflows that now justify them.

Examples:

* embedding jobs,
* resource processing,
* long judge execution,
* asynchronous evaluation.

---

## 24. Testing Strategy

Tests should emphasize deterministic domain logic.

High-value unit tests include:

* prerequisite evaluation,
* planner ranking,
* diagnostic scoring,
* mastery update calculations,
* judge aggregation,
* evidence weighting.

API tests should cover core happy paths and important validation failures.

LLM behavior should not make the normal unit-test suite flaky.

Prefer:

* mocking / fake ModelGateway for unit tests,
* structured output validation,
* a small opt-in integration/evaluation suite for real model calls later.

---

## 25. Engineering Principles for AI Coding Agents

Any AI agent working on this repository should follow these rules.

### 25.1 Read before writing

Inspect existing files and patterns before proposing or editing code.

### 25.2 Preserve the modular monolith

Do not split services into independently deployed microservices without explicit approval.

### 25.3 Build incrementally

Do not scaffold every future module, abstraction, database table, and integration in one pass.

Implement the smallest clean slice needed for the current milestone.

### 25.4 Avoid speculative abstractions

Do not create generic framework layers before at least one real use case demonstrates the need.

Examples:

* no generic agent framework before a real agent needs it,
* no event bus before there is meaningful asynchronous domain behavior,
* no repository abstraction everywhere merely because it might be useful someday.

### 25.5 Keep AI separated from domain policy

LLMs may:

* explain,
* generate structured semantic evaluations,
* answer grounded questions,
* use controlled tools.

LLMs should not silently own deterministic product rules such as prerequisite satisfaction or basic topic eligibility.

### 25.6 Structured AI outputs

When AI output drives application behavior, prefer validated structured output over free-form text parsing.

### 25.7 Evidence over completion

Never equate "watched a video" with "mastered the skill."

### 25.8 Prefer deterministic signals

If something can be measured reliably without an LLM, measure it directly and provide that evidence to the LLM if semantic interpretation is still needed.

### 25.9 Keep provider coupling low

Domain modules should not directly depend on OpenAI- or Anthropic-specific types where a small LearnZo abstraction suffices.

### 25.10 Do not over-engineer infrastructure

The interview value of this project comes from:

* adaptive learner modeling,
* judge design,
* evaluation quality,
* personalization,
* clean architecture,
* product thinking.

It does **not** come from the number of infrastructure technologies used.

---

## 26. Definition of Prototype Success

The prototype is successful when a demo can show this story end to end:

```text
1. New learner starts.
2. Learner completes a diagnostic.
3. LearnZo creates an initial skill profile.
4. LearnZo chooses today's topic and explains why.
5. Learner opens a curated lesson/video.
6. Learner asks a lesson-specific question to the TA.
7. Learner completes practice / an engineering assignment.
8. The multi-signal judge evaluates the submission.
9. Evaluation creates visible skill evidence.
10. Learner mastery changes.
11. LearnZo chooses a different / more appropriate next learning action.
12. Mentor can explain the learner's progress using the learner model.
```

If the prototype demonstrates that loop convincingly, it has achieved its primary goal even if many production features are absent.

---

## 27. Immediate Next Task

The next task is **backend foundation scaffolding** inside:

```text
LearnZo/backend
```

Do not begin with curriculum, AI, pgvector, Redis, or Celery.

First establish:

```text
uv
FastAPI
configuration
PostgreSQL
SQLAlchemy
Alembic
/api/v1/health
pytest
Ruff
```

Before implementation, inspect the current repository contents and avoid overwriting any existing developer work.

---

## 28. Current Design Decisions Summary

Use this as the short canonical checklist when context is limited:

```text
Repo: LearnZo monorepo
Folders: backend/, frontend/
Start: backend first

Architecture: modular monolith
Backend: Python 3.12 + FastAPI
Dependency manager: uv
DB: PostgreSQL
ORM: SQLAlchemy 2.x
Migrations: Alembic
Validation/config: Pydantic + pydantic-settings
Testing: pytest + httpx
Quality: Ruff

Frontend later: Next.js + TypeScript + Tailwind + shadcn/ui

Vector later: pgvector
Cache later: Redis
Jobs later: Celery + Redis
AI: direct provider SDKs behind custom ModelGateway
Agent frameworks: avoid initially; LangGraph only if justified later
Video resources: curated YouTube mapping, not dynamic search at runtime

Core product primitives:
1. Curriculum / Skill Graph
2. Learner Model
3. Daily Planner
4. Multi-Signal Judge
5. TA
6. Mentor

Core product loop:
Diagnostic -> skill profile -> select topic -> learn -> practice -> judge
-> evidence -> update mastery -> select next topic

Primary prototype value:
adaptive learning + evidence-backed mastery + strong judge architecture

Avoid in v1:
microservices, Kubernetes, Kafka, Temporal, separate vector DB,
production live-class system, career matching, support automation.
```

---

## 29. Change Policy

This document records decisions made with the human owner of LearnZo.

An AI coding agent may recommend improvements, but should not silently change major architecture, scope, or stack decisions.

For a material change, state:

1. what existing decision would change,
2. why,
3. trade-offs,
4. the smallest alternative,
5. whether the change is required now or merely desirable later.

Then wait for human approval before implementing that material architectural change.

---

**End of project context specification.**
