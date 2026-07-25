# Vision

## 1. The Vision

Saint is an adaptive context-driven agent that helps people move from **what they want to accomplish** to **what they need to understand and do next**.

Instead of forcing users to begin with a predefined curriculum, a blank chat window, or a search query, Saint begins with the user's intent.

The system then uses the DataHub context graph to understand the environment surrounding that goal and generates a contextual path toward the desired outcome.

```text
User Goal
    ↓
Intent Understanding
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

---

## 2. The Problem

Modern data ecosystems contain enormous amounts of information and relationships.

A user may have access to:

* Datasets
* Dashboards
* Pipelines
* Tables
* Columns
* Glossaries
* Ownership information
* Data quality information
* Lineage
* Domains
* Documentation

The problem is often not a lack of information.

The problem is understanding:

> **What is relevant to my goal, what do I need to understand first, and what should I do next?**

A user may know what they want to accomplish:

> "I need to understand why this dashboard changed."

But they may not know:

* Which data assets are relevant
* Which concepts they need to understand
* Which relationships matter
* Which prerequisites they are missing
* Which steps should happen first

Saint exists to help bridge this gap.

---

## 3. The Core Idea

Saint transforms:

```text
"I want to accomplish something."
```

into:

```text
"Here is what you need to understand,
here is the context that matters,
and here is the next best path forward."
```

The system does not assume that every user needs the same knowledge.

It does not assume that every goal should become a traditional course.

Instead, it dynamically connects:

```text
User Intent
    +
DataHub Context
    +
Required Outcome
```

to generate a path that is relevant to the situation.

---

## 4. The User Experience

Saint should not begin with an empty canvas.

The user should be able to choose how they want to approach their goal.

For example:

```text
What do you want to do?

    Learn
    Understand
    Explore
    Get something done
    I'm not sure yet
```

These entry points are not rigid limitations.

They are ways to help users express intent without requiring them to understand the full capabilities of the system.

The interface should provide structure while the underlying agent remains flexible.

> **Constrain the interface, not the intelligence.**

---

## 5. Goal Visualization

After receiving the user's goal, Saint should make its interpretation visible.

For example:

```text
User:
"I want to understand why revenue dropped."

                    ↓

Saint understands:

Investigate Revenue Change
        │
        ├── Find affected dashboard
        ├── Identify underlying datasets
        ├── Trace upstream lineage
        ├── Check freshness and quality
        └── Investigate recent changes
```

The user can then:

* Confirm the interpretation
* Correct the interpretation
* Add missing information
* Remove irrelevant steps

This creates a shared understanding between the user and the agent before deeper reasoning begins.

---

## 6. DataHub as the Context Graph

DataHub provides the environment in which the user's goal exists.

The same goal may require different paths depending on the available context.

For example:

```text
Goal:
Find the correct dataset for customer retention analysis
```

Without context:

```text
Generic Advice
    ↓
Search for customer data
    ↓
Check data quality
```

With DataHub context:

```text
Goal
 ↓
Candidate Dataset A
 ├── Owner
 ├── Freshness
 ├── Quality
 └── Lineage

Candidate Dataset B
 ├── Owner
 ├── Freshness
 ├── Quality
 └── Lineage

Candidate Dataset C
 ├── Owner
 ├── Freshness
 ├── Quality
 └── Lineage
```

The agent can then guide the user through the actual context surrounding the decision.

The user does not learn from an abstract example when the real environment is available.

---

## 7. One Context, Multiple Paths

The same DataHub context can support different user intentions.

```text
                    DataHub Context
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
        LEARN           EXPLORE           ACT
          │               │               │
          ▼               ▼               ▼
    Understand       Investigate       Complete
     concepts         context           a task
```

### Learn

The user wants to build understanding.

```text
Real Context
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

The user wants to investigate something.

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

### Act

The user wants to complete a task.

```text
Goal
    ↓
Required Context
    ↓
Required Knowledge
    ↓
Guided Action
    ↓
Outcome
```

These modes are not isolated.

A user may move between them naturally:

```text
Act
 ↓
Blocked
 ↓
Learn
 ↓
Understand
 ↓
Act Again
```

---

## 8. Learning Through Context

Saint should make learning feel useful because it is connected to a real goal.

The intended learning experience is:

```text
Encounter a Real Context
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

For example, instead of beginning with:

> "Data lineage is..."

The user may first be asked:

> "Find out where this dashboard's revenue data comes from."

After exploring the context, the system can explain:

> "You just traced data lineage."

The concept becomes meaningful because the user has already experienced why it matters.

---

## 9. Adaptive Paths

Saint does not treat a curriculum as a fixed list of lessons.

A path is a dynamic route through relevant context and knowledge.

```text
Goal
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

The path may change based on:

* Existing user knowledge
* User decisions
* User performance
* New context discovered
* Changes to the user's goal

The system should be able to:

```text
Skip
    ↓
Teach
    ↓
Practice
    ↓
Revisit
    ↓
Replan
```

The objective is not to maximize the amount of content consumed.

The objective is to help the user reach the desired outcome.

---

## 10. The Long-Term Vision

The long-term vision is a system where users do not need to know:

> "What should I learn?"

before they can begin.

They only need to know:

> "What am I trying to accomplish?"

Saint should help them discover:

```text
What they need to understand
        ↓
Why it matters
        ↓
How it relates to their environment
        ↓
What they should do next
        ↓
How to know they succeeded
```

The system should become a bridge between:

```text
Human Intent
        │
        ▼
Context Graph
        │
        ▼
Understanding
        │
        ▼
Action
```

---

## Vision Statement

> **Saint turns goals into contextual paths toward understanding and action.**
>
> **By combining adaptive agent reasoning with DataHub's context graph, Saint helps users discover not only what they need to do, but what they need to understand to do it well.**
