# Technical Decisions

> A record of significant technical decisions made during the development of Saint.

---

## TD-001: Separate Frontend and Backend

### Status

Accepted

### Decision

The frontend and backend will be maintained as clearly separated application boundaries.

```text
saint/
├── frontend/
└── backend/
```

### Frontend Responsibilities

The frontend is responsible for:

* User interaction
* Goal input
* Intent selection
* Goal visualization
* Contextual path visualization
* Learn, Explore, and Act experiences
* Displaying agent output

### Backend Responsibilities

The backend is responsible for:

* Application logic
* Agent orchestration
* Goal understanding
* DataHub integration
* LLM integration
* Context processing
* Path generation
* Assessment and adaptation

### Rationale

The product contains complex agent and context logic that should not be tightly coupled to the user interface.

Clear separation allows:

* Independent frontend and backend development
* Easier testing
* Cleaner architecture
* Greater flexibility in changing the UI
* Reduced coupling between presentation and application logic

---

## TD-002: Use DataHub MCP Server as the Primary DataHub Integration

### Status

Accepted

### Decision

Saint will use the DataHub MCP Server as the primary interface for interacting with DataHub's context graph.

```text
Saint
  ↓
MCP Client / Adapter
  ↓
DataHub MCP Server
  ↓
DataHub Context Graph
```

### Rationale

The core product requires an agent to interact with structured context from DataHub.

The MCP Server provides a natural integration boundary between:

* The Saint agent
* The application backend
* DataHub's context graph

This allows Saint to use DataHub context without tightly coupling the entire application to provider-specific API implementation details.

### Consequence

Saint will introduce an integration boundary between the application domain and DataHub access.

The exact MCP client implementation may evolve as development progresses.

---

## TD-003: Use an Adapter Boundary for DataHub

### Status

Accepted

### Decision

Core application logic should not directly depend on raw DataHub or MCP response formats.

The integration should conceptually follow:

```text
DataHub MCP Server
        ↓
MCP Client
        ↓
DataHub Adapter
        ↓
Application Domain
```

### Rationale

This allows the application to:

* Transform external data into application-relevant representations
* Avoid provider-specific coupling
* Test application logic independently
* Change the integration mechanism if necessary

The DataHub integration remains central to the product, while the internal application remains modular.

---

## TD-004: Use a Provider-Agnostic LLM Layer

### Status

Accepted

### Decision

The application should interact with LLMs through an abstraction layer rather than directly coupling core logic to a single model provider.

```text
Application Logic
        ↓
LLM Interface
        ↓
Provider Adapter
        ↓
LLM Provider
```

Possible providers may include:

* Cloud model providers
* Local model providers
* Other compatible providers

### Rationale

The project is being developed under resource constraints.

Model availability, pricing, latency, and capability may change during development.

The application should therefore allow the LLM provider or model to be changed through configuration and provider implementation rather than requiring major changes to core product logic.

---

## TD-005: Use Environment-Based Configuration

### Status

Accepted

### Decision

Environment-specific configuration and secrets should be managed through environment configuration.

Examples include:

* API keys
* DataHub connection information
* LLM provider
* LLM model
* API endpoints
* Runtime environment
* Logging configuration

Conceptually:

```text
Environment
    ↓
Configuration Loader
    ↓
Application Settings
    ↓
Modules
```

### Rationale

The project may need to change:

* Model providers
* Model names
* API endpoints
* Development environments
* Deployment environments

These changes should not require modifying application logic.

Secrets must not be hardcoded into the codebase.

---

## TD-006: Keep the Application Modular

### Status

Accepted

### Decision

Major application responsibilities should be separated into modular components with clear responsibilities.

The architecture should conceptually separate:

```text
Goal Understanding
        ↓
Context Discovery
        ↓
Path Generation
        ↓
Learn / Explore / Act
```

### Rationale

The product is expected to evolve during development.

Modularity allows individual components to change without requiring the entire system to be rewritten.

The project should prefer:

```text
Small Component
    +
Clear Responsibility
    +
Stable Interface
```

over large components that combine unrelated responsibilities.

---

## TD-007: Keep Core Product Logic Independent from External Providers

### Status

Accepted

### Decision

Core product concepts should be represented independently from external provider-specific data formats.

Potential domain concepts include:

```text
Goal
Intent
Context
Relationship
Path
Task
Assessment
Outcome
```

External data should be transformed where necessary:

```text
External Provider
        ↓
Adapter
        ↓
Domain Representation
        ↓
Product Logic
```

