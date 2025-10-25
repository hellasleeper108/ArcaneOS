export interface ArchonOption {
  id: string;
  title: string;
  description?: string;
  spell?: string;
  details?: string[];
  daemonHint?: string;
}

export interface ArchonDelegate {
  target?: string;
  spec?: Record<string, unknown> | null;
}

export interface ParsedArchonMessage {
  displayText: string;
  options?: ArchonOption[];
  phase?: string;
  summary?: string;
  reasoning?: string;
  question?: string;
  designSpec?: Record<string, unknown> | null;
  delegate?: ArchonDelegate | null;
  raw?: unknown;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  Boolean(value) && typeof value === 'object' && !Array.isArray(value);

const toTextArray = (value: unknown): string[] | undefined => {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const lines = value
    .map((entry) => {
      if (typeof entry === 'string') {
        return entry.trim();
      }

      if (isRecord(entry)) {
        const textLike =
          typeof entry.text === 'string'
            ? entry.text
            : typeof entry.description === 'string'
              ? entry.description
              : undefined;
        return textLike?.trim();
      }

      return undefined;
    })
    .filter((line): line is string => Boolean(line));

  return lines.length ? lines : undefined;
};

const normaliseOptions = (rawOptions: unknown): ArchonOption[] | undefined => {
  if (!rawOptions) {
    return undefined;
  }

  const entries = Array.isArray(rawOptions) ? rawOptions : [rawOptions];
  const options: ArchonOption[] = [];

  entries.forEach((entry, index) => {
    if (!entry) return;

    if (typeof entry === 'string') {
      const text = entry.trim();
      if (text) {
        options.push({
          id: `option-${index}`,
          title: text,
          spell: text,
        });
      }
      return;
    }

    if (isRecord(entry)) {
      const titleValue =
        typeof entry.title === 'string'
          ? entry.title
          : typeof entry.name === 'string'
            ? entry.name
            : typeof entry.label === 'string'
              ? entry.label
              : undefined;
      const title = titleValue?.trim() ?? `Option ${index + 1}`;

      const descriptionValue =
        typeof entry.description === 'string'
          ? entry.description
          : typeof entry.summary === 'string'
            ? entry.summary
            : undefined;

      const spellValue =
        typeof entry.spell === 'string'
          ? entry.spell
          : typeof entry.command === 'string'
            ? entry.command
            : typeof entry.task === 'string'
              ? entry.task
              : typeof entry.text === 'string'
                ? entry.text
                : undefined;

      const daemonValue =
        typeof entry.daemon === 'string'
          ? entry.daemon
          : typeof entry.recommendedDaemon === 'string'
            ? entry.recommendedDaemon
            : undefined;

      const details =
        toTextArray(entry.plan) ||
        toTextArray(entry.steps) ||
        toTextArray(entry.notes);

      options.push({
        id: typeof entry.id === 'string' && entry.id.trim() ? entry.id.trim() : `option-${index}`,
        title,
        description: descriptionValue?.trim(),
        spell: spellValue?.trim(),
        details,
        daemonHint: daemonValue?.trim(),
      });
    }
  });

  return options.length ? options : undefined;
};

const parsedFromObject = (
  obj: Record<string, unknown>,
  fallback: string,
): { displayText: string; options?: ArchonOption[] } => {
  const summaryValue =
    typeof obj.summary === 'string'
      ? obj.summary
      : typeof obj.narration === 'string'
        ? obj.narration
        : typeof obj.reasoning === 'string'
          ? obj.reasoning
          : typeof obj.message === 'string'
            ? obj.message
            : undefined;

  const options =
    normaliseOptions(obj.options) ||
    normaliseOptions(obj.choices) ||
    (Array.isArray(obj.plan) && obj.plan.every((step) => typeof step === 'string')
      ? normaliseOptions(obj.plan)
      : undefined);

  const displayText =
    (summaryValue ?? fallback ?? '').trim() ||
    fallback ||
    'The Archon speaks in whispers beyond structure.';

  return { displayText, options };
};

const enrichWithMetadata = (
  base: { displayText: string; options?: ArchonOption[] },
  source: Record<string, unknown>,
  fallback: string,
): ParsedArchonMessage => {
  const phase = typeof source.phase === 'string' ? source.phase : undefined;
  const summary = typeof source.summary === 'string' ? source.summary : undefined;
  const reasoning = typeof source.reasoning === 'string' ? source.reasoning : undefined;
  const question =
    typeof source.question === 'string'
      ? source.question
      : typeof source.prompt === 'string'
        ? source.prompt
        : undefined;

  const specCandidate = isRecord(source.spec) ? (source.spec as Record<string, unknown>) : undefined;

  const delegateRecord = isRecord(source.delegate)
    ? (source.delegate as Record<string, unknown>)
    : undefined;

  const delegate: ArchonDelegate | null = delegateRecord
    ? {
        target: typeof delegateRecord.target === 'string' ? delegateRecord.target : undefined,
        spec: isRecord(delegateRecord.spec) ? (delegateRecord.spec as Record<string, unknown>) : null,
      }
    : null;

  const designSpec = delegate?.spec ?? specCandidate ?? null;

  return {
    ...base,
    phase,
    summary,
    reasoning,
    question,
    designSpec,
    delegate,
    raw: source,
  };
};

export const parseArchonMessage = (message: unknown): ParsedArchonMessage => {
  const fallback = typeof message === 'string' ? message.trim() : '';

  if (typeof message === 'string') {
    const trimmed = message.trim();
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
      try {
        const json = JSON.parse(trimmed);
        if (Array.isArray(json)) {
          const options = normaliseOptions(json);
          return {
            displayText: options ? 'Select one of these options:' : trimmed,
            options,
            raw: json,
          };
        }

        if (isRecord(json)) {
          const base = parsedFromObject(json, fallback);
          return enrichWithMetadata(base, json, fallback);
        }
      } catch {
        // ignore malformed JSON and fall through
      }
    }

    return { displayText: trimmed || 'The Archon remains silent.', raw: message };
  }

  if (isRecord(message)) {
    const base = parsedFromObject(message, fallback);
    return enrichWithMetadata(base, message, fallback);
  }

  return { displayText: fallback || 'The Archon remains silent.', raw: message };
};

export type { ArchonOption as ParsedArchonOption };
