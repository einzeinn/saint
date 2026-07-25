# Roadmap

> **Current execution direction (2026-07-25):** The accepted revision changes Saint's primary surface from a web application to an installable interactive terminal application. The roadmap stages below remain useful for product capabilities, but active implementation should target Saint Core and the CLI. The frontend and hosted web deployment are archived compatibility surfaces.

## 1. Roadmap Philosophy

Saint should be developed incrementally.

Each phase should validate an important assumption before significant complexity is added.

The preferred development cycle is:

```text
Define
  ↓
Build
  ↓
Validate
  ↓
Learn
  ↓
Refine
```

The roadmap prioritizes the core product loop:

```text
User Goal
    ↓
Goal Understanding
    ↓
Goal Visualization
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

---

# Phase 0: Foundation

## Objective

Establish the repository and development foundation.

### Focus

* Initialize project structure
* Establish frontend/backend separation
* Configure development environments
* Establish environment-based configuration
* Set up basic application communication
* Establish basic logging and error handling

### Expected Result

The application can run locally with a clear separation between:

```text id="1b8y6t"
Frontend
    ↕
Backend
```

No major product feature is required at this stage.

---

# Phase 1: Product Flow Prototype

## Objective

Validate the core user experience without requiring the complete DataHub integration.

### Focus

Implement a minimal version of:

```text id="v0a1e8"
User Goal
    ↓
Intent
    ↓
Goal Visualization
    ↓
User Confirmation
    ↓
Mock Context
    ↓
Mock Path
    ↓
Interaction
```

### Questions to Validate

* Does the user understand the entry points?
* Is the goal visualization clear?
* Does confirmation feel useful?
* Does the contextual path feel more useful than a normal chat response?
* Is the Learn / Explore / Act model understandable?

### Expected Result

A user can experience the core interaction loop.

---

# Phase 2: DataHub Integration

## Objective

Connect the product to real DataHub context.

### Focus

* Establish DataHub MCP integration
* Implement DataHub adapter boundary
* Discover available context
* Retrieve relevant entities and relationships
* Transform DataHub context into application-relevant representations

### Flow

```text id="2r66kq"
Confirmed Goal
      ↓
DataHub Context Discovery
      ↓
Relevant Context
      ↓
Application Representation
```

### Expected Result

The application can retrieve meaningful context from DataHub based on a user's goal.

---

# Phase 3: Contextual Path Generation

## Objective

Generate a meaningful path using real DataHub context.

### Focus

Combine:

```text id="q8hr1e"
User Goal
    +
Intent
    +
DataHub Context
    +
User Understanding
```

to generate:

```text id="g8k2xn"
Contextual Path
```

### Path Components May Include

* Context discovery
* Explanations
* Questions
* Tasks
* Hints
* Decisions
* Prerequisites
* Assessments

### Expected Result

The path is visibly influenced by actual DataHub context.

---

# Phase 4: Core Interaction Experience

## Objective

Create one complete user journey.

### Focus

Select one primary experience from:

```text id="h9t0un"
LEARN
EXPLORE
ACT
```

and implement it end-to-end.

### Preferred Flow

```text id="p88q5c"
Goal
    ↓
Interpretation
    ↓
Confirmation
    ↓
DataHub Context
    ↓
Contextual Path
    ↓
User Interaction
    ↓
Guidance
    ↓
Outcome
```

### Expected Result

A user can complete a meaningful task or gain meaningful understanding through Saint.

---

# Phase 5: Adaptive Behavior

## Objective

Make the experience respond to the user's demonstrated understanding and progress.

### Focus

* Identify missing prerequisites
* Skip known concepts
* Add explanations when necessary
* Provide additional practice
* Replan the path

### Flow

```text id="d0w1yz"
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

### Expected Result

The system can adapt rather than simply executing a static sequence.

---

# Phase 6: Demo Refinement

## Objective

Transform the validated experience into a clear hackathon demonstration.

### Focus

* Improve user experience
* Remove unnecessary complexity
* Improve visual clarity
* Improve feedback
* Improve reliability
* Prepare a clear narrative

### Demo Structure

```text id="3j3j4m"
Problem
  ↓
User Goal
  ↓
Saint Interpretation
  ↓
DataHub Context
  ↓
Contextual Path
  ↓
Interaction
  ↓
Outcome
```

### Expected Result

The product's core idea is understandable within a short demonstration.

---

# Phase 7: Contribution

## Objective

Identify meaningful ways to contribute back to the DataHub ecosystem.

### Possible Directions

* Reusable agent workflow
* DataHub Skill
* Documentation
* Integration pattern
* Reusable tool
* Technical contribution

### Principle

The contribution should emerge from the actual development process.

The project should not create an artificial contribution merely to claim one.

---

# Priority Order

The project should prioritize:

```text id="j7ty23"
1. Complete User Experience
        ↓
2. Meaningful DataHub Integration
        ↓
3. Contextual Path Generation
        ↓
4. Strong Interaction
        ↓
5. Adaptation
        ↓
6. Contribution
        ↓
7. Additional Features
```

---

# MVP Definition

The MVP is complete when the following flow works:

```text id="n7ubx5"
┌─────────────────────┐
│      USER GOAL      │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  GOAL UNDERSTANDING │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ GOAL VISUALIZATION  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│      CONFIRMATION   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   DATAHUB CONTEXT   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ CONTEXTUAL PATH     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   USER INTERACTION  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│      OUTCOME        │
└─────────────────────┘
```

---

# Roadmap Principles

## Validate Before Expanding

Do not build complex features before validating the underlying product assumption.

## Prefer Complete Flows

A complete experience is more valuable than isolated features.

## Keep Complexity Earned

New infrastructure and abstractions should be introduced only when actual requirements justify them.

## Preserve Flexibility

The architecture should remain adaptable while the product is still being validated.

## Focus on the Core Thesis

Every major feature should strengthen the connection between:

```text id="53e2b4"
User Goal
    +
DataHub Context
    ↓
Meaningful Path
    ↓
Outcome
```

---

## Roadmap Summary

> **First make the loop work. Then make the loop real. Then make the loop adaptive. Then make the loop undeniable.**
