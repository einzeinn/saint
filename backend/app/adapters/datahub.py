import asyncio
import json
import os
import re
from typing import Any, Protocol

import httpx

from backend.app.config import Settings
from backend.app.domain import ContextEntity, DataHubContextDiscovery, DataHubIntegrationStatus, GoalInterpretation


class DataHubAdapter(Protocol):
    provider_name: str

    async def status(self) -> DataHubIntegrationStatus:
        """Return readiness details for the configured DataHub integration."""

    async def discover_context(
        self, interpretation: GoalInterpretation
    ) -> DataHubContextDiscovery:
        """Return context relevant to the confirmed goal interpretation."""


class MockDataHubAdapter:
    provider_name = "mock"

    async def status(self) -> DataHubIntegrationStatus:
        return DataHubIntegrationStatus(
            provider=self.provider_name,
            configured=True,
            reachable=True,
            mode="mock",
            detail="Using built-in mock DataHub context for prototype development.",
        )

    async def discover_context(
        self, interpretation: GoalInterpretation
    ) -> DataHubContextDiscovery:
        goal = interpretation.original_goal.lower()

        if "revenue" in goal or "dashboard" in goal:
            entities = [
                ContextEntity(
                    urn="urn:li:dashboard:revenue-overview",
                    name="Revenue Overview Dashboard",
                    entity_type="dashboard",
                    relevance="Likely downstream surface for the user's investigation.",
                    relationships=["urn:li:dataset:warehouse.revenue_daily"],
                    metadata={"domain": "revenue", "owner": "analytics"},
                ),
                ContextEntity(
                    urn="urn:li:dataset:warehouse.revenue_daily",
                    name="warehouse.revenue_daily",
                    entity_type="dataset",
                    relevance="Underlying dataset used to explain dashboard movement.",
                    relationships=["urn:li:dataJob:daily-revenue-pipeline"],
                    metadata={"freshness": "daily", "quality": "tracked"},
                ),
                ContextEntity(
                    urn="urn:li:dataJob:daily-revenue-pipeline",
                    name="daily-revenue-pipeline",
                    entity_type="pipeline",
                    relevance="Upstream processing context for freshness and changes.",
                    relationships=[],
                    metadata={"schedule": "daily", "status": "active"},
                ),
            ]
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="mock-revenue-fixture",
                entities=entities,
                notes=["Mock fixture shaped like DataHub context for Phase 1 and Phase 2 initial validation."],
            )

        return DataHubContextDiscovery(
            provider=self.provider_name,
            source="mock-generic-fixture",
            entities=[
                ContextEntity(
                    urn="urn:li:dataset:sample.core_context",
                    name="sample.core_context",
                    entity_type="dataset",
                    relevance="Mock context until the DataHub MCP adapter is connected.",
                    relationships=[],
                    metadata={},
                )
            ],
            notes=["No matching fixture found, so generic mock context was returned."],
        )


