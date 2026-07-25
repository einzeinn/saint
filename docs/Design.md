# Design

## 1. Design Direction

Saint should feel like a system that helps users think through a goal.

The experience should not feel like:

* A generic chatbot
* A traditional learning management system
* A search engine
* A blank canvas with no direction

Instead, the experience should feel like:

```text
User has a goal
        ↓
Saint helps clarify it
        ↓
Saint makes the path visible
        ↓
Saint brings relevant context
        ↓
User understands what matters
        ↓
User takes meaningful action
```

The interface should reduce cognitive load while preserving the flexibility of the underlying agent.

---

## 2. Core Design Principle

> **The interface should provide structure without making the user feel constrained.**

Saint should not expose every capability at once.

Instead of:

```text
What do you want to do?
[ Completely Empty Input ]
```

The user should receive clear entry points:

```text
What brings you here?

┌──────────────┐  ┌──────────────┐
│    LEARN     │  │   EXPLORE    │
│              │  │              │
│ Understand   │  │ Investigate  │
│ something    │  │ a context    │
└──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐
│     ACT      │  │  NOT SURE    │
│              │  │              │
│ Complete     │  │ Help me find │
│ a task       │  │ the next step│
└──────────────┘  └──────────────┘
```

These entry points are interaction affordances, not hard limitations.

---

## 3. The Core User Experience

The primary experience is:

```text
INTENT
  ↓
GOAL
  ↓
UNDERSTANDING
  ↓
VISUALIZATION
  ↓
CONFIRMATION
  ↓
CONTEXT
  ↓
PATH
  ↓
INTERACTION
  ↓
OUTCOME
```

The user should always have a general understanding of:

1. What they are trying to accomplish
2. What Saint believes they are trying to accomplish
3. Why the current step exists
4. What context is being used
5. What they should do next

---

## 4. Goal First

The experience should begin with the user's goal rather than with the system's internal structure.

The user should not need to understand:

* DataHub
* Metadata
* Lineage
* Graph structures
* Agent architecture

before using Saint.

The system should translate user goals into the relevant context and concepts.

```text id="23m6lo"
User Language
    ↓
Intent
    ↓
Structured Goal
    ↓
DataHub Context
```

The system should use technical complexity internally while presenting understandable concepts to the user.

---

## 5. Goal Visualization

The system should make its interpretation visible.

Example:

```text id="0g3gkk"
Your goal:

Understand why revenue changed
            │
            ├── Find the affected dashboard
            │
            ├── Identify underlying data
            │
            ├── Trace upstream lineage
            │
            ├── Check data quality
            │
            └── Investigate recent changes
```

The user should be able to:

```text id="c04h40"
CONFIRM
    │
    ├── Edit
    │
    ├── Remove
    │
    └── Add Context
```

The goal visualization should make the system's assumptions inspectable.

---

## 6. Progressive Disclosure

Saint should reveal complexity gradually.

The experience should follow:

```text id="k5bguk"
Simple Goal
    ↓
Relevant Context
    ↓
Relevant Relationships
    ↓
Relevant Concepts
    ↓
Deeper Details
```

The user should not be presented with the entire context graph at once.

Instead:

> Show the user what is relevant now, and allow them to go deeper when necessary.

This is especially important for complex DataHub environments.

---

## 7. Context Visualization

DataHub context should be presented as something meaningful, not as raw technical metadata.

The system may represent context through:

```text id="knjvju"
Entity
  ↓
Relationship
  ↓
Context
  ↓
Meaning
```

For example:

```text id="s9d18v"
Revenue Dashboard
        │
        ▼
Revenue Dataset
        │
        ▼
Upstream Pipeline
        │
        ▼
Source Data
```

The user should understand why these relationships matter to their goal.

The system should prioritize:

> **Contextual meaning over graph complexity.**

---

## 8. The Contextual Path

The path should be visually understandable.

Example:

```text id="93vl4f"
YOUR GOAL
    ↓
Understand Revenue Change
    ↓
CURRENT STEP
    ├── Find affected dashboard
    ├── Trace upstream data
    └── Check recent changes
```

The user should be able to understand:

* Where they are
* What they are doing
* Why they are doing it
* What comes next

The path should not feel like a rigid course syllabus.

It should feel like an adaptive route.

---

## 9. Learn Mode Design

Learn Mode should be context-first.

The ideal experience is:

```text id="5e6j5x"
CONTEXT
    ↓
QUESTION
    ↓
EXPLORATION
    ↓
DISCOVERY
    ↓
EXPLANATION
    ↓
APPLICATION
```

The system should avoid immediately presenting long educational explanations when the user can first interact with the relevant context.

Example:

```text id="0tx2qv"
Task:

Find where this metric comes from.
```

After the user explores:

```text id="4t9fja"
You just followed data lineage.

Lineage shows how data moves from upstream
sources to downstream consumers.
```

The explanation becomes connected to an experience.

---

## 10. Explore Mode Design

Explore Mode should help users investigate.

The interface should encourage:

