import pytest
import httpx
from fastapi.testclient import TestClient

from backend.app.adapters.datahub import (
    AgentContextAdapter,
    DataHubMCPAdapter,
    MockDataHubAdapter,
    build_datahub_adapter,
)
from backend.app.config import Settings
from backend.app.domain import GoalInterpretation, Intent
from backend.app.main import app


def test_datahub_status_endpoint_uses_mock_by_default() -> None:
    client = TestClient(app)

    response = client.get("/integrations/datahub/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "mock"
    assert payload["configured"] is True
    assert payload["reachable"] is True


def test_datahub_adapter_factory_selects_mcp_provider() -> None:
    settings = Settings(datahub_provider="mcp", datahub_mcp_url="")

    adapter = build_datahub_adapter(settings)

    assert isinstance(adapter, DataHubMCPAdapter)


@pytest.mark.anyio
async def test_mcp_status_reports_missing_url_as_not_configured() -> None:
    adapter = DataHubMCPAdapter(Settings(datahub_provider="mcp", datahub_mcp_url=""))

    status = await adapter.status()

    assert status.provider == "mcp"
    assert status.configured is False
    assert status.reachable is False
    assert "DATAHUB_MCP_URL" in status.detail


@pytest.mark.anyio
async def test_mock_context_discovery_returns_application_representation() -> None:
    adapter = MockDataHubAdapter()
    interpretation = GoalInterpretation(
        original_goal="I want to understand why the revenue dashboard changed",
        intent=Intent.explore,
        desired_outcome="Understand the dashboard change",
        required_actions=["Identify dashboard"],
    )

    discovery = await adapter.discover_context(interpretation)

    assert discovery.provider == "mock"
    assert discovery.source == "mock-revenue-fixture"
    assert discovery.entities[0].entity_type == "dashboard"
    assert discovery.entities[0].relationships


@pytest.mark.anyio
async def test_mcp_context_discovery_normalizes_search_and_entity_results() -> None:
    requests: list[tuple[bytes, httpx.Headers]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read()
        requests.append((payload, request.headers))
        body = payload.decode()
        if '"method":"initialize"' in body:
            return httpx.Response(
                200,
                headers={"mcp-session-id": "test-session"},
                json={"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {}}},
            )
        if '"method":"notifications/initialized"' in body:
            return httpx.Response(202)
        if '"method":"tools/list"' in body:
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"tools": [{"name": "search"}, {"name": "get_entity"}]},
                },
            )
        if '"name":"search"' in body:
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "structuredContent": {
                            "results": [
                                {
                                    "urn": "urn:li:dataset:warehouse.revenue_daily",
                                    "name": "warehouse.revenue_daily",
                                    "type": "DATASET",
                                    "owner": "analytics",
                                    "freshness": "daily",
                                    "relationships": ["urn:li:dataJob:daily-revenue-pipeline"],
                                }
                            ]
                        }
                    },
                },
            )
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "structuredContent": {
                        "data": [{"relationships": ["urn:li:dashboard:revenue-overview"]}]
                    }
                },
            },
        )

    adapter = DataHubMCPAdapter(
        Settings(datahub_provider="mcp", datahub_mcp_url="http://datahub.test/mcp"),
        transport=httpx.MockTransport(handler),
    )
    interpretation = GoalInterpretation(
        original_goal="Explain the revenue dashboard change",
        intent=Intent.explore,
        desired_outcome="Explain the change",
        required_actions=["Find relevant context"],
    )

    discovery = await adapter.discover_context(interpretation)

    assert discovery.source == "mcp"
    assert len(discovery.entities) == 1
    assert discovery.entities[0].entity_type == "dataset"
    assert discovery.entities[0].relationships == [
        "urn:li:dataJob:daily-revenue-pipeline",
        "urn:li:dashboard:revenue-overview",
    ]
    assert discovery.entities[0].metadata == {"owner": "analytics", "freshness": "daily"}
    assert any(headers.get("mcp-session-id") == "test-session" for _, headers in requests[2:])


def test_mcp_entity_results_are_deduplicated() -> None:
    first = {
        "urn": "urn:li:dataset:orders",
        "name": "orders",
        "type": "DATASET",
        "relationships": ["urn:li:dataJob:orders-pipeline"],
        "owner": "data-platform",
    }
    second = {
        "urn": "urn:li:dataset:orders",
        "name": "orders",
        "type": "DATASET",
        "relationships": ["urn:li:dashboard:orders"],
        "quality": "tracked",
    }

    entities = DataHubMCPAdapter._entities_from_search({"results": [first, second]})

    assert len(entities) == 1
    assert entities[0].relationships == [
        "urn:li:dataJob:orders-pipeline",
        "urn:li:dashboard:orders",
    ]
    assert entities[0].metadata == {"owner": "data-platform", "quality": "tracked"}


def test_metadata_summarizes_nested_ownership_payload_into_readable_names() -> None:
    record = {
        "urn": "urn:li:dataset:logging_events",
        "name": "logging_events",
        "type": "DATASET",
        "owner": {
            "owners": [
                {
                    "owner": {
                        "urn": "urn:li:corpuser:jdoe",
                        "properties": {"displayName": "John Doe"},
                    },
                    "type": "DATAOWNER",
                },
                {
                    "owner": {
                        "urn": "urn:li:corpuser:datahub",
                        "properties": {"displayName": "DataHub"},
                    },
                    "type": "DATAOWNER",
                },
            ]
        },
    }

    entities = DataHubMCPAdapter._entities_from_search({"results": [record]})

    assert entities[0].metadata["owner"] == "John Doe, DataHub"


def test_metadata_omits_empty_or_unresolvable_nested_values() -> None:
    record = {
        "urn": "urn:li:glossaryTerm:CustomerAccount",
        "name": "CustomerAccount",
        "type": "GLOSSARY_TERM",
        "owner": {"owners": []},
    }

    entities = DataHubMCPAdapter._entities_from_search({"results": [record]})

    assert "owner" not in entities[0].metadata


@pytest.mark.parametrize(
    ("goal", "expected_type"),
    [
        ("I want to see the table for all datasets I have now", "dataset"),
        ("Show me the revenue dashboard", "dashboard"),
        ("Explain the daily ingestion pipeline", "dataJob"),
        ("What glossary terms exist for revenue", "glossaryTerm"),
        ("List every domain in the catalog", "domain"),
        ("How does the system generally work", None),
    ],
)
def test_infer_entity_type_filter_matches_explicit_entity_mentions(goal, expected_type) -> None:
    assert AgentContextAdapter._infer_entity_type_filter(goal) == expected_type
