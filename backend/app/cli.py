import argparse
import asyncio
from typing import Sequence

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.theme import Theme

from backend.app.adapters.datahub import build_datahub_adapter
from backend.app.adapters.llm import build_llm_adapter
from backend.app.config import Settings
from backend.app.domain import GoalRequest, Intent, PathAssessment
from backend.app.orchestration import SaintOrchestrator


# ---------------------------------------------------------------------------
# Theme: one place to control Saint's visual identity. Change colors here,
# not scattered across the file.
# ---------------------------------------------------------------------------
SAINT_THEME = Theme(
    {
        "saint.brand": "bold cyan",
        "saint.dim": "grey62",
        "saint.ok": "bold green",
        "saint.warn": "bold yellow",
        "saint.error": "bold red",
        "saint.step": "bold white",
        "saint.label": "bold cyan",
        "saint.muted": "italic grey58",
    }
)

console = Console(theme=SAINT_THEME)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="saint", description="Context-aware path to understanding and action.")
    parser.add_argument("command", nargs="?", choices=("demo", "init", "doctor", "version"), default="run")
    args = parser.parse_args(argv)

    if args.command == "version":
        console.print("[saint.brand]Saint[/saint.brand] 0.1.0")
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
    console.print("[saint.muted]Using safe built-in context. No Docker or DataHub credentials are required.[/saint.muted]\n")
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
    console.print("[saint.label]1[/saint.label] Learn   [saint.label]2[/saint.label] Explore   [saint.label]3[/saint.label] Solve")
    choice = IntPrompt.ask("Choose an entry", choices=["1", "2", "3"], default=1)
    intent = {1: Intent.learn, 2: Intent.explore, 3: Intent.act}[choice]
    labels = {Intent.learn: "Learn", Intent.explore: "Explore", Intent.act: "Solve"}
    console.print(f"\n[saint.label]Entry:[/saint.label] {labels[intent]}")
    goal = Prompt.ask("What do you want to accomplish?")
    if len(goal.strip()) < 3:
        console.print("[saint.error]Goal must contain at least 3 characters.[/saint.error]")
        return 2
    return _run_flow(GoalRequest(goal=goal, intent=intent), Settings())


def _run_flow(request: GoalRequest, settings: Settings, demo: bool = False) -> int:
    orchestrator = SaintOrchestrator(
        llm=build_llm_adapter(settings),
        datahub=build_datahub_adapter(settings),
    )

    with console.status("[saint.dim]Interpreting your goal...[/saint.dim]", spinner="dots"):
        interpretation = asyncio.run(orchestrator.interpret_goal(request))

    console.print(Rule("[saint.label]Goal[/saint.label]", style="saint.dim"))
    console.print(Panel(interpretation.desired_outcome, title="I understand your goal as", box=box.ROUNDED, border_style="saint.brand"))
    console.print("\n[saint.label]Required actions[/saint.label]")
    for action in interpretation.required_actions:
        console.print(f"  [saint.brand]→[/saint.brand] {action}")

    confirmed = demo or Confirm.ask("\nContinue to discover context?", default=True)
    if not confirmed:
        console.print("[saint.dim]Goal not confirmed. Nothing else was executed.[/saint.dim]")
        return 0

    console.print(Rule("[saint.label]Context[/saint.label]", style="saint.dim"))
    with console.status("[saint.dim]Discovering context from DataHub...[/saint.dim]", spinner="dots"):
        path = asyncio.run(orchestrator.generate_contextual_path(request))

    if not path.context:
        console.print("[saint.warn]⚠ No context was found. The path is using a safe fallback.[/saint.warn]")
    else:
        table = Table(title=f"DataHub context ({path.context_source})", box=box.ROUNDED, header_style="saint.label", border_style="saint.dim")
        table.add_column("Type")
        table.add_column("Name")
        table.add_column("Evidence")
        for entity in path.context:
            evidence = ", ".join(f"{key}: {value}" for key, value in entity.metadata.items()) or "—"
            table.add_row(entity.entity_type, entity.name, evidence)
        console.print(table)

    console.print(Rule("[saint.label]Path[/saint.label]", style="saint.dim"))
    _render_steps(path.steps)

    if path.steps:
        selected = 1 if demo else IntPrompt.ask("\nSelect a step for guidance", default=1)
        if 1 <= selected <= len(path.steps):
            with console.status("[saint.dim]Preparing guidance...[/saint.dim]", spinner="dots"):
                guidance = orchestrator.feedback_for_step(path, selected - 1)
            console.print(Panel(guidance, title="Guidance", box=box.ROUNDED, border_style="saint.brand"))

    console.print(Rule("[saint.label]Assessment[/saint.label]", style="saint.dim"))
    assessment = _assess_path(demo)
    if assessment.useful:
        console.print("[saint.ok]✓ Assessment: this path was useful.[/saint.ok]")
    else:
        console.print(f"[saint.warn]↻ Assessment: refine the path next time.[/saint.warn] {assessment.feedback or ''}")
        with console.status("[saint.dim]Replanning...[/saint.dim]", spinner="dots"):
            path = orchestrator.replan_path(path, assessment)
        console.print("\n[saint.label]Replanned path[/saint.label]")
        _render_steps(path.steps, show_purpose=False)

    console.print(Rule(style="saint.dim"))
    console.print(Panel(path.outcome, title="Outcome", box=box.DOUBLE, border_style="saint.ok"))
    return 0


