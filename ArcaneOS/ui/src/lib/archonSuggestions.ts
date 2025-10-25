import type { ArchonOption } from './archonParsers';

export interface ChatTurnLike {
  role: 'user' | 'assistant' | 'claude';
  content: string;
  options?: ArchonOption[];
}

export interface ArchonSuggestion {
  id: string;
  title: string;
  description: string;
  spell: string;
  daemon?: string;
}

export interface DesignContextInfo {
  title?: string;
  phase?: string | null;
  delegateTarget?: string | null;
}

const FALLBACK_SUGGESTIONS: ArchonSuggestion[] = [
  {
    id: 'summon-claude',
    title: 'Summon Claude for diagnostics',
    description: 'Bring the logic keeper online to inspect recent changes.',
    spell: 'summon claude to inspect the latest code changes',
    daemon: 'claude',
  },
  {
    id: 'invoke-gemini',
    title: 'Invoke Gemini to ideate',
    description: 'Explore creative angles or UX beats before implementation.',
    spell: 'invoke gemini to brainstorm user experience refinements',
    daemon: 'gemini',
  },
  {
    id: 'invoke-liquidmetal',
    title: 'Invoke LiquidMetal to summarise',
    description: 'Request a fast synthesis of the current context.',
    spell: 'invoke liquidmetal to summarise the active threads and blockers',
    daemon: 'liquidmetal',
  },
  {
    id: 'reveal-state',
    title: 'Reveal current veil state',
    description: 'Check whether the realm shows fantasy or developer mode.',
    spell: 'reveal the current veil status',
  },
];

const KEYWORD_RULES: Array<{
  keywords: string[];
  suggestion: ArchonSuggestion;
}> = [
  {
    keywords: ['bug', 'error', 'fix', 'debug', 'exception', 'stack', 'traceback'],
    suggestion: {
      id: 'invoke-claude-debug',
      title: 'Invoke Claude to debug',
      description: 'Let Claude trace the issue with a targeted invocation.',
      spell: 'invoke claude to debug the failing module and suggest fixes',
      daemon: 'claude',
    },
  },
  {
    keywords: ['design', 'idea', 'brainstorm', 'concept', 'copy', 'story', 'narrative', 'ux', 'ui'],
    suggestion: {
      id: 'summon-gemini-ideate',
      title: 'Summon Gemini for concepts',
      description: 'Use Gemini to weave fresh concepts or copy variations.',
      spell: 'summon gemini to ideate on tone and concept',
      daemon: 'gemini',
    },
  },
  {
    keywords: ['summarise', 'summarize', 'summary', 'recap', 'digest', 'synthesise', 'synthesize'],
    suggestion: {
      id: 'invoke-liquidmetal-summary',
      title: 'Invoke LiquidMetal to recap',
      description: 'Ask LiquidMetal for a succinct briefing of the situation.',
      spell: 'invoke liquidmetal to summarise the recent archon dialogue',
      daemon: 'liquidmetal',
    },
  },
  {
    keywords: ['deploy', 'release', 'ship', 'plan', 'spec', 'implementation'],
    suggestion: {
      id: 'claude-plan',
      title: 'Have Claude draft a plan',
      description: 'Request a concrete implementation plan with tests.',
      spell: 'invoke claude to draft an actionable implementation plan',
      daemon: 'claude',
    },
  },
  {
    keywords: ['veil', 'fantasy', 'developer'],
    suggestion: {
      id: 'toggle-veil',
      title: 'Toggle the veil mode',
      description: 'Switch between fantasy presentation and developer tooling.',
      spell: 'reveal the veil and toggle the realm presentation',
    },
  },
];

const normalise = (text: string): string => text.trim().toLowerCase();

const latestUserUtterance = (history: ChatTurnLike[]): string => {
  const lastUser = [...history].reverse().find((turn) => turn.role === 'user');
  return lastUser?.content ?? '';
};

const collectSuggestionsFromHistory = (history: ChatTurnLike[]): ArchonSuggestion[] => {
  const lastAssistant = [...history]
    .reverse()
    .find((turn) => turn.role === 'assistant' && turn.options?.length);
  if (!lastAssistant?.options) {
    return [];
  }

  return lastAssistant.options.slice(0, 4).map((option, index) => ({
    id: option.id ?? `history-option-${index}`,
    title: option.title,
    description: option.description ?? option.details?.[0] ?? 'Recommended path from the Archon.',
    spell: option.spell ?? option.title,
    daemon: option.daemonHint,
  }));
};

const applyKeywordRules = (prompt: string, history: ChatTurnLike[]): ArchonSuggestion[] => {
  const context = `${prompt} ${latestUserUtterance(history)}`.trim();
  const text = normalise(context);
  if (!text) {
    return [];
  }

  return KEYWORD_RULES.filter((rule) => rule.keywords.some((keyword) => text.includes(keyword))).map(
    (rule) => rule.suggestion,
  );
};

const designContextSuggestions = (designContext: DesignContextInfo | null): ArchonSuggestion[] => {
  if (!designContext) {
    return [];
  }

  const title = designContext.title ?? 'this design plan';

  const suggestions: ArchonSuggestion[] = [
    {
      id: 'claude-code-send',
      title: 'Send to Claude Code',
      description: `Hand "${title}" to Claude Code for implementation.`,
      spell: `ask the archon to route "${title}" to claude code for implementation`,
      daemon: 'claude',
    },
    {
      id: 'archon-revise-design',
      title: 'Revise the design',
      description: 'Request revisions or additional edge cases before coding.',
      spell: 'ask the archon to refine the plan with extra validation and edge cases',
    },
  ];

  if (!designContext.delegateTarget) {
    suggestions.unshift({
      id: 'archon-route-design',
      title: 'Delegate via Archon',
      description: 'Let the Archon choose the best daemon to execute the plan.',
      spell: `ask the archon which daemon should execute "${title}"`,
    });
  }

  return suggestions;
};

const dedupeSuggestions = (suggestions: ArchonSuggestion[]): ArchonSuggestion[] => {
  const seen = new Set<string>();

  return suggestions.filter((suggestion) => {
    const key = suggestion.spell.toLowerCase();
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
};

export const deriveArchonSuggestions = (
  prompt: string,
  history: ChatTurnLike[],
  designContext: DesignContextInfo | null = null,
  desiredCount = 4,
): ArchonSuggestion[] => {
  const fromDesign = designContextSuggestions(designContext);
  const fromHistory = collectSuggestionsFromHistory(history);
  const fromKeywords = applyKeywordRules(prompt, history);

  const combined = dedupeSuggestions([
    ...fromDesign,
    ...fromHistory,
    ...fromKeywords,
    ...FALLBACK_SUGGESTIONS,
  ]);

  return combined.slice(0, desiredCount);
};
