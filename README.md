# SAINT — Context-Aware Path to Insight

> **"People don't need more information. They need help discovering which information matters, why it matters, and what to do with it."**

[![PyPI](https://img.shields.io/pypi/v/saint-datahub?color=00c4a7)](https://pypi.org/project/saint-datahub/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![Built with DataHub](https://img.shields.io/badge/built%20with-DataHub%20Agent%20Context%20Kit-00c4a7)](https://docs.datahub.com/docs/dev-guides/agent-context/agent-context)
[![Hackathon](https://img.shields.io/badge/DataHub-Agent%20Hackathon%202026-orange)](https://datahub.devpost.com/)

---

SAINT is an AI agent that turns user goals into **contextual paths** — grounded in your organization's actual DataHub metadata. It reads your data catalog, reasons about what you need to understand, walks you through a structured investigation, and writes the result back to DataHub so the next person inherits your knowledge.

It is **not** a chatbot. It is not a search tool. It is a goal-driven agent that uses DataHub's context graph to figure out what you need to do *next*.

---

## How It Works

```
You give Saint a goal
        ↓
Saint interprets your intent
        ↓
You confirm the interpretation
        ↓
Saint reads your DataHub context graph
(schemas, lineage, ownership, quality, glossary)
        ↓
Saint builds a Contextual Path
(ordered steps grounded in real assets)
        ↓
You explore, learn, or act
        ↓
Saint synthesizes the final outcome
        ↓
You publish the investigation to DataHub
(so the next person or agent inherits your knowledge)
```

This is the key loop that DataHub's context graph makes possible. Without real metadata, every step would be generic advice. With DataHub, the path reflects the actual data environment around your goal.

---

## Quick Start

**No DataHub, no Docker, no credentials required to try:**

**Option A — Install from PyPI (easiest):**

```bash
pip install saint-datahub
saint demo
```

**Option B — Install from source:**

```bash
git clone https://github.com/einzeinn/saint.git
cd saint
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -e .
saint demo
```

`saint demo` runs a complete, deterministic investigation journey using built-in sample context. No tokens, no configuration, nothing to break.

---

## Modes

| Command | What it does | Requires DataHub? |
|---|---|---|
| `saint demo` | Full guided walkthrough with built-in sample context | No |
| `saint demo --live` | Same journey, but using your real DataHub connection | Yes |
| `saint` | Interactive menu — Learn, Explore, or Solve | Optional |
| `saint solve` | Hypothesis testing mode against DataHub evidence | Optional |
| `saint doctor` | Diagnose your DataHub and LLM configuration | Optional |
| `saint init` | Configure your DataHub connection | — |

---

## What SAINT Does That DataHub Doesn't

DataHub is a metadata platform. SAINT is a **goal-oriented agent that uses that platform** to help you answer questions you didn't know how to ask.

| Capability | DataHub Catalog | SAINT |
|---|---|---|
| Browse assets | ✅ | ✅ (via context graph) |
| Search metadata | ✅ | ✅ (via Agent Context Kit) |
| Interpret user goals | ❌ | ✅ |
| Build a contextual investigation path | ❌ | ✅ |
| Synthesize findings from evidence | ❌ | ✅ |
| Write structured outcomes back to catalog | ❌ | ✅ (`publish_result`) |
| Ground reasoning in real lineage/ownership | ❌ | ✅ |

---

## Architecture

```
┌────────────────────────────────┐
│             CLI                │
│  saint / saint demo / solve    │
└─────────────┬──────────────────┘
              │
┌─────────────▼──────────────────┐
│         Orchestrator           │
│  interpret → path → synthesize │
│  → assess → publish            │
└──────┬──────────────┬──────────┘
       │              │
┌──────▼──────┐ ┌─────▼────────┐
│ LLM Adapter │ │ DataHub      │
│ (Groq /     │ │ Adapter      │
│  Gemini)    │ │ (Agent Ctx / │
└─────────────┘ │  Mock)       │
                └──────┬───────┘
                       │
                ┌──────▼───────┐
                │   DataHub    │
                │  Context     │
                │  Graph       │
                └──────────────┘
```

**Key modules:**

- [`backend/app/orchestration/orchestrator.py`](backend/app/orchestration/orchestrator.py) — Core reasoning: goal → path → outcome → write-back
- [`backend/app/adapters/datahub.py`](backend/app/adapters/datahub.py) — DataHub integration via Agent Context Kit (`AgentContextAdapter`) with a full `MockDataHubAdapter` for offline demo
- [`backend/app/adapters/llm.py`](backend/app/adapters/llm.py) — LLM adapter (Groq / Gemini), protocol-based and swappable
- [`backend/app/cli.py`](backend/app/cli.py) — Rich terminal UI with full interactive and demo flows
- [`skills/saint_investigator.py`](skills/saint_investigator.py) — Registered as a DataHub Skill entry-point

---

## DataHub Integration

SAINT uses DataHub's **Agent Context Kit** (`datahub-agent-context`) as its primary integration. It does **not** require an MCP server to run.

```
saint[agent-context]
    ↓
datahub_agent_context SDK
    ↓
DataHub GMS (REST)
    ↓
Context graph: schemas, lineage, ownership, quality, domains
```

**Read operations** (via `search_entities`, `get_entity_relationships`, `get_lineage`):
- Schema and field-level metadata
- Upstream/downstream lineage
- Asset ownership and domain membership
- Data quality signals

**Write operations** (via `save_document`):
- Investigation summaries published as DataHub Documents
- Related assets linked by entity-level URN
- Tagged with `saint-analysis` and intent topic

---

## Connected Mode (Optional)

```bash
pip install "saint-datahub[agent-context]"
```

Set environment variables:

```env
DATAHUB_PROVIDER=agent_context
DATAHUB_GMS_URL=http://localhost:8080
DATAHUB_GMS_TOKEN=<personal-access-token>
```

Then run:

```bash
saint demo --live   # Full demo with your real DataHub data
saint               # Interactive mode
```

`saint doctor` will confirm your connection is healthy before you start.

---

## Sample Output

See [`examples/`](examples/) for example investigation outputs, including a published DataHub Document from a real `saint solve` session.

---

## Project Structure

```
backend/
  app/
    cli.py                  # Terminal UI — all modes
    orchestration/          # SaintOrchestrator — core agent logic
    adapters/               # DataHub + LLM adapters
    domain/                 # Pydantic models (GoalRequest, ContextualPath, etc.)
    config.py               # Settings (pydantic-settings, .env)
docs/
  RFC/                      # Technical RFCs (including RFC-003: DataHub write-back)
  Architecture.md
  Hackathon.md
  JudgeSetup.md
skills/
  saint_investigator.py     # DataHub Skill entry-point
tests/
  test_datahub_integration.py
  test_health.py
```

---

## For Hackathon Judges

See **[docs/JudgeSetup.md](docs/JudgeSetup.md)** for the reproducible judge setup. The one-line quickstart:

```bash
pip install -e . && saint demo
```

No DataHub instance, no API key, no Docker. The demo runs a complete investigation journey with deterministic built-in context, ending with a simulated publish preview that shows exactly what would be written back to DataHub.

If you have a DataHub instance running locally, see [docs/JudgeSetup.md](docs/JudgeSetup.md) for the connected mode setup.

---

## Compatibility API

A FastAPI surface is available for existing integrations:

```bash
uvicorn backend.app.main:app --reload
# → http://127.0.0.1:8000/health
```

This is a secondary surface; the primary product is the CLI.

---

## License

[Apache 2.0](LICENSE) — open source and free to use, modify, and distribute.
