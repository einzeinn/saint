# Product Principles

> Foundational principles for Saint.

## 1. Start With the User's Goal

Saint does not begin by asking users to understand the system.

The user begins with a goal.

The goal may be:

* Learn something
* Understand something
* Explore a context
* Complete a task
* Figure out what to do next

The system's responsibility is to understand that goal and help transform it into a meaningful path toward an outcome.

---

## 2. Constrain the Interface, Not the Intelligence

Saint should not present users with an empty canvas and expect them to understand every possibility the system supports.

Instead, the interface should provide clear entry points such as:

* Learn
* Explore
* Act
* Discover what to do

The system may remain flexible and capable behind the interface, while the user experience remains understandable and approachable.

> The product should feel focused without being artificially limited.

---

## 3. DataHub Is the Context Layer

DataHub is not an optional data source or a decorative integration.

DataHub is the primary context layer and source of truth for the system.

Saint should use the DataHub context graph to understand:

* Entities
* Relationships
* Lineage
* Metadata
* Ownership
* Glossary
* Data quality
* Other relevant contextual information

The system should derive meaningful context from the relationships between these elements rather than treating them as isolated documents.

---

## 4. Goal Before Curriculum

Saint should not force every user through the same predefined sequence of lessons.

The learning or guidance path should be derived from the user's goal.

The system should determine:

```text
User Goal
    ↓
Required Outcome
    ↓
Required Capabilities
    ↓
Required Knowledge
    ↓
Prerequisites
    ↓
Contextual Path
```

The resulting path should be relevant to what the user is actually trying to accomplish.

---

## 5. Learn Through Context

Learning should happen inside the context where the knowledge is useful.

Saint should prefer:

```text
Real Context
    ↓
Explore
    ↓
Make a Decision
    ↓
Receive Guidance
    ↓
Understand the Concept
    ↓
Apply the Concept
```

Rather than:

```text
Read Definition
    ↓
Memorize
    ↓
Answer Quiz
```

The system should help users discover why a concept matters before asking them to remember its definition.

---

## 6. Learning and Doing Are Connected

Saint does not treat learning and execution as completely separate activities.

A user may:

```text
Learn → Explore → Act
```

or:

```text
Act → Get Blocked → Learn → Continue Acting
```

The system should be able to provide the knowledge required to complete a task when that knowledge becomes relevant.

> Users should not need to know what they need to learn before they can begin.

---

## 7. Make the Agent's Understanding Visible

Before taking significant action, the system should make its interpretation of the user's goal visible.

The general flow is:

```text
User Goal
    ↓
Intent Understanding
    ↓
Goal Visualization
    ↓
User Confirmation
    ↓
Contextual Path
```

This gives the user the opportunity to:

* Confirm the interpretation
* Correct the agent
* Add missing context
* Remove irrelevant steps

The system should not silently make major assumptions when those assumptions can be shown and corrected.

---

## 8. Context Should Drive the Path

The path should be determined by the relationship between:

```text
User Goal
        +
DataHub Context
        +
User's Current Understanding
```

The system should avoid generating generic paths when relevant context is available.

The goal is not to produce the most comprehensive path.

The goal is to produce the most relevant path toward the user's desired outcome.

---

## 9. Adaptive by Default

The system should adapt based on the user's interaction and demonstrated understanding.

The general cycle is:

```text
Goal
    ↓
Contextual Path
    ↓
Learn / Explore / Act
    ↓
Assessment
    ↓
Update Understanding
    ↓
Replan
```

The system should be able to:

* Skip concepts the user already understands
* Add prerequisite concepts when necessary
* Provide additional practice when the user struggles
* Change the path when the user's goal changes

Progress should represent understanding and capability, not merely completed screens.

---

## 10. DataHub Should Be Used Meaningfully

Every major feature should be evaluated against the following question:

> **Does this feature meaningfully benefit from DataHub's context graph?**

DataHub should not be included merely because the project is participating in a DataHub hackathon.

The product should demonstrate that structured context, relationships, metadata, and lineage enable capabilities that would be significantly weaker without them.

---

## 11. Modular and Provider-Agnostic Architecture

The product should be designed so that major external providers can be replaced without rewriting the core product logic.

This applies to:

* LLM providers
* DataHub access methods
* Storage providers
* Other external services

The core product should depend on stable interfaces and domain concepts rather than directly coupling itself to a specific provider implementation.

Conceptually:

```text
Provider
    ↓
Adapter
    ↓
Application Domain
    ↓
Product Logic
```

The application should be configuration-driven wherever practical.

---

## 12. Configuration Over Hardcoding

Environment-specific configuration and secrets should be managed through environment configuration.

Provider choices, API endpoints, model choices, and other environment-dependent settings should not be scattered throughout the codebase.

The application should allow changes such as:

```text
LLM Provider A
        ↓
Configuration Change
        ↓
LLM Provider B
```

without requiring unnecessary changes to core product logic.

---

## 13. Significant Changes Require Documentation

Significant changes to the product, architecture, technical direction, or scope should be documented before implementation.

Examples include:

* Major architecture changes
* Changes to the core user flow
* New major features
* Changes to DataHub's role
* Changes to the LLM abstraction
* Changes to the frontend/backend boundary
* Significant changes to the data model

The project should use RFCs or other appropriate documentation to record these decisions.

The purpose is not bureaucracy.

The purpose is to preserve intent, prevent accidental architectural drift, and ensure that future agents and contributors understand why a decision was made.

---

## 14. Build the Smallest Meaningful System

Saint should prioritize a complete and meaningful experience over a large collection of disconnected features.

The preferred direction is:

```text
One Goal
    ↓
One Clear Interpretation
    ↓
Relevant DataHub Context
    ↓
One Meaningful Path
    ↓
One Measurable Outcome
```

A smaller system that clearly demonstrates the core idea is preferable to a larger system where the core idea is difficult to understand.

---

## Core Principle

> **Saint turns user goals into contextual paths toward understanding or action, using DataHub as the context graph that makes those paths meaningful.**
