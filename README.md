# Saint

Saint is an adaptive, context-driven agent that turns user goals into contextual paths toward understanding or action.

Saint's primary direction is an installable interactive terminal application. The web API and frontend remain as a secondary compatibility surface while the terminal experience becomes the main product.

## Project Structure

```text
docs/              Product, architecture, design, roadmap, and RFC documents
backend/           Saint Core, CLI, API, orchestration, domain models, adapters
frontend/          Secondary web prototype and compatibility surface
tests/              Backend and core-focused tests
docs/               Product direction, deployment strategy, RFCs, and judge setup
```

## Run Saint

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
saint demo
```

`saint demo` runs without Docker or DataHub credentials using safe built-in sample context.

For an interactive session:

```powershell
saint
```

For environment diagnostics:

```powershell
saint doctor
```

For connected DataHub setup guidance:

```powershell
saint init
```

See [docs/deployment.md](docs/deployment.md), [docs/JudgeSetup.md](docs/JudgeSetup.md), and [docs/revision.md](docs/revision.md) for the current direction.

## Compatibility API

The FastAPI surface can still be run for existing integrations:

```powershell
uvicorn backend.app.main:app --reload
```

The health endpoint is available at:

```text
GET http://127.0.0.1:8000/health
```

The secondary frontend prototype can still be run in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Then open:

```text
http://127.0.0.1:5173
```
