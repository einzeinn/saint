# Revision: Saint Architecture and Product Direction

## Status

Accepted

## Scope

Major Product and Architecture Revision

## Date

2026-07-25

---

# 1. Summary

Saint's product direction is revised from a web application into an interactive terminal application.

The core product concept remains unchanged:

```text
User Goal
    ↓
Goal Understanding
    ↓
DataHub Context
    ↓
Adaptive Path
    ↓
Learning / Exploration / Action
    ↓
Assessment
    ↓
Outcome
```

However, the primary user interface and deployment strategy are changed.

Saint will now prioritize:

```text
Interactive Terminal Application
        +
Rich Terminal UI
        +
Saint Core
        +
DataHub Integration
```

Instead of:

```text
Web Frontend
        +
Backend API
        +
Remote DataHub
        +
MCP Server
```

---

# 2. Motivation

The previous direction introduced unnecessary infrastructure complexity before the core product had been validated.

The previous architecture required consideration of:

```text
Frontend
    ↓
Vercel
    ↓
Backend
    ↓
Render
    ↓
MCP Server
    ↓
DataHub Instance
```

This created several additional challenges:

* DataHub instance availability
* Remote DataHub deployment
* MCP Server deployment
* Docker requirements
* Docker Desktop local development
* Potential Linux or virtualization requirements
* Network access between services
* Remote authentication
* Render deployment limitations

The project risked spending too much development effort on infrastructure rather than the core product.

The project should prioritize proving:

> **Can Saint use DataHub context to transform a user's goal into a meaningful path toward understanding and action?**

The new direction reduces infrastructure overhead while preserving the core product thesis.

---

# 3. Product Direction

Saint is an interactive terminal application that helps users move from an intention to a meaningful outcome.

Saint should not be treated as:

```text
User
    ↓
Chat Box
    ↓
LLM Answer
```

Instead:

```text
User Goal
    ↓
Goal Understanding
    ↓
User Confirmation
    ↓
DataHub Context
    ↓
Contextual Path
    ↓
Interaction
    ↓
Assessment
    ↓
Outcome
```

The terminal is the interface.

The intelligence and product logic remain inside the Saint Core.

---

# 4. The CLI Is Not a Basic Command Interface

Saint should not resemble a traditional CLI consisting only of:

```bash
saint learn "some topic"
```

The preferred direction is a rich interactive terminal application.

Conceptually:

```text
╭──────────────────────────────────────────────────────╮
│  ✦ SAINT                                      v0.1   │
│  Context-aware path to understanding                 │
╰──────────────────────────────────────────────────────╯

  WHAT DO YOU WANT TO ACCOMPLISH?

  ┌─ 01 ──────────────────────────────────────────────┐
  │  ◉ Learn                                           │
  │    Build understanding from your current context   │
  └────────────────────────────────────────────────────┘

  ┌─ 02 ──────────────────────────────────────────────┐
  │  ◌ Explore                                         │
  │    Discover relationships, lineage, and context    │
  └────────────────────────────────────────────────────┘

  ┌─ 03 ──────────────────────────────────────────────┐
  │  ◆ Solve                                           │
  │    Investigate a real problem using your data      │
  └────────────────────────────────────────────────────┘
```

The user should receive structured choices instead of being presented with an empty input field immediately.

This preserves the previously established product principle:

> **Narrow the initial experience without making the product feel limited.**

The system should guide the user toward meaningful actions while preserving flexibility through natural-language input.

---

# 5. Interaction Model

The primary interaction flow is:

```text
┌─────────────────────┐
│       ENTRY         │
│ Learn / Explore /   │
│ Solve               │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│     USER GOAL       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ GOAL INTERPRETATION │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ USER CONFIRMATION   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  DATAHUB CONTEXT    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ CONTEXTUAL PATH     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ USER INTERACTION    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│    ASSESSMENT       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│      OUTCOME        │
└─────────────────────┘
```

---

# 6. Goal Visualization

Saint should make its understanding of the user's goal visible.

Example:

