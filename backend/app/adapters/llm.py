import json
from typing import Any, Protocol

import httpx
import logging
 
logger = logging.getLogger("saint.llm")

from backend.app.config import Settings
from backend.app.domain import (
    AssessmentContext,
    AssessmentResult,
    ContextPackage,
    GoalInterpretation,
    GoalRequest,
    Intent,
    SynthesisContext,      # NEW
    SynthesisResult,       # NEW (opsional, tapi kita pakai return string saja)
)


class LLMAdapter(Protocol):
    provider_name: str

    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        """Convert a user goal into a structured interpretation."""

    async def explain_context(self, context: ContextPackage) -> str:
        """Explain structured context in natural language."""

    async def assess_response(self, context: AssessmentContext, user_response: str) -> AssessmentResult:
        """Assess a user reply against the current evidence context."""

    # NEW: Synthesize final outcome from all evidence collected along the path
    async def synthesize_outcome(self, context: SynthesisContext) -> str:
        """Synthesize a final, evidence-backed outcome statement."""


class MockLLMAdapter:
    provider_name = "mock"

    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        goal = request.goal.strip()
        intent = request.intent

        if intent == Intent.unsure:
            intent = self._infer_intent(goal)

        actions = self._actions_for(goal, intent)
        target = self._target_for(goal, intent)

        return GoalInterpretation(
            original_goal=goal,
            original_input=goal,
            intent=intent,
            desired_outcome=self._outcome_for(goal, intent),
            required_actions=actions,
            target=target,
            required_evidence=self._evidence_for(goal, intent),
            confidence=0.82,
            required_capabilities=[
                "Understand relevant DataHub entities",
                "Follow relationships between context assets",
                "Decide the next step from evidence",
            ],
            constraints=["User confirmation required before context discovery"],
        )

    async def explain_context(self, context: ContextPackage) -> str:
        def sentence(text: str) -> str:
            text = text.strip()
            return text if text.endswith((".", "!", "?")) else f"{text}."

        pieces = [sentence(f"The current goal is {context.goal.rstrip('.')}")]
        if context.current_entity:
            pieces.append(sentence(f"The active entity is {context.current_entity.rstrip('.')}"))
        if context.evidence:
            joined = ", ".join(item.rstrip(".") for item in context.evidence)
            pieces.append(sentence(f"Evidence includes {joined}"))
        if context.relationships:
            joined = ", ".join(item.rstrip(".") for item in context.relationships)
            pieces.append(sentence(f"Related assets include {joined}"))
        if context.next_action:
            pieces.append(sentence(f"The suggested next action is {context.next_action.rstrip('.')}"))
        return " ".join(pieces)

    async def assess_response(self, context: AssessmentContext, user_response: str) -> AssessmentResult:
        normalized = user_response.lower()
        if any(word in normalized for word in ["because", "due", "caused", "pipeline", "delay", "change"]):
            return AssessmentResult(
                status="partial",
                understanding="The user identified a plausible cause but did not confirm it against evidence.",
                evidence_gap=["No verified evidence was cited yet."],
                recommended_action="inspect_recent_upstream_activity",
            )
        return AssessmentResult(
            status="needs_clarification",
            understanding="The user response did not yet point to evidence-backed reasoning.",
            evidence_gap=["The response lacks confirmed facts or a concrete evidence reference."],
            recommended_action="clarify_the_observed_change",
        )

    # NEW: Mock implementation for synthesis
    async def synthesize_outcome(self, context: SynthesisContext) -> str:
        # Build a simple summary from available evidence
        evidence_list = []
        for entity in context.entities:
            for key, value in entity.metadata.items():
                if value:
                    evidence_list.append(f"{key}: {value}")
        evidence_text = ", ".join(evidence_list) if evidence_list else "no specific evidence discovered"
        step_titles = [step.title for step in context.steps]
        steps_text = ", ".join(step_titles)
        return (
            f"Based on the gathered evidence ({evidence_text}), the goal '{context.goal}' "
            f"can be addressed by following these steps: {steps_text}. "
            "It is recommended to verify recent upstream changes and check freshness metadata "
            "to confirm the root cause."
        )

    def _infer_intent(self, goal: str) -> Intent:
        normalized = goal.lower()
        if any(word in normalized for word in ["why", "investigate", "explore"]):
            return Intent.explore
        if any(word in normalized for word in ["find", "choose", "complete", "fix"]):
            return Intent.act
        if any(word in normalized for word in ["learn", "understand"]):
            return Intent.learn
        return Intent.explore

    def _actions_for(self, goal: str, intent: Intent) -> list[str]:
        normalized = goal.lower()
        if "revenue" in normalized or "dashboard" in normalized:
            return [
                "Identify the affected dashboard",
                "Find the underlying data assets",
                "Trace upstream lineage",
                "Check freshness and quality signals",
                "Investigate recent upstream changes",
            ]

        if intent == Intent.learn:
            return [
                "Identify the concept or context to understand",
                "Find relevant DataHub entities",
                "Explore relationships",
                "Connect the concept to a practical task",
            ]

        if intent == Intent.act:
            return [
                "Clarify the concrete outcome",
                "Find candidate data assets",
                "Evaluate metadata, ownership, quality, and lineage",
                "Make a supported decision",
            ]

        return [
            "Clarify the question",
            "Find relevant context",
            "Inspect relationships and evidence",
            "Summarize the most likely explanation",
        ]

    def _target_for(self, goal: str, intent: Intent) -> str:
        if intent == Intent.act:
            return "actionable outcome"
        if intent == Intent.learn:
            return "understanding"
        if "dashboard" in goal.lower() or "revenue" in goal.lower():
            return "dashboard change"
        return "context"

    def _evidence_for(self, goal: str, intent: Intent) -> list[str]:
        if "dashboard" in goal.lower() or "revenue" in goal.lower():
            return ["dashboard", "underlying_dataset", "upstream_pipeline", "recent_changes"]
        if intent == Intent.act:
            return ["candidate_entity", "metadata", "lineage"]
        return ["context", "relationships", "evidence"]

    def _outcome_for(self, goal: str, intent: Intent) -> str:
        if intent == Intent.learn:
            return f"Build practical understanding needed to: {goal}"
        if intent == Intent.act:
            return f"Complete the task with relevant DataHub context: {goal}"
        return f"Reach an evidence-backed explanation for: {goal}"


