from enum import StrEnum
from typing import Any

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
    original_goal: str
    intent: Intent
    desired_outcome: str
    required_actions: list[str]
    required_capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


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
