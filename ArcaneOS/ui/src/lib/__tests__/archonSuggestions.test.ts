import { deriveArchonSuggestions } from '../archonSuggestions';
import type { ArchonOption } from '../archonParsers';

describe('deriveArchonSuggestions', () => {
  const historyWithOptions = [
    {
      role: 'assistant' as const,
      content: 'Options from the Archon.',
      options: [
        {
          id: 'opt-1',
          title: 'Invoke Claude to patch',
          description: 'Let Claude apply targeted fixes.',
          spell: 'invoke claude to patch the failing tests',
          daemonHint: 'claude',
        } as ArchonOption,
      ],
    },
  ];

  it('returns keyword-based suggestions', () => {
    const result = deriveArchonSuggestions('We have a critical bug in production', [], null);
    expect(result.some((entry) => entry.id === 'invoke-claude-debug')).toBe(true);
  });

  it('folds in the most recent assistant options', () => {
    const result = deriveArchonSuggestions('What next?', historyWithOptions, null);
    expect(result.find((entry) => entry.id === 'opt-1')).toBeTruthy();
  });

  it('caps the number of suggestions at four', () => {
    const result = deriveArchonSuggestions('', [], null);
    expect(result).toHaveLength(4);
  });

  it('prioritises design context suggestions', () => {
    const result = deriveArchonSuggestions(
      'Here is the latest spec',
      [],
      { title: 'Realtime presence indicator', delegateTarget: 'claude' },
    );
    expect(result[0].id).toBe('claude-code-send');
    expect(result.some((entry) => entry.id === 'archon-revise-design')).toBe(true);
  });
});
