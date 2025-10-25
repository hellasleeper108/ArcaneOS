import React, { useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { parseArchonMessage, ArchonOption } from '../lib/archonParsers';

const ARCHON_SYSTEM_PROMPT = `You are The Archon, orchestrator of ArcaneOS.
Offer succinct insight plus a handful of actionable options drawn from the user's spell.
Each option should include a short title, when to use it, and the daemon you would enlist.
Favor clear prose or lightweight structure - strict JSON is optional.`;

type SpeakerRole = 'user' | 'assistant' | 'claude';

interface ChatTurn {
  role: SpeakerRole;
  content: string;
  options?: ArchonOption[];
  phase?: string;
  designSpec?: Record<string, unknown> | null;
  delegateTarget?: string | null;
}

interface DesignContext {
  spec: Record<string, unknown>;
  summary: string;
  title?: string;
  phase?: string | null;
  question?: string;
  delegateTarget?: string | null;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  Boolean(value) && typeof value === 'object' && !Array.isArray(value);

const getStringField = (source: Record<string, unknown>, key: string): string | undefined => {
  const value = source[key];
  return typeof value === 'string' ? value : undefined;
};

const listFromUnknown = (value: unknown): string[] =>
  Array.isArray(value)
    ? value
        .map((item) => {
          if (typeof item === 'string') return item;
          if (isRecord(item)) return JSON.stringify(item);
          if (item === undefined || item === null) return '';
          return String(item);
        })
        .filter((entry) => entry && entry !== '[object Object]')
    : [];

const changeListFrom = (value: unknown): string[] =>
  Array.isArray(value)
    ? value
        .map((item) => {
          if (!isRecord(item)) {
            if (typeof item === 'string') return item;
            return JSON.stringify(item);
          }
          const path = getStringField(item, 'path') ?? getStringField(item, 'file');
          const action = getStringField(item, 'action');
          const detail = getStringField(item, 'description') ?? getStringField(item, 'detail');
          return [action, path, detail].filter(Boolean).join(' • ') || JSON.stringify(item);
        })
        .filter((entry) => entry && entry !== '[object Object]')
    : [];

const constraintListFrom = (value: unknown): string[] =>
  isRecord(value)
    ? Object.entries(value).map(([key, val]) =>
        `${key}: ${typeof val === 'string' ? val : JSON.stringify(val)}`,
      )
    : [];

const resolveBackendBaseUrl = (): string => {
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    const isDev = process.env.NODE_ENV === 'development';
    const port = isDev ? '8000' : window.location.port;
    const formattedPort = port ? `:${port}` : '';
    return `${protocol}//${hostname}${formattedPort}`.replace(/\/+$/, '');
  }

  return 'http://localhost:8000';
};

const BACKEND_BASE_URL = resolveBackendBaseUrl();
const ARCHON_ENDPOINT = `${BACKEND_BASE_URL}/archon/chat`;
const CLAUDE_ENDPOINT = `${BACKEND_BASE_URL}/archon/claude-code`;

export const ArchonConsole: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [history, setHistory] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [designContext, setDesignContext] = useState<DesignContext | null>(null);
  const [claudeStatus, setClaudeStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [claudeMessage, setClaudeMessage] = useState<string | null>(null);
  const [claudeError, setClaudeError] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    const trimmed = prompt.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    setHistory((prev) => [...prev, { role: 'user', content: trimmed }]);
    setPrompt('');

    try {
      const serialisedHistory = history
        .filter((turn) => turn.role === 'assistant' || turn.role === 'user')
        .map(({ role, content }) => ({ role, content }));

      const response = await fetch(ARCHON_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: trimmed,
          history: serialisedHistory,
        }),
      });

      if (!response.ok) {
        throw new Error(`Archon gateway returned ${response.status}`);
      }

      const data = await response.json();
      const primaryMessage = data?.message ?? data?.raw ?? data;
      const parsed = parseArchonMessage(primaryMessage);
      const designSpec = parsed.designSpec && isRecord(parsed.designSpec) ? parsed.designSpec : null;
      const delegateTarget = parsed.delegate?.target ?? null;

      setHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: parsed.displayText,
          options: parsed.options,
          phase: parsed.phase,
          designSpec,
          delegateTarget,
        },
      ]);

      if (designSpec) {
        setDesignContext({
          spec: designSpec,
          summary: parsed.summary ?? parsed.displayText,
          title: getStringField(designSpec, 'title'),
          phase: parsed.phase ?? null,
          question: parsed.question,
          delegateTarget,
        });
        setClaudeStatus('idle');
        setClaudeMessage(null);
        setClaudeError(null);
      } else if (
        parsed.phase &&
        ['DECIDE', 'VERIFY', 'ABORT'].includes(parsed.phase.toUpperCase())
      ) {
        setDesignContext(null);
      }
    } catch (err) {
      const msg = (err as Error).message || 'Unknown error';
      setError(msg);
      setHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `The Archon encountered a disturbance: ${msg}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [prompt, loading, history]);

  const handleSendToClaude = useCallback(async () => {
    if (!designContext) return;

    setClaudeStatus('loading');
    setClaudeError(null);
    setClaudeMessage(null);

    try {
      const response = await fetch(CLAUDE_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spec: designContext.spec,
          prompt: designContext.summary,
        }),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`Claude Code responded with ${response.status}: ${detail}`);
      }

      const payload = await response.json();
      const outputCandidate = payload?.result?.output ?? payload?.result ?? payload;
      const output =
        typeof outputCandidate === 'string'
          ? outputCandidate
          : JSON.stringify(outputCandidate, null, 2);

      setClaudeStatus('success');
      setClaudeMessage(output);
      setHistory((prev) => [
        ...prev,
        {
          role: 'claude',
          content: output,
        },
      ]);
    } catch (err) {
      setClaudeStatus('error');
      setClaudeError((err as Error).message || 'Claude Code invocation failed.');
    }
  }, [designContext]);

  const renderDesignContext = () => {
    if (!designContext) {
      return null;
    }

    const { spec } = designContext;
    const goal = getStringField(spec, 'goal');
    const taskId = getStringField(spec, 'task_id');
    const acceptance = listFromUnknown(spec['acceptance']);
    const changes = changeListFrom(spec['changes']);
    const constraints = constraintListFrom(spec['constraints']);

    const extraKeys = Object.keys(spec).filter(
      (key) => !['title', 'goal', 'acceptance', 'changes', 'constraints', 'task_id'].includes(key),
    );

    const extras = extraKeys.reduce<Record<string, unknown>>((acc, key) => {
      acc[key] = spec[key];
      return acc;
    }, {});

    return (
      <div className="rounded-lg border border-sky-400/40 bg-sky-500/10 px-4 py-4 text-[12px] text-sky-100/90">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-sky-300/80">Design Outline Ready</p>
            <p className="text-[13px] font-semibold text-sky-100">
              {designContext.title ?? 'Proposed implementation plan'}
            </p>
            {taskId && <p className="mt-1 text-[10px] text-sky-200/80">Task ID: {taskId}</p>}
          </div>
          {designContext.phase && (
            <span className="rounded border border-sky-300/40 bg-sky-300/10 px-2 py-1 text-[10px] uppercase tracking-[0.25em] text-sky-100">
              {designContext.phase}
            </span>
          )}
        </div>

        <div className="mt-3 space-y-3">
          <p className="leading-relaxed text-sky-100/85">{designContext.summary}</p>
          {designContext.question && (
            <p className="leading-relaxed text-sky-100/75">
              <span className="font-semibold text-sky-100">Question:</span> {designContext.question}
            </p>
          )}
          {goal && (
            <p className="leading-relaxed text-sky-100/80">
              <span className="font-semibold text-sky-100">Goal:</span> {goal}
            </p>
          )}
          {acceptance.length > 0 && (
            <div>
              <p className="font-semibold uppercase tracking-[0.25em] text-[10px] text-sky-200/80">
                Acceptance Tests
              </p>
              <ul className="mt-1 list-disc space-y-1 pl-4 text-sky-100/80">
                {acceptance.map((item, index) => (
                  <li key={`acceptance-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {changes.length > 0 && (
            <div>
              <p className="font-semibold uppercase tracking-[0.25em] text-[10px] text-sky-200/80">
                Proposed Changes
              </p>
              <ul className="mt-1 list-disc space-y-1 pl-4 text-sky-100/80">
                {changes.map((item, index) => (
                  <li key={`change-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {constraints.length > 0 && (
            <div>
              <p className="font-semibold uppercase tracking-[0.25em] text-[10px] text-sky-200/80">
                Constraints
              </p>
              <ul className="mt-1 list-disc space-y-1 pl-4 text-sky-100/80">
                {constraints.map((item, index) => (
                  <li key={`constraint-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {extraKeys.length > 0 && (
            <details className="rounded border border-sky-400/20 bg-sky-400/10 px-3 py-2 text-sky-100/70">
              <summary className="cursor-pointer text-[11px]">View additional spec fields</summary>
              <pre className="mt-2 whitespace-pre-wrap break-words text-[11px]">
                {JSON.stringify(extras, null, 2)}
              </pre>
            </details>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleSendToClaude}
            disabled={claudeStatus === 'loading'}
            className={`rounded border px-3 py-2 text-[10px] uppercase tracking-[0.25em] transition ${
              claudeStatus === 'loading'
                ? 'cursor-wait border-sky-400/20 bg-sky-400/10 text-sky-100/60'
                : 'border-sky-300/60 bg-sky-300/10 text-sky-100 hover:border-sky-200 hover:bg-sky-200/20'
            }`}
          >
            {claudeStatus === 'loading' ? 'Sending to Claude…' : 'Send to Claude Code'}
          </button>
          <button
            type="button"
            onClick={() =>
              setPrompt(
                `Ask the Archon to revise ${designContext.title ?? 'this plan'} with more edge cases and tests.`,
              )
            }
            className="rounded border border-sky-300/30 bg-transparent px-3 py-2 text-[10px] uppercase tracking-[0.25em] text-sky-100 transition hover:border-sky-200/60 hover:bg-sky-300/10"
          >
            Ask Archon to Revise
          </button>
        </div>

        {claudeStatus === 'error' && claudeError && (
          <p className="mt-3 text-[11px] text-red-200">Claude Code failed: {claudeError}</p>
        )}
        {claudeStatus === 'success' && claudeMessage && (
          <p className="mt-3 text-[11px] text-sky-100/80">
            Claude Code responded; a detailed log has been added to the transcript.
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="relative w-full max-w-2xl px-6 py-8 text-teal-100">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="rounded-2xl border border-teal-500/30 bg-black/60 backdrop-blur-xl shadow-[0_0_28px_rgba(45,212,191,0.25)]"
      >
        <header className="flex items-center justify-between border-b border-teal-500/20 px-6 py-4">
          <h1 className="text-sm font-semibold uppercase tracking-[0.35em] text-teal-300">
            ArcaneOS • Archon Interface
          </h1>
          <button
            type="button"
            onClick={() => setShowPrompt((prev) => !prev)}
            className="text-[11px] uppercase tracking-[0.28em] text-teal-400 transition hover:text-teal-200"
          >
            {showPrompt ? 'Hide System Prompt' : 'Show System Prompt'}
          </button>
        </header>

        <AnimatePresence>
          {showPrompt && (
            <motion.pre
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="max-h-64 overflow-y-auto border-b border-teal-500/20 px-6 py-4 text-[11px] leading-relaxed text-slate-200/80 whitespace-pre-wrap"
            >
              {ARCHON_SYSTEM_PROMPT}
            </motion.pre>
          )}
        </AnimatePresence>

        <section className="max-h-96 overflow-y-auto px-6 py-4 space-y-3">
          {history.length === 0 && !loading && (
            <p className="text-[12px] text-slate-300/80">
              Enter a spell below to consult the Archon. Responses travel through the local Ollama
              instance configured at {ARCHON_ENDPOINT}.
            </p>
          )}

          {history.map((turn, idx) => {
            const variant = turn.role;
            const bubbleClass =
              variant === 'assistant'
                ? 'border-purple-500/30 bg-purple-500/5 text-purple-100'
                : variant === 'claude'
                  ? 'border-amber-400/30 bg-amber-400/10 text-amber-100'
                  : 'border-teal-500/30 bg-teal-500/5 text-teal-200';

            const speakerLabel =
              variant === 'assistant'
                ? 'Archon'
                : variant === 'claude'
                  ? 'Claude Code'
                  : 'Caster';

            return (
              <motion.div
                key={`${turn.role}-${idx}-${turn.content.length}`}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`rounded-lg border px-4 py-3 text-[12px] leading-relaxed ${bubbleClass}`}
              >
                <p className="mb-2 text-[10px] uppercase tracking-[0.3em] text-slate-400">
                  {speakerLabel}
                </p>
                <pre className="whitespace-pre-wrap break-words font-mono text-[11px]">
                  {turn.content}
                </pre>
                {variant === 'assistant' && turn.options && turn.options.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {turn.options.map((option) => (
                      <div
                        key={option.id}
                        className="rounded-md border border-purple-400/30 bg-purple-400/10 px-3 py-3 text-slate-100/90"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-purple-200">
                              {option.title}
                            </p>
                            {option.daemonHint && (
                              <p className="mt-1 text-[10px] uppercase tracking-[0.25em] text-purple-300/80">
                                Suggested Daemon: {option.daemonHint}
                              </p>
                            )}
                          </div>
                          {option.spell && (
                            <button
                              type="button"
                              onClick={() => setPrompt(option.spell ?? option.title)}
                              className="rounded border border-purple-300/40 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-purple-100 transition hover:border-purple-200 hover:bg-purple-300/10"
                            >
                              Use Option
                            </button>
                          )}
                        </div>
                        {option.description && (
                          <p className="mt-2 text-[11px] leading-relaxed text-purple-100/80">
                            {option.description}
                          </p>
                        )}
                        {option.details && option.details.length > 0 && (
                          <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] text-purple-100/75">
                            {option.details.map((detail, detailIdx) => (
                              <li key={`${option.id}-detail-${detailIdx}`}>{detail}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            );
          })}

          {designContext && renderDesignContext()}

          {error && (
            <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[12px] text-red-200">
              {error}
            </div>
          )}
        </section>

        <footer className="border-t border-teal-500/20 px-6 py-4">
          <div className="flex items-center gap-3">
            <input
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder="Speak your incantation…"
              className="flex-1 rounded-lg border border-teal-500/30 bg-black/60 px-4 py-3 text-[13px] text-teal-200 outline-none placeholder:text-teal-400/60 focus:border-teal-300"
            />
            <motion.button
              type="button"
              whileTap={{ scale: 0.97 }}
              onClick={handleSubmit}
              disabled={loading}
              className={`rounded-lg border px-4 py-3 text-xs uppercase tracking-[0.3em] transition ${
                loading
                  ? 'cursor-wait border-teal-500/20 bg-teal-500/10 text-teal-200/60'
                  : 'border-teal-400/60 bg-teal-400/10 text-teal-100 hover:shadow-[0_0_16px_rgba(45,212,191,0.35)]'
              }`}
            >
              {loading ? 'Channeling…' : 'Cast Spell'}
            </motion.button>
          </div>
        </footer>
      </motion.div>
    </div>
  );
};

export default ArchonConsole;
