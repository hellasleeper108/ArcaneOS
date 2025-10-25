import { parseArchonMessage } from '../archonParsers';

describe('parseArchonMessage', () => {
  it('returns plain text for simple string replies', () => {
    const parsed = parseArchonMessage('Insight arrives in whispers.');
    expect(parsed.displayText).toBe('Insight arrives in whispers.');
    expect(parsed.options).toBeUndefined();
    expect(parsed.designSpec).toBeNull();
    expect(parsed.delegate).toBeUndefined();
  });

  it('parses JSON strings containing option entries', () => {
    const jsonReply = JSON.stringify([
      {
        id: 'plan-a',
        title: 'Invoke Claude for diagnostics',
        description: 'Best for code-level insights.',
        daemon: 'claude',
        plan: ['Collect recent logs', 'Summarise anomalies'],
      },
      {
        id: 'plan-b',
        title: 'Summon Gemini for ideation',
        spell: 'summon the dreamer to storyboard UI changes',
        notes: ['Focus on narrative tone', 'Keep latency low'],
      },
    ]);

    const parsed = parseArchonMessage(jsonReply);

    expect(parsed.displayText).toBe('Select one of these options:');
    expect(parsed.options).toHaveLength(2);
    expect(parsed.options?.[0]).toMatchObject({
      id: 'plan-a',
      title: 'Invoke Claude for diagnostics',
      description: 'Best for code-level insights.',
      daemonHint: 'claude',
      details: ['Collect recent logs', 'Summarise anomalies'],
    });
    expect(parsed.options?.[1]).toMatchObject({
      id: 'plan-b',
      title: 'Summon Gemini for ideation',
      spell: 'summon the dreamer to storyboard UI changes',
      details: ['Focus on narrative tone', 'Keep latency low'],
    });
    expect(parsed.designSpec).toBeNull();
  });

  it('extracts summary and options from object replies', () => {
    const replyObject = {
      summary: 'Three viable paths present themselves.',
      options: [
        'Summon Gemini to ideate UI vignettes',
        {
          title: 'Invoke LiquidMetal for synthesis',
          command: 'invoke liquidmetal to merge existing drafts',
        },
      ],
    };

    const parsed = parseArchonMessage(replyObject);
    expect(parsed.displayText).toBe('Three viable paths present themselves.');
    expect(parsed.options).toHaveLength(2);
    expect(parsed.options?.[0]).toMatchObject({
      title: 'Summon Gemini to ideate UI vignettes',
      spell: 'Summon Gemini to ideate UI vignettes',
    });
    expect(parsed.options?.[1]).toMatchObject({
      title: 'Invoke LiquidMetal for synthesis',
      spell: 'invoke liquidmetal to merge existing drafts',
    });
    expect(parsed.phase).toBeUndefined();
  });

  it('captures design specs and delegation metadata', () => {
    const designReply = JSON.stringify({
      phase: 'DESIGN',
      summary: 'Outlined a feature flow.',
      question: 'Ship to Claude Code or request revisions?',
      spec: {
        task_id: 'spec-123',
        title: 'Realtime presence indicator',
        goal: 'Show who is editing a document in real-time.',
      },
      delegate: {
        target: 'claude',
        spec: {
          task_id: 'spec-123',
          title: 'Realtime presence indicator',
          changes: [{ path: 'src/presence.ts', action: 'create' }],
        },
      },
    });

    const parsed = parseArchonMessage(designReply);
    expect(parsed.phase).toBe('DESIGN');
    expect(parsed.question).toBe('Ship to Claude Code or request revisions?');
    expect(parsed.summary).toBe('Outlined a feature flow.');
    expect(parsed.designSpec).toMatchObject({
      task_id: 'spec-123',
      title: 'Realtime presence indicator',
    });
    expect(parsed.delegate).toMatchObject({
      target: 'claude',
    });
    expect(parsed.delegate?.spec).toMatchObject({
      changes: [{ path: 'src/presence.ts', action: 'create' }],
    });
  });
});
