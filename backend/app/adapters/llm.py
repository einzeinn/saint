from typing import Protocol

from backend.app.domain import GoalInterpretation, GoalRequest, Intent


class LLMAdapter(Protocol):
    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        """Convert a user goal into a structured interpretation."""


class MockLLMAdapter:
    async def interpret_goal(self, request: GoalRequest) -> GoalInterpretation:
        goal = request.goal.strip()
        intent = request.intent

        if intent == Intent.unsure:
            intent = self._infer_intent(goal)

        actions = self._actions_for(goal, intent)

        return GoalInterpretation(
            original_goal=goal,
            intent=intent,
            desired_outcome=self._outcome_for(goal, intent),
            required_actions=actions,
            required_capabilities=[
                "Understand relevant DataHub entities",
                "Follow relationships between context assets",
                "Decide the next step from evidence",
            ],
            constraints=["User confirmation required before context discovery"],
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

    def _outcome_for(self, goal: str, intent: Intent) -> str:
        if intent == Intent.learn:
            return f"Build practical understanding needed to: {goal}"
        if intent == Intent.act:
            return f"Complete the task with relevant DataHub context: {goal}"
        return f"Reach an evidence-backed explanation for: {goal}"

