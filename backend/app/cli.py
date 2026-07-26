import argparse
import asyncio
from typing import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from backend.app.adapters.datahub import build_datahub_adapter
from backend.app.adapters.llm import build_llm_adapter
from backend.app.config import Settings
from backend.app.domain import GoalRequest, Intent, PathAssessment
from backend.app.orchestration import SaintOrchestrator


console = Console()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="saint", description="Context-aware path to understanding and action.")
    parser.add_argument("command", nargs="?", choices=("demo", "init", "doctor", "version"), default="run")
    args = parser.parse_args(argv)

    if args.command == "version":
        console.print("Saint 0.1.0")
        return 0
    if args.command == "init":
        return run_init()
    if args.command == "doctor":
        return run_doctor()
    if args.command == "demo":
        return run_demo()
    return run_interactive()


def run_demo() -> int:
    _render_header("Demo mode")
    console.print("Using safe built-in context. No Docker or DataHub credentials are required.\n")
    return _run_flow(
        GoalRequest(
            goal="I want to understand why the revenue dashboard changed",
            intent=Intent.explore,
        ),
        Settings(datahub_provider="mock"),
        demo=True,
    )


def run_interactive() -> int:
    _render_header("Interactive mode")
    choice = IntPrompt.ask("Choose an entry", choices=["1", "2", "3"], default=1)
    intent = {1: Intent.learn, 2: Intent.explore, 3: Intent.act}[choice]
    labels = {Intent.learn: "Learn", Intent.explore: "Explore", Intent.act: "Solve"}
    console.print(f"\n[bold]Entry:[/bold] {labels[intent]}")
    goal = Prompt.ask("What do you want to accomplish?")
    if len(goal.strip()) < 3:
        console.print("[red]Goal must contain at least 3 characters.[/red]")
        return 2
    return _run_flow(GoalRequest(goal=goal, intent=intent), Settings())


def _run_flow(request: GoalRequest, settings: Settings, demo: bool = False) -> int:
    orchestrator = SaintOrchestrator(
        llm=build_llm_adapter(settings),
        datahub=build_datahub_adapter(settings),
    )
    interpretation = asyncio.run(orchestrator.interpret_goal(request))
    console.print(Panel(interpretation.desired_outcome, title="I understand your goal as"))
    console.print("\n[bold]Required actions[/bold]")
    for action in interpretation.required_actions:
        console.print(f" • {action}")

    confirmed = demo or Confirm.ask("\nContinue to discover context?", default=True)
    if not confirmed:
        console.print("Goal not confirmed. Nothing else was executed.")
        return 0

    path = asyncio.run(orchestrator.generate_contextual_path(request))
    if not path.context:
        console.print("\n[yellow]No context was found. The path is using a safe fallback.[/yellow]")
    else:
        table = Table(title=f"DataHub context ({path.context_source})")
        table.add_column("Type")
        table.add_column("Name")
        table.add_column("Evidence")
        for entity in path.context:
            evidence = ", ".join(f"{key}: {value}" for key, value in entity.metadata.items()) or "—"
            table.add_row(entity.entity_type, entity.name, evidence)
        console.print(table)

    console.print("\n[bold]Contextual path[/bold]")
    for index, step in enumerate(path.steps, start=1):
        console.print(f"{index}. [bold]{step.title}[/bold] ({step.step_type})")
        console.print(f"   {step.purpose}")
        console.print(f"   [dim]Next: {step.user_action}[/dim]")

    if path.steps:
        if demo:
            selected = 1
        else:
            selected = IntPrompt.ask("\nSelect a step for guidance", default=1)
        if 1 <= selected <= len(path.steps):
            console.print(Panel(orchestrator.feedback_for_step(path, selected - 1), title="Guidance"))

    assessment = _assess_path(demo)
    if assessment.useful:
        console.print("\n[green]Assessment: this path was useful.[/green]")
    else:
        console.print(f"\n[yellow]Assessment: refine the path next time.[/yellow] {assessment.feedback or ''}")
        path = orchestrator.replan_path(path, assessment)
        console.print("\n[bold]Replanned path[/bold]")
        for index, step in enumerate(path.steps, start=1):
            console.print(f"{index}. [bold]{step.title}[/bold] ({step.step_type})")
            console.print(f"   {step.user_action}")
    console.print(Panel(path.outcome, title="Outcome"))
    return 0


def _assess_path(demo: bool) -> PathAssessment:
    if demo:
        return PathAssessment(useful=True, feedback="Demo completed with evidence-backed context.")
    useful = Confirm.ask("\nWas this path useful?", default=True)
    feedback = None if useful else Prompt.ask("What should Saint improve?", default="More specific evidence")
    return PathAssessment(useful=useful, feedback=feedback)


def run_init() -> int:
    _render_header("Initialize Saint")
    console.print("Saint keeps configuration in environment variables and never writes credentials to the repository.\n")
    console.print("For a direct Agent Context Kit connection, install the optional extra:")
    console.print('  python -m pip install "saint[agent-context]"')
    console.print("  DATAHUB_PROVIDER=agent_context")
    console.print("  DATAHUB_GMS_URL=https://<your-datahub-host>")
    console.print("  DATAHUB_GMS_TOKEN=<personal-access-token>")
    console.print("\nThe base demo works without DataHub, Docker, MCP, or credentials.")
    return 0


def run_doctor() -> int:
    settings = Settings()
    adapter = build_datahub_adapter(settings)
    status = asyncio.run(adapter.status())
    _render_header("Saint Doctor")
    checks = Table(show_header=False)
    checks.add_column("Check")
    checks.add_column("Result")
    checks.add_row("DataHub provider", status.provider)
    checks.add_row("Configured", "yes" if status.configured else "no")
    checks.add_row("Reachable", "yes" if status.reachable else "no")
    checks.add_row("Details", status.detail)
    console.print(checks)
    return 0 if status.reachable else 1


def _render_header(mode: str) -> None:
    console.print(Panel("[bold cyan]SAINT[/bold cyan]\nContext-aware path to insight", subtitle=mode))


if __name__ == "__main__":
    raise SystemExit(main())
