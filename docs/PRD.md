# Product Requirements Document

## 1. Product Overview

Saint is an adaptive context-driven agent that helps users move from a goal to a meaningful outcome by combining:

```text
User Intent
    +
DataHub Context Graph
    +
Agent Reasoning
    ↓
Contextual Path
    ↓
Understanding or Action
```

Saint does not force users through a fixed curriculum or require them to understand the structure of the underlying data ecosystem before they begin.

Instead, users start with an intent or goal.

Saint then:

1. Understands the user's intent
2. Interprets the user's goal
3. Visualizes its understanding
4. Allows the user to confirm or modify the interpretation
5. Retrieves relevant context from DataHub
6. Determines the relevant path toward the user's desired outcome
7. Guides the user through learning, exploration, or action
8. Evaluates progress where appropriate
9. Adapts the path when new information becomes available

---

## 2. Core Product Loop

```text
USER GOAL
    ↓
INTENT
    ↓
GOAL VISUALIZATION
    ↓
USER CONFIRMATION
    ↓
DATAHUB CONTEXT GRAPH
    ↓
CONTEXTUAL PATH
    ↓
┌─────────────┬──────────────┬─────────────┐
│    LEARN    │   EXPLORE    │     ACT     │
│             │              │             │
│ Understand  │ Investigate  │ Complete    │
│ concepts    │ context      │ task        │
└─────────────┴──────────────┴─────────────┘
                    ↓
              LLM GUIDANCE
                    ↓
                 OUTCOME
```

---

## 3. Target User

Saint is initially designed for people working with or learning within complex data ecosystems.

Potential users include:

* Data Analysts
* Analytics Engineers
* Data Engineers
* New team members onboarding into a data ecosystem
* Technical users who need to understand unfamiliar data assets

The initial product should focus on users who need to understand or work with:

* Datasets
* Dashboards
* Pipelines
* Tables
* Data relationships
* Metadata
* Data quality
* Ownership
* Lineage

The product should not be positioned as a general-purpose learning platform during the initial scope.

Its flexibility should come from the goal-driven interaction model rather than from supporting every possible domain.

---

## 4. User Entry Point

Saint should not begin with an empty input field as the primary experience.

The user should be able to express intent through structured entry points.

Example:

```text
What do you want to do?

[ Learn ]
Build understanding around a topic or context.

[ Explore ]
Investigate how something works or why something happened.

[ Act ]
Complete a task using the available data context.

[ I'm Not Sure ]
Help me figure out what I need to understand or do.
```

A custom goal may also be provided when the user's intent does not fit a predefined entry point.

The interface should provide structure without artificially limiting the underlying agent.

---

## 5. Goal Understanding

After the user provides a goal, Saint should convert the goal into a structured interpretation.

Example:

```text
User:
"I want to understand why the revenue dashboard changed."

Saint:

Intent:
Investigation

Desired Outcome:
Identify the reason for the revenue change

Required Actions:
1. Identify the affected dashboard
2. Find the underlying data assets
3. Trace upstream lineage
4. Check freshness and quality
5. Investigate recent changes
```

The user should be able to confirm or modify the interpretation before the system proceeds.

---

## 6. Context Retrieval

After the goal is confirmed, Saint should retrieve relevant context from DataHub.

Relevant context may include:

* Entities
* Relationships
* Lineage
* Metadata
* Ownership
* Glossary terms
* Data quality information
* Freshness
* Domains
* Documentation
* Other relevant DataHub context

The system should prioritize context based on its relevance to the user's goal.

The objective is not to retrieve everything.

The objective is to retrieve the context necessary to move toward the desired outcome.

---

## 7. Contextual Path Generation

Saint should transform the user's goal and relevant DataHub context into a contextual path.

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

* Explanations
* Explorations
* Questions
* Tasks
* Hints
* Assessments
* Decisions
* Additional prerequisite concepts

The path should adapt based on the user's interaction.

---

## 8. Learn Mode

Learn Mode should prioritize contextual discovery over passive content consumption.

The intended learning loop is:

```text
Encounter Real Context
        ↓
Explore
        ↓
Make a Decision
        ↓
Receive Guidance
        ↓
Discover the Concept
        ↓
Apply the Concept
```

Example:

```text
Task:
Find the upstream source of this dashboard metric.
```

After the user explores the context, Saint may explain:

> "You just traced data lineage. Lineage helps you understand how data moves from upstream sources to downstream consumers."

The user learns the concept in the context where it matters.

