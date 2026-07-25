# Saint Deployment Strategy

## Status

Accepted

The terminal package is now the primary deployment target. The earlier web deployment files are retained only as historical/legacy compatibility material and are not part of the active implementation path.

## Scope

Deployment and Distribution Strategy

---

# 1. Overview

Saint is an interactive terminal application.

Therefore, its primary deployment strategy is not a traditional web application deployment.

The primary goal is:

> **A user should be able to install Saint and start using it with minimal setup.**

The preferred experience is:

```bash
pip install saint
saint
```

Or, when using `uv`:

```bash
uvx saint
```

The deployment strategy should prioritize:

```text
Install
    ↓
Initialize
    ↓
Run
```

rather than:

```text
Clone Repository
    ↓
Install Multiple Dependencies
    ↓
Configure Services
    ↓
Deploy Frontend
    ↓
Deploy Backend
    ↓
Configure DataHub
    ↓
Run
```

---

# 2. Primary Distribution Model

Saint should be distributed as a Python package.

The target user experience is:

```bash
pip install saint
saint
```

The package should provide:

* Saint CLI
* Rich terminal UI
* Saint Core
* LLM provider adapter
* DataHub integration adapter
* Configuration management
* Initialization commands

Conceptually:

```text
┌────────────────────────────┐
│       Python Package       │
│           Saint            │
├────────────────────────────┤
│                            │
│  Interactive Terminal UI   │
│            ↓               │
│       Saint Core           │
│            ↓               │
│   ┌────────────┬────────┐  │
│   │ LLM Adapter │DataHub │  │
│   │             │Adapter │  │
│   └────────────┴────────┘  │
│                            │
└────────────────────────────┘
```

---

# 3. Installation Experience

## Target Experience

```bash
pip install saint
saint
```

The user should not need to manually clone the repository for the primary usage flow.

The application should launch into the interactive terminal interface.

Example:

```text
╭────────────────────────────────────╮
│              ✦ SAINT               │
│   Context-aware path to insight     │
╰────────────────────────────────────╯
```

---

# 4. Runtime Modes

Saint should support multiple runtime modes.

## 4.1 Demo Mode

The goal of demo mode is to allow a user or judge to experience Saint with minimal setup.

```bash
pip install saint
saint demo
```

Demo mode may use:

* Preconfigured sample data
* A bundled or remotely accessible demo environment
* A controlled dataset
* A predefined demonstration scenario

The goal is:

```text
Install
    ↓
Run Demo
    ↓
Experience Saint
```

Demo mode should minimize external configuration.

---

## 4.2 Connected DataHub Mode

For users with an existing DataHub instance:

```bash
pip install saint
saint init
```

The user configures the DataHub connection.

Conceptually:

```text
Saint
    ↓
DataHub Adapter
    ↓
DataHub Instance
```

Required configuration may include:

```env
DATAHUB_GMS_URL=...
DATAHUB_TOKEN=...
```

The exact configuration mechanism should remain modular and may be implemented through:

* Environment variables
* Configuration file
* Interactive initialization
* Secure credential storage

The application should not hard-code credentials.

---

# 5. Initialization

The preferred initialization flow is:

```bash
saint init
```

The command should guide the user through configuration.

Example:

```text
╭─ SAINT INITIALIZATION ─────────────────╮
│                                        │
│  Choose your environment:              │
│                                        │
│  ◉ Connect existing DataHub            │
│  ○ Configure LLM provider              │
│  ○ Use demo environment                │
│                                        │
╰────────────────────────────────────────╯
```

The initialization process should validate:

```text
Environment
    ↓
LLM Configuration
    ↓
DataHub Configuration
    ↓
Connection Test
    ↓
Ready
```

Example:

```text
Checking configuration...

✓ LLM provider configured
✓ DataHub URL configured
✓ Authentication successful
✓ DataHub connection verified

Saint is ready.
```

---

# 6. Recommended Command Structure

The CLI should expose clear commands.

Initial conceptual command structure:

```bash
saint
```

Launch the interactive application.

```bash
saint init
```

Initialize or configure the environment.

```bash
saint demo
```

Launch the demo experience.

```bash
saint doctor
```

Check the environment and diagnose configuration issues.

```bash
saint version
```

Display the installed Saint version.

The exact command structure may change during implementation.

---

# 7. Judge Experience

The hackathon submission should optimize for the shortest path from discovery to experience.

Preferred flow:

```text
Judge
  ↓
README
  ↓
Install Saint
  ↓
Run Saint
  ↓
Experience Demo
```

Ideal:

```bash
pip install saint
saint demo
```

The judge should not be required to:

* Clone the repository for the primary experience
* Manually install many unrelated dependencies
* Configure a complex infrastructure stack
* Deploy a web application
* Run multiple services
* Install Docker unless explicitly required by the selected environment

The repository should still remain publicly available for:

* Source inspection
* Technical evaluation
* Reproducibility
* Contribution

---

# 8. Repository and Package Relationship

The GitHub repository remains the source of truth for development.

The Python package is the distribution artifact.

