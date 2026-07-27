Tentu! Berikut README lengkap yang tidak kepotong:
# Saint Investigator Skill

**AI-powered data investigation for DataHub Agent Context Kit.**

Saint Investigator is a skill that enables AI-driven investigation of data issues directly within DataHub. It helps answer questions like:

- "Why did the revenue dashboard change?"
- "What caused this pipeline to fail?"
- "Is my hypothesis about the data issue correct?"
- "Who owns this dataset and what changed recently?"

---

## 🎯 Features

| Feature | Description |
| :--- | :--- |
| **Investigate** | Automatically discover context and evidence for any data problem |
| **Validate Hypotheses** | Test user hypotheses against real DataHub evidence (lineage, metadata, assertions) |
| **Synthesize Conclusions** | Get evidence-backed recommendations and next steps |
| **Trace Lineage** | Follow upstream/downstream dependencies to find root causes |
| **Quality Assertions** | Use DataHub quality signals (freshness, volume anomalies) as concrete evidence |
| **Multi-LLM Support** | Works with Groq, Gemini, or Mock provider |

---

## 📦 Installation

### Prerequisites

- Python 3.9+
- DataHub instance with GMS API access
- DataHub Agent Context Kit installed

### Install the Skill

The skill is included with the DataHub Agent Context Kit. To install:

```bash
pip install datahub-agent-context
```

### Optional: LLM Provider

For enhanced AI capabilities, set up one of these providers:

**Groq (recommended, fastest):**
```bash
export GROQ_API_KEY="your-groq-api-key"
export GROQ_MODEL="llama-3.1-8b-instant"
```

**Gemini:**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export LLM_MODEL="gemini-2.0-flash"
```

**Mock (no API key needed, limited intelligence):**
```
# No configuration needed - falls back automatically
```


## 🚀 Quick Start

```python
from datahub_agent_context.context import DataHubContext
from datahub.sdk.main_client import DataHubClient
from skills.saint_investigator import SaintInvestigatorSkill

# 1. Initialize DataHub client
client = DataHubClient(
    server="https://your-datahub-instance.com",
    token="your-personal-access-token"
)

# 2. Create the skill
skill = SaintInvestigatorSkill(client)

# 3. Investigate a problem
result = skill.investigate("revenue dashboard changed unexpectedly")

# 4. See the synthesis
print(result["synthesis"])
# Output: "The root cause of the revenue dashboard change is a delayed upstream pipeline..."

# 5. Validate a hypothesis
validation = skill.validate_hypothesis(
    goal="revenue dashboard changed unexpectedly",
    hypothesis="the daily pipeline was delayed due to network timeout"
)

print(f"Status: {validation['status']}")          # partial, confirmed, needs_clarification
print(f"Evidence gaps: {validation['evidence_gap']}")
print(f"Recommended action: {validation['recommended_action']}")
```

---

## 📖 API Reference

### `SaintInvestigatorSkill(client, llm_provider=None)`

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `client` | `DataHubClient` | DataHub SDK client instance |
| `llm_provider` | `Optional[Any]` | Custom LLM provider (defaults to auto-detection) |

---

### `.investigate(goal: str) -> dict`

Perform a full investigation of a data problem.

**Parameters:**
- `goal` (str): The problem to investigate (e.g., "why revenue dashboard changed")

**Returns:**
```python
{
    "interpretation": {...},      # Goal interpretation
    "context": [...],             # Discovered DataHub entities
    "steps": [...],               # Investigation path steps
    "synthesis": "Final conclusion...",
    "success": True
}
```

**Example:**
```python
result = skill.investigate("why is the sales pipeline failing?")
print(result["synthesis"])
```



### `.validate_hypothesis(goal: str, hypothesis: str) -> dict`

Validate a user's hypothesis against DataHub evidence.

**Parameters:**
- `goal` (str): The problem being investigated
- `hypothesis` (str): User's proposed cause (e.g., "pipeline was delayed")

**Returns:**
```python
{
    "status": "confirmed|partial|needs_clarification",
    "understanding": "What the user seems to understand",
    "evidence_gap": ["specific missing evidence 1", ...],
    "recommended_action": "next_step_to_take",
    "success": True
}
```

**Example:**
```python
validation = skill.validate_hypothesis(
    goal="revenue dashboard changed",
    hypothesis="the upstream dataset was updated late"
)
# Status: partial
# Evidence gaps: ["No pipeline execution logs found"]
# Recommended action: "inspect_recent_pipeline_runs"
```



### `.synthesize(goal: str) -> str`

Quick synthesis of a final outcome without full investigation steps.

**Parameters:**
- `goal` (str): The problem being investigated

**Returns:**
- `str`: Evidence-backed conclusion

**Example:**
```python
conclusion = skill.synthesize("why did the revenue drop 20%?")
# "Based on DataHub evidence, the drop is due to a freshness failure..."
```



## 🧪 Example Workflow

Here's a complete example of investigating a revenue dashboard issue:

```python
from datahub.sdk.main_client import DataHubClient
from datahub_agent_context.context import DataHubContext
from skills.saint_investigator import SaintInvestigatorSkill

# Setup
client = DataHubClient(server="https://datahub.company.com")
skill = SaintInvestigatorSkill(client)

# Step 1: Investigate
result = skill.investigate("revenue dashboard changed unexpectedly")

