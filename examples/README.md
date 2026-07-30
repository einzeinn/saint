# Saint — Example Outputs

This directory contains sample outputs from real SAINT investigation sessions.
They demonstrate the quality of artifacts that SAINT produces — without requiring
you to run a live DataHub instance.

---

## Contents

| File | Description |
|---|---|
| [`investigation_revenue_dashboard.md`](investigation_revenue_dashboard.md) | Published DataHub Document from a `saint solve` session on revenue dashboard drift |
| [`contextual_path_revenue.json`](contextual_path_revenue.json) | Raw `ContextualPath` JSON — the structured output that powers Saint's investigation |
| [`publish_preview.txt`](publish_preview.txt) | Terminal output from the publish preview step before write-back |

---

These examples are generated from a locally running DataHub instance seeded with the
bootstrap sample data pack. The session goal was:

> *"I want to understand why the revenue dashboard changed"*
