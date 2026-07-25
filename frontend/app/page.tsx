"use client";

import { FormEvent, useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Intent = "learn" | "explore" | "act" | "unsure";

type GoalInterpretation = {
  original_goal: string;
  intent: Intent;
  desired_outcome: string;
  required_actions: string[];
  required_capabilities: string[];
  constraints: string[];
};

type ContextEntity = {
  urn: string;
  name: string;
  entity_type: string;
  relevance: string;
  relationships: string[];
  metadata: Record<string, unknown>;
};

type PathStep = {
  title: string;
  mode: Intent;
  purpose: string;
  user_action: string;
  context_refs: string[];
  step_type: string;
};

type ContextualPath = {
  interpretation: GoalInterpretation;
  context: ContextEntity[];
  steps: PathStep[];
  outcome: string;
  context_source: string;
  context_notes: string[];
};

type PrototypeSession = {
  session_id: string;
  request: {
    goal: string;
    intent: Intent;
  };
  interpretation: GoalInterpretation;
  confirmed: boolean;
  path: ContextualPath | null;
  selected_step_index: number | null;
  feedback: string | null;
};

type DataHubStatus = {
  provider: string;
  configured: boolean;
  reachable: boolean;
  mode: string;
  detail: string;
};

const intents: Array<{ intent: Intent; title: string; body: string }> = [
  { intent: "learn", title: "Learn", body: "Build understanding around a context." },
  { intent: "explore", title: "Explore", body: "Investigate a question or change." },
  { intent: "act", title: "Act", body: "Complete a task with context." },
  { intent: "unsure", title: "Not sure", body: "Let Saint infer the best mode." },
];

export default function Home() {
  const [intent, setIntent] = useState<Intent>("learn");
  const [goal, setGoal] = useState("I want to understand why the revenue dashboard changed");
  const [session, setSession] = useState<PrototypeSession | null>(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [dataHubStatus, setDataHubStatus] = useState<DataHubStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkStatus() {
      try {
        await getJson("/health");
        setApiOnline(true);
        setDataHubStatus(await getJson<DataHubStatus>("/integrations/datahub/status"));
      } catch {
        setApiOnline(false);
        setDataHubStatus(null);
      }
    }

    void checkStatus();
  }, []);

  async function createSession(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await postJson<PrototypeSession>("/prototype/sessions", { goal, intent });
      setSession(created);
    } catch {
      setError("Saint tidak dapat menginterpretasikan goal. Pastikan backend sedang berjalan.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmSession() {
    if (!session) {
      return;
    }

    setBusy(true);
    setError(null);
    try {
      const confirmed = await postJson<PrototypeSession>(`/prototype/sessions/${session.session_id}/confirm`, { confirmed: true });
      setSession(confirmed);
    } catch {
      setError("Context DataHub belum dapat dimuat. Coba lagi.");
    } finally {
      setBusy(false);
    }
  }

  async function selectStep(stepIndex: number) {
    if (!session) {
      return;
    }

    setBusy(true);
    setError(null);
    try {
      const updated = await postJson<PrototypeSession>(`/prototype/sessions/${session.session_id}/steps`, { step_index: stepIndex });
      setSession(updated);
    } catch {
      setError("Step belum dapat dipilih. Coba lagi.");
    } finally {
      setBusy(false);
    }
  }

  const path = session?.path ?? null;

  return (
    <main className="min-h-screen p-5 md:p-8">
      <section className="mx-auto w-full max-w-[1180px]">
        <header className="mb-6 grid gap-4 md:flex md:items-end md:justify-between">
          <div>
            <p className="eyebrow">Saint</p>
            <h1 className="text-[40px] font-extrabold leading-none tracking-normal md:text-[58px]">
              Goal to Contextual Path
            </h1>
          </div>
          <div className="grid gap-2 md:min-w-72">
            <StatusBadge online={apiOnline} />
            <DataHubBadge status={dataHubStatus} />
          </div>
        </header>

        <section className="panel mb-5 grid gap-5" aria-labelledby="goal-title">
          <div>
            <p className="eyebrow">Intent</p>
            <h2 id="goal-title" className="text-2xl font-extrabold tracking-normal">
              What brings you here?
            </h2>
          </div>
          <div className="grid gap-3 md:grid-cols-4" role="radiogroup" aria-label="Intent">
            {intents.map((card) => (
              <button
                className={`intent-card ${intent === card.intent ? "intent-card-active" : ""}`}
                key={card.intent}
                type="button"
                onClick={() => setIntent(card.intent)}
              >
                <span className="mb-2.5 block font-extrabold">{card.title}</span>
                <small className="leading-6 text-saint-muted">{card.body}</small>
              </button>
            ))}
          </div>
          <form className="grid gap-2" onSubmit={createSession}>
            <label className="text-sm font-bold text-saint-muted" htmlFor="goalInput">
              Goal
            </label>
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto]">
              <input
                id="goalInput"
                className="min-h-12 w-full rounded-lg border border-saint-line bg-[#fbfcfb] px-3.5 text-saint-ink"
                value={goal}
                onChange={(event) => setGoal(event.target.value)}
                autoComplete="off"
                required
                minLength={3}
              />
              <button className="button-primary" type="submit" disabled={busy}>
                {busy ? "Working..." : "Interpret"}
              </button>
            </div>
          </form>
        </section>

        <section className="mb-5 grid gap-5 lg:grid-cols-2">
          <article className="panel" aria-labelledby="interpretation-title">
            <div className="mb-4">
              <p className="eyebrow">Understanding</p>
              <h2 id="interpretation-title" className="text-2xl font-extrabold tracking-normal">
                Goal Interpretation
              </h2>
            </div>
            {session ? <Interpretation interpretation={session.interpretation} /> : <div className="empty-state">No interpretation yet.</div>}
            <div className="mt-5 flex gap-2.5">
              <button className="button-primary" type="button" disabled={!session || session.confirmed || busy} onClick={confirmSession}>
                {busy ? "Loading..." : "Confirm"}
              </button>
              <button
                className="button-secondary"
                type="button"
                onClick={() => {
                  setSession(null);
                  setGoal("I want to understand why the revenue dashboard changed");
                  setIntent("learn");
                }}
              >
                Reset
              </button>
            </div>
          </article>

          <article className="panel" aria-labelledby="context-title">
            <div className="mb-4">
              <p className="eyebrow">{dataHubStatus?.provider === "mcp" ? "DataHub MCP" : "Mock Context"}</p>
              <h2 id="context-title" className="text-2xl font-extrabold tracking-normal">
                Relevant DataHub Context
              </h2>
            </div>
            {path ? <ContextList context={path.context} /> : <div className="empty-state">Confirm a goal to load context.</div>}
          </article>
        </section>

        <section className="panel" aria-labelledby="path-title">
          <div className="mb-4">
            <p className="eyebrow">Path</p>
            <h2 id="path-title" className="text-2xl font-extrabold tracking-normal">
              Contextual Path
            </h2>
          </div>
          {path && session ? (
            <PathList session={session} busy={busy} onSelectStep={selectStep} />
          ) : (
            <div className="empty-state">No path yet.</div>
          )}
          {error ? <div className="mt-4 rounded-lg border border-[#dfb8a2] bg-[#fff4ee] p-3.5 text-[#7b341b]">{error}</div> : null}
          {session?.feedback ? (
            <div className="mt-4 rounded-lg border border-[#cfd7e6] bg-[#e8eef7] p-3.5 text-[#24466f]">
              {session.feedback}
            </div>
          ) : null}
        </section>
      </section>
    </main>
  );
}