print("=== INVESTIGATION SUMMARY ===")
print(result["synthesis"])
print("\n=== EVIDENCE FOUND ===")
for entity in result["context"]:
    print(f"- {entity['name']} ({entity['entity_type']})")
    for key, value in entity.get('metadata', {}).items():
        if 'assertion' in key or 'freshness' in key or 'anomaly' in key:
            print(f"  ⚠️ {key}: {value}")

# Step 2: Validate hypothesis
hypothesis = "the daily pipeline was delayed due to network issues"
validation = skill.validate_hypothesis(
    goal="revenue dashboard changed unexpectedly",
    hypothesis=hypothesis
)

print("\n=== HYPOTHESIS VALIDATION ===")
print(f"Status: {validation['status']}")
if validation['evidence_gap']:
    print("Evidence gaps:")
    for gap in validation['evidence_gap']:
        print(f"  - {gap}")
print(f"Recommended: {validation['recommended_action']}")

# Step 3: Get final recommendation
conclusion = skill.synthesize("revenue dashboard changed unexpectedly")
print("\n=== FINAL RECOMMENDATION ===")
print(conclusion)
```



## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATAHUB_GMS_URL` | DataHub GMS endpoint URL | Required |
| `DATAHUB_GMS_TOKEN` | Personal Access Token | Required |
| `GROQ_API_KEY` | Groq API key for LLM | Optional |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `LLM_MODEL` | LLM model name | `gemini-2.0-flash` |
| `LLM_PROVIDER` | Force specific provider | Auto-detected |

### Skill-Specific Settings

The skill automatically uses:
- **DataHub**: Connected via `DataHubClient`
- **LLM**: Groq > Gemini > Mock (fallback)
- **Context**: Search + Entity details + Lineage (3 levels deep)



## 🎨 Advanced Usage

### Custom LLM Provider

```python
from your_custom_llm import CustomLLM

custom_llm = CustomLLM(api_key="xxx")
skill = SaintInvestigatorSkill(client, llm_provider=custom_llm)
```

### Batch Investigations

```python
goals = [
    "revenue dashboard changed",
    "sales pipeline is slow",
    "customer churn model accuracy dropped"
]

for goal in goals:
    result = skill.investigate(goal)
    print(f"{goal}: {result['synthesis'][:100]}...")
```

### Export Results

```python
import json

result = skill.investigate("revenue dashboard changed")
with open("investigation_result.json", "w") as f:
    json.dump(result, f, indent=2)
```


## 🧩 Integration with Existing Workflows

### Jupyter Notebook

```python
# In a Jupyter notebook
from datahub_agent_context.context import DataHubContext
from skills.saint_investigator import SaintInvestigatorSkill

# Setup once
skill = SaintInvestigatorSkill(client)

# Quick investigation in a notebook cell
result = skill.investigate("why did the KPI change?")
display(result["synthesis"])
```

### CI/CD Pipeline

```python
# In your deployment pipeline
import sys

def validate_data_health():
    result = skill.investigate("data quality check before deployment")
    if "FAILING" in result["synthesis"]:
        print("❌ Data quality issues detected!")
        sys.exit(1)
    print("✅ Data health check passed")
```

### Slack Bot Integration

```python
# Slack bot handler
def handle_investigation_command(goal):
    result = skill.investigate(goal)
    return {
        "text": f"🔍 *Investigation Result*\n{result['synthesis']}",
        "blocks": [...]
    }
```


## 📊 Performance & Limitations

| Aspect | Details |
| :--- | :--- |
| **Search Depth** | Up to 10 entities per search |
| **Lineage Depth** | 3 levels (upstream/downstream) |
| **LLM Latency** | ~2-5s (Groq), ~5-15s (Gemini) |
| **Caching** | Results cached per session |
| **Rate Limits** | Respects DataHub GMS limits |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report bugs**: Open an issue on GitHub
2. **Suggest features**: Start a discussion
3. **Submit code**: Fork the repo and open a PR
4. **Improve docs**: Update README or add examples

### Development Setup

```bash
git clone https://github.com/datahub-project/datahub-agent-context
cd datahub-agent-context
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/skills/saint_investigator/

# Lint
ruff check skills/saint_investigator/
```

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with `black`
- [ ] Type hints are complete
- [ ] Documentation is updated
- [ ] No breaking changes (if any, justify)

---

## 🌟 Open Source Contribution

Saint Investigator Skill for DataHub Agent Context Kit

We've packaged Saint's core investigation capabilities as a reusable skill for the DataHub Agent Context Kit. This means any DataHub user can now:
- Run AI-powered investigations on their data assets
- Validate hypotheses against real DataHub evidence
- Get evidence-backed conclusions and recommendations

**Skill Location:** `skills/saint_investigator/`

**PR Link:** 
## 📝 License

Apache 2.0 — See [LICENSE](https://github.com/datahub-project/datahub-agent-context/blob/main/LICENSE) for details.

---

## 🙏 Acknowledgments

- Built on top of **DataHub Agent Context Kit**
- Powered by **Groq** and **Gemini** LLMs
- Inspired by real-world data investigation challenges

---

## 📬 Support

- **GitHub Issues**: [datahub-agent-context/issues](https://github.com/datahub-project/datahub-agent-context/issues)
- **DataHub Slack**: [#agent-context](https://slack.datahubproject.io/)
- **Email**: datahub@example.com

---

**Made with ❤️ for the DataHub community**