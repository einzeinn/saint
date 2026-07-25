# Hackathon

## 1. Purpose

Saint is being developed as a hackathon project built around the capabilities of DataHub.

The hackathon version should demonstrate a focused, meaningful use of DataHub rather than attempting to build a complete production platform.

The goal is to create a strong proof of concept that demonstrates:

```text
User Goal
    ↓
Agent Reasoning
    ↓
DataHub Context Graph
    ↓
Contextual Path
    ↓
Understanding or Action
```

---

## 2. Hackathon Thesis

The central hackathon thesis is:

> **DataHub's context graph can be used not only to answer questions about data, but to determine what a person needs to understand and do next in order to accomplish a goal.**

This transforms DataHub context from a passive metadata layer into an active environment for contextual guidance.

---

## 3. Why DataHub Is Essential

DataHub provides structured context that is difficult to reproduce through ordinary document retrieval alone.

Relevant context may include:

* Relationships between data assets
* Upstream and downstream lineage
* Ownership
* Metadata
* Glossary concepts
* Data quality
* Freshness
* Domains
* Documentation

These relationships allow the agent to reason about the user's goal in relation to the actual data ecosystem.

Without the context graph, Saint would be significantly more likely to produce generic advice.

With the context graph, the system can generate paths based on the actual environment surrounding the user's goal.

---

## 4. Primary Hackathon Integration

The primary integration path is:

```text
Saint
  ↓
MCP Client / Adapter
  ↓
DataHub MCP Server
  ↓
DataHub Context Graph
```

The DataHub MCP Server should serve as the primary interface between the application agent and the DataHub context layer.

The application should use an abstraction layer to keep the core product logic modular.

---

## 5. Hackathon Demo Objective

The demo should communicate the core idea quickly:

> **Give Saint a goal. Saint discovers the relevant DataHub context and turns it into a path toward understanding or action.**

The demo should avoid requiring the audience to understand the entire architecture before seeing the value.

---

## 6. Preferred Demo Structure

The demo should follow a simple narrative:

```text
1. User has a real goal
        ↓
2. Saint interprets the goal
        ↓
3. Saint visualizes the required path
        ↓
4. User confirms the interpretation
        ↓
5. Saint discovers relevant DataHub context
        ↓
6. Saint generates a contextual path
        ↓
7. User learns, explores, or acts
        ↓
8. User reaches a meaningful outcome
```

The strongest demo should show that the path is derived from actual DataHub context rather than generic LLM knowledge.

---

## 7. Hackathon Scope

The hackathon version should prioritize:

### One Strong User Journey

A complete end-to-end experience is more valuable than many incomplete modes.

### One Strong DataHub Context

The demo should use a sufficiently rich DataHub environment that allows the relationship between entities and metadata to be visible.

### One Strong Outcome

The user should clearly reach a meaningful result.

The preferred scope is:

```text
One Goal
    ↓
One Interpretation
    ↓
Relevant DataHub Context
    ↓
One Contextual Path
    ↓
One Meaningful Outcome
```

---

## 8. What Should Be Demonstrated

The hackathon demo should demonstrate that Saint can:

* Understand a user goal
* Identify intent
* Make its interpretation visible
* Retrieve relevant DataHub context
* Reason about relationships and prerequisites
* Generate a contextual path
* Guide the user through an interaction
* Adapt the path when appropriate

The demo should make clear that DataHub is a core mechanism of the product.

---

## 9. What Should Not Be Prioritized

The hackathon version should not prioritize:

* Supporting every possible user intent
* Multiple unrelated domains
* A large number of LLM providers
* A large number of integrations
* Complex enterprise authentication
* A complete mastery tracking system
* A production-scale deployment architecture

These may become relevant later, but they should not distract from demonstrating the core thesis.

---

## 10. Contribution Strategy

The specific contribution to the DataHub ecosystem should be determined after the core product and integration have been validated.

Potential contribution directions may include:

* Reusable agent workflows
* DataHub Skills
* Documentation
* A reusable integration pattern
* A new workflow enabled by DataHub context
* A technical proposal or RFC if a meaningful platform-level need is discovered

The contribution should emerge from actual development rather than being artificially designed before the product has been tested.

---

## 11. Hackathon Success Criteria

The hackathon project is successful if the audience can understand:

1. What the user's goal is
2. Why generic AI assistance is insufficient
3. What context DataHub provides
4. How Saint uses that context
5. Why the resulting path is more useful than a generic answer
6. What outcome the user reaches

The ideal reaction is:

> **"The agent didn't just answer the question. It figured out what the user needed to understand and do next by navigating the context graph."**

---

## 12. Hackathon Principle

> **Build one complete, undeniable demonstration of the core idea before expanding the product.**

The hackathon version should optimize for:

```text
Clarity
    +
Meaningful DataHub Usage
    +
Strong User Experience
    +
Visible Agent Reasoning
    +
Complete Outcome
```

The project should be judged by the strength of the demonstrated idea, not by the number of features implemented.
