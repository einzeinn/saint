# Saint

Saint is an adaptive, context-driven agent that turns user goals into contextual paths toward understanding or action.

Saint's primary direction is an installable interactive terminal application. A FastAPI surface remains as a secondary compatibility API for existing integrations.

## Project Structure

```text
docs/              Product, architecture, design, roadmap, deployment, and judge setup docs
backend/           Saint Core, CLI, API, orchestration, domain models, adapters
tests/             Backend and core-focused tests
```

## Run Saint

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
saint demo
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
saint demo
```

`saint demo` runs without Docker or DataHub credentials using safe built-in sample context.

For an interactive session:

```bash
saint
```

For environment diagnostics:

```bash
saint doctor
```

For connected DataHub setup guidance:

```bash
saint init
```

See [docs/deployment.md](docs/deployment.md), [docs/JudgeSetup.md](docs/JudgeSetup.md), and [docs/revision.md](docs/revision.md) for the current direction.

## Compatibility API

The FastAPI surface can still be run for existing integrations:

```bash
uvicorn backend.app.main:app --reload
```

The health endpoint is available at:

```text
GET http://127.0.0.1:8000/health
```
