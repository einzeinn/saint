from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Intent(StrEnum):
    learn = "learn"
    explore = "explore"
    act = "act"
    unsure = "unsure"


class GoalRequest(BaseModel):
    goal: str = Field(min_length=3)
    intent: Intent = Intent.unsure


class GoalInterpretation(BaseModel):
    original_goal: str = ""
    original_input: str | None = None
    intent: Intent
    desired_outcome: str
    required_actions: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    target: str | None = None
    required_evidence: list[str] = Field(default_factory=list)
    confidence: float = 0.75


class ContextPackage(BaseModel):
    goal: str
    current_entity: str | None = None
    evidence: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    next_action: str | None = None


class AssessmentContext(BaseModel):
    goal: str
    current_step: str | None = None
    evidence: list[str] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    status: str = "partial"
    understanding: str = ""
    evidence_gap: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


# NEW: Context for final synthesis
class SynthesisContext(BaseModel):
    goal: str
    steps: list["PathStep"]
    entities: list["ContextEntity"]
    assessment_results: list[AssessmentResult] | None = None
    context_notes: list[str] = Field(default_factory=list)


# NEW: Result of final synthesis
class SynthesisResult(BaseModel):
    synthesis: str
    confidence: float | None = None


class ContextEntity(BaseModel):
    urn: str
    name: str
    entity_type: str
    relevance: str
    relationships: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PathStep(BaseModel):
    title: str
    mode: Intent
    purpose: str
    user_action: str
    context_refs: list[str] = Field(default_factory=list)
    step_type: str = "context"


class ContextualPath(BaseModel):
    interpretation: GoalInterpretation
    context: list[ContextEntity]
    steps: list[PathStep]
    outcome: str
    context_source: str = "unknown"
    context_notes: list[str] = Field(default_factory=list)
    synthesis: str | None = None  # NEW: stored synthesis result


class PrototypeSession(BaseModel):
    session_id: str
    request: GoalRequest
    interpretation: GoalInterpretation
    confirmed: bool = False
    path: ContextualPath | None = None
    selected_step_index: int | None = None
    feedback: str | None = None


class SessionConfirmation(BaseModel):
    confirmed: bool = True


class StepSelection(BaseModel):
    step_index: int = Field(ge=0)


class PathAssessment(BaseModel):
    useful: bool
    feedback: str | None = None


class DataHubIntegrationStatus(BaseModel):
    provider: str
    configured: bool
    reachable: bool
    mode: str
    detail: str


class DataHubContextDiscovery(BaseModel):
    provider: str
    source: str
    entities: list[ContextEntity]
    notes: list[str] = Field(default_factory=list)


# Rebuild forward references after class definitions
SynthesisContext.model_rebuild()