```text id="tck2c6"
Question
    ↓
Relevant Entity
    ↓
Related Context
    ↓
Evidence
    ↓
Conclusion
```

The user should be able to follow relationships without becoming lost inside the full graph.

The system should maintain a visible relationship between:

```text id="8w75cm"
Original Question
        ↓
Current Context
        ↓
Next Investigation
```

---

## 11. Act Mode Design

Act Mode should focus on completing a concrete task.

The interface should emphasize:

```text id="yq8l2p"
GOAL
  ↓
CURRENT ACTION
  ↓
RELEVANT CONTEXT
  ↓
DECISION
  ↓
OUTCOME
```

When the user becomes blocked:

```text id="6f4w8q"
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

The transition should feel natural rather than like leaving the product.

---

## 12. Learning Through Interaction

The system should favor active understanding over passive consumption.

Preferred:

```text id="7hxj0p"
Question
    ↓
User Attempts
    ↓
System Responds
    ↓
User Understands
    ↓
User Applies
```

Rather than:

```text id="0zjtp7"
Long Explanation
    ↓
Scroll
    ↓
More Explanation
    ↓
Quiz
```

The system should make the user think, explore, decide, and apply.

---

## 13. Agent Transparency

Saint should make important agent reasoning visible without exposing unnecessary internal chain-of-thought.

The user should be able to understand:

* What the system believes the goal is
* What context it found
* Why the context is relevant
* What the current step is trying to accomplish
* Why a recommendation was made

The system should show concise explanations such as:

> "I found this dataset because it is upstream of the metric you are investigating."

or:

> "This concept is included because it is required to understand the next step."

The interface should explain decisions without exposing private internal reasoning traces.

---

## 14. Visual Hierarchy

The interface should prioritize:

```text id="zj4hsp"
1. Current Goal
2. Current Step
3. Relevant Context
4. User Action
5. Supporting Explanation
6. Deeper Details
```

The user should not need to search through a dense interface to determine what to do next.

---

## 15. Feedback and Confirmation

The system should provide clear feedback after user actions.

The user should understand:

```text id="zq58ls"
What I did
    ↓
What happened
    ↓
What I learned
    ↓
What I should do next
```

Examples:

* Correctly identified a relationship
* Selected a relevant dataset
* Found the upstream source
* Misunderstood a concept
* Requires a prerequisite

Feedback should be specific and connected to the user's goal.

---

## 16. Adaptive Experience

The interface should adapt to the user's current state.

The system may:

```text id="4csh1d"
Skip
    ↓
Continue
    ↓
Explain
    ↓
Practice
    ↓
Replan
```

The user should not be forced to repeat content they already understand.

The user should also not be silently pushed forward when a missing prerequisite is blocking progress.

---

## 17. Design Language

The visual design should aim for:

### Clear

The user should understand what is happening.

### Focused

The interface should avoid unnecessary information density.

### Contextual

The relevant DataHub context should feel connected to the user's goal.

### Interactive

Users should explore, decide, and act.

### Intelligent Without Being Mysterious

The system should feel capable while remaining understandable.

### Modern

The interface should feel like a contemporary AI-native product rather than a traditional enterprise dashboard.

---

## 18. Design Anti-Patterns

Saint should avoid:

### Empty Canvas First

Do not force users to invent the interaction model themselves.

### Generic Chatbot UI

Do not reduce the entire product to a chat window.

### Information Dumping

Do not show all available context simply because it exists.

### Fixed Curriculum

Do not force every user through the same path.

### Hidden Agent Assumptions

Do not silently build complex plans around unconfirmed interpretations.

### Graph for the Sake of Graph

Do not visualize relationships without explaining their relevance.

### Excessive Technical Jargon

Do not require users to understand internal system terminology before benefiting from the product.

---

## 19. Design Principle

> **Make the user's goal visible, make the relevant context meaningful, and make the next step obvious.**

---

## Core Experience

```text id="u1x4jf"
┌────────────────────────────────────┐
│              USER GOAL             │
│                                    │
│     "What am I trying to do?"      │
└──────────────────┬─────────────────┘
                   ▼
┌────────────────────────────────────┐
│          GOAL VISUALIZATION        │
│                                    │
│    "Is this what you mean?"        │
└──────────────────┬─────────────────┘
                   ▼
┌────────────────────────────────────┐
│          CONTEXT DISCOVERY         │
│                                    │
│     "What is relevant here?"       │
└──────────────────┬─────────────────┘
                   ▼
┌────────────────────────────────────┐
│         CONTEXTUAL PATH            │
│                                    │
│       "What should I do next?"     │
└──────────────────┬─────────────────┘
                   ▼
┌────────────────────────────────────┐
│          LEARN / EXPLORE / ACT     │
│                                    │
│       "Understand and apply."      │
└──────────────────┬─────────────────┘
                   ▼
┌────────────────────────────────────┐
│              OUTCOME               │
└────────────────────────────────────┘
```

> **Saint should feel less like asking an AI for an answer and more like having a capable guide help you navigate a complex environment toward a meaningful goal.**
