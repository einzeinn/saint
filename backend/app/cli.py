import argparse
import asyncio
import logging
from typing import Sequence

from rich import box
from rich.align import Align
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from backend.app.adapters.datahub import build_datahub_adapter
from backend.app.adapters.llm import build_llm_adapter
from backend.app.config import Settings
from backend.app.domain import GoalRequest, Intent, PathAssessment
from backend.app.orchestration import SaintOrchestrator


# ---------------------------------------------------------------------------
# Theme: one place to control Saint's visual identity.
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

# ---------------------------------------------------------------------------
# Hero banner: shown once, on the plain `saint` entry point.
# ---------------------------------------------------------------------------
SAINT_LOGO = (
    "███████╗ █████╗ ██╗███╗   ██╗████████╗\n"
    "██╔════╝██╔══██╗██║████╗  ██║╚══██╔══╝\n"
    "███████╗███████║██║██╔██╗ ██║   ██║   \n"
    "╚════██║██╔══██║██║██║╚██╗██║   ██║   \n"
    "███████║██║  ██║██║██║ ╚████║   ██║   \n"
    "╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   "
)

MENU_ITEMS: list[tuple[str, str, str]] = [
    ("1", "Learn", "Understand a concept, grounded in real DataHub context"),
    ("2", "Explore", "Investigate a dataset, dashboard, or pipeline from scratch"),
    ("3", "Solve", "Test your own hypothesis against DataHub evidence"),
    ("4", "Demo", "See Saint in action instantly \u2014 no setup required"),
    ("5", "Doctor", "Check your DataHub and LLM configuration"),
    ("6", "Init", "Configure your DataHub connection"),
    ("0", "Exit", "Quit Saint"),
]


def _render_hero() -> None:
    console.print()
    console.print(Align.center(Text(SAINT_LOGO, style="saint.brand")))
    console.print(Align.center(Text("Context-aware path to insight", style="saint.dim")))
    console.print()

    menu = Table.grid(padding=(0, 2, 0, 0))
    menu.add_column(style="saint.label", justify="right", no_wrap=True)
    menu.add_column(style="saint.step", no_wrap=True)
    menu.add_column(style="saint.dim")
    for key, label, description in MENU_ITEMS:
        menu.add_row(key, label, description)
    console.print(Align.center(menu))
    console.print()


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="[%(name)s] %(message)s")

    parser = argparse.ArgumentParser(prog="saint", description="Context-aware path to understanding and action.")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("demo", "init", "doctor", "version", "solve",),
        default=None,
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="For 'demo': use your configured DataHub connection instead of built-in mock data.",
    )
    args = parser.parse_args(argv)

    if args.command is None:
        return run_interactive()
    if args.command == "version":
        console.print("[saint.brand]Saint[/saint.brand] 0.1.0")
        return 0
    if args.command == "solve":
        return run_solve()
    if args.command == "init":
        return run_init()
    if args.command == "doctor":
        return run_doctor()
    if args.command == "demo":
        return run_demo(live=args.live)

    # Unreachable: argparse already restricts choices above.
    return run_interactive()


def run_demo(live: bool = False) -> int:
    _render_header("Demo mode" + (" (live DataHub)" if live else ""))
    if live:
        console.print("[saint.muted]Using your configured DataHub connection for live context.[/saint.muted]\n")
        settings = Settings()
    else:
        console.print("[saint.muted]Using safe built-in context. No Docker or DataHub credentials are required.[/saint.muted]\n")
        settings = Settings(datahub_provider="mock")

    return _run_flow(
        GoalRequest(
            goal="I want to understand why the revenue dashboard changed",
            intent=Intent.explore,
        ),
        settings,
        demo=True,
    )