```text
╭─ I UNDERSTAND YOUR GOAL AS ───────────╮
│                                       │
│  Investigate the possible causes of   │
│  inaccurate revenue data.             │
│                                       │
│  To do this, I'll investigate:        │
│                                       │
│  ◉ Revenue Dashboard                  │
│  ◉ Upstream Datasets                  │
│  ◉ Schema & Fields                    │
│  ◉ Data Lineage                       │
│                                       │
│  [ Continue ]  [ Adjust ]             │
╰───────────────────────────────────────╯
```

This allows the user to correct a misunderstanding before the system generates an entire path based on an incorrect assumption.

The flow is:

```text
User Goal
    ↓
Saint's Interpretation
    ↓
User Confirmation
    ↓
Context Discovery
```

---

# 7. DataHub Integration Direction

Saint will no longer prioritize DataHub MCP Server as its primary integration method.

The preferred integration direction is:

```text
Saint Core
    ↓
DataHub Integration Adapter
    ↓
Agent Context Kit / DataHub SDK
    ↓
DataHub
```

The reason is that Saint is a custom application with its own orchestration and user experience.

The DataHub integration should be embedded into the Saint backend/core rather than requiring a separate MCP service unless future requirements justify it.

The integration boundary should remain modular.

```text
┌──────────────────────────────┐
│        Saint Core            │
├──────────────────────────────┤
│ Goal                         │
│ Path                         │
│ Learning                     │
│ Assessment                   │
│ Orchestration                │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    DataHub Adapter           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Agent Context Kit / SDK      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          DataHub             │
└──────────────────────────────┘
```

---

# 8. Why MCP Is Not the Primary Direction

MCP remains a valid possible integration method.

However, it is not currently the preferred path because it introduces additional operational complexity:

```text
Saint
    ↓
MCP Client
    ↓
MCP Server
    ↓
DataHub
```

This potentially requires:

* MCP server lifecycle management
* Additional deployment considerations
* Remote service configuration
* Authentication between services
* Additional infrastructure

The project should not introduce this complexity unless it provides a clear product or technical advantage.

The principle is:

> **Use the simplest integration that provides meaningful DataHub capabilities.**

---

# 9. DataHub Instance Strategy

The DataHub hackathon resources provide resources such as:

* Documentation
* Repositories
* Sample datasets
* Integration examples

They do not necessarily provide a ready-to-use remote DataHub instance with credentials.

Therefore, Saint should not assume that the following already exist:

```text
DATAHUB_GMS_URL
DATAHUB_TOKEN
```

The project must first establish how the DataHub environment will be provided.

Possible environments include:

```text
Development:
Local DataHub instance

Production:
Remote DataHub instance
```

The initial development priority is to validate the core integration and product flow.

A remote production DataHub deployment should not block early product validation.

---

# 10. Docker Strategy

Docker Desktop is not a mandatory development dependency for Saint.

The project should not require Docker Desktop simply because a possible DataHub integration method uses containers.

The following distinction must be maintained:

```text
Running Full DataHub Locally
        ≠
Using DataHub Integration Libraries
```

If local DataHub development requires Docker, that is an environment-specific requirement.

It should not automatically become a requirement for the entire Saint development workflow.

The project should first investigate:

* Native DataHub integration
* Agent Context Kit
* DataHub SDK
* Remote DataHub instances
* Cloud deployment options

before introducing Docker as a mandatory local dependency.

---

# 11. UI Direction

Saint should have a visually distinctive terminal interface.

The interface should not rely on the traditional appearance of:

```text
Black Background
Green Text
Blinking Cursor
```

The visual direction should be closer to:

```text
Interactive Terminal Application
        +
IDE
        +
Data Lineage Explorer
        +
Interactive Tutor
```

Potential interface elements include:

* Panels
* Cards
* Sidebar navigation
* Tabs
* Progress indicators
* Interactive selectors
* Modal views
* Markdown rendering
* Tables
* Loading states
* Context visualizations
* Graph representations

The UI should make the Saint methodology visible.

