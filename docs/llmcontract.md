# LLM Contract & Implementation

## Status

Proposed

## Purpose

Saint uses an interchangeable LLM intelligence layer to improve natural-language interaction, goal interpretation, contextual explanation, and user-response assessment.

The LLM is not the source of truth and is not the system orchestrator.

The system has three distinct responsibilities:

- LLM: language interaction and high-level interpretation
- Saint Core: orchestration, state, path generation, validation, and replanning
- DataHub: metadata, entities, relationships, and evidence source

---

# 1. Core Principle

The LLM must enhance Saint without becoming a mandatory runtime dependency.

Saint must remain functional when:

- no LLM API key is configured
- the selected provider is unavailable
- the provider reaches a rate limit
- the API request fails
- the response is malformed
- the user is running in demo or offline mode

The LLM is therefore an optional intelligence layer.

```text
User
  ↓
LLM Interaction Layer
  ↓
Structured Contract
  ↓
Saint Core
  ↓
DataHub
  ↓
Evidence
  ↓
Saint Core
  ↓
LLM Explanation Layer
  ↓
User
2. Responsibility Boundaries
LLM

The LLM may:

interpret natural-language goals
identify user intent
identify a possible target
identify a desired outcome
identify potential evidence requirements
explain structured context in natural language
assess user responses
identify possible knowledge or evidence gaps
suggest a possible next action

The LLM must not:

invent DataHub entities
invent metadata
invent relationships
directly mutate Saint state
directly create a final learning path without validation
override deterministic core rules
become the only source of truth
Saint Core

Saint Core is responsible for:

validating LLM outputs
maintaining application state
validating entities against DataHub context
generating contextual paths
maintaining path progression
executing replanning
applying assessment results
handling provider failures
selecting fallback behavior
enforcing system constraints

The LLM may suggest.

Saint Core decides.

DataHub

DataHub is the source of truth for:

entities
metadata
relationships
lineage
ownership
domain context
available evidence

LLM-generated claims must not be treated as DataHub evidence unless verified against DataHub.

3. LLM Provider Contract

The core must depend on an abstract provider interface rather than a specific vendor.

LLMProvider
    ├── GeminiProvider
    ├── GroqProvider
    └── MockProvider

The provider abstraction must allow the implementation to switch providers without modifying Saint Core.

4. Required Operations
4.1 Goal Interpretation
interpret_goal(
    user_input: str
) -> GoalInterpretation
Input

Natural-language user goal.

Example:

I want to understand why the revenue dashboard changed.
Output
GoalInterpretation(
    original_input="I want to understand why the revenue dashboard changed.",
    intent="learn",
    target="revenue dashboard",
    desired_outcome="evidence-backed explanation",
    required_evidence=[
        "dashboard",
        "underlying_dataset",
        "upstream_pipeline",
        "recent_changes"
    ],
    confidence=0.92
)

The result must be validated before entering Saint Core.

4.2 Context Explanation
explain_context(
    context: ContextPackage
) -> str

The LLM receives structured context that has already been discovered by Saint Core and DataHub.

Example:

Goal:
Understand why the revenue dashboard changed.

Current entity:
warehouse.revenue_daily

Evidence:
- freshness: daily
- quality: tracked

Relationship:
- Used by Revenue Overview Dashboard

Next action:
Review metadata and recent upstream changes.

The LLM must explain the supplied context without inventing additional facts.

4.3 User Response Assessment
assess_response(
    context: AssessmentContext,
    user_response: str
) -> AssessmentResult

Example user response:

I think the dashboard changed because the pipeline was delayed.

Example output:

AssessmentResult(
    status="partial",
    understanding="The user identified freshness or pipeline timing as a possible cause.",
    evidence_gap=[
        "No confirmed pipeline delay evidence."
    ],
    recommended_action="inspect_recent_pipeline_activity"
)

The result is then processed by Saint Core.

The LLM does not directly replan the path.

5. Structured Output Requirements

LLM outputs that enter Saint Core must use structured schemas.

Free-form LLM output must not directly control application state.

Natural Language
      ↓
LLM
      ↓
Structured Output
      ↓
Validation
      ↓
Saint Core

Invalid output must trigger:

retry if configured
provider fallback if available
deterministic fallback
6. Fallback Strategy
LLM enabled
User
  ↓
LLM Goal Interpretation
  ↓
Saint Core
  ↓
DataHub
  ↓
Saint Core
  ↓
LLM Explanation
  ↓
User
LLM unavailable
User
  ↓
Deterministic Goal Parser
  ↓
Saint Core
  ↓
DataHub
  ↓
Template Explanation
  ↓
User

The application must preserve its core functionality in both modes.

7. Provider Selection

Provider selection must be configuration-driven.

Example:

SAINT_LLM_PROVIDER=gemini
SAINT_LLM_MODEL=provider-model-name
GEMINI_API_KEY=
GROQ_API_KEY=

The exact provider and model must not be hardcoded into Saint Core.

8. Initial Provider Strategy

The initial implementation may use:

Gemini as the primary provider
Groq as an alternative provider
Mock provider for tests and development

The implementation must avoid provider-specific logic leaking into core orchestration.

Saint Core
    ↓
LLMProvider
    ↓
Provider Adapter
    ↓
Gemini / Groq / Mock
9. Failure Handling

The LLM layer must handle:

missing API key
invalid API key
timeout
network failure
rate limit
provider error
malformed response
invalid structured output
unavailable model

The system must degrade gracefully.

Example:

LLM request failed
        ↓
Log failure
        ↓
Try configured fallback
        ↓
If unavailable
        ↓
Use deterministic behavior

A provider failure must not crash the Saint Core.

10. Architecture Decision

Saint is not an LLM-first application.

Saint is a DataHub-grounded orchestration system with an optional LLM interaction layer.

DataHub
    = Source of Truth

Saint Core
    = Orchestration and Decision Layer

LLM
    = Interaction and Reasoning Layer

The LLM acts as the interface between the user's natural language and Saint's structured system.

The LLM may guide the interaction.

Saint Core controls the journey.

DataHub grounds the facts.

11. Implementation Order

The implementation must follow this order:

Define schemas
GoalInterpretation
ContextPackage
AssessmentContext
AssessmentResult
Define the LLMProvider interface.
Implement MockProvider.
Integrate the MockProvider into the existing flow.
Implement the first real provider.
Add provider configuration.
Add structured output validation.
Add fallback handling.
Add tests for:
valid output
malformed output
missing API key
provider failure
deterministic fallback
Re-run the full existing regression suite.
Rebuild and validate the distribution wheel.
12. Definition of Done

The LLM integration is complete when:

Saint Core depends only on the provider abstraction.
At least one real LLM provider works.
Mock mode remains functional.
Saint works without an API key.
LLM output is validated before entering Saint Core.
LLM cannot invent DataHub evidence.
Provider failures do not crash the application.
Existing deterministic flows continue to pass.
saint demo remains functional.
The distribution wheel installs successfully in a clean Python 3.12 environment.
The full test suite passes.
Final Principle

The LLM should make Saint feel intelligent.

DataHub should make Saint grounded.

Saint Core should make Saint reliable.