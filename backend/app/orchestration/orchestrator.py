from backend.app.adapters.datahub import DataHubAdapter
from backend.app.adapters.llm import LLMAdapter
from backend.app.domain import (
    AssessmentContext,
    AssessmentResult,
    ContextPackage,
    ContextualPath,
    GoalInterpretation,
    GoalRequest,
    Intent,
    PathAssessment,
    PathStep,
    SynthesisContext,   # NEW
)


class SaintOrchestrator:
    def __init__(self, llm: LLMAdapter, datahub: DataHubAdapter) -> None:
        self._llm = llm
        self._datahub = datahub

    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        return await self._llm.interpret_goal(request)

    async def generate_contextual_path(self, request: GoalRequest) -> ContextualPath:
        interpretation = await self.interpret_goal(request)
        discovery = await self._datahub.discover_context(interpretation)
        context = discovery.entities

        context_refs = [entity.urn for entity in context]
        steps = [
            PathStep(
                title="Confirm goal interpretation",
                mode=interpretation.intent,
                purpose="Make Saint's assumptions visible before deeper execution.",
                user_action="Review the desired outcome and required actions.",
                context_refs=[],
                step_type="confirmation",
            ),
        ]

        if context:
            for entity in context[:5]:
                # NEW: Get real lineage from DataHub
                lineage = await self._datahub.get_lineage(entity.urn)
                if lineage:
                    entity.relationships = list(dict.fromkeys(entity.relationships + lineage))
                
                metadata_hint = self._metadata_hint(entity.metadata)
                steps.append(
                    PathStep(
                        title=f"Review {entity.name}",
                        mode=Intent.explore,
                        purpose=(
                            f"Use this {entity.entity_type} as evidence: {entity.relevance}"
                            f"{metadata_hint}"
                        ),
                        user_action=f"Review the metadata and relevance of {entity.name}.",
                        context_refs=[entity.urn],
                        step_type="context",
                    )
                )
                if entity.relationships:
                    steps.append(
                        PathStep(
                            title=f"Trace relationships from {entity.name}",
                            mode=Intent.explore,
                            purpose="Connect this asset to related upstream or downstream context.",
                            user_action="Compare the selected asset with its related DataHub assets.",
                            context_refs=[entity.urn, *entity.relationships],
                            step_type="relationship",
                        )
                    )
        else:
            steps.append(
                PathStep(
                    title="Inspect relevant DataHub context",
                    mode=Intent.explore,
                    purpose="Use discovered context instead of generic guidance.",
                    user_action="Review the entities and relationships Saint found.",
                    context_refs=[],
                    step_type="context",
                )
            )

        steps.append(
            PathStep(
                title="Choose the next evidence-backed action",
                mode=interpretation.intent,
                purpose=f"Move from the discovered context toward: {interpretation.desired_outcome}.",
                user_action="Select the next step based on the visible evidence and relationships.",
                context_refs=context_refs[:1],
                step_type="action",
            )
        )
        

        return ContextualPath(
            interpretation=interpretation,
            context=context,
            steps=steps,
            outcome=interpretation.desired_outcome,
            context_source=discovery.source,
            context_notes=discovery.notes,
            synthesis=None,   # NEW: initial empty
        )

    @staticmethod
    def _metadata_hint(metadata: dict) -> str:
        priority_keys = ("owner", "freshness", "quality", "domain", "assertion_status")
        relevant = [
            f"{key}: {value}"
            for key in priority_keys
            if (value := metadata.get(key)) not in (None, "")
        ]
        extra = [
            f"{key}: {value}"
            for key, value in metadata.items()
            if key not in priority_keys and value not in (None, "") and ("quality" in key.lower() or "assertion" in key.lower() or "anomaly" in key.lower())
        ]
        relevant.extend(extra)
        return f" Metadata evidence: {', '.join(relevant)}." if relevant else ""

    async def datahub_status(self):
        return await self._datahub.status()

    async def feedback_for_step(self, path: ContextualPath, step_index: int) -> str:
        step = path.steps[step_index]
        entities_by_urn = {entity.urn: entity for entity in path.context}
        step_entities = [entities_by_urn[ref] for ref in step.context_refs if ref in entities_by_urn]

        if not step_entities:
            # No DataHub entity anchors this step (e.g. the initial goal
            # confirmation step); explain the interpreted goal itself rather
            # than a static line that says nothing about it.
            context = ContextPackage(
                goal=path.interpretation.desired_outcome,
                current_entity=None,
                evidence=path.interpretation.required_actions,
                relationships=[],
                next_action=step.user_action,
            )
            return await self._llm.explain_context(context)

        primary = step_entities[0]
        evidence = [f"{primary.name} ({primary.entity_type}): {primary.relevance}"]
        evidence.extend(f"{key}: {value}" for key, value in primary.metadata.items())
        evidence.extend(
            f"{extra.name} ({extra.entity_type}): {extra.relevance}" for extra in step_entities[1:]
        )
        relationships = [
            entities_by_urn[urn].name if urn in entities_by_urn else urn
            for urn in primary.relationships
        ]

        context = ContextPackage(
            goal=path.interpretation.desired_outcome,
            current_entity=primary.name,
            evidence=evidence,
            relationships=relationships,
            next_action=step.user_action,
        )
        return await self._llm.explain_context(context)

    def replan_path(self, path: ContextualPath, assessment: PathAssessment) -> ContextualPath:
        """Add a prerequisite when the user says the current path was not useful."""
        if assessment.useful:
            return path

        revised = path.model_copy(deep=True)
        anchor_refs = revised.steps[1].context_refs if len(revised.steps) > 1 else []
        revised.steps.insert(
            1,
            PathStep(
                title="Clarify the evidence gap",
                mode=Intent.explore,
                purpose="Identify what is still unclear before continuing through the path.",
                user_action=assessment.feedback or "Describe which evidence or relationship needs more explanation.",
                context_refs=anchor_refs,
                step_type="assessment",
            ),
        )
        revised.context_notes.append("Path replanned after the user reported that the previous path was not useful.")
        revised.outcome = "A revised contextual path that addresses the user's evidence gap."
        # NEW: reset synthesis because path changed
        revised.synthesis = None
        return revised

    async def assess_user_response(
        self,
        path: ContextualPath,
        step_index: int,
        user_response: str,
    ) -> AssessmentResult:
        # Build context dari step yang dipilih
        step = path.steps[step_index]
        entities_by_urn = {entity.urn: entity for entity in path.context}
        step_entities = [entities_by_urn[ref] for ref in step.context_refs if ref in entities_by_urn]

        evidence = []
        for entity in step_entities:
            for key, value in entity.metadata.items():
                if value:
                    evidence.append(f"{key}: {value}")

        context = AssessmentContext(
            goal=path.interpretation.desired_outcome,
            current_step=step.title,
            evidence=evidence,
        )

        return await self._llm.assess_response(context, user_response)

    # NEW: Synthesize final outcome
    async def synthesize_final_outcome(self, path: ContextualPath) -> str:
        """Synthesize a final, evidence-backed outcome from all collected evidence."""
        # If already synthesized, return cached version
        if path.synthesis:
            return path.synthesis

        # Gather all evidence from all steps
        all_evidence = []
        for step in path.steps:
            entities_by_urn = {entity.urn: entity for entity in path.context}
            step_entities = [entities_by_urn[ref] for ref in step.context_refs if ref in entities_by_urn]
            for entity in step_entities:
                for key, value in entity.metadata.items():
                    if value:
                        all_evidence.append(f"{key}: {value}")

        # Build synthesis context
        context = SynthesisContext(
            goal=path.interpretation.desired_outcome,
            steps=path.steps,
            entities=path.context,
            context_notes=path.context_notes,
        )
        synthesis = await self._llm.synthesize_outcome(context)
        # Cache the result
        path.synthesis = synthesis
        return synthesis