---

# 12. Recommended UI Framework

The initial UI framework direction is Textual.

Conceptually:

```text
┌───────────────────────┬───────────────────────────┐
│                       │                           │
│   Saint               │   Context                 │
│                       │                           │
│   Goal                │   ┌───────┐               │
│   ───────────────     │   │ Data  │               │
│   ✓ Understand        │   └───┬───┘               │
│   ◉ Explore           │       │                   │
│   ○ Assess            │   ┌───▼───┐               │
│                       │   │ Table │               │
│                       │   └───────┘               │
├───────────────────────┴───────────────────────────┤
│ > What do you think this relationship means?       │
└─────────────────────────────────────────────────────┘
```

The UI should be interactive rather than merely rendering text output.

---

# 13. New High-Level Architecture

The preferred architecture is:

```text
┌──────────────────────────────┐
│       Textual UI             │
│    Interactive Terminal      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Saint Application      │
│            Core              │
├──────────────────────────────┤
│ Goal                         │
│ Curriculum                   │
│ Context                      │
│ Assessment                   │
│ Orchestration                │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│ LLM Provider │ │ DataHub      │
│ Adapter      │ │ Adapter      │
└──────────────┘ └──────┬───────┘
                        │
                        ▼
                   ┌─────────┐
                   │ DataHub │
                   └─────────┘
```

The application core should not be directly coupled to a specific LLM provider or DataHub integration implementation.

---

# 14. Recommended Project Direction

The project should prioritize:

```text
Python
    ↓
Textual UI
    ↓
Saint Core
    ↓
DataHub Integration
    ↓
LLM Provider
```

The primary MVP does not require:

```text
Vercel
Render
Separate Frontend
Separate MCP Server
```

These may become relevant in future versions if the product requires a web interface or remote service architecture.

---

# 15. Modular Boundaries

The architecture should maintain clear boundaries:

```text
┌─────────────────────────┐
│          UI             │
│       Textual           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Application Core     │
│                         │
│ Goal                    │
│ Path                    │
│ Curriculum              │
│ Assessment              │
└───────┬─────────┬───────┘
        │         │
        ▼         ▼
┌────────────┐ ┌────────────┐
│ LLM        │ │ DataHub    │
│ Adapter    │ │ Adapter    │
└────────────┘ └────────────┘
```

The core should not directly depend on:

* Specific terminal rendering details
* A specific LLM provider
* A specific DataHub transport mechanism

This preserves flexibility.

---

# 16. Example Saint Experience

## Step 1: Start Saint

```bash
saint
```

## Step 2: Select an Intent

```text
What do you want to accomplish?

[ Learn ]
[ Explore ]
[ Solve ]
```

## Step 3: Define a Goal

```text
> I want to understand why our revenue dashboard may contain
  incorrect data.
```

## Step 4: Saint Interprets the Goal

```text
I understand your goal as:

Investigate possible causes of inaccurate revenue data.

Relevant context required:

✓ Revenue Dashboard
✓ Upstream Datasets
✓ Schema
✓ Data Lineage
✓ Query Usage

[ Continue ] [ Adjust ]
```

## Step 5: DataHub Context Discovery

```text
Searching DataHub...

✓ Dashboard found
✓ 3 upstream datasets found
✓ Revenue-related fields identified
✓ Lineage path constructed
✓ 12 relevant queries found
```

## Step 6: Context Visualization

```text
Dashboard
    ↓
revenue_daily
    ↓
orders_clean
    ↓
raw_orders
```

Saint explains why the path is relevant.

## Step 7: Contextual Path

```text
Investigation Path

[1] Understand the dashboard
[2] Inspect revenue_daily
[3] Trace upstream lineage
[4] Inspect revenue calculation fields
[5] Analyze query usage
[6] Form a hypothesis
```

## Step 8: Interaction

Saint does not simply provide a final answer.

It may ask:

```text
What do you think could happen if duplicate order IDs
are introduced into the upstream dataset?
```

The user responds.