function StatusBadge({ online }: { online: boolean }) {
  const classes = online
    ? "border-[#a6d3c8] bg-[#eef8f5] text-saint-strong"
    : "border-[#dfb8a2] bg-[#fff4ee] text-[#7b341b]";

  return <div className={`rounded-lg border px-3 py-2 text-sm ${classes}`}>{online ? "Backend online" : "Backend offline"}</div>;
}

function DataHubBadge({ status }: { status: DataHubStatus | null }) {
  if (!status) {
    return <div className="rounded-lg border border-saint-line bg-white px-3 py-2 text-sm text-saint-muted">DataHub not checked</div>;
  }

  const classes = status.reachable
    ? "border-[#a6d3c8] bg-[#eef8f5] text-saint-strong"
    : "border-[#dfb8a2] bg-[#fff4ee] text-[#7b341b]";

  return (
    <div title={status.detail} className={`rounded-lg border px-3 py-2 text-sm ${classes}`}>
      DataHub: {status.provider} / {status.mode}
    </div>
  );
}

function Interpretation({ interpretation }: { interpretation: GoalInterpretation }) {
  return (
    <div className="grid gap-4">
      <div className="border-l-4 border-saint-accent pl-3">
        <strong className="mb-1 block">{interpretation.intent.toUpperCase()}</strong>
        <span>{interpretation.desired_outcome}</span>
      </div>
      <div>
        <strong>Required actions</strong>
        <ol className="mt-2 list-decimal pl-5">
          {interpretation.required_actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}

function ContextList({ context }: { context: ContextEntity[] }) {
  if (context.length === 0) {
    return <div className="empty-state">Belum ada entity relevan yang ditemukan untuk goal ini.</div>;
  }

  return (
    <div className="grid gap-3">
      {context.map((entity) => (
        <article className="rounded-lg border border-saint-line bg-[#fbfcfb] p-3.5" key={entity.urn}>
          <header className="mb-2 flex items-center justify-between gap-3">
            <strong>{entity.name}</strong>
            <span className="badge">{entity.entity_type}</span>
          </header>
          <p className="leading-6 text-saint-muted">{entity.relevance}</p>
          {Object.entries(entity.metadata).length > 0 ? (
            <dl className="mt-3 grid gap-1 text-sm text-saint-muted">
              {Object.entries(entity.metadata).map(([key, value]) => (
                <div className="flex gap-2" key={key}>
                  <dt className="font-bold capitalize">{key}:</dt>
                  <dd>{String(value)}</dd>
                </div>
              ))}
            </dl>
          ) : null}
          <code className="mt-2.5 block break-words text-xs text-[#8b5b18]">{entity.urn}</code>
        </article>
      ))}
    </div>
  );
}

function PathList({
  session,
  busy,
  onSelectStep,
}: {
  session: PrototypeSession;
  busy: boolean;
  onSelectStep: (stepIndex: number) => Promise<void>;
}) {
  if (!session.path) {
    return <div className="empty-state">No path yet.</div>;
  }

  return (
    <div className="grid gap-3">
      {session.path.steps.map((step, index) => {
        const active = session.selected_step_index === index ? "border-saint-accent bg-saint-soft" : "border-saint-line bg-[#fbfcfb]";
        return (
          <button
            className={`grid gap-2 rounded-lg border ${active} p-3.5 text-left`}
            key={`${step.title}-${index}`}
            type="button"
            disabled={busy}
            onClick={() => void onSelectStep(index)}
          >
            <header className="flex items-center justify-between gap-3">
              <strong>
                {index + 1}. {step.title}
              </strong>
              <span className="badge">{step.step_type} · {step.mode}</span>
            </header>
            <p className="leading-6 text-saint-muted">{step.purpose}</p>
            <p className="leading-6 text-saint-muted">{step.user_action}</p>
          </button>
        );
      })}
    </div>
  );
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
