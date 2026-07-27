"""Saint Investigator Skill for DataHub Agent Context Kit.

This skill provides AI-powered data investigation capabilities:
- Investigate why a dashboard or metric changed
- Validate hypotheses against DataHub evidence
- Synthesize final conclusions from lineage and metadata
"""

from .skill import SaintInvestigatorSkill

__all__ = ["SaintInvestigatorSkill"]