class DataHubMCPAdapter:
    provider_name = "mcp"

    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url = settings.datahub_mcp_url.rstrip("/")
        self._token = settings.datahub_token
        self._timeout = settings.datahub_mcp_timeout_seconds
        self._search_tool = settings.datahub_mcp_search_tool
        self._entity_tool = settings.datahub_mcp_entity_tool
        self._transport = transport
        self._session_id: str | None = None

    async def status(self) -> DataHubIntegrationStatus:
        if not self._url:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=False,
                reachable=False,
                mode="mcp",
                detail="DATAHUB_MCP_URL is not configured.",
            )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=self._transport
            ) as client:
                response = await client.get(self._url, headers=self._headers())
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=response.status_code < 500,
                mode="mcp",
                detail=f"DataHub MCP endpoint responded with HTTP {response.status_code}.",
            )
        except httpx.HTTPError as exc:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=False,
                mode="mcp",
                detail=f"DataHub MCP endpoint is not reachable: {exc.__class__.__name__}.",
            )

    async def discover_context(
        self, interpretation: GoalInterpretation
    ) -> DataHubContextDiscovery:
        status = await self.status()
        if not status.configured or not status.reachable:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="mcp-unavailable",
                entities=[],
                notes=[status.detail],
            )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=self._transport
            ) as client:
                await self._initialize(client)
                tools = await self._list_tools(client)
                search_tool = self._resolve_tool(tools, self._search_tool, ("search", "find"))
                entity_tool = self._resolve_tool(
                    tools, self._entity_tool, ("get_entity", "entity", "get_data_entity")
                )
                search_result = await self._call_tool(
                    client,
                    search_tool,
                    {"query": interpretation.original_goal, "limit": 10},
                )
                entities = self._entities_from_search(search_result)

                if entity_tool:
                    for entity in entities:
                        details = await self._call_tool(
                            client, entity_tool, self._entity_arguments(entity_tool, entity.urn)
                        )
                        self._enrich_entity(entity, details)

            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="mcp",
                entities=entities,
                notes=[
                    f"Discovered context for confirmed goal: {interpretation.original_goal}",
                    f"Search tool: {search_tool or 'not available'}.",
                ],
            )
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="mcp-error",
                entities=[],
                notes=[f"DataHub context discovery failed: {exc.__class__.__name__}."],
            )

    async def _initialize(self, client: httpx.AsyncClient) -> None:
        await self._mcp_request(
            client,
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "saint", "version": "0.1.0"},
            },
        )
        response = await client.post(
            self._url,
            headers=self._headers(),
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
        response.raise_for_status()

    async def _list_tools(self, client: httpx.AsyncClient) -> list[dict[str, Any]]:
        response = await self._mcp_request(client, "tools/list", {})
        tools = response.get("tools", [])
        if not isinstance(tools, list):
            raise ValueError("MCP tools/list returned an invalid tools collection")
        return [tool for tool in tools if isinstance(tool, dict)]

    async def _call_tool(
        self, client: httpx.AsyncClient, tool_name: str | None, arguments: dict[str, Any]
    ) -> Any:
        if not tool_name:
            return None
        response = await self._mcp_request(
            client, "tools/call", {"name": tool_name, "arguments": arguments}
        )
        return response.get("structuredContent", response.get("content", response))

    async def _mcp_request(
        self, client: httpx.AsyncClient, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        response = await client.post(
            self._url,
            headers=self._headers(),
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        )
        response.raise_for_status()
        session_id = response.headers.get("mcp-session-id")
        if session_id:
            self._session_id = session_id
        payload = response.json()
        if "error" in payload:
            raise ValueError(f"MCP request failed: {payload['error']}")
        result = payload.get("result", {})
        if not isinstance(result, dict):
            raise ValueError("MCP response result is not an object")
        return result

    @staticmethod
    def _resolve_tool(
        tools: list[dict[str, Any]], configured: str, aliases: tuple[str, ...]
    ) -> str | None:
        names = [str(tool.get("name", "")) for tool in tools]
        if configured in names:
            return configured
        for alias in aliases:
            match = next((name for name in names if name.lower() == alias), None)
            if match:
                return match
        return None

    @staticmethod
    def _entity_arguments(tool_name: str, urn: str) -> dict[str, Any]:
        if tool_name.lower() == "get_entities":
            return {"urns": [urn]}
        return {"urn": urn}

    @classmethod
    def _entities_from_search(cls, result: Any) -> list[ContextEntity]:
        records = cls._records(result)
        entities: list[ContextEntity] = []
        for record in records:
            urn = cls._value(record, "urn", "entityUrn", "entity.urn")
            if not urn:
                continue
            name = cls._value(record, "name", "entityName", "entity.name", "properties.name") or urn.rsplit(":", 1)[-1]
            entity_type = cls._value(record, "entityType", "type", "entity.type") or "unknown"
            entities.append(
                ContextEntity(
                    urn=str(urn),
                    name=str(name),
                    entity_type=str(entity_type).lower(),
                    relevance=cls._value(record, "relevance", "description") or "Relevant DataHub search result.",
                    relationships=cls._relationships(record),
                    metadata=cls._metadata(record),
                )
            )
        return cls._deduplicate_entities(entities)

    @staticmethod
    def _deduplicate_entities(entities: list[ContextEntity]) -> list[ContextEntity]:
        by_urn: dict[str, ContextEntity] = {}
        for entity in entities:
            existing = by_urn.get(entity.urn)
            if existing is None:
                by_urn[entity.urn] = entity
                continue
            existing.relationships = list(
                dict.fromkeys(existing.relationships + entity.relationships)
            )
            existing.metadata.update(entity.metadata)
            if entity.relevance and entity.relevance != existing.relevance:
                existing.relevance = f"{existing.relevance} {entity.relevance}"
        return list(by_urn.values())

    @classmethod
    def _enrich_entity(cls, entity: ContextEntity, result: Any) -> None:
        for record in cls._records(result):
            entity.relationships = list(dict.fromkeys(entity.relationships + cls._relationships(record)))
            entity.metadata.update(cls._metadata(record))

    @staticmethod
    def _records(result: Any) -> list[dict[str, Any]]:
        if isinstance(result, dict):
            for key in ("entities", "results", "searchResults", "items", "data"):
                value = result.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
            return [result]
        if isinstance(result, list):
            records: list[dict[str, Any]] = []
            for item in result:
                if isinstance(item, dict):
                    text_value = item.get("text")
                    if isinstance(text_value, str):
                        try:
                            decoded = json.loads(text_value)
                            records.extend(DataHubMCPAdapter._records(decoded))
                        except json.JSONDecodeError:
                            continue
                    else:
                        records.append(item)
                elif isinstance(item, dict) is False and isinstance(item, str):
                    try:
                        decoded = json.loads(item)
                        if isinstance(decoded, dict):
                            records.extend(DataHubMCPAdapter._records(decoded))
                    except json.JSONDecodeError:
                        continue
            return records
        return []

    @staticmethod
    def _value(record: dict[str, Any], *paths: str) -> Any:
        for path in paths:
            value: Any = record
            for part in path.split("."):
                if not isinstance(value, dict) or part not in value:
                    value = None
                    break
                value = value[part]
            if value not in (None, ""):
                return value
        return None

    @classmethod
    def _relationships(cls, record: dict[str, Any]) -> list[str]:
        value = cls._value(record, "relationships", "relatedUrns", "lineage") or []
        if isinstance(value, dict):
            value = value.get("urns", value.get("entities", []))
        if not isinstance(value, list):
            return []
        return [str(item.get("urn")) if isinstance(item, dict) and item.get("urn") else str(item) for item in value]

    @staticmethod
    def _metadata(record: dict[str, Any]) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        aliases = {
            "owner": ("owner", "ownership", "owners"),
            "freshness": ("freshness", "freshnessStatus"),
            "quality": ("quality", "qualityStatus"),
            "domain": ("domain", "domainName"),
            "documentation": (
                "documentation",
                "description",
                "properties.description",
                "definition",
                "properties.definition",
            ),
        }
        for key, paths in aliases.items():
            value = DataHubMCPAdapter._value(record, *paths)
            if value not in (None, ""):
                summarized = DataHubMCPAdapter._summarize_value(value)
                if summarized and summarized != "—":
                    metadata[key] = summarized
        return metadata

    @staticmethod
    def _summarize_value(value: Any) -> str:
        """Render a raw DataHub API value as short, human-readable text.

        DataHub's ownership/search payloads are deeply nested (owner lists,
        corpuser URNs, ownership-type URNs, ...). Rendering that structure
        with ``str(value)`` dumps the whole Python repr into the UI, so this
        collapses common shapes down to the names/labels a person cares about.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, dict):
            owners = value.get("owners")
            if isinstance(owners, list):
                names: list[str] = []
                for item in owners:
                    owner = item.get("owner", {}) if isinstance(item, dict) else {}
                    props = owner.get("properties", {}) if isinstance(owner, dict) else {}
                    display = props.get("displayName") if isinstance(props, dict) else None
                    label = display or owner.get("urn")
                    if label:
                        names.append(str(label))
                deduped = list(dict.fromkeys(names))
                return ", ".join(deduped) if deduped else "—"
            for key in ("displayName", "name", "label", "value", "urn"):
                candidate = value.get(key)
                if isinstance(candidate, (str, int, float)):
                    return str(candidate)
            return "—"
        if isinstance(value, list):
            parts = [DataHubMCPAdapter._summarize_value(item) for item in value]
            parts = [part for part in parts if part and part != "—"]
            deduped = list(dict.fromkeys(parts))
            return ", ".join(deduped) if deduped else "—"
        return str(value)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-03-26",
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers


class DataHubStdioAdapter(DataHubMCPAdapter):
    provider_name = "local_mcp"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._gms_url = settings.datahub_gms_url
        self._command = settings.datahub_mcp_command
        self._args = settings.datahub_mcp_args.split()

    async def status(self) -> DataHubIntegrationStatus:
        if not self._gms_url:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=False,
                reachable=False,
                mode="stdio",
                detail="DATAHUB_GMS_URL is not configured.",
            )
        try:
            process = await self._start_process()
            await self._stdio_request(process, "initialize", self._initialize_params())
            await self._stop_process(process)
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=True,
                mode="stdio",
                detail="Local DataHub MCP stdio server initialized successfully.",
            )
        except (OSError, asyncio.TimeoutError, ValueError) as exc:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=False,
                mode="stdio",
                detail=f"Local DataHub MCP server is not reachable: {exc.__class__.__name__}.",
            )

    async def discover_context(
        self, interpretation: GoalInterpretation
    ) -> DataHubContextDiscovery:
        status = await self.status()
        if not status.reachable:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="stdio-unavailable",
                entities=[],
                notes=[status.detail],
            )

        process: asyncio.subprocess.Process | None = None
        try:
            process = await self._start_process()
            await self._stdio_request(process, "initialize", self._initialize_params())
            await self._stdio_notification(process, "notifications/initialized")
            tools_result = await self._stdio_request(process, "tools/list", {})
            tools = tools_result.get("tools", [])
            search_tool = self._resolve_tool(tools, self._search_tool, ("search", "find"))
            entity_tool = self._resolve_tool(
                tools,
                self._entity_tool,
                ("get_entities", "get_entity", "entity", "get_data_entity"),
            )
            search_result = await self._stdio_request(
                process,
                "tools/call",
                {
                    "name": search_tool,
                    "arguments": {"query": interpretation.original_goal, "limit": 10},
                },
            )
            entities = self._entities_from_search(
                search_result.get("structuredContent", search_result.get("content", search_result))
            )
            for entity in entities:
                if entity_tool:
                    detail = await self._stdio_request(
                        process,
                        "tools/call",
                        {
                            "name": entity_tool,
                            "arguments": self._entity_arguments(entity_tool, entity.urn),
                        },
                    )
                    self._enrich_entity(
                        entity,
                        detail.get("structuredContent", detail.get("content", detail)),
                    )
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="local-mcp-stdio",
                entities=entities,
                notes=[f"Discovered local DataHub context for: {interpretation.original_goal}"],
            )
        except (OSError, asyncio.TimeoutError, ValueError, KeyError) as exc:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="stdio-error",
                entities=[],
                notes=[f"Local DataHub MCP discovery failed: {exc.__class__.__name__}."],
            )
        finally:
            if process is not None:
                await self._stop_process(process)

    async def _start_process(self) -> asyncio.subprocess.Process:
        environment = os.environ.copy()
        environment["DATAHUB_GMS_URL"] = self._gms_url
        if self._token:
            environment["DATAHUB_GMS_TOKEN"] = self._token
        return await asyncio.create_subprocess_exec(
            self._command,
            *self._args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=environment,
        )

    async def _stdio_request(
        self,
        process: asyncio.subprocess.Process,
        method: str,
        params: dict,
    ) -> dict:
        if process.stdin is None or process.stdout is None:
            raise ValueError("MCP stdio process pipes are unavailable")
        process.stdin.write(
            (json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}) + "\n").encode()
        )
        await process.stdin.drain()
        while True:
            line = await asyncio.wait_for(process.stdout.readline(), self._timeout)
            if not line:
                raise ValueError("MCP stdio process exited before returning a response")
            payload = json.loads(line)
            if "result" in payload:
                return payload["result"]
            if "error" in payload:
                raise ValueError(f"MCP stdio request failed: {payload['error']}")

    async def _stdio_notification(self, process: asyncio.subprocess.Process, method: str) -> None:
        if process.stdin is None:
            raise ValueError("MCP stdio process input is unavailable")
        process.stdin.write((json.dumps({"jsonrpc": "2.0", "method": method}) + "\n").encode())
        await process.stdin.drain()

    async def _stop_process(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), 2)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()

    def _initialize_params(self) -> dict:
        return {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "saint", "version": "0.1.0"},
        }


class AgentContextAdapter:
    """Direct Agent Context Kit integration; no MCP process is started."""

    provider_name = "agent_context"

    def __init__(self, settings: Settings) -> None:
        self._server = settings.datahub_gms_url.rstrip("/")
        self._token = settings.datahub_gms_token or settings.datahub_token

    def _client(self) -> Any:
        from datahub.sdk.main_client import DataHubClient

        return DataHubClient(server=self._server, token=self._token or None)

    async def status(self) -> DataHubIntegrationStatus:
        if not self._server:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=False,
                reachable=False,
                mode="agent-context",
                detail="DATAHUB_GMS_URL is not configured.",
            )
        try:
            client = self._client()
            await asyncio.to_thread(client.test_connection)
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=True,
                mode="agent-context",
                detail="Agent Context Kit connected directly to DataHub.",
            )
        except ImportError:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=False,
                mode="agent-context",
                detail="Optional Agent Context Kit dependency is not installed.",
            )
        except Exception as exc:
            return DataHubIntegrationStatus(
                provider=self.provider_name,
                configured=True,
                reachable=False,
                mode="agent-context",
                detail=f"Agent Context Kit connection failed: {exc.__class__.__name__}.",
            )

    async def discover_context(
        self, interpretation: GoalInterpretation
    ) -> DataHubContextDiscovery:
        try:
            entities = await asyncio.to_thread(self._discover_sync, interpretation.original_goal)
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="agent-context-kit",
                entities=entities,
                notes=[f"Discovered DataHub context for: {interpretation.original_goal}"],
            )
        except ImportError:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="agent-context-unavailable",
                entities=[],
                notes=["Install the optional Agent Context Kit dependency first."],
            )
        except Exception as exc:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="agent-context-error",
                entities=[],
                notes=[f"Agent Context Kit discovery failed: {exc.__class__.__name__}."],
            )

    def _discover_sync(self, query: str) -> list[ContextEntity]:
        from datahub_agent_context.context import DataHubContext
        from datahub_agent_context.mcp_tools.entities import get_entities
        from datahub_agent_context.mcp_tools.search import search

        client = self._client()
        with DataHubContext(client):
            entity_filter = self._infer_entity_type_filter(query)

            def attempt(search_query: str, use_filter: bool) -> tuple[Any, list[ContextEntity]]:
                filter_arg = (
                    f"entity_type = {entity_filter}" if use_filter and entity_filter else None
                )
                search_result = search(query=search_query, filter=filter_arg, num_results=10)
                return search_result, DataHubMCPAdapter._entities_from_search(search_result)

            result, entities = attempt(query, use_filter=True)
            if not entities and entity_filter:
                # The type guess may be wrong, or nothing of that type matched
                # this query; fall back to an unfiltered search rather than
                # returning nothing.
                result, entities = attempt(query, use_filter=False)

            if not entities:
                stopwords = {"understand", "explain", "find", "show", "what", "when", "where", "why", "how", "the", "from", "with"}
                keywords = [
                    word
                    for word in re.findall(r"[a-zA-Z0-9_]+", query.lower())
                    if len(word) >= 4 and word not in stopwords
                ]
                if keywords:
                    fallback_query = "/q " + " OR ".join(keywords[-6:])
                    result, entities = attempt(fallback_query, use_filter=True)
                    if not entities and entity_filter:
                        result, entities = attempt(fallback_query, use_filter=False)

            records = DataHubMCPAdapter._records(result)
            urns = [
                str(DataHubMCPAdapter._value(record, "urn", "entityUrn", "entity.urn"))
                for record in records
                if DataHubMCPAdapter._value(record, "urn", "entityUrn", "entity.urn")
            ]
            details = get_entities(urns=urns) if urns else []
        _enrich_entity_map(entities, details)
        return entities

    @staticmethod
    def _infer_entity_type_filter(goal: str) -> str | None:
        """Best-effort guess at which DataHub entity type a goal is about.

        A generic full-text search over a mixed catalog can surface entities
        that merely mention the right words rather than the entities the
        person actually asked about -- e.g. asking to see "all datasets" can
        return Document write-ups or ML feature keys that reference the word
        "dataset" instead of the dataset entities themselves. When the goal
        clearly names a DataHub entity type, that type is searched first;
        callers still fall back to an unfiltered search if this comes up
        empty, so a wrong guess here never loses results it would otherwise
        have found.
        """
        text = goal.lower()
        keyword_to_type: tuple[tuple[tuple[str, ...], str], ...] = (
            (("dashboard",), "dashboard"),
            (("chart", "visualization", "visualisation"), "chart"),
            (("pipeline", "dag", "orchestrat", " job", "data job"), "dataJob"),
            (("glossary",), "glossaryTerm"),
            (("domain",), "domain"),
            (("dataset", "table", "data source"), "dataset"),
        )
        for keywords, entity_type in keyword_to_type:
            if any(keyword in text for keyword in keywords):
                return entity_type
        return None


def _enrich_entity_map(entities: list[ContextEntity], result: Any) -> None:
    by_urn = {entity.urn: entity for entity in entities}
    for record in DataHubMCPAdapter._records(result):
        urn = DataHubMCPAdapter._value(record, "urn", "entityUrn", "entity.urn")
        entity = by_urn.get(str(urn))
        if entity:
            DataHubMCPAdapter._enrich_entity(entity, record)


def build_datahub_adapter(settings: Settings) -> DataHubAdapter:
    provider = settings.datahub_provider.lower().strip()
    if provider in {"local_mcp", "stdio"}:
        return DataHubStdioAdapter(settings)
    if provider == "mcp":
        return DataHubMCPAdapter(settings)
    if provider in {"agent_context", "ack", "native"}:
        if settings.datahub_gms_url.strip():
            return AgentContextAdapter(settings)
        return MockDataHubAdapter()
    return MockDataHubAdapter()
