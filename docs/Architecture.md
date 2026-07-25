# Architecture

> **Current direction (2026-07-25):** The accepted architecture revision makes the interactive terminal application and Saint Core primary. The web frontend/API diagrams below describe the earlier compatibility surface and are retained as historical context. New implementation should follow `docs/revision.md` and `docs/deployment.md`.

## 1. Architectural Overview

Saint is built around a goal-driven agent architecture that connects:

```text
User Intent
    ↓
Goal Understanding
    ↓
Goal Visualization
    ↓
User Confirmation
    ↓
DataHub Context Graph
    ↓
Contextual Path
    ↓
Learn / Explore / Act
    ↓
Outcome
```

The system is divided into two primary application boundaries:

```text
┌─────────────────────┐
│      FRONTEND       │
│                     │
│ User Experience     │
│ Goal Visualization  │
│ Contextual UI       │
│ Interaction         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       BACKEND       │
│                     │
│ Orchestration       │
│ Agent Logic         │
│ DataHub Context     │
│ LLM Integration     │
│ Domain Logic        │
└─────────────────────┘
```

The frontend and backend should remain clearly separated.

---

## 2. Core Architectural Model

The core architecture follows:

```text
USER
  ↓
INTENT
  ↓
GOAL UNDERSTANDING
  ↓
GOAL VISUALIZATION
  ↓
USER CONFIRMATION
  ↓
DATAHUB CONTEXT
  ↓
CONTEXTUAL PATH
  ↓
LEARN / EXPLORE / ACT
  ↓
LLM GUIDANCE
  ↓
OUTCOME
```

The system should not treat the LLM as the entire application.

The LLM is one component within a larger system that combines:

* User intent
* Structured domain logic
* DataHub context
* Agent reasoning
* User interaction

---

## 3. Frontend Boundary

The frontend is responsible for user experience and interaction.

Its responsibilities include:

* Presenting entry points
* Accepting user goals
* Displaying intent selection
* Visualizing the agent's interpretation
* Allowing user confirmation or correction
* Visualizing contextual paths
* Presenting relevant DataHub context
* Supporting Learn, Explore, and Act experiences
* Displaying agent guidance
* Showing progress and outcomes

The frontend should not contain core agent reasoning or direct provider-specific integration logic.

Conceptually:

```text
User
 ↓
Frontend
 ↓
Backend API
```

The frontend should receive structured state from the backend and render the appropriate experience.

---

## 4. Backend Boundary

The backend is responsible for application logic and orchestration.

Its responsibilities include:

* Goal interpretation
* Intent processing
* Agent orchestration
* DataHub context retrieval
* Context transformation
* Path generation
* Learning logic
* Exploration logic
* Action guidance
* Assessment
* Adaptation
* LLM provider integration

Conceptually:

```text
Frontend
    ↓
Backend API
    ↓
Orchestrator
    ├── Goal Understanding
    ├── Context Discovery
    ├── Path Generation
    ├── Learn Logic
    ├── Explore Logic
    └── Act Logic
```

---

## 5. Orchestration Layer

The orchestration layer coordinates the major stages of the product.

```text
┌──────────────────────────────┐
│        ORCHESTRATOR          │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  Goal Flow        Context Flow
       │                │
       └───────┬────────┘
               ▼
        Path Generation
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
    LEARN    EXPLORE    ACT
```

The orchestrator should coordinate the flow without owning every piece of domain logic.

Major logic should remain modular and independently testable.

---

## 6. Goal Understanding Flow

The initial flow begins with the user's goal.

```text
User Goal
    ↓
Intent Interpretation
    ↓
Goal Decomposition
    ↓
Required Outcome
    ↓
Required Actions
```

The result should be a structured representation of the agent's understanding.

Conceptually:

```text
Goal
├── Intent
├── Desired Outcome
├── Required Actions
├── Required Capabilities
└── Constraints
```

This representation is then visualized for user confirmation.

---

## 7. Goal Visualization Flow

The system should not immediately execute a complex plan based on an unverified interpretation.

The flow is:

```text
User Goal
    ↓
Agent Interpretation
    ↓
Structured Goal Representation
    ↓
Goal Visualization
    ↓
User Confirmation / Correction
```

After confirmation:

```text
Confirmed Goal
    ↓
Context Discovery
```

This creates an explicit boundary between:

```text
What the user said
```

and:

```text
What the system believes the user means
```

---

## 8. DataHub Context Layer

DataHub is the primary context layer and source of truth.

The application should access DataHub through an integration abstraction.

```text
┌──────────────────────┐
│   Application Logic  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   DataHub Adapter    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│    MCP Client        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ DataHub MCP Server   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ DataHub Context Graph│
└──────────────────────┘
```

The adapter exists to prevent core product logic from being tightly coupled to a specific external integration mechanism.

The initial primary integration is the DataHub MCP Server.

---

## 9. Context Discovery

After the user confirms the goal, the system determines what context is relevant.

```text
Confirmed Goal
      ↓
Context Discovery
      ↓
Relevant Entities
      ↓
Relevant Relationships
      ↓
Relevant Metadata
      ↓
Contextual Representation
```

The system should prioritize context according to the goal.

Possible context includes:

