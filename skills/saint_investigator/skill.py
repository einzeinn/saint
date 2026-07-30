"""Saint Investigator Skill - Core implementation."""

import asyncio
import sys
from typing import Any, Dict, List, Optional

# ======================================================================
# 1. DataHub SDK imports with graceful fallback
# ======================================================================
try:
    from datahub.sdk.main_client import DataHubClient
except ImportError:
    try:
        from datahub.sdk import DataHubClient
    except ImportError:
        DataHubClient = None
        print("Warning: DataHub SDK not installed. Install: pip install datahub-sdk")

try:
    from datahub_agent_context.context import DataHubContext
except ImportError:
    DataHubContext = None
    print("Warning: DataHub Agent Context Kit not installed. Install: pip install datahub-agent-context")

try:
    from datahub_agent_context.mcp_tools.search import search
except ImportError:
    search = None
    print("Warning: search tool not available.")

try:
    from datahub_agent_context.mcp_tools.entities import get_entities
except ImportError:
    get_entities = None
    print("Warning: get_entities tool not available.")

# ======================================================================
# 2. Prompt templates (imported from separate file)
# ======================================================================
from .prompt_templates import (
    INVESTIGATE_PROMPT,
    VALIDATE_HYPOTHESIS_PROMPT,
    SYNTHESIZE_OUTCOME_PROMPT,
)

# ======================================================================
# 3. Mock LLM Provider (fallback)
# ======================================================================
class MockLLMProvider:
    """Simple mock LLM for when no real provider is available."""
    provider_name = "mock"
    
    async def interpret_goal(self, request):
        # Avoid circular import by using dict
        return {
            "original_goal": request.goal if hasattr(request, 'goal') else str(request),
            "intent": "explore",
            "desired_outcome": f"Investigate: {request.goal if hasattr(request, 'goal') else request}",
            "required_actions": ["Gather evidence", "Analyze context", "Draw conclusion"],
            "confidence": 0.8,
        }
    
    async def explain_context(self, context):
        return f"Context for goal: {context.goal}. Evidence available: {len(context.evidence)} items."
    
    async def assess_response(self, context, user_response):
        return {
            "status": "partial",
            "understanding": f"User responded: {user_response}",
            "evidence_gap": ["Need more evidence"],
            "recommended_action": "gather_more_evidence",
        }
    
    async def synthesize_outcome(self, context):
        return f"Synthesis: Based on {len(context.entities)} entities and {len(context.steps)} steps, the investigation suggests further analysis is needed."


# ======================================================================
# 4. Skill-specific adapter (standalone, uses DataHub SDK)
# ======================================================================
class _DataHubSkillAdapter:
    """
    DataHub adapter for the SaintInvestigatorSkill.
    Bridges SaintOrchestrator to DataHub using the Agent Context Kit.
    """
    provider_name = "skill_adapter"

    def __init__(self, client: DataHubClient):
        if client is None:
            raise ValueError("DataHubClient is required")
        self._client = client
        self._context = DataHubContext(client) if DataHubContext else None

    async def status(self):
        from backend.app.domain import DataHubIntegrationStatus  # used for type only
        return DataHubIntegrationStatus(
            provider=self.provider_name,
            configured=True,
            reachable=self._context is not None,
            mode="skill",
            detail="Using DataHub Agent Context Kit inside Saint Investigator skill.",
        )

    async def discover_context(self, interpretation):
        """Discover entities using DataHub search."""
        from backend.app.domain import DataHubContextDiscovery, ContextEntity

        if self._context is None or search is None:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="unavailable",
                entities=[],
                notes=["DataHub Agent Context Kit not available."],
            )

        # Extract query from interpretation (dict or object)
        query = ""
        if isinstance(interpretation, dict):
            query = interpretation.get("original_goal", "")
        else:
            query = getattr(interpretation, "original_goal", "")

        if not query:
            query = str(interpretation)

        try:
            # Use DataHub search
            with self._context:
                result = search(query=query, num_results=10)
                entities = []
                for item in result.get("results", []):
                    entity = item.get("entity", {})
                    entities.append(ContextEntity(
                        urn=entity.get("urn", ""),
                        name=entity.get("name", "Unknown"),
                        entity_type=entity.get("type", "unknown"),
                        relevance="Found via DataHub search",
                        relationships=[],
                        metadata=entity.get("properties", {}),
                    ))
                return DataHubContextDiscovery(
                    provider=self.provider_name,
                    source="agent-context-skill",
                    entities=entities,
                    notes=[f"Discovered context for: {query}"],
                )
        except Exception as e:
            return DataHubContextDiscovery(
                provider=self.provider_name,
                source="skill-error",
                entities=[],
                notes=[f"Discovery failed: {str(e)}"],
            )

    async def get_lineage(self, urn: str) -> List[str]:
        """Get lineage using DataHub get_entities."""
        if self._context is None or get_entities is None:
            return []

        try:
            with self._context:
                details = get_entities(urns=[urn])
                relationships = []
                # Extract relationships from response
                for record in details.get("entities", []):
                    rels = record.get("relationships", [])
                    if rels:
                        relationships.extend([r.get("urn", "") for r in rels if r.get("urn")])
                return list(dict.fromkeys(relationships))
        except Exception:
            return []


# ======================================================================
# 5. Saint Investigator Skill - Main Class
# ======================================================================
class SaintInvestigatorSkill:
    """
    AI-powered data investigation skill for DataHub Agent Context Kit.
    
    This skill enables users to:
    - Investigate unexpected changes in dashboards or metrics
    - Validate hypotheses against real DataHub evidence
    - Get evidence-backed conclusions and recommendations
    
    Usage:
        skill = SaintInvestigatorSkill(client)
        result = skill.investigate("revenue dashboard changed")
    """

    def __init__(self, client: DataHubClient, llm_provider: Optional[Any] = None):
        """
        Initialize the Saint Investigator skill.
        
        Args:
            client: DataHubClient instance for accessing DataHub
            llm_provider: Optional LLM provider (Groq, Gemini, or Mock)
        """
        if client is None:
            raise ValueError("DataHubClient is required")
        self._client = client
        self._llm = llm_provider or self._default_llm()
        self._adapter = _DataHubSkillAdapter(client)

    def _default_llm(self) -> Any:
        """Return default LLM provider (Mock if none configured)."""
        # Try to import real providers from backend if available
        try:
            from backend.app.adapters.llm import build_llm_adapter
            from backend.app.config import Settings
            settings = Settings()
            return build_llm_adapter(settings)
        except ImportError:
            # Fallback to mock
            return MockLLMProvider()

    # ======================================================================
    # Public API Methods
    # ======================================================================

    def investigate(self, goal: str) -> Dict[str, Any]:
        """
        Investigate a data problem and return evidence-backed conclusion.
        
        Args:
            goal: The problem to investigate (e.g., "why revenue dashboard changed")
            
        Returns:
            dict with investigation results:
            {
                "interpretation": {...},
                "context": [...],
                "steps": [...],
                "synthesis": "Final conclusion...",
                "success": True
            }
        """
        try:
            # Import orchestrator here to avoid circular imports
            from backend.app.orchestration import SaintOrchestrator
            from backend.app.domain import GoalRequest, Intent

            orchestrator = SaintOrchestrator(self._llm, self._adapter)
            
            # Run async methods
            request = GoalRequest(goal=goal, intent=Intent.explore)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                interpretation = loop.run_until_complete(orchestrator.interpret_goal(request))
                path = loop.run_until_complete(orchestrator.generate_contextual_path(request))
                synthesis = loop.run_until_complete(orchestrator.synthesize_final_outcome(path))
            finally:
                loop.close()

            return {
                "interpretation": interpretation.model_dump() if hasattr(interpretation, 'model_dump') else interpretation,
                "context": [e.model_dump() if hasattr(e, 'model_dump') else e for e in path.context],
                "steps": [s.model_dump() if hasattr(s, 'model_dump') else s for s in path.steps],
                "synthesis": synthesis,
                "success": True,
            }
        except ImportError as e:
            # Fallback if backend is not available
            return self._fallback_investigate(goal)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def validate_hypothesis(self, goal: str, hypothesis: str) -> Dict[str, Any]:
        """
        Validate a user's hypothesis against DataHub evidence.
        
        Args:
            goal: The problem being investigated
            hypothesis: User's proposed cause (e.g., "pipeline was delayed")
            
        Returns:
            dict with validation results
        """
        try:
            from backend.app.orchestration import SaintOrchestrator
            from backend.app.domain import GoalRequest, Intent

            orchestrator = SaintOrchestrator(self._llm, self._adapter)
            
            request = GoalRequest(goal=goal, intent=Intent.act)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                path = loop.run_until_complete(orchestrator.generate_contextual_path(request))
                result = loop.run_until_complete(orchestrator.assess_user_response(path, 0, hypothesis))
            finally:
                loop.close()

            return {
                "status": result.status,
                "understanding": result.understanding,
                "evidence_gap": result.evidence_gap,
                "recommended_action": result.recommended_action,
                "success": True,
            }
        except ImportError:
            # Simple fallback
            return self._fallback_assess(hypothesis)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def synthesize(self, goal: str) -> str:
        """
        Synthesize a final outcome from all available evidence.
        
        Args:
            goal: The problem being investigated
            
        Returns:
            str: Evidence-backed conclusion
        """
        result = self.investigate(goal)
        return result.get("synthesis", "Unable to synthesize outcome.")

    # ======================================================================
    # Fallback Methods (used when backend is not available)
    # ======================================================================

    def _fallback_investigate(self, goal: str) -> Dict[str, Any]:
        """Fallback when backend is not available."""
        return {
            "interpretation": {
                "original_goal": goal,
                "intent": "explore",
                "desired_outcome": f"Investigate: {goal}",
            },
            "context": [],
            "steps": [
                {"title": "Install SAINT backend", "type": "error"},
                {"title": "Run 'pip install -e .' in SAINT project", "type": "error"},
            ],
            "synthesis": f"Cannot investigate '{goal}' because SAINT backend is not available. Please install the full SAINT project.",
            "success": False,
            "error": "Backend not available",
        }

    def _fallback_assess(self, hypothesis: str) -> Dict[str, Any]:
        """Fallback assessment when backend is not available."""
        if "pipeline" in hypothesis.lower() or "delay" in hypothesis.lower():
            return {
                "status": "partial",
                "understanding": "User identified a plausible cause",
                "evidence_gap": ["Need pipeline execution data"],
                "recommended_action": "check_pipeline_logs",
                "success": False,
                "error": "Backend not available",
            }
        return {
            "status": "needs_clarification",
            "understanding": "Hypothesis not yet supported by evidence",
            "evidence_gap": ["No direct evidence found"],
            "recommended_action": "gather_more_evidence",
            "success": False,
            "error": "Backend not available",
        }