def run_interactive() -> int:
    _render_hero()
    choice = IntPrompt.ask(
        "Choose an option",
        choices=[item[0] for item in MENU_ITEMS],
        default=1,
        show_choices=False,
    )

    if choice == 0:
        return 0
    if choice == 3:
        return run_solve()
    if choice == 4:
        return run_demo()
    if choice == 5:
        return run_doctor()
    if choice == 6:
        return run_init()

    intent = {1: Intent.learn, 2: Intent.explore}[choice]
    labels = {Intent.learn: "Learn", Intent.explore: "Explore"}
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
            with console.status("[saint.dim]Asking the LLM to explain this step...[/saint.dim]", spinner="dots"):
                guidance = asyncio.run(orchestrator.feedback_for_step(path, selected - 1))
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

    # NEW: Synthesize final outcome instead of showing path.outcome directly
    console.print(Rule(style="saint.dim"))
    with console.status("[saint.dim]Synthesizing final outcome from all evidence...[/saint.dim]", spinner="dots"):
        synthesis = asyncio.run(orchestrator.synthesize_final_outcome(path))
    console.print(Panel(synthesis, title="Outcome", box=box.DOUBLE, border_style="saint.ok"))

    _handle_writeback(orchestrator, path, demo=demo)
    return 0


def _render_steps(steps, show_purpose: bool = True) -> None:
    for index, step in enumerate(steps, start=1):
        console.print(f"[saint.step]{index}.[/saint.step] [bold]{step.title}[/bold] [saint.dim]({step.step_type})[/saint.dim]")
        if show_purpose:
            console.print(f"   {step.purpose}")
        console.print(f"   [saint.muted]Next: {step.user_action}[/saint.muted]")
        console.print()


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
    console.print("  " + escape('python -m pip install "saint[agent-context]"'), style="saint.label")
    console.print("  [saint.label]DATAHUB_PROVIDER[/saint.label]=agent_context")
    console.print("  [saint.label]DATAHUB_GMS_URL[/saint.label]=https://<your-datahub-host>")
    console.print("  [saint.label]DATAHUB_GMS_TOKEN[/saint.label]=<personal-access-token>")
    console.print("\n[saint.muted]The base demo works without DataHub, Docker, MCP, or credentials.[/saint.muted]")
    console.print("[saint.muted]Run 'saint demo --live' to use your configured DataHub connection instead of mock data.[/saint.muted]")
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
    checks.add_row("LLM provider", settings.llm_provider)
    checks.add_row("Groq key set", "[saint.ok]✓ yes[/saint.ok]" if settings.groq_api_key.strip() else "[saint.dim]— no[/saint.dim]")
    checks.add_row("Gemini key set", "[saint.ok]✓ yes[/saint.ok]" if settings.gemini_api_key.strip() else "[saint.dim]— no[/saint.dim]")
    console.print(checks)
    return 0 if status.reachable else 1

def run_solve() -> int:
    _render_header("Solve mode — test your hypothesis against DataHub evidence")

    goal = Prompt.ask("What's the problem you're trying to solve?")
    if len(goal.strip()) < 3:
        console.print("[saint.error]Goal must contain at least 3 characters.[/saint.error]")
        return 2

    settings = Settings()
    orchestrator = SaintOrchestrator(
        llm=build_llm_adapter(settings),
        datahub=build_datahub_adapter(settings),
    )

    with console.status("[saint.dim]Interpreting your goal...[/saint.dim]", spinner="dots"):
        interpretation = asyncio.run(orchestrator.interpret_goal(GoalRequest(goal=goal, intent=Intent.act)))

    console.print(Panel(interpretation.desired_outcome, title="I understand your goal as", box=box.ROUNDED))

    with console.status("[saint.dim]Discovering context from DataHub...[/saint.dim]", spinner="dots"):
        path = asyncio.run(orchestrator.generate_contextual_path(GoalRequest(goal=goal, intent=Intent.act)))

    _render_steps(path.steps)

    selected = IntPrompt.ask("\nSelect a step to test your hypothesis against", default=1)
    if not (1 <= selected <= len(path.steps)):
        console.print("[saint.error]Invalid step.[/saint.error]")
        return 1

    hypothesis = Prompt.ask("\n[bold]What's your hypothesis?[/bold]\n(e.g., 'menurutku karena pipeline telat')")

    with console.status("[saint.dim]Validating your hypothesis against DataHub evidence...[/saint.dim]", spinner="dots"):
        result = asyncio.run(orchestrator.assess_user_response(path, selected - 1, hypothesis))

    console.print(Rule("[saint.label]Assessment Result[/saint.label]", style="saint.dim"))
    status_color = "saint.ok" if result.status == "confirmed" else "saint.warn"
    console.print(f"Status: [{status_color}]{result.status}[/{status_color}]")
    console.print(f"Understanding: {result.understanding}")

    if result.evidence_gap:
        console.print("\n[saint.label]Evidence gaps:[/saint.label]")
        for gap in result.evidence_gap:
            console.print(f" [saint.brand]→[/saint.brand] {gap}")

    if result.recommended_action:
        console.print(f"\n[saint.label]Recommended action:[/saint.label] {result.recommended_action}")

    # NEW: Also show final synthesis after assessment in solve mode
    console.print(Rule(style="saint.dim"))
    with console.status("[saint.dim]Synthesizing final outcome from all evidence...[/saint.dim]", spinner="dots"):
        synthesis = asyncio.run(orchestrator.synthesize_final_outcome(path))
    console.print(Panel(synthesis, title="Final Outcome", box=box.DOUBLE, border_style="saint.ok"))

    _handle_writeback(orchestrator, path, demo=False)
    console.print(Rule(style="saint.dim"))
    return 0


