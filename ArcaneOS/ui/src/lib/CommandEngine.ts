import { useCallback, useMemo, useState } from 'react';

export interface CommandDefinition {
  id: string;
  matcher: (input: string) => boolean;
  successMessage: (input: string) => string;
  display: string;
}

export interface CommandValidationResult {
  valid: boolean;
  message: string;
  step: number;
}

export interface CommandHistoryEntry {
  input: string;
  output: string;
  success: boolean;
  step: number | null;
  type: 'success' | 'error' | 'help';
}

export const COMMAND_SEQUENCE: CommandDefinition[] = [
  {
    id: 'init-relic',
    matcher: (input) => input.trim() === 'init-relic',
    successMessage: () => 'Runic lattice initialized.',
    display: 'init-relic',
  },
  {
    id: 'mount-soul',
    matcher: (input) => input.trim() === 'mount /dev/soul /mnt',
    successMessage: () => 'Soul conduit mounted at /mnt.',
    display: 'mount /dev/soul /mnt',
  },
  {
    id: 'generate-keyrings',
    matcher: (input) => input.trim() === 'generate-keyrings',
    successMessage: () => 'Astral keyrings forged.',
    display: 'generate-keyrings',
  },
  {
    id: 'assign-core-name',
    matcher: (input) => /^assign-core-name\s+.+$/i.test(input.trim()),
    successMessage: (input) => {
      const name = input.trim().split(/\s+/).slice(1).join(' ');
      return `Core identity inscribed as "${name}".`;
    },
    display: 'assign-core-name <name>',
  },
  {
    id: 'install-daemon-logic',
    matcher: (input) => input.trim() === 'install-daemon logic',
    successMessage: () => 'Logic daemon integrated.',
    display: 'install-daemon logic',
  },
  {
    id: 'install-daemon-artisan',
    matcher: (input) => input.trim() === 'install-daemon artisan',
    successMessage: () => 'Artisan daemon attuned.',
    display: 'install-daemon artisan',
  },
  {
    id: 'enable-voice',
    matcher: (input) => input.trim() === 'enable-voice',
    successMessage: () => 'Vocal resonators online.',
    display: 'enable-voice',
  },
  {
    id: 'activate-archon',
    matcher: (input) => input.trim() === 'activate-archon',
    successMessage: () => 'Archon awakened. Prepare for manifestation.',
    display: 'activate-archon',
  },
];

export const validateCommand = (input: string): CommandValidationResult => {
  const trimmed = input.trim();
  for (let step = 0; step < COMMAND_SEQUENCE.length; step += 1) {
    const command = COMMAND_SEQUENCE[step];
    if (command.matcher(trimmed)) {
      return {
        valid: true,
        message: command.successMessage(trimmed),
        step,
      };
    }
  }
  return {
    valid: false,
    message: 'The runes do not recognize that incantation.',
    step: -1,
  };
};

interface UseCommandEngineResult {
  handleInput: (rawInput: string) => CommandValidationResult;
  history: CommandHistoryEntry[];
  progress: number;
  completed: boolean;
  currentStep: number;
  nextExpectedCommand: string | null;
}

export const useCommandEngine = (): UseCommandEngineResult => {
  const [currentStep, setCurrentStep] = useState(0);
  const [history, setHistory] = useState<CommandHistoryEntry[]>([]);
  const [completed, setCompleted] = useState(false);

  const progress = useMemo(() => {
    if (COMMAND_SEQUENCE.length === 0) return 100;
    return Math.min((currentStep / COMMAND_SEQUENCE.length) * 100, 100);
  }, [currentStep]);

  const nextExpectedCommand = useMemo(
    () => COMMAND_SEQUENCE[currentStep]?.display ?? null,
    [currentStep],
  );

  const handleInput = useCallback(
    (rawInput: string) => {
      const input = rawInput.trim();
      if (!input) {
        const silentMessage = 'Silence carries no power.';
        setHistory((prev) => [
          ...prev,
          {
            input: rawInput,
            output: silentMessage,
            success: false,
            step: currentStep,
            type: 'error',
          },
        ]);
        return { valid: false, message: silentMessage, step: currentStep };
      }

      if (input.toLowerCase() === 'help') {
        const remaining = COMMAND_SEQUENCE.slice(currentStep).map((cmd) => `- ${cmd.display}`);
        const helpMessage =
          remaining.length > 0
            ? ['Remaining incantations:', ...remaining].join('\n')
            : 'All rituals complete. No commands remain.';
        setHistory((prev) => [
          ...prev,
          {
            input: rawInput,
            output: helpMessage,
            success: false,
            step: currentStep,
            type: 'help',
          },
        ]);
        return { valid: false, message: helpMessage, step: currentStep };
      }

      const result = validateCommand(input);

      if (!result.valid) {
        if (input.toLowerCase() === 'cat /etc/archon.conf') {
          const asciiArt = ['   /\\\\', '  /__\\\\   THE ARCHON', '  \\  /', '   \\/'].join('\n');
          const message = `${asciiArt}\nConfiguration: fragmented but awakening.`;
          setHistory((prev) => [
            ...prev,
            {
              input: rawInput,
              output: message,
              success: false,
              step: currentStep,
              type: 'help',
            },
          ]);
          return { valid: false, message, step: currentStep };
        }
        setHistory((prev) => [
          ...prev,
          {
            input: rawInput,
            output: result.message,
            success: false,
            step: currentStep,
            type: 'error',
          },
        ]);
        return { valid: false, message: result.message, step: currentStep };
      }

      if (result.step !== currentStep) {
        const misorderMessage = 'The ritual must proceed in the ordained order.';
        setHistory((prev) => [
          ...prev,
          {
            input: rawInput,
            output: misorderMessage,
            success: false,
            step: currentStep,
            type: 'error',
          },
        ]);
        return { valid: false, message: misorderMessage, step: currentStep };
      }

      setHistory((prev) => [
        ...prev,
        {
          input: rawInput,
          output: result.message,
          success: true,
          step: currentStep,
          type: 'success',
        },
      ]);

      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      if (nextStep >= COMMAND_SEQUENCE.length) {
        setCompleted(true);
      }

      return result;
    },
    [currentStep],
  );

  return {
    handleInput,
    history,
    progress,
    completed,
    currentStep,
    nextExpectedCommand,
  };
};

export default useCommandEngine;