### Rationale

The product's core concept is not the DataHub API response itself.

The product's core concept is the transformation of:

```text
User Goal
    +
Context
    ↓
Path Toward Outcome
```

This distinction allows the application to preserve its product logic even when external integrations change.

---

## TD-008: DataHub Must Provide Meaningful Product Value

### Status

Accepted

### Decision

DataHub should be used as a meaningful part of the product's core mechanism.

The project should not integrate DataHub only to satisfy a hackathon requirement.

A feature should be evaluated by asking:

> Does DataHub context meaningfully improve this capability?

### Rationale

The hackathon project should demonstrate that DataHub's context graph enables capabilities that generic LLM knowledge or ordinary document retrieval would not provide as effectively.

The product should demonstrate meaningful use of:

* Relationships
* Lineage
* Metadata
* Ownership
* Glossary
* Quality
* Freshness
* Other relevant context

---

## TD-009: Goal Interpretation Must Be Visible Before Deep Execution

### Status

Accepted

### Decision

The system should make its interpretation of a user's goal visible before proceeding with significant downstream reasoning.

```text
User Goal
    ↓
Agent Interpretation
    ↓
Goal Visualization
    ↓
User Confirmation
    ↓
Context Discovery
```

### Rationale

Agent systems can make incorrect assumptions.

Making the interpretation visible allows the user to:

* Confirm the goal
* Correct the goal
* Add missing context
* Remove irrelevant assumptions

This reduces the risk of building a complex path around a misunderstood objective.

---

## TD-010: Start with One Complete End-to-End Experience

### Status

Accepted

### Decision

The initial implementation should prioritize one complete, meaningful user journey over a large number of incomplete features.

```text
Goal
    ↓
Intent
    ↓
Interpretation
    ↓
Confirmation
    ↓
DataHub Context
    ↓
Contextual Path
    ↓
Interaction
    ↓
Outcome
```

### Rationale

The product's core value is demonstrated through the complete flow.

A smaller system with a clear end-to-end experience is more valuable for the hackathon than a large system with disconnected capabilities.

---

## TD-011: Avoid Premature Infrastructure

### Status

Accepted

### Decision

The project should not introduce additional infrastructure, services, abstractions, or files unless they solve a demonstrated problem.

### Rationale

The project is still in early development.

Premature infrastructure increases:

* Complexity
* Setup cost
* Maintenance cost
* Cognitive overhead

The preferred progression is:

```text
Need
    ↓
Problem
    ↓
Simple Solution
    ↓
Validation
    ↓
Additional Complexity Only If Necessary
```

---

## TD-012: Significant Technical Changes Require an RFC

### Status

Accepted

### Decision

Significant changes to architecture, core product flow, DataHub integration, or other major technical direction should be documented through an RFC before implementation.

Examples include:

* Changing the primary DataHub integration
* Replacing the orchestration architecture
* Changing the frontend/backend boundary
* Introducing a major data storage layer
* Changing the role of the LLM
* Adding a major architectural subsystem

### Rationale

The purpose is to preserve:

* Intent
* Context
* Trade-offs
* Alternatives
* Decision history

The project should be able to explain not only:

> What was built?

but also:

> Why was it built this way?

---

## Decision Principles

Technical decisions should generally favor:

### Simplicity

Prefer the simplest solution that satisfies the actual requirement.

### Modularity

Keep responsibilities separated.

### Flexibility

Avoid unnecessary coupling to a single provider.

### Meaningful DataHub Usage

Use DataHub as a core context mechanism.

### Reversibility

Avoid decisions that create unnecessary lock-in during early development.

### Demonstrable Value

Prioritize decisions that help produce a clear, meaningful end-to-end product experience.

---

## Current Technical Direction

```text
┌─────────────────────────────┐
│          FRONTEND           │
│                             │
│ Goal / Intent / Context UI  │
│ Learn / Explore / Act       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          BACKEND            │
│                             │
│ Orchestration               │
│ Goal Understanding          │
│ Context Processing          │
│ Path Generation             │
└──────┬───────────────┬──────┘
       │               │
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│ LLM Adapter  │ │ DataHub      │
│              │ │ Adapter      │
└──────┬───────┘ └──────┬───────┘
       │                │
       ▼                ▼
  LLM Provider    MCP Client
                        │
                        ▼
                DataHub MCP Server
                        │
                        ▼
                DataHub Context Graph
```

> **Technical decisions should serve the product's core loop: transforming user goals and contextual data into meaningful paths toward understanding or action.**
