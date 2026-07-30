# RFC-003: DataHub Agent Context Write-Back Integration

## Status

Accepted

## Type

Feature / DataHub Integration

## Date

2026-07-31

---

# 1. Summary

This RFC documents the design, user experience, and technical implementation of the DataHub Write-Back capability for Saint's interactive terminal application.

Saint can publish investigation outcomes, synthesis summaries, notes, asset descriptions, and tags directly back into DataHub using the official `datahub-agent-context` Python SDK.

---

# 2. Motivation & Core Improvements

Prior to this feature, Saint's integration with DataHub was strictly read-only. With write-back capabilities:
- Saint persists investigation findings as standalone **Document** entities in DataHub (`Insight`, `Decision`, `Analysis`, `Summary`, `Note`).
- Documents are automatically linked to the primary data asset URNs (`related_assets`) evaluated during the session.

### Key Refinements (Phase Write Principles):
1. **Deterministic Demo Mode**: `saint demo` NEVER auto-publishes or generates spurious mock documents. Instead, it renders a deterministic **Simulated Document Publish Preview**.
2. **Generic Method Surface**: Orchestrator uses `publish_result()` and `build_publish_preview()`, supporting diverse flows (Investigations, Recommendations, Summaries, Incidents).
3. **Interactive UX Preview**: Before writing to DataHub, Saint displays a Rich preview box listing **Title**, **Type**, **Topics**, and **Related Assets**, requiring double user confirmation (`Publish? [y/N]` -> `Confirm? [Y/n]`).
4. **Filtered Related Assets**: Restricts linked `related_assets` to the top primary evidence assets (max 5) rather than linking every searched asset.
5. **Clean Document Titles**: Replaces long descriptive sentences with concise, readable titles (e.g. `Revenue Overview Dashboard Investigation`).

---

# 3. Architecture & Interaction Strategy

```text
User CLI Session (saint / saint solve)
       │
       ▼
SaintOrchestrator.synthesize_final_outcome()
       │
       ▼
CLI Prompt: "Publish investigation summary to DataHub as a Document?" [y/N]
       │
       ├─► [N] No -> Finish Sesi
       │
       └─► [Y] Yes
            │
            ▼
   SaintOrchestrator.build_publish_preview()
            │
            ▼
   Render Rich Preview Panel (Title, Type, Top Assets, Topics)
            │
            ▼
   CLI Prompt: "Confirm publishing to DataHub?" [Y/n]
            │
            ├─► [N] Cancelled
            │
            └─► [Y] Confirmed
                 │
                 ▼
        SaintOrchestrator.publish_result()
                 │
                 ▼
        DataHubAdapter.save_document()
                 │
                 ├─► AgentContextAdapter ──► datahub_agent_context.mcp_tools.save_document() ──► Local Docker DataHub
                 │
                 └─► MockDataHubAdapter  ──► Deterministic Mock Result
```

---

# 4. Technical Details

### 4.1 Domain Models (`backend/app/domain/models.py`)

- `WriteBackRequest`: Payload carrying document type, title, Markdown content, topics, and related asset URNs.
- `WriteBackResult`: Standard response carrying success status, generated Document URN (`urn:li:document:...`), message, and executed action.

### 4.2 DataHub Adapter Protocol (`backend/app/adapters/datahub.py`)

The `DataHubAdapter` Protocol specifies three write-back methods:
1. `save_document(document_type, title, content, topics, related_assets)`: Creates or updates a standalone document entity.
2. `update_description(entity_urn, description, operation)`: Appends or replaces documentation on a dataset or asset.
3. `add_tags(tag_urns, entity_urns)`: Attaches tags (e.g., `urn:li:tag:SaintVerified`) to entities.

#### Implementations:
- **`AgentContextAdapter`**: Invokes `datahub_agent_context.mcp_tools` (`save_document`, `update_description`, `add_tags`) within `asyncio.to_thread` inside a `DataHubContext(client)` block.
- **`MockDataHubAdapter`**: Returns deterministic mock responses.
- **`DataHubMCPAdapter`**: Fallback response directing users to the `agent_context` provider.

### 4.3 Orchestrator Integration (`backend/app/orchestration/orchestrator.py`)

- `_format_clean_title(path)`: Derives clean titles (e.g., `Revenue Overview Dashboard Investigation`).
- `build_publish_preview(path, title, document_type)`: Generates Markdown content and filters `related_assets` to top 5 evidence entities.
- `publish_result(path, title, document_type)`: Publishes the report via `DataHubAdapter`.

### 4.4 CLI Terminal Experience (`backend/app/cli.py`)

- **Demo mode (`saint demo`)**: Renders a `[Simulated Document Publish (Demo Mode)]` panel. No live or mock document is created.
- **Interactive mode (`saint solve`, `saint`)**: Asks user if they want to publish, shows the `Publishing Preview` panel, and requires final confirmation before sending the GraphQL mutation to DataHub.

---

# 5. Verification & Milestone Status

| Milestone Check | Status | Verification Method |
| :--- | :---: | :--- |
| **Mock Mode** | ✅ | Deterministic simulated preview in `saint demo` |
| **ACK (Agent Context Kit)** | ✅ | Direct SDK integration via `datahub_agent_context` |
| **Local Docker Connectivity** | ✅ | Connected to `http://localhost:8080` (GMS Token validated) |
| **Real Document in DataHub UI** | ✅ | Verified live creation of URN `urn:li:document:shared-...` in local Docker container |

### Verification Command:
```powershell
$env:PYTHONIOENCODING="utf-8"
.\.package-test-312\Scripts\python.exe -m backend.app.cli solve
```
Upon completion and confirmation, the published document is immediately searchable and visible in the DataHub UI (`http://localhost:9002`).