class StructuredLLMAdapter:
    provider_name = "mock"
 
    def __init__(self, provider: LLMAdapter, fallback: LLMAdapter | None = None) -> None:
        self._provider = provider
        self._fallback = fallback or MockLLMAdapter()
        self.provider_name = getattr(provider, "provider_name", "mock")
 
    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        try:
            result = await self._provider.interpret_goal(request)
            return self._coerce_goal_interpretation(result, request)
        except Exception as exc:
            logger.warning(
                "LLM provider '%s' failed on interpret_goal (%s); falling back to '%s'",
                self.provider_name,
                exc,
                getattr(self._fallback, "provider_name", "mock"),
            )
            return await self._fallback.interpret_goal(request)
 
    async def explain_context(self, context: ContextPackage) -> str:
        try:
            result = await self._provider.explain_context(context)
            if isinstance(result, str) and result.strip():
                return result
            raise ValueError("provider returned an invalid explanation")
        except Exception as exc:
            logger.warning(
                "LLM provider '%s' failed on explain_context (%s); falling back to '%s'",
                self.provider_name,
                exc,
                getattr(self._fallback, "provider_name", "mock"),
            )
            return await self._fallback.explain_context(context)
 
    async def assess_response(self, context: AssessmentContext, user_response: str) -> AssessmentResult:
        try:
            result = await self._provider.assess_response(context, user_response)
            return self._coerce_assessment_result(result)
        except Exception as exc:
            logger.warning(
                "LLM provider '%s' failed on assess_response (%s); falling back to '%s'",
                self.provider_name,
                exc,
                getattr(self._fallback, "provider_name", "mock"),
            )
            return await self._fallback.assess_response(context, user_response)

    # NEW: synthesize_outcome with fallback
    async def synthesize_outcome(self, context: SynthesisContext) -> str:
        try:
            result = await self._provider.synthesize_outcome(context)
            if isinstance(result, str) and result.strip():
                return result
            raise ValueError("provider returned an invalid synthesis")
        except Exception as exc:
            logger.warning(
                "LLM provider '%s' failed on synthesize_outcome (%s); falling back to '%s'",
                self.provider_name,
                exc,
                getattr(self._fallback, "provider_name", "mock"),
            )
            return await self._fallback.synthesize_outcome(context)

    @staticmethod
    def _coerce_goal_interpretation(value: Any, request: GoalRequest) -> GoalInterpretation:
        if isinstance(value, GoalInterpretation):
            return value
        if not isinstance(value, dict):
            raise ValueError("Provider returned an invalid goal interpretation")

        payload = dict(value)
        intent_value = payload.get("intent") or request.intent
        if isinstance(intent_value, str):
            try:
                intent = Intent(intent_value)
            except ValueError:
                raise ValueError("Provider returned an invalid intent")
        elif isinstance(intent_value, Intent):
            intent = intent_value
        else:
            raise ValueError("Provider returned an invalid intent")

        desired_outcome = str(payload.get("desired_outcome") or payload.get("target") or "").strip()
        required_actions = payload.get("required_actions")
        if not isinstance(required_actions, list) or not required_actions:
            raise ValueError("Provider did not return any required actions")

        return GoalInterpretation(
            original_goal=str(payload.get("original_goal") or payload.get("original_input") or request.goal),
            original_input=str(payload.get("original_input") or payload.get("original_goal") or request.goal),
            intent=intent,
            desired_outcome=desired_outcome or request.goal,
            required_actions=[str(action) for action in required_actions],
            required_capabilities=[str(item) for item in (payload.get("required_capabilities") or [])],
            constraints=[str(item) for item in (payload.get("constraints") or [])],
            target=str(payload.get("target") or "") or None,
            required_evidence=[str(item) for item in (payload.get("required_evidence") or [])],
            confidence=float(payload.get("confidence", 0.75) or 0.75),
        )

    @staticmethod
    def _coerce_assessment_result(value: Any) -> AssessmentResult:
        if isinstance(value, AssessmentResult):
            return value
        if isinstance(value, dict):
            payload = dict(value)
            status = str(payload.get("status") or "").strip()
            understanding = str(payload.get("understanding") or "").strip()
            if not status or not understanding:
                raise ValueError("Provider returned an invalid assessment result")
            return AssessmentResult.model_validate(payload)
        if isinstance(value, str):
            return AssessmentResult(status="partial", understanding=value)
        raise ValueError("Provider returned an invalid assessment result")


