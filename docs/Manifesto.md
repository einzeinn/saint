# Manifesto

## Saint

Saint exists to help people move from intention to understanding and action.

The system should not merely answer questions.

It should help users discover:

```text
What do I want to achieve?
        ↓
What do I need to understand?
        ↓
What context matters?
        ↓
What should I do next?
        ↓
How do I know I succeeded?
```

---

## 1. Start With the Goal

The user's goal comes before the system's capabilities.

Saint should begin with:

> **What are you trying to accomplish?**

Not:

> **Here are all the things the system can do.**

The system should adapt its capabilities to the user's goal.

---

## 2. Context Is More Valuable Than Generic Answers

A generic answer may be correct.

A contextual answer is useful.

Saint should prioritize understanding the environment surrounding the user's goal.

```text
Generic Knowledge
        +
Actual Context
        ↓
Meaningful Understanding
```

DataHub context should not be treated as decoration.

It should be part of the reasoning that makes the result useful.

---

## 3. Understanding Should Lead Somewhere

Learning is not valuable merely because information was consumed.

Understanding should enable:

```text
Knowledge
    ↓
Capability
    ↓
Action
    ↓
Outcome
```

Saint should help users move beyond:

> "I understand this concept."

toward:

> "I can use this understanding to accomplish something."

---

## 4. The Path Should Be Discovered, Not Assumed

A user's goal does not always reveal the complete path required to achieve it.

Saint should help discover:

* Required knowledge
* Missing prerequisites
* Relevant context
* Necessary actions
* Possible obstacles

The system should not assume that every user needs the same path.

---

## 5. Make the System's Understanding Visible

AI systems make assumptions.

Those assumptions should not remain invisible when they meaningfully affect the user's path.

Saint should make important interpretations inspectable.

```text
User Goal
    ↓
Saint's Understanding
    ↓
User Confirmation
    ↓
Action
```

The user should be able to correct the system before a misunderstanding becomes an entire workflow.

---

## 6. Complexity Should Serve the User

The underlying system may be complex.

The user's experience should not need to be.

Saint should use:

* Agents
* Context graphs
* Metadata
* Relationships
* Models
* Orchestration

to make the user's path clearer.

Not to make the product appear more intelligent.

---

## 7. Do Not Build a Chatbot by Accident

A conversational interface is a tool.

It is not the product.

Saint should not reduce every interaction to:

```text
User
    ↓
Chat Box
    ↓
AI Answer
```

The system should support:

```text
Goal
    ↓
Context
    ↓
Path
    ↓
Interaction
    ↓
Outcome
```

Conversation may exist inside this flow.

It should not replace the flow.

---

## 8. Progress Means Capability

Progress should not be measured only by:

* Number of messages
* Number of lessons completed
* Amount of content consumed
* Time spent in the application

The more important question is:

> **What can the user do now that they could not do before?**

---

## 9. Adaptation Is a Requirement

The system should adapt when the user:

* Already understands something
* Does not understand something
* Takes an unexpected path
* Discovers new information
* Changes their goal

A path that cannot adapt is merely a syllabus with better marketing.

---

## 10. DataHub Should Be Used Meaningfully

Saint should use DataHub because the context graph enables meaningful capabilities.

Not because an integration checkbox exists.

The product should continuously ask:

> **Would this experience be meaningfully weaker without DataHub context?**

If the answer is no, the integration may be superficial.

---

## 11. Build the Smallest Complete Thing

The first goal is not to build the biggest system.

The first goal is to prove the core idea.

```text
One Goal
    ↓
One Context
    ↓
One Path
    ↓
One Outcome
```

A complete experience is more valuable than a collection of unfinished possibilities.

---

## 12. Earn Complexity

Complexity must be justified.

The project should not introduce:

* Infrastructure
* Abstractions
* Services
* Features
* Dependencies

without a real problem that requires them.

The preferred direction is:

```text
Problem
    ↓
Simple Solution
    ↓
Validation
    ↓
Necessary Complexity
```

Not:

```text
Complex Architecture
    ↓
Search for a Problem
```

---

## 13. Document Significant Change

Important decisions should not disappear into implementation history.

Significant changes should be documented through the appropriate project documentation or RFC.

The project should preserve:

```text
Decision
    ↓
Reason
    ↓
Trade-offs
    ↓
Result
```

Future contributors, including future versions of ourselves, should not have to perform archaeological excavation through old commits to understand why something exists.

---

## 14. Stay Flexible Without Becoming Directionless

Flexibility does not mean having no decisions.

It means:

* Make decisions deliberately
* Keep boundaries clear
* Avoid unnecessary lock-in
* Revisit decisions when evidence changes

The system should be flexible in implementation while remaining focused in purpose.

---

## 15. The Core Belief

> **People often do not need more information. They need help discovering which information matters, why it matters, and what to do with it.**

Saint exists to help make that path visible.

---

## Final Principle

```text
USER INTENTION
      ↓
UNDERSTANDING
      ↓
CONTEXT
      ↓
PATH
      ↓
CAPABILITY
      ↓
ACTION
      ↓
OUTCOME
```

> **Saint should not merely tell users what is true. It should help them understand what matters and move toward what they are trying to achieve.**