def _handle_writeback(orchestrator: SaintOrchestrator, path, demo: bool = False) -> None:
    console.print()
    preview = asyncio.run(orchestrator.build_publish_preview(path))

    if demo:
        # Demo mode: Simulated preview, NO live/mock auto-publish!
        preview_table = Table(show_header=False, box=box.SIMPLE, border_style="saint.dim")
        preview_table.add_column("Field", style="saint.label", no_wrap=True)
        preview_table.add_column("Value")
        preview_table.add_row("Title", preview["title"])
        preview_table.add_row("Type", preview["document_type"])
        asset_names = ", ".join(e.name for e in preview["top_entities"]) or "None"
        preview_table.add_row("Related Assets", f"{asset_names} ({len(preview['top_entities'])} asset(s))")
        preview_table.add_row("Topics", ", ".join(preview["topics"]))

        console.print(
            Panel(
                preview_table,
                title="[saint.dim]Simulated Document Publish (Demo Mode)[/saint.dim]",
                subtitle="[saint.muted]Deterministic demo: no document was published[/saint.muted]",
                box=box.ROUNDED,
                border_style="saint.dim",
            )
        )
        return

    # Interactive mode (saint, saint solve)
    want_publish = Confirm.ask(
        "[saint.label]Publish investigation summary to DataHub as a Document?[/saint.label]",
        default=False,
    )
    if not want_publish:
        return

    # Render Preview Panel
    preview_table = Table(show_header=False, box=box.ROUNDED, border_style="saint.brand")
    preview_table.add_column("Field", style="saint.label", no_wrap=True)
    preview_table.add_column("Value")
    preview_table.add_row("Title", preview["title"])
    preview_table.add_row("Type", preview["document_type"])
    asset_names = ", ".join(e.name for e in preview["top_entities"]) or "None"
    preview_table.add_row("Related Assets", asset_names)
    preview_table.add_row("Topics", ", ".join(preview["topics"]))

    console.print()
    console.print(Panel(preview_table, title="Publishing Preview", box=box.ROUNDED, border_style="saint.brand"))

    confirmed = Confirm.ask("\n[saint.label]Confirm publishing to DataHub?[/saint.label]", default=True)
    if not confirmed:
        console.print("[saint.dim]Publish cancelled.[/saint.dim]")
        return

    with console.status("[saint.dim]Publishing document to DataHub...[/saint.dim]", spinner="dots"):
        result = asyncio.run(
            orchestrator.publish_result(
                path, title=preview["title"], document_type=preview["document_type"]
            )
        )

    if result.success:
        urn_info = f"\nURN: {result.urn}" if result.urn else ""
        console.print(f"[saint.ok]✓ Published to DataHub![/saint.ok] {result.message}{urn_info}")
    else:
        console.print(f"[saint.error]✗ Write-back failed:[/saint.error] {result.message}")


def _render_header(mode: str) -> None:
    console.print(
        Panel(
            "[saint.brand]SAINT[/saint.brand]\n[saint.dim]Context-aware path to insight[/saint.dim]",
            subtitle=mode,
            box=box.HEAVY,
            border_style="saint.brand",
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())