---

## 9. Explore Mode

Explore Mode should help users investigate a question or context.

Example:

```text
User Goal:
Why is this dataset unreliable?
```

Saint may guide the user through:

```text
Dataset
    ↓
Freshness
    ↓
Quality
    ↓
Ownership
    ↓
Upstream Lineage
    ↓
Evidence
```

The result should be an understanding supported by relevant context rather than a generic answer detached from the DataHub environment.

---

## 10. Act Mode

Act Mode should help users complete a concrete task.

Example:

```text
Goal:
Find the best dataset for customer retention analysis.
```

Saint may guide the user through:

```text
Candidate Discovery
        ↓
Metadata Comparison
        ↓
Quality Evaluation
        ↓
Freshness Evaluation
        ↓
Ownership Evaluation
        ↓
Lineage Evaluation
        ↓
Final Decision
```

When the user lacks required knowledge, the system may transition into contextual learning.

```text
ACT
 ↓
BLOCKED
 ↓
LEARN
 ↓
UNDERSTAND
 ↓
ACT AGAIN
```

---

## 11. Adaptive Learning and Mastery

Saint should adapt based on the user's demonstrated understanding.

The system should be able to:

* Skip concepts the user already understands
* Identify missing prerequisites
* Provide additional explanations
* Provide additional practice
* Replan the path
* Adjust the level of guidance

Conceptually:

```text
Goal
    ↓
Path
    ↓
Interaction
    ↓
Assessment
    ↓
Updated Understanding
    ↓
Replan
```

Progress should represent capability and understanding rather than simply completed lessons.

---

## 12. Agent Responsibilities

The agent should be responsible for:

### Goal Understanding

Interpreting the user's intent and desired outcome.

### Goal Decomposition

Breaking a broad goal into relevant actions and capabilities.

### Context Discovery

Finding relevant DataHub context.

### Prerequisite Reasoning

Determining what knowledge or context is required.

### Path Generation

Creating a contextual path toward the desired outcome.

### Guidance

Providing explanations, questions, hints, and feedback.

### Assessment

Evaluating user decisions, explanations, or task completion where appropriate.

### Adaptation

Updating the path based on the user's progress and newly discovered context.

---

## 13. DataHub Responsibilities

DataHub should serve as the primary context layer and source of truth.

Saint should use DataHub to access relevant context rather than maintaining a disconnected duplicate knowledge universe.

The initial integration should use the DataHub MCP Server as the primary access layer.

Conceptually:

```text
Saint
  ↓
MCP Client / Adapter
  ↓
DataHub MCP Server
  ↓
DataHub Context Graph
```

The application should interact with DataHub through an abstraction layer so that the core product logic remains decoupled from provider-specific implementation details.

---

## 14. Core Product Output

Depending on the user's intent, Saint may produce:

### Learning Path

```text
Concept
    ↓
Context
    ↓
Task
    ↓
Assessment
```

### Exploration Path

```text
Question
    ↓
Relevant Context
    ↓
Relationships
    ↓
Evidence
    ↓
Understanding
```

### Action Path

```text
Goal
    ↓
Required Context
    ↓
Guided Steps
    ↓
Outcome
```

---

## 15. MVP Boundary

The MVP should demonstrate one complete end-to-end experience.

The MVP must be able to:

1. Accept a user goal
2. Identify the user's intent
3. Visualize the agent's interpretation
4. Allow user confirmation or correction
5. Retrieve relevant DataHub context
6. Generate a contextual path
7. Guide the user through at least one meaningful interaction
8. Produce a meaningful outcome

The MVP should prioritize a complete experience over a large feature set.

The core product loop is more important than supporting every possible intent.

---

## 16. Non-Goals

The initial version should not attempt to become:

* A general-purpose LMS
* A general-purpose chatbot
* A replacement for DataHub
* A generic search engine
* A universal AI agent for every domain
* A full enterprise data governance platform

The system should remain focused on its core value:

> **Turning user goals and DataHub context into a meaningful path toward understanding or action.**

---

## 17. Success Criteria

The MVP is successful if a user can:

1. Start with a real goal
2. Understand how Saint interprets that goal
3. See relevant context from DataHub
4. Follow a meaningful contextual path
5. Learn, explore, or act using that context
6. Reach an outcome they could not reach as efficiently without the system

The product should make the following experience possible:

> **"I knew what I wanted to accomplish, but I didn't know what I needed to understand first. Saint helped me discover that path using the context already present in my data ecosystem."**
