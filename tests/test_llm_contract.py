import asyncio

import httpx
from fastapi.testclient import TestClient

from backend.app.adapters.llm import (
    GeminiProvider,
    GroqProvider,
    MockLLMAdapter,
    StructuredLLMAdapter,
    build_llm_adapter,
)
from backend.app.config import Settings
from backend.app.domain import ContextEntity, GoalRequest, Intent, PathStep, SynthesisContext
from backend.app.main import app


class MalformedProvider:
    provider_name = "malformed"

    async def interpret_goal(self, request: GoalRequest):
        return {"bad": "shape"}

    async def explain_context(self, context):
        return "not structured"

    async def assess_response(self, context, user_response):
        return {"status": "bad"}


def test_structured_llm_adapter_falls_back_when_provider_returns_malformed_output() -> None:
    adapter = StructuredLLMAdapter(provider=MalformedProvider(), fallback=MockLLMAdapter())

    result = asyncio.run(
        adapter.interpret_goal(GoalRequest(goal="why did the dashboard change", intent=Intent.unsure))
    )

    assert result.intent == Intent.explore
    assert result.desired_outcome
    assert result.required_actions


def test_build_llm_adapter_uses_mock_without_api_keys() -> None:
    adapter = build_llm_adapter(Settings(llm_provider="gemini", gemini_api_key=""))

    assert adapter.provider_name == "mock"


def test_gemini_provider_calls_http_api_and_parses_result() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "example.test"
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": '{"original_input":"why did the dashboard change","intent":"explore","desired_outcome":"evidence-backed explanation","required_actions":["Inspect the relevant context"],"required_evidence":["context"],"confidence":0.9}'}]}}
                ]
            },
        )

    provider = GeminiProvider(
        Settings(llm_provider="gemini", gemini_api_key="demo-key", llm_base_url="https://example.test/models"),
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(provider.interpret_goal(GoalRequest(goal="why did the dashboard change", intent=Intent.unsure)))

    assert result.intent == Intent.explore
    assert result.required_actions == ["Inspect the relevant context"]


def test_groq_provider_calls_http_api_and_parses_result() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "example.test"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"original_input":"why did the dashboard change","intent":"explore","desired_outcome":"evidence-backed explanation","required_actions":["Inspect the relevant context"],"required_evidence":["context"],"confidence":0.9}'}}
                ]
            },
        )

    provider = GroqProvider(
        Settings(llm_provider="groq", groq_api_key="demo-key", groq_base_url="https://example.test/chat"),
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(provider.interpret_goal(GoalRequest(goal="why did the dashboard change", intent=Intent.unsure)))

    assert result.intent == Intent.explore
    assert result.required_actions == ["Inspect the relevant context"]


def test_gemini_provider_explain_and_assess_via_http() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        body = request.read().decode()
        if "response-assessment" in body:
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": '{"status":"partial","understanding":"The user inferred a likely cause.","evidence_gap":["No verified evidence was cited."],"recommended_action":"inspect_recent_upstream_activity"}'}]}}]})
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "This step looks at the upstream dataset and dashboard relationship."}]}}]})

    provider = GeminiProvider(
        Settings(llm_provider="gemini", gemini_api_key="demo-key", llm_base_url="https://example.test/models"),
        transport=httpx.MockTransport(handler),
    )

    explanation = asyncio.run(provider.explain_context({"goal": "Understand the dashboard change", "current_entity": "warehouse.revenue_daily", "evidence": ["freshness: daily"], "relationships": ["urn:li:dashboard:revenue-overview"], "next_action": "inspect_recent_upstream_activity"}))
    assessment = asyncio.run(provider.assess_response({"goal": "Explain the dashboard change", "current_step": "inspect_recent_upstream_activity", "evidence": ["freshness: daily"]}, "The pipeline was delayed."))

    assert "upstream dataset" in explanation.lower()
    assert assessment.status == "partial"


def test_explain_context_endpoint_returns_text() -> None:
    client = TestClient(app)

    response = client.post(
        "/llm/explain-context",
        json={
            "goal": "Understand why the revenue dashboard changed",
            "current_entity": "warehouse.revenue_daily",
            "evidence": ["freshness: daily"],
            "relationships": ["urn:li:dashboard:revenue-overview"],
            "next_action": "inspect_recent_upstream_activity",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "warehouse.revenue_daily" in payload
    assert "inspect_recent_upstream_activity" in payload


def test_assess_response_endpoint_returns_structured_result() -> None:
    client = TestClient(app)

    response = client.post(
        "/llm/assess-response",
        json={
            "context": {
                "goal": "Explain the dashboard change",
                "current_step": "inspect_recent_upstream_activity",
                "evidence": ["freshness: daily"],
            },
            "user_response": "The pipeline was delayed, which caused the dashboard to change.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "partial"
    assert "understanding" in payload
    assert "evidence_gap" in payload


def test_mock_synthesize_outcome_leads_with_failing_assertions() -> None:
    context = SynthesisContext(
        goal="Understand why the revenue dashboard changed",
        steps=[
            PathStep(
                title="Review revenue_daily",
                mode=Intent.explore,
                purpose="Check the dataset",
                user_action="Review it",
            )
        ],
        entities=[
            ContextEntity(
                urn="urn:li:dataset:revenue_daily",
                name="revenue_daily",
                entity_type="dataset",
                relevance="Underlying dataset",
                metadata={"quality": "1 assertion FAILING (FRESHNESS); 2 passing", "owner": "data_engineering"},
            ),
        ],
    )

    synthesis = asyncio.run(MockLLMAdapter().synthesize_outcome(context))

    assert "FAILING" in synthesis
    assert synthesis.count("assertion_status") == 0  # no raw key dump
    assert "revenue_daily" in synthesis


def test_mock_synthesize_outcome_deduplicates_repeated_metadata_keys() -> None:
    context = SynthesisContext(
        goal="Understand the pipeline",
        steps=[],
        entities=[
            ContextEntity(
                urn="urn:li:dataset:a",
                name="a",
                entity_type="dataset",
                relevance="r",
                metadata={"owner": "team-a"},
            ),
            ContextEntity(
                urn="urn:li:dataset:b",
                name="b",
                entity_type="dataset",
                relevance="r",
                metadata={"owner": "team-b"},
            ),
        ],
    )

    synthesis = asyncio.run(MockLLMAdapter().synthesize_outcome(context))

    # "owner" key appears once in the highlight list, not once per entity
    assert synthesis.count("owner:") == 1