* Data assets
* Dashboards
* Pipelines
* Tables
* Columns
* Lineage
* Ownership
* Glossary
* Domains
* Data quality
* Freshness
* Documentation

The goal is not to retrieve the entire DataHub graph.

The goal is to find the context necessary to move toward the desired outcome.

---

## 10. Contextual Path Generation

The path generation stage combines:

```text
User Goal
    +
User Intent
    +
Relevant DataHub Context
    +
User Understanding
```

to produce:

```text
Contextual Path
```

Conceptually:

```text
Goal
    ↓
Required Outcome
    ↓
Required Actions
    ↓
Required Capabilities
    ↓
Required Knowledge
    ↓
Prerequisites
    ↓
Contextual Path
```

The path may contain:

* Context exploration
* Explanations
* Questions
* Tasks
* Hints
* Assessments
* Decisions
* Additional prerequisite steps

---

## 11. Mode Architecture

The contextual path may enter one of three primary modes.

```text
                    CONTEXTUAL PATH
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
        LEARN            EXPLORE            ACT
```

### Learn

Focuses on developing understanding.

```text
Context
    ↓
Explore
    ↓
Discover
    ↓
Understand
    ↓
Apply
```

### Explore

Focuses on investigation and understanding.

```text
Question
    ↓
Context
    ↓
Relationships
    ↓
Evidence
    ↓
Understanding
```

### Act

Focuses on completing a concrete task.

```text
Goal
    ↓
Required Context
    ↓
Guided Action
    ↓
Outcome
```

The modes are not isolated.

A flow may transition between them:

```text
ACT
 ↓
BLOCKED
 ↓
LEARN
 ↓
UNDERSTAND
 ↓
ACT
```

---

## 12. LLM Integration

The LLM should be treated as a replaceable provider.

Conceptually:

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

The core application should not depend directly on one specific provider.

Provider selection should be controlled through configuration.

---

## 13. Domain Layer

The application should use domain concepts independent of external provider formats.

Potential domain concepts include:

```text
Goal
Intent
Context
Knowledge Node
Relationship
Path
Task
Assessment
Mastery
Outcome
```

External data should be transformed into domain representations where appropriate.

Conceptually:

```text
External Data
    ↓
Adapter
    ↓
Domain Representation
    ↓
Application Logic
```

This keeps the application modular and reduces provider-specific coupling.

---

## 14. Configuration Architecture

Environment-specific configuration should be separated from application logic.

Conceptually:

```text
Environment Configuration
        ↓
Configuration Loader
        ↓
Application Settings
        ↓
Modules
```

Configuration should control environment-specific values such as:

* LLM provider
* LLM model
* API endpoints
* DataHub connection
* Tokens and secrets
* Runtime environment
* Logging configuration

The application should avoid scattering direct environment variable access throughout the codebase.

---

## 15. Provider Abstraction

External integrations should be replaceable through adapters or interfaces.

```text
                INTERFACE
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
   Provider A              Provider B
```

This principle applies to:

* LLM providers
* DataHub access mechanisms
* Other external services

The product's core logic should depend on the interface rather than the provider implementation.

---

## 16. Data Flow

The primary data flow is:

```text
USER
  │
  ▼
FRONTEND
  │
  ▼
BACKEND API
  │
  ▼
ORCHESTRATOR
  │
  ├──► Goal Understanding
  │
  ├──► LLM
  │
  ├──► DataHub Adapter
  │          │
  │          ▼
  │    DataHub MCP
  │          │
  │          ▼
  │    DataHub Graph
  │
  └──► Path Generation
           │
           ▼
     Learn / Explore / Act
           │
           ▼
        FRONTEND
```

---

## 17. Architectural Principles

The architecture should follow these principles:

### Modular

Components should have clear responsibilities.

### Provider-Agnostic

External providers should be replaceable where practical.

### Configuration-Driven

Environment-specific behavior should be controlled through configuration.

### DataHub-Centered

DataHub should be a meaningful part of the product's core mechanism.

### Frontend/Backend Separation

User experience and application logic should remain clearly separated.

### Domain-Oriented

Core product concepts should not be tightly coupled to external API formats.

### RFC-Governed

Significant architectural changes should be documented before implementation.

---

## 18. Architectural Direction

The architecture should remain flexible during early development.

The system should avoid premature complexity.

The preferred direction is:

```text
Clear Boundaries
    ↓
Simple Interfaces
    ↓
Modular Components
    ↓
Validated Integrations
    ↓
Incremental Complexity
```

The architecture should evolve as the product's actual requirements become clearer.

The system should not introduce additional infrastructure, services, abstractions, or components without a demonstrated need.

---

## Core Architecture

```text
                         ┌──────────────┐
                         │     USER     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   FRONTEND   │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ BACKEND API  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ ORCHESTRATOR │
                         └──────┬───────┘
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
            GOAL ENGINE     LLM LAYER    DATAHUB LAYER
                  │             │             │
                  └─────────────┼─────────────┘
                                ▼
                       CONTEXTUAL PATH
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
                LEARN        EXPLORE         ACT
                  │             │             │
                  └─────────────┼─────────────┘
                                ▼
                              OUTCOME
```

> **Saint is a modular goal-to-outcome system where the agent uses DataHub's context graph to determine what the user needs to understand and do next.**
