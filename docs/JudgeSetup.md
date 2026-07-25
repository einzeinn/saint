# Judge Setup: Saint CLI

> Current direction: Saint is submitted as an installable terminal application. MCP and Docker are optional integration experiments, not requirements for the primary demo.

This is the reproducible, read-only setup for the hackathon demo. It runs the Saint Core journey with safe built-in sample context. No Docker, MCP server, DataHub account, or production token is required.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer

## Install Saint

```powershell
python -m pip install saint
```

For repository-based judging, use `python -m pip install .` instead.

## Run the demo

```powershell
saint demo
```

The demo automatically runs:

```text
Goal → Interpretation → Confirmation → Context → Path → Guidance → Assessment → Outcome
```

## Optional connected DataHub mode

The primary demo does not require DataHub connectivity. If a judge already has a DataHub instance, install the optional Agent Context Kit dependency and configure connected mode with:

```env
DATAHUB_PROVIDER=agent_context
DATAHUB_GMS_URL=http://localhost:8080
DATAHUB_GMS_TOKEN=<personal-access-token>
```

Install the optional integration with `python -m pip install "saint[agent-context]"`. This direct Python integration uses Agent Context Kit functions; it does not start an MCP server. The HTTP and stdio MCP adapters are retained for experiments and hosted integrations but are not required for the submission demo.

### Local DataHub sample data

For a local OSS DataHub quickstart, the bundled bootstrap pack can be loaded with Saint's compatibility loader. The standard `datahub datapack load bootstrap` command may fail on mixed MCE/MCP-wrapper packs in some CLI versions.

```powershell
$env:DATAHUB_GMS_URL="http://localhost:8080"
$env:DATAHUB_GMS_TOKEN="<personal-access-token>"
python scripts/load_datapack.py "$env:USERPROFILE\.datahub\datapack-cache\<bootstrap-pack>.json"
```

The loader supports both event shapes and reports the number of loaded and skipped records.

## Interactive mode

```powershell
saint
```

Use `saint doctor` to inspect the configured optional integration and `saint init` for configuration guidance.
