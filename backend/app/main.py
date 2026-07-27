from uuid import uuid4

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.adapters.datahub import build_datahub_adapter
from backend.app.adapters.llm import build_llm_adapter
from backend.app.config import get_settings
from backend.app.domain import (
    AssessmentContext,
    AssessmentResult,
    ContextPackage,
    ContextualPath,
    DataHubIntegrationStatus,
    GoalInterpretation,
    GoalRequest,
    PrototypeSession,
    SessionConfirmation,
    StepSelection,
)
from backend.app.orchestration import SaintOrchestrator

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.frontend_origin.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = SaintOrchestrator(
    llm=build_llm_adapter(settings),
    datahub=build_datahub_adapter(settings),
)

prototype_sessions: dict[str, PrototypeSession] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@app.post("/goals/interpret", response_model=GoalInterpretation)
async def interpret_goal(request: GoalRequest) -> GoalInterpretation:
    return await orchestrator.interpret_goal(request)


@app.post("/goals/contextual-path", response_model=ContextualPath)
async def contextual_path(request: GoalRequest) -> ContextualPath:
    return await orchestrator.generate_contextual_path(request)


@app.post("/llm/explain-context")
async def explain_context(request: ContextPackage) -> str:
    return await orchestrator._llm.explain_context(request)


@app.post("/llm/assess-response", response_model=AssessmentResult)
async def assess_response(request: dict[str, object]) -> AssessmentResult:
    context_payload = request.get("context")
    user_response = request.get("user_response")
    if not isinstance(context_payload, dict) or not isinstance(user_response, str):
        raise HTTPException(status_code=422, detail="context and user_response are required")
    context = AssessmentContext.model_validate(context_payload)
    return await orchestrator._llm.assess_response(context, user_response)


@app.get("/integrations/datahub/status", response_model=DataHubIntegrationStatus)
async def datahub_status() -> DataHubIntegrationStatus:
    return await orchestrator.datahub_status()


@app.post("/prototype/sessions", response_model=PrototypeSession)
async def create_prototype_session(request: GoalRequest) -> PrototypeSession:
    interpretation = await orchestrator.interpret_goal(request)
    session = PrototypeSession(
        session_id=str(uuid4()),
        request=request,
        interpretation=interpretation,
    )
    prototype_sessions[session.session_id] = session
    return session


@app.post("/prototype/sessions/{session_id}/confirm", response_model=PrototypeSession)
async def confirm_prototype_session(
    session_id: str, confirmation: SessionConfirmation
) -> PrototypeSession:
    session = _get_session(session_id)
    session.confirmed = confirmation.confirmed

    if confirmation.confirmed:
        session.path = await orchestrator.generate_contextual_path(session.request)
    else:
        session.path = None
        session.feedback = "Goal interpretation was not confirmed."

    prototype_sessions[session_id] = session
    return session


@app.post("/prototype/sessions/{session_id}/steps", response_model=PrototypeSession)
async def select_prototype_step(
    session_id: str, selection: StepSelection
) -> PrototypeSession:
    session = _get_session(session_id)

    if session.path is None:
        raise HTTPException(status_code=409, detail="Session has no contextual path yet.")

    if selection.step_index >= len(session.path.steps):
        raise HTTPException(status_code=422, detail="Step index is outside the current path.")

    session.selected_step_index = selection.step_index
    session.feedback = await orchestrator.feedback_for_step(session.path, selection.step_index)
    prototype_sessions[session_id] = session
    return session


def _get_session(session_id: str) -> PrototypeSession:
    session = prototype_sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Prototype session not found.")
    return session