class GeminiProvider:
    provider_name = "gemini"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._api_key = settings.gemini_api_key.strip()
        self._model = settings.llm_model or "gemini-2.0-flash"
        self._base_url = (settings.llm_base_url or "https://generativelanguage.googleapis.com/v1beta/models").rstrip("/")
        self._timeout = 15.0
        self._transport = transport

    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        prompt = self._build_goal_prompt(request)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                f"{self._base_url}/{self._model}:generateContent",
                params={"key": self._api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)
        return self._parse_goal_json(text, request)

    async def explain_context(self, context: ContextPackage) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        payload = {
            "contents": [{"parts": [{"text": self._build_context_prompt(context)}]}],
            "generationConfig": {"responseMimeType": "text/plain"},
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                f"{self._base_url}/{self._model}:generateContent",
                params={"key": self._api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    async def assess_response(self, context: AssessmentContext, user_response: str) -> AssessmentResult:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        payload = {
            "contents": [{"parts": [{"text": self._build_assessment_prompt(context, user_response)}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                f"{self._base_url}/{self._model}:generateContent",
                params={"key": self._api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)
        return self._parse_assessment_json(text)

    # NEW: synthesize_outcome for Gemini
    async def synthesize_outcome(self, context: SynthesisContext) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        prompt = self._build_synthesis_prompt(context)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "text/plain"},
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                f"{self._base_url}/{self._model}:generateContent",
                params={"key": self._api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    @staticmethod
    def _build_goal_prompt(request: GoalRequest) -> str:
        return (
            "You are Saint's goal-interpretation layer. Read the user's natural-language "
            "goal and return ONLY a JSON object (no prose, no markdown fences) matching "
            "this exact shape:\n\n"
            '{\n'
            '  "original_input": "<the user goal, verbatim>",\n'
            '  "intent": "<one of: learn, explore, act>",\n'
            '  "target": "<the specific thing the user cares about, e.g. a dashboard, '
            'dataset, or pipeline name mentioned or implied in the goal>",\n'
            '  "desired_outcome": "<a one-sentence outcome specific to THIS goal, '
            'not a generic phrase>",\n'
            '  "required_actions": ["<3-5 concrete steps specific to this goal>"],\n'
            '  "required_evidence": ["<specific evidence types needed, e.g. '
            '\'upstream pipeline logs\', \'freshness metadata\'>"],\n'
            '  "confidence": <float 0-1>\n'
            '}\n\n'
            f'User goal: "{request.goal}"\n'
            f'User-selected intent (may be "unsure"): "{request.intent.value}"\n\n'
            "Base your interpretation on the actual wording and subject of the goal above. "
            "Do not reuse example values from this prompt in your answer."
        )

    @staticmethod
    def _build_context_prompt(context: "ContextPackage | dict") -> str:
        if isinstance(context, dict):
            context = ContextPackage(**context)
        return (
            "You are Saint's context-explanation layer. Below is structured context "
            "that Saint's core has already discovered from DataHub. Explain it to the "
            "user in 2-4 plain-English sentences. Do not invent facts that are not in "
            "the data below. Do not add a preamble like 'Here is the explanation' — "
            "just write the explanation directly.\n\n"
            f"Goal: {context.goal}\n"
            f"Current entity: {context.current_entity or 'none'}\n"
            f"Evidence: {', '.join(context.evidence) if context.evidence else 'none'}\n"
            f"Related assets: {', '.join(context.relationships) if context.relationships else 'none'}\n"
            f"Suggested next action: {context.next_action or 'none'}\n"
        )

    @staticmethod
    def _build_assessment_prompt(context: "AssessmentContext | dict", user_response: str) -> str:
        if isinstance(context, dict):
            context = AssessmentContext(**context)
        return (
            "You are Saint's response-assessment layer. The user was given a goal and "
            "some evidence, then asked a question. Assess whether their reply shows "
            "evidence-backed understanding, a partial guess, or needs clarification. "
            "Return ONLY a JSON object (no prose, no markdown fences) matching this "
            "exact shape:\n\n"
            '{\n'
            '  "status": "<one of: understood, partial, needs_clarification>",\n'
            '  "understanding": "<one sentence describing what the user seems to '
            'understand, based on THEIR actual wording>",\n'
            '  "evidence_gap": ["<specific missing evidence, if any>"],\n'
            '  "recommended_action": "<a concrete next step, snake_case-style label '
            'or short phrase>"\n'
            '}\n\n'
            f"Goal: {context.goal}\n"
            f"Current step: {context.current_step}\n"
            f"Evidence available: {', '.join(context.evidence) if context.evidence else 'none'}\n"
            f'User response: "{user_response}"\n'
        )

    # NEW: Synthesis prompt
    @staticmethod
    def _build_synthesis_prompt(context: SynthesisContext) -> str:
        steps_summary = "\n".join(
            f"- {step.title}: {step.purpose}" for step in context.steps
        )
        entities_summary = "\n".join(
            f"- {entity.name} ({entity.entity_type}): relevance={entity.relevance}, metadata={entity.metadata}"
            for entity in context.entities
        )
        notes = "\n".join(f"- {note}" for note in context.context_notes) if context.context_notes else "None"
        return (
            "You are Saint's synthesis layer. You have been given a goal and a path of steps with evidence "
            "collected from DataHub. Synthesize a final, evidence-backed outcome that directly answers the user's "
            "original goal. Write 2-4 plain-English sentences that summarize the key findings, the most relevant "
            "evidence, and a recommended next action or conclusion. Do not add a preamble like 'Here is the synthesis' — "
            "just write the outcome directly.\n\n"
            f"Goal: {context.goal}\n\n"
            "Steps taken:\n"
            f"{steps_summary}\n\n"
            "Entities discovered:\n"
            f"{entities_summary}\n\n"
            "Additional notes:\n"
            f"{notes}\n\n"
            "Based on all this, what is the final outcome?"
        )

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini response did not contain any candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("Gemini response did not contain any content parts")
        return str(parts[0].get("text", ""))

    @staticmethod
    def _parse_goal_json(text: str, request: GoalRequest) -> GoalInterpretation:
        payload = json.loads(text)
        return GoalInterpretation(
            original_goal=str(payload.get("original_input") or request.goal),
            original_input=str(payload.get("original_input") or request.goal),
            intent=Intent(payload.get("intent", request.intent.value)),
            desired_outcome=str(payload.get("desired_outcome") or "evidence-backed explanation"),
            required_actions=list(payload.get("required_actions") or ["Inspect the relevant context"]),
            required_evidence=list(payload.get("required_evidence") or []),
            confidence=float(payload.get("confidence", 0.75) or 0.75),
        )

    @staticmethod
    def _parse_assessment_json(text: str) -> AssessmentResult:
        payload = json.loads(text)
        return AssessmentResult(
            status=str(payload.get("status") or "partial"),
            understanding=str(payload.get("understanding") or ""),
            evidence_gap=list(payload.get("evidence_gap") or []),
            recommended_action=str(payload.get("recommended_action") or "") or None,
        )


class GroqProvider:
    provider_name = "groq"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._api_key = settings.groq_api_key.strip()
        self._model = settings.groq_model or "llama-3.1-8b-instant"
        self._base_url = (settings.groq_base_url or settings.llm_base_url or "https://api.groq.com/openai/v1/chat/completions").rstrip("/")
        self._timeout = 15.0
        self._transport = transport

    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        prompt = self._build_goal_prompt(request)
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)
        return self._parse_goal_json(text, request)

    async def explain_context(self, context: ContextPackage) -> str:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": self._build_context_prompt(context)}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    async def assess_response(self, context: AssessmentContext, user_response: str) -> AssessmentResult:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": self._build_assessment_prompt(context, user_response)}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)
        return self._parse_assessment_json(text)

    # NEW: synthesize_outcome for Groq
    async def synthesize_outcome(self, context: SynthesisContext) -> str:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": self._build_synthesis_prompt(context)}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    @staticmethod
    def _build_goal_prompt(request: GoalRequest) -> str:
        return (
            "You are Saint's goal-interpretation layer. Read the user's natural-language "
            "goal and return ONLY a JSON object (no prose, no markdown fences) matching "
            "this exact shape:\n\n"
            '{\n'
            '  "original_input": "<the user goal, verbatim>",\n'
            '  "intent": "<one of: learn, explore, act>",\n'
            '  "target": "<the specific thing the user cares about, e.g. a dashboard, '
            'dataset, or pipeline name mentioned or implied in the goal>",\n'
            '  "desired_outcome": "<a one-sentence outcome specific to THIS goal, '
            'not a generic phrase>",\n'
            '  "required_actions": ["<3-5 concrete steps specific to this goal>"],\n'
            '  "required_evidence": ["<specific evidence types needed, e.g. '
            '\'upstream pipeline logs\', \'freshness metadata\'>"],\n'
            '  "confidence": <float 0-1>\n'
            '}\n\n'
            f'User goal: "{request.goal}"\n'
            f'User-selected intent (may be "unsure"): "{request.intent.value}"\n\n'
            "Base your interpretation on the actual wording and subject of the goal above. "
            "Do not reuse example values from this prompt in your answer."
        )

    @staticmethod
    def _build_context_prompt(context: "ContextPackage | dict") -> str:
        if isinstance(context, dict):
            context = ContextPackage(**context)
        return (
            "You are Saint's context-explanation layer. Below is structured context "
            "that Saint's core has already discovered from DataHub. Explain it to the "
            "user in 2-4 plain-English sentences. Do not invent facts that are not in "
            "the data below. Do not add a preamble like 'Here is the explanation' — "
            "just write the explanation directly.\n\n"
            f"Goal: {context.goal}\n"
            f"Current entity: {context.current_entity or 'none'}\n"
            f"Evidence: {', '.join(context.evidence) if context.evidence else 'none'}\n"
            f"Related assets: {', '.join(context.relationships) if context.relationships else 'none'}\n"
            f"Suggested next action: {context.next_action or 'none'}\n"
        )


    @staticmethod
    def _build_assessment_prompt(context: "AssessmentContext | dict", user_response: str) -> str:
        if isinstance(context, dict):
            context = AssessmentContext(**context)
        return (
            "You are Saint's response-assessment layer. The user was given a goal and "
            "some evidence, then asked a question. Assess whether their reply shows "
            "evidence-backed understanding, a partial guess, or needs clarification. "
            "Return ONLY a JSON object (no prose, no markdown fences) matching this "
            "exact shape:\n\n"
            '{\n'
            '  "status": "<one of: understood, partial, needs_clarification>",\n'
            '  "understanding": "<one sentence describing what the user seems to '
            'understand, based on THEIR actual wording>",\n'
            '  "evidence_gap": ["<specific missing evidence, if any>"],\n'
            '  "recommended_action": "<a concrete next step, snake_case-style label '
            'or short phrase>"\n'
            '}\n\n'
            f"Goal: {context.goal}\n"
            f"Current step: {context.current_step}\n"
            f"Evidence available: {', '.join(context.evidence) if context.evidence else 'none'}\n"
            f'User response: "{user_response}"\n'
        )

    # NEW: Synthesis prompt (same as Gemini)
    @staticmethod
    def _build_synthesis_prompt(context: SynthesisContext) -> str:
        steps_summary = "\n".join(
            f"- {step.title}: {step.purpose}" for step in context.steps
        )
        entities_summary = "\n".join(
            f"- {entity.name} ({entity.entity_type}): relevance={entity.relevance}, metadata={entity.metadata}"
            for entity in context.entities
        )
        notes = "\n".join(f"- {note}" for note in context.context_notes) if context.context_notes else "None"
        return (
            "You are Saint's synthesis layer. You have been given a goal and a path of steps with evidence "
            "collected from DataHub. Synthesize a final, evidence-backed outcome that directly answers the user's "
            "original goal. Write 2-4 plain-English sentences that summarize the key findings, the most relevant "
            "evidence, and a recommended next action or conclusion. Do not add a preamble like 'Here is the synthesis' — "
            "just write the outcome directly.\n\n"
            f"Goal: {context.goal}\n\n"
            "Steps taken:\n"
            f"{steps_summary}\n\n"
            "Entities discovered:\n"
            f"{entities_summary}\n\n"
            "Additional notes:\n"
            f"{notes}\n\n"
            "Based on all this, what is the final outcome?"
        )

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("Groq response did not contain any choices")
        message = choices[0].get("message", {})
        return str(message.get("content", ""))

    @staticmethod
    def _parse_goal_json(text: str, request: GoalRequest) -> GoalInterpretation:
        payload = json.loads(text)
        return GoalInterpretation(
            original_goal=str(payload.get("original_input") or request.goal),
            original_input=str(payload.get("original_input") or request.goal),
            intent=Intent(payload.get("intent", request.intent.value)),
            desired_outcome=str(payload.get("desired_outcome") or "evidence-backed explanation"),
            required_actions=list(payload.get("required_actions") or ["Inspect the relevant context"]),
            required_evidence=list(payload.get("required_evidence") or []),
            confidence=float(payload.get("confidence", 0.75) or 0.75),
        )

    @staticmethod
    def _parse_assessment_json(text: str) -> AssessmentResult:
        payload = json.loads(text)
        return AssessmentResult(
            status=str(payload.get("status") or "partial"),
            understanding=str(payload.get("understanding") or ""),
            evidence_gap=list(payload.get("evidence_gap") or []),
            recommended_action=str(payload.get("recommended_action") or "") or None,
        )


def build_llm_adapter(settings: Settings) -> LLMAdapter:
    has_groq = bool(settings.groq_api_key.strip())
    has_gemini = bool(settings.gemini_api_key.strip())
 
    # Innermost fallback is always Mock, so the app never crashes even if
    # both real providers are unavailable.
    gemini_layer: LLMAdapter = (
        StructuredLLMAdapter(provider=GeminiProvider(settings), fallback=MockLLMAdapter())
        if has_gemini
        else MockLLMAdapter()
    )
 
    if has_groq:
        # Groq is primary; if it fails, fall through to the Gemini layer
        # (which itself falls through to Mock if Gemini also fails).
        return StructuredLLMAdapter(provider=GroqProvider(settings), fallback=gemini_layer)
 
    if has_gemini:
        return gemini_layer
 
    return StructuredLLMAdapter(provider=MockLLMAdapter(), fallback=MockLLMAdapter())