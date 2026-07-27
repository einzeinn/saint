import asyncio

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.domain import GoalRequest, PathAssessment
from backend.app.orchestration import SaintOrchestrator
from backend.app.adapters.datahub import AgentContextAdapter, MockDataHubAdapter
from backend.app.adapters.llm import MockLLMAdapter
from backend.app.config import Settings


def test_prototype_session_flow() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/prototype/sessions",
        json={
            "goal": "I want to understand why the revenue dashboard changed",
            "intent": "unsure",
        },
    )

    assert create_response.status_code == 200
    session = create_response.json()
    assert session["confirmed"] is False
    assert session["interpretation"]["intent"] == "explore"
    assert session["path"] is None

    confirm_response = client.post(
        f"/prototype/sessions/{session['session_id']}/confirm",
        json={"confirmed": True},
    )

    assert confirm_response.status_code == 200
    confirmed = confirm_response.json()
    assert confirmed["confirmed"] is True
    assert confirmed["path"]["context"]
    assert confirmed["path"]["context_source"] == "mock-revenue-fixture"
    assert confirmed["path"]["steps"][0]["step_type"] == "confirmation"
    assert "Revenue Overview Dashboard" in confirmed["path"]["steps"][1]["title"]
    assert any(step["step_type"] == "relationship" for step in confirmed["path"]["steps"])
    assert any("freshness: daily" in step["purpose"] for step in confirmed["path"]["steps"])
    assert len(confirmed["path"]["steps"]) >= 3

    step_response = client.post(
        f"/prototype/sessions/{session['session_id']}/steps",
        json={"step_index": 1},
    )

    assert step_response.status_code == 200
    stepped = step_response.json()
    assert stepped["selected_step_index"] == 1
    assert "Revenue Overview Dashboard" in stepped["feedback"]
    assert "context reference" not in stepped["feedback"]


def test_step_selection_requires_confirmed_path() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/prototype/sessions",
        json={"goal": "Find the best dataset for retention analysis", "intent": "act"},
    )
    session = create_response.json()

    step_response = client.post(
        f"/prototype/sessions/{session['session_id']}/steps",
        json={"step_index": 0},
    )

    assert step_response.status_code == 409


def test_unhelpful_assessment_replans_path() -> None:
    orchestrator = SaintOrchestrator(MockLLMAdapter(), MockDataHubAdapter())
    request = {"goal": "Understand the revenue dashboard", "intent": "explore"}

    path = asyncio.run(orchestrator.generate_contextual_path(GoalRequest(**request)))
    revised = orchestrator.replan_path(
        path,
        PathAssessment(useful=False, feedback="Explain the upstream data change first."),
    )

    assert revised.steps[1].step_type == "assessment"
    assert revised.steps[1].user_action == "Explain the upstream data change first."
    assert "replanned" in revised.context_notes[-1]


def test_agent_context_mode_is_optional_when_dependency_is_missing() -> None:
    adapter = AgentContextAdapter(Settings(datahub_provider="agent_context"))
    status = asyncio.run(adapter.status())

    assert status.provider == "agent_context"
    assert status.configured is True
    assert status.reachable is False
    assert "dependency" in status.detail.lower()


def test_feedback_for_step_explains_the_grounded_entity_and_its_metadata() -> None:
    orchestrator = SaintOrchestrator(MockLLMAdapter(), MockDataHubAdapter())
    request = GoalRequest(goal="Understand the revenue dashboard", intent="explore")

    path = asyncio.run(orchestrator.generate_contextual_path(request))
    context_step_index = next(
        index for index, step in enumerate(path.steps) if step.step_type == "context"
    )

    feedback = asyncio.run(orchestrator.feedback_for_step(path, context_step_index))

    entity = path.context[0]
    assert entity.name in feedback
    assert "context reference" not in feedback


def test_feedback_for_step_explains_the_goal_when_no_entity_is_grounded() -> None:
    orchestrator = SaintOrchestrator(MockLLMAdapter(), MockDataHubAdapter())
    request = GoalRequest(goal="Understand the revenue dashboard", intent="explore")

    path = asyncio.run(orchestrator.generate_contextual_path(request))
    confirmation_step_index = next(
        index for index, step in enumerate(path.steps) if step.step_type == "confirmation"
    )

    feedback = asyncio.run(orchestrator.feedback_for_step(path, confirmation_step_index))

    assert path.interpretation.desired_outcome in feedback
