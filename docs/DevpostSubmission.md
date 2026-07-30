# SAINT — Devpost Submission Description

*Copy-paste langsung ke submission form Devpost. Edit bagian yang perlu disesuaikan sebelum submit.*

---

## Short Tagline (< 100 chars)

> An AI agent that turns data goals into contextual investigation paths — powered by DataHub.

---

## Live Demo / Install

```bash
pip install saint-datahub && saint demo
```

**PyPI:** https://pypi.org/project/saint-datahub/  
**GitHub:** https://github.com/einzeinn/saint  
**Judge Setup:** https://github.com/einzeinn/saint/blob/main/docs/JudgeSetup.md

---

## Submission Description (full)

Everyone's building AI agents on top of data platforms. Most of them are glorified search boxes. SAINT is different.

**SAINT** (Structured Agentic Investigation with Navigational Transparency) is a CLI-first AI agent that helps data practitioners move from a vague goal to a structured, evidence-backed understanding — and writes the result back to DataHub so the knowledge doesn't disappear.

### The Problem

A data engineer wakes up to alerts. Revenue is down. The dashboard looks wrong. They open DataHub to look for answers — and find metadata. Lots of metadata. Lineage graphs, schema history, ownership records, data quality assertions. All the raw materials to understand what happened. But no agent to help them figure out what to look at first, or in what order, or what the right question even is.

Generic AI assistants make this worse. Without access to the real context graph — the actual schemas, the real lineage, the specific owners — they produce generic advice that sounds plausible and is often wrong.

### What SAINT Does

SAINT uses DataHub's **Agent Context Kit** (`datahub-agent-context`) to:

1. **Interpret** the user's goal and make its understanding explicit before taking action
2. **Read** the DataHub context graph (schemas, lineage, ownership, data quality, domains)
3. **Build** a `ContextualPath` — an ordered investigation structure grounded in real assets, not generic advice
4. **Guide** the user through each step with LLM reasoning backed by actual metadata
5. **Assess** hypotheses against DataHub evidence in `saint solve` mode
6. **Write back** — publish the investigation as a DataHub Document, linked to the relevant assets, so the next person or agent inherits the knowledge

The write-back step is what closes the loop. Context flows *in* from DataHub through the Agent Context Kit. Investigation findings flow *back* via `save_document`. The catalog grows more useful with every session.

### Technical Stack

- **DataHub Agent Context Kit** — primary integration layer; no MCP server required
- **DataHub Skills** — SAINT registers as a `saint_investigator` DataHub Skill entry-point
- **LLM** — Groq (llama-3.3-70b) or Gemini, hot-swappable via adapter protocol
- **Rich terminal UI** — full interactive and demo flows with structured preview before any write-back
- **Python 3.11+**, FastAPI compatibility surface, `pyproject.toml` with optional extras

### Key Design Decisions

- **Demo mode is deterministic.** `saint demo` uses built-in mock context and never auto-publishes. It shows exactly what *would* be written to DataHub — a simulated preview — without touching any live system. Run it 20 times, get the same result.
- **Write-back is opt-in.** Interactive mode (`saint solve`, `saint`) shows a publishing preview and requires double confirmation before writing to DataHub.
- **schemaField URNs are filtered.** DataHub's `document` aspect only accepts entity-level URNs in `relatedAssets`. SAINT filters sub-entity URNs before write-back to avoid 422 errors.

### Try It in 30 Seconds

```bash
pip install -e .
saint demo
```

No DataHub. No Docker. No API key. A complete investigation journey runs with built-in sample context.

### What Makes This Different

Most DataHub integrations are read-only. SAINT reads context *and writes knowledge back*. The investigation doesn't end at the terminal — it lives in the catalog, ready for the next engineer, the next agent, the next question.

> *"The agent didn't just answer the question. It figured out what I needed to understand and do next by navigating the context graph."*

---

## Technologies Used (checkboxes on Devpost form)

- DataHub Agent Context Kit
- DataHub Skills
- Python
- Groq LLaMA 3.3 70B
- Google Gemini
- Rich (terminal UI)
- FastAPI
- Pydantic

---

## Category

**Open / Wildcard** — SAINT is a novel application of DataHub's context graph as a *goal-driven navigation layer*. It reframes the catalog from a passive metadata store into an active reasoning environment: the agent uses DataHub to figure out what a person needs to understand and do next, then writes the result back so knowledge persists. This goes beyond standard "agents that do work" — it's a new interaction paradigm on top of DataHub's open-source stack (Agent Context Kit + DataHub Skills).
