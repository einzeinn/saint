# Judge Setup: SAINT CLI

> **TL;DR:** `pip install saint-datahub && saint demo` — no DataHub, no Docker, no API key required.

---

## What You're Evaluating

SAINT is a CLI-first AI agent that turns data goals into structured investigation paths, grounded in DataHub context. The primary demo is fully self-contained. An optional connected mode shows live DataHub read + write-back.

**Hackathon category:** Agents That Do Real Work  
**Primary integration:** DataHub Agent Context Kit (`datahub-agent-context`)

---

## Prerequisites

- Python **3.12** (3.12.x — other versions not tested)
- Git

No Docker, no DataHub account, no MCP server, no tokens required for the base demo.

---

## Install

**Option A — PyPI (no clone needed):**

```bash
pip install saint-datahub
```

**Option B — From source:**

```bash
git clone https://github.com/einzeinn/saint.git
cd saint
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -e .
```

---

## Run the Demo

```bash
saint demo
```

This runs a complete, deterministic investigation journey:

```
Goal → Interpretation → Confirmation → Context Discovery
    → Contextual Path → Guidance → Assessment → Outcome → Publish Preview
```

The demo uses built-in sample context (no DataHub required). At the end, it shows a **Simulated Document Publish** preview — exactly what would be written back to DataHub — without touching any live system.

**The demo is deterministic.** Run it 10 times, get the same result.

---

## Explore Interactive Mode

```bash
saint        # Opens the interactive menu (Learn / Explore / Solve)
saint solve  # Hypothesis testing mode — test a theory against DataHub evidence
```

Interactive mode accepts a freeform goal, builds a real contextual path, and offers to publish the investigation to DataHub at the end.

---

## Other Commands

```bash
saint doctor    # Diagnose DataHub + LLM configuration
saint init      # Configuration guide for connected mode
saint version   # Print version
```

---

## Connected Mode (Optional — Live DataHub)

If you have a DataHub instance running, you can see live context discovery and write-back.

**Step 1:** Install the Agent Context Kit extra

```bash
pip install "saint-datahub[agent-context]"
```

**Step 2:** Set environment variables (`.env` file or shell):

```env
DATAHUB_PROVIDER=agent_context
DATAHUB_GMS_URL=http://localhost:8080
DATAHUB_GMS_TOKEN=<personal-access-token>
```

**Step 3:** Verify connectivity

```bash
saint doctor
```

Expected output:
```
DataHub provider    agent_context
Configured          ✓ yes
Reachable           ✓ yes
```

**Step 4:** Run demo with live DataHub data

```bash
saint demo --live
```

Or run a full interactive investigation:

```bash
saint solve
```

Type a goal like `"why did the revenue dashboard change?"`, confirm, and let SAINT discover real context from your catalog. At the end, you'll be prompted to publish the investigation summary to DataHub.

---

## Loading Sample Data into DataHub (Optional)

For a local OSS DataHub quickstart with sample data, use Saint's compatibility loader:

```bash
# macOS / Linux
export DATAHUB_GMS_URL="http://localhost:8080"
export DATAHUB_GMS_TOKEN="<personal-access-token>"
python scripts/load_datapack.py "$HOME/.datahub/datapack-cache/<bootstrap-pack>.json"

# Windows (PowerShell)
$env:DATAHUB_GMS_URL = "http://localhost:8080"
$env:DATAHUB_GMS_TOKEN = "<personal-access-token>"
python scripts/load_datapack.py "$env:USERPROFILE\.datahub\datapack-cache\<bootstrap-pack>.json"
```

The loader handles mixed MCE/MCP-wrapper packs and skips unsupported aspects instead of aborting.

---

## Sample Outputs

See [`examples/`](../examples/) for:
- A sample investigation document that was published to DataHub
- The raw `ContextualPath` JSON produced by an investigation session
- Terminal output from the publish preview and write-back flow

---

## LLM Configuration (Optional)

SAINT uses an LLM for goal interpretation, path guidance, and outcome synthesis. The demo works without an LLM key (falls back to structural responses). For full output quality, set one of:

```env
GROQ_API_KEY=<your-key>        # Recommended: free tier available at console.groq.com
GEMINI_API_KEY=<your-key>
```

`saint doctor` will show whether your LLM key is configured.

---

## Notes for Judges

- **No auto-publish in demo mode.** `saint demo` shows a simulated preview at the end — nothing is written to any system.
- **Write-back is opt-in.** In interactive mode, SAINT shows a publishing preview and asks for double confirmation before writing to DataHub.
- **schemaField URNs are automatically filtered.** DataHub's `document` aspect only accepts entity-level URNs in `relatedAssets`. SAINT handles this transparently.
- **The agent registers as a DataHub Skill.** See `pyproject.toml` → `[project.entry-points."datahub_agent_context.skills"]`.