Saint evaluates the answer and adapts the next step.

---

# 17. Product Thesis Remains Unchanged

The architectural direction has changed.

The product thesis has not.

Saint still exists to help users move from:

```text
Intention
    ↓
Understanding
    ↓
Context
    ↓
Path
    ↓
Capability
    ↓
Action
    ↓
Outcome
```

The change is primarily about reducing infrastructure complexity and increasing focus on the core experience.

---

# 18. Impact on Roadmap

The roadmap should be interpreted as follows.

## Phase 0: Foundation

Build:

* Python project foundation
* Environment configuration
* Modular boundaries
* Logging
* Basic Textual application

## Phase 1: Product Flow Prototype

Build:

```text
Entry
    ↓
Intent Selection
    ↓
Goal Input
    ↓
Goal Interpretation
    ↓
Confirmation
    ↓
Mock Context
    ↓
Mock Path
```

## Phase 2: DataHub Integration

Build:

```text
Saint Core
    ↓
DataHub Adapter
    ↓
Agent Context Kit / SDK
    ↓
DataHub
```

Validate:

* DataHub connectivity
* Dataset discovery
* Entity retrieval
* Schema access
* Lineage retrieval
* Relevant context extraction

## Phase 3: Contextual Path Generation

Transform:

```text
User Goal
    +
DataHub Context
    +
Intent
```

into:

```text
Contextual Path
```

## Phase 4: Core Interaction Experience

Complete one end-to-end experience:

```text
Goal
    ↓
Interpretation
    ↓
DataHub Context
    ↓
Path
    ↓
Interaction
    ↓
Outcome
```

## Phase 5: Adaptive Behavior

Add:

* Assessment
* Understanding state
* Path adaptation
* Prerequisite discovery
* Replanning

## Phase 6: Demo Refinement

Improve:

* Terminal UI
* Visual clarity
* Interaction flow
* Loading states
* Reliability
* Demo narrative

---

# 19. MVP Definition

The MVP is complete when a user can:

```text
1. Start Saint
        ↓
2. Select an intention
        ↓
3. Define a goal
        ↓
4. Confirm Saint's interpretation
        ↓
5. Discover relevant DataHub context
        ↓
6. Receive a contextual path
        ↓
7. Interact with the path
        ↓
8. Reach a meaningful outcome
```

The core demo should demonstrate that DataHub is not superficial.

The result should be meaningfully better because DataHub context is available.

---

# 20. Decision

The following decisions are accepted:

### Product Interface

Saint will prioritize an interactive terminal application.

### UI

Saint will use a rich terminal UI rather than a basic command-line interface.

### DataHub Integration

Saint will prioritize direct integration through Agent Context Kit, SDK, or another appropriate DataHub-native integration layer over a separate MCP Server.

### MCP

MCP remains a possible future integration path but is not the primary implementation direction.

### Docker

Docker Desktop is not a mandatory local development dependency unless a specific integration requirement makes it necessary.

### Web Application

A web application is deferred.

The core product should be validated through the interactive terminal application first.

### Architecture

Saint Core must remain modular and decoupled from:

* UI implementation
* LLM provider
* DataHub integration mechanism

---

# 21. Final Direction

Saint is:

> **An interactive terminal application that uses DataHub context to help users move from a goal to understanding, action, and outcome through an adaptive path.**

The core experience is:

```text
┌──────────────┐
│    GOAL      │
└──────┬───────┘
       ▼
┌──────────────┐
│ UNDERSTAND   │
└──────┬───────┘
       ▼
┌──────────────┐
│   DATAHUB    │
└──────┬───────┘
       ▼
┌──────────────┐
│   CONTEXT    │
└──────┬───────┘
       ▼
┌──────────────┐
│     PATH     │
└──────┬───────┘
       ▼
┌──────────────┐
│  INTERACT    │
└──────┬───────┘
       ▼
┌──────────────┐
│    OUTCOME   │
└──────────────┘
```

> **Reduce the infrastructure. Preserve the ambition. Focus the intelligence where it matters.**
