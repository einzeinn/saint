# RFC-002: Local DataHub MCP Strategy for Hackathon Submission

## Status

Superseded by the accepted architecture revision in `docs/revision.md`.

This RFC remains useful as historical context for the local DataHub/MCP experiment, but it is no longer the primary product or deployment direction.

## Date

2026-07-24

## Decision

For the hackathon submission, Saint will use DataHub OSS/Core locally with the official DataHub MCP Server over stdio.

The submission will not depend on a DataHub Cloud account, paid infrastructure, or a production DataHub token.

## Problem

The deployed Render/Vercel architecture cannot directly reach a DataHub instance running on a developer laptop. DataHub Cloud would solve that connectivity problem, but it adds account, access-token, and availability dependencies that are unnecessary for a hackathon-only submission.

The hackathon provides a local DataHub quickstart and sample datasets. The project should use that path while keeping the judge setup safe and reproducible.

## Context

The current Saint adapter speaks Streamable HTTP MCP. The local DataHub MCP Server is expected to run as a local stdio process backed by a local DataHub GMS instance.

The hackathon requires DataHub OSS/Core plus at least one supported integration, including MCP Server, Agent Context Kit, DataHub Skills, or Analytics Agent. Saint selects MCP Server as its primary integration.

## Proposed Architecture

```text
Judge Laptop
    |
    +-- DataHub OSS/Core (Docker quickstart)
    |       |
    |       +-- Sample datapack: showcase-ecommerce
    |
    +-- DataHub MCP Server (stdio, read-only)
    |
    +-- Saint Backend
    |       |
    |       +-- MCP stdio adapter
    |
    +-- Saint Frontend
```

The existing HTTP MCP adapter remains available for future hosted deployments. The local stdio adapter will be selected through configuration.

## Safety Requirements

- Mutation tools remain disabled.
- No DataHub token is committed to the repository.
- The default demo uses synthetic/sample metadata.
- MCP failures produce an explicit fallback state rather than crashing the application.
- The mock adapter remains available for frontend and backend development without DataHub running.
- Judge instructions must explain that DataHub is local and that no production credentials are required.

## Sample Dataset

The preferred dataset is `showcase-ecommerce` because it provides cross-platform entities, lineage, governance, glossary, domains, and quality scenarios. The lightweight `bootstrap` datapack may be used as a faster fallback.

## Configuration Direction

Local submission mode will use values equivalent to:

```env
DATAHUB_PROVIDER=local_mcp
DATAHUB_GMS_URL=http://localhost:8080
DATAHUB_MCP_TRANSPORT=stdio
TOOLS_IS_MUTATION_ENABLED=false
```

The exact process command and environment wiring will be documented in the judge setup guide after implementation.

## Alternatives Considered

### DataHub Cloud

Pros: public MCP endpoint and easier remote deployment.

Cons: requires tenant access, authentication, and a stable external dependency. Not necessary for this submission.

### Deploying Full DataHub on Render or Hugging Face Free Tier

Rejected because DataHub Core requires multiple supporting services and persistent state. Free-tier application hosting is not a reliable catalog deployment.

### HTTP Tunnel to a Local DataHub

Rejected as the primary submission architecture because it creates a fragile public dependency and exposes a developer machine.

### Mock Context Only

Rejected as the primary demo because it would weaken the evidence that Saint meaningfully uses DataHub. It remains a safe fallback.

## Acceptance Criteria

This decision is implemented when:

1. A fresh environment can start DataHub using the official local quickstart.
2. The sample datapack can be loaded without private credentials.
3. Saint can discover context through the local MCP stdio server.
4. Saint transforms search results, entity metadata, and relationships into application models.
5. The application remains usable when DataHub is unavailable through the mock fallback.
6. Automated tests cover stdio request/response handling and failure behavior.
7. README documentation contains judge-safe setup and teardown instructions.

## Consequences

The submission will prioritize reproducibility and safety over always-on hosted access. A later hosted deployment can reuse the existing HTTP adapter by changing configuration, without changing the domain and orchestration layers.