```text
GitHub Repository
        ↓
      Build
        ↓
   Python Package
        ↓
    pip / uv
        ↓
      User
```

Conceptually:

```text
┌──────────────────┐
│ GitHub Repository │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Package Build    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Package Registry │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   pip / uvx      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│      Saint       │
└──────────────────┘
```

---

# 9. Deployment Does Not Mean Hosting

Saint does not need to be hosted as a traditional web application for the MVP.

The primary deployment target is:

```text
User Device
    ↓
Python Environment
    ↓
Saint CLI
```

This is fundamentally different from:

```text
Browser
    ↓
Frontend Hosting
    ↓
Backend Hosting
    ↓
DataHub Hosting
```

The product should not introduce a hosted web architecture unless there is a clear product requirement.

---

# 10. DataHub Dependency

Saint's core functionality depends on DataHub context.

Therefore, DataHub remains an external system or environment.

The relationship is:

```text
Saint
    ↓
DataHub Integration Adapter
    ↓
DataHub
```

The deployment strategy must support multiple DataHub environments:

```text
┌─────────────────────┐
│ Local DataHub       │
│ Development         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Remote DataHub      │
│ Production / Demo   │
└─────────────────────┘
```

Saint should not hard-code a single environment.

---

# 11. Environment Configuration

Configuration must remain external to the package.

The application should support environment-based configuration.

Example:

```env
DATAHUB_GMS_URL=...
DATAHUB_TOKEN=...
LLM_PROVIDER=...
LLM_API_KEY=...
```

Secrets must:

* Never be hard-coded
* Never be committed to Git
* Never be included in package source
* Be configurable per environment

The application should provide clear configuration errors.

Bad:

```text
Connection failed.
```

Preferred:

```text
DataHub connection failed.

Possible causes:
- DATAHUB_GMS_URL is missing
- Authentication token is invalid
- DataHub instance is unreachable

Run:

saint doctor
```

---

# 12. Environment Diagnostics

The `saint doctor` command should eventually provide environment diagnostics.

Example:

```text
╭─ SAINT DOCTOR ─────────────────────────╮
│                                        │
│ Python                  ✓              │
│ Saint Installation      ✓              │
│ LLM Configuration       ✓              │
│ DataHub URL             ✓              │
│ DataHub Authentication  ✓              │
│ DataHub Connectivity    ✓              │
│                                        │
│ Environment is ready.                  │
╰────────────────────────────────────────╯
```

This reduces setup friction and improves the judge experience.

---

# 13. Distribution Strategy

The preferred distribution sequence is:

```text
Development
    ↓
GitHub Repository
    ↓
Package Build
    ↓
Package Registry
    ↓
pip install saint
    ↓
saint
```

For early development, the package may be installed locally:

```bash
pip install -e .
```

or:

```bash
uv run saint
```

The final hackathon distribution should prioritize a published installable package if the project is sufficiently stable.

---

# 14. Hackathon Submission Strategy

The submission should provide:

## Source

A public GitHub repository.

## Installation

A minimal installation command.

Preferred:

```bash
pip install saint
```

## Execution

A minimal launch command.

```bash
saint demo
```

## Documentation

The README should clearly explain:

```text
1. What Saint is
2. What problem it solves
3. How DataHub is used
4. How to install Saint
5. How to run the demo
6. How to connect a real DataHub instance
```

## Demonstration

A short video should demonstrate the product in action.

The video should focus on:

```text
User Goal
    ↓
Saint Understanding
    ↓
DataHub Context
    ↓
Contextual Path
    ↓
User Interaction
    ↓
Outcome
```

The video should not spend significant time showing:

* Dependency installation
* Docker setup
* Environment debugging
* Infrastructure configuration

The product experience is the focus.

---

# 15. Deployment Principle

The primary deployment principle is:

> **Make the path from installation to meaningful experience as short as possible.**

The ideal:

```text
pip install saint
        ↓
saint demo
        ↓
Experience Saint
```

The full connected experience:

```text
pip install saint
        ↓
saint init
        ↓
Connect DataHub
        ↓
saint
```

---

# 16. Future Expansion

A web application may be introduced in the future.

If that happens, the architecture should allow:

```text
┌───────────────┐
│ Textual UI    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Saint Core   │
└───────┬───────┘
        ▲
        │
┌───────┴───────┐
│ Web Interface │
└───────────────┘
```

The core product should remain independent of the current interface.

This means the terminal application is not a dead-end.

It is the first interface built on top of Saint Core.

---

# 17. Final Deployment Direction

Saint's primary deployment target is:

> **A distributable Python package that provides an interactive terminal application and can be installed with minimal setup.**

The target experience is:

```bash
pip install saint
saint demo
```

For connected DataHub environments:

```bash
pip install saint
saint init
saint
```

The project should prioritize:

```text
Simple Installation
        ↓
Clear Initialization
        ↓
Reliable Execution
        ↓
Meaningful DataHub-Powered Experience
```

> **Saint should be easy to install, easy to start, and difficult to mistake for another disposable hackathon web app.**