def _render_steps(steps, show_purpose: bool = True) -> None:
    for index, step in enumerate(steps, start=1):
        console.print(f"[saint.step]{index}.[/saint.step] [bold]{step.title}[/bold] [saint.dim]({step.step_type})[/saint.dim]")
        if show_purpose:
            console.print(f"   {step.purpose}")
        console.print(f"   [saint.muted]Next: {step.user_action}[/saint.muted]")


def _assess_path(demo: bool) -> PathAssessment:
    if demo:
        return PathAssessment(useful=True, feedback="Demo completed with evidence-backed context.")
    useful = Confirm.ask("\nWas this path useful?", default=True)
    feedback = None if useful else Prompt.ask("What should Saint improve?", default="More specific evidence")
    return PathAssessment(useful=useful, feedback=feedback)


def run_init() -> int:
    _render_header("Initialize Saint")
    console.print("[saint.dim]Saint keeps configuration in environment variables and never writes credentials to the repository.[/saint.dim]\n")
    console.print("For a direct Agent Context Kit connection, install the optional extra:")
    console.print('  [saint.label]python -m pip install "saint[agent-context]"[/saint.label]')
    console.print("  [saint.label]DATAHUB_PROVIDER[/saint.label]=agent_context")
    console.print("  [saint.label]DATAHUB_GMS_URL[/saint.label]=https://<your-datahub-host>")
    console.print("  [saint.label]DATAHUB_GMS_TOKEN[/saint.label]=<personal-access-token>")
    console.print("\n[saint.muted]The base demo works without DataHub, Docker, MCP, or credentials.[/saint.muted]")
    return 0


def run_doctor() -> int:
    settings = Settings()
    adapter = build_datahub_adapter(settings)
    with console.status("[saint.dim]Running diagnostics...[/saint.dim]", spinner="dots"):
        status = asyncio.run(adapter.status())
    _render_header("Saint Doctor")
    checks = Table(show_header=False, box=box.SIMPLE, border_style="saint.dim")
    checks.add_column("Check", style="saint.label")
    checks.add_column("Result")
    checks.add_row("DataHub provider", status.provider)
    checks.add_row("Configured", "[saint.ok]✓ yes[/saint.ok]" if status.configured else "[saint.error]✗ no[/saint.error]")
    checks.add_row("Reachable", "[saint.ok]✓ yes[/saint.ok]" if status.reachable else "[saint.error]✗ no[/saint.error]")
    checks.add_row("Details", status.detail)
    console.print(checks)
    return 0 if status.reachable else 1


def _render_header(mode: str) -> None:
    console.print(Panel("[saint.brand]SAINT[/saint.brand]\n[saint.dim]Context-aware path to insight[/saint.dim]", subtitle=mode, box=box.HEAVY, border_style="saint.brand"))


if __name__ == "__main__":
    raise SystemExit(main())