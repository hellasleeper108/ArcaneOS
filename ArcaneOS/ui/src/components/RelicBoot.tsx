import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import RelicVisuals from './RelicVisuals';
import LoreFeed from './LoreFeed';
import BootSound from '../lib/BootSound';
import {
  startHumIfNeeded,
  updateHumProgress,
  stopHum,
  playActivationSequence,
} from '../lib/VoiceManager';

interface RelicBootProps {
  onFinished?: () => void;
  archMode?: boolean;
}

type RitualStage = 'intro' | 'installing' | 'activation' | 'complete';

type ConsoleLine = {
  id: string;
  text: string;
  tone: 'boot' | 'prompt' | 'success' | 'error' | 'help';
};

type CommandStep = {
  command: string;
  successLogs: (input: string) => string[];
};

const BASE_BOOT_LINES = [
  '[BOOT] Relic core detected',
  '[BOOT] Mind-fragment integrity: partial',
  'To awaken the Archon, run: init-relic',
];

const ARCH_PRE_LOGS = [
  '[ARCH] Initializing Arch mirrorlist generator…',
  '[ARCH] Syncing crystalline pacman keys…',
  '[ARCH] Preparing spectral pacstrap manifests…',
];

const HUMOROUS_DEPS = [
  "checking dependency 'wyrm-breath'... done",
  "checking dependency 'obsidian-heart'... done",
  "checking dependency 'sigil-lattice'... done",
  "checking dependency 'synth-ether'... done",
  "checking dependency 'astral-rust'... done",
];

const ARCH_COMMANDS: CommandStep[] = [
  {
    command: 'load-mirrorlist',
    successLogs: () => [
      '[ARCH] Reflecting regional mirrors for optimal latency.',
      `[ARCH] ${HUMOROUS_DEPS[Math.floor(Math.random() * HUMOROUS_DEPS.length)]}`,
      '[ARCH] Mirrorlist committed to /etc/pacman.d/mirrorlist.',
    ],
  },
  {
    command: 'pacstrap /mnt base-essence',
    successLogs: () => [
      '[ARCH] Installing base essence packages into /mnt…',
      `[ARCH] ${HUMOROUS_DEPS[Math.floor(Math.random() * HUMOROUS_DEPS.length)]}`,
      '[ARCH] Base essence infusion complete.',
    ],
  },
  {
    command: 'genfstab -U /mnt >> /mnt/etc/fstab',
    successLogs: () => [
      '[ARCH] Generating fstab bindings with UUIDs…',
      `[ARCH] ${HUMOROUS_DEPS[Math.floor(Math.random() * HUMOROUS_DEPS.length)]}`,
      '[ARCH] fstab inscribed within /mnt/etc/fstab.',
    ],
  },
  {
    command: 'arch-chroot /mnt',
    successLogs: () => [
      '[ARCH] Entering chrooted realm…',
      '[ARCH] Base system ready. Handing ritual back to the Archon.',
    ],
  },
];

const RITUAL_COMMANDS: CommandStep[] = [
  {
    command: 'init-relic',
    successLogs: () => ['[RITUAL] Runic lattice initialized.'],
  },
  {
    command: 'mount /dev/soul /mnt',
    successLogs: () => ['[RITUAL] Soul conduit mounted at /mnt.'],
  },
  {
    command: 'generate-keyrings',
    successLogs: () => ['[RITUAL] Astral keyrings forged.'],
  },
  {
    command: 'assign-core-name',
    successLogs: (input: string) => {
      const name = input.trim().split(/\s+/).slice(1).join(' ');
      return [`[RITUAL] Core identity inscribed as "${name}".`];
    },
  },
  {
    command: 'install-daemon logic',
    successLogs: () => ['[RITUAL] Logic daemon integrated.'],
  },
  {
    command: 'install-daemon artisan',
    successLogs: () => ['[RITUAL] Artisan daemon attuned.'],
  },
  {
    command: 'enable-voice',
    successLogs: () => ['[RITUAL] Vocal resonators online.'],
  },
  {
    command: 'activate-archon',
    successLogs: () => ['[RITUAL] Archon awakened. Prepare for manifestation.'],
  },
];

const ERROR_LINES = [
  'The runes do not recognise that incantation.',
  'Command out of sequence. Realign your focus.',
];

const HELP_HEADER = 'Remaining incantations:';

const makeLineId = (() => {
  let counter = 0;
  return () => `line-${Date.now()}-${counter++}`;
})();

const RelicBoot: React.FC<RelicBootProps> = ({ onFinished, archMode = false }) => {
  const [stage, setStage] = useState<RitualStage>('intro');
  const [consoleLines, setConsoleLines] = useState<ConsoleLine[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [errorPulse, setErrorPulse] = useState(false);
  const [lastLoreStep, setLastLoreStep] = useState(0);
  const [bootReady, setBootReady] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  const introTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [awakeningTriggered, setAwakeningTriggered] = useState(false);

  const commandSequence = useMemo<CommandStep[]>(() => {
    if (!archMode) return RITUAL_COMMANDS;
    return [...ARCH_COMMANDS, ...RITUAL_COMMANDS];
  }, [archMode]);

  const totalSteps = commandSequence.length;
  const progress = useMemo(() => (stepIndex / totalSteps) * 100, [stepIndex, totalSteps]);

  const visualsProgress = useMemo(() => {
    if (stage === 'intro') return 0;
    if (stage === 'activation' || stage === 'complete') return 100;
    return progress;
  }, [stage, progress]);

  useEffect(() => {
    introTimerRef.current = setTimeout(() => {
      setStage('installing');
    }, 3000);
    return () => {
      if (introTimerRef.current) clearTimeout(introTimerRef.current);
      BootSound.stopAll();
      stopHum();
    };
  }, []);

  useEffect(() => {
    if (stage !== 'installing') return;
    startHumIfNeeded();
    updateHumProgress(progress);
  }, [stage, progress]);

  useEffect(() => {
    if (stage !== 'installing') return;
    if (consoleLines.length > 0) return;
    const baseLines = archMode ? [...ARCH_PRE_LOGS, ...BASE_BOOT_LINES] : BASE_BOOT_LINES;
    setConsoleLines(baseLines.map((text) => ({ id: makeLineId(), text, tone: 'boot' })));
    setTimeout(() => {
      setBootReady(true);
      inputRef.current?.focus();
    }, 400);
  }, [stage, archMode, consoleLines.length]);

  useEffect(() => {
    updateHumProgress(progress);
  }, [progress]);

  const appendLines = useCallback(
    (entries: ConsoleLine | ConsoleLine[]) => {
      setConsoleLines((prev) => [...prev, ...(Array.isArray(entries) ? entries : [entries])]);
    },
    [],
  );

  const expectedStep = commandSequence[stepIndex];

  const remainingCommands = useMemo(
    () => commandSequence.slice(stepIndex).map((step) => step.command),
    [commandSequence, stepIndex],
  );

  const handleSubmit = useCallback(
    (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (stage !== 'installing' || !bootReady || stepIndex >= commandSequence.length) return;
      const raw = inputValue;
      const trimmed = raw.trim();
      if (!trimmed) return;

      appendLines({ id: makeLineId(), text: `> ${trimmed}`, tone: 'prompt' });

      if (trimmed.toLowerCase() === 'help') {
        appendLines([
          { id: makeLineId(), text: HELP_HEADER, tone: 'help' },
          ...remainingCommands.map((cmd) => ({ id: makeLineId(), text: ` - ${cmd}`, tone: 'help' as const })),
        ]);
        setInputValue('');
        return;
      }

      const expected = commandSequence[stepIndex];
      const expectAssign = expected.command === 'assign-core-name';
      const commandMatch = expectAssign
        ? trimmed.startsWith('assign-core-name ')
        : trimmed === expected.command;

      if (!commandMatch) {
        appendLines({
          id: makeLineId(),
          text: ERROR_LINES[Math.floor(Math.random() * ERROR_LINES.length)],
          tone: 'error',
        });
        setErrorPulse(true);
        setTimeout(() => setErrorPulse(false), 400);
        setInputValue('');
        return;
      }

      const successLogs = expected.successLogs(trimmed).map((text) => ({
        id: makeLineId(),
        text,
        tone: 'success' as const,
      }));
      appendLines(successLogs);
      setLastLoreStep((prev) => prev + 1);
      BootSound.playTone(stepIndex);

      const nextIndex = stepIndex + 1;
      setStepIndex(nextIndex);
      updateHumProgress((nextIndex / commandSequence.length) * 100);

      if (expected.command === 'arch-chroot /mnt') {
        appendLines({
          id: makeLineId(),
          text: '[ARCH] Chroot environment established. Continue with ritual directives…',
          tone: 'boot',
        });
      }

      setInputValue('');
    },
    [stage, bootReady, stepIndex, commandSequence, inputValue, appendLines, remainingCommands],
  );

  useEffect(() => {
    if (!awakeningTriggered && stepIndex >= commandSequence.length) {
      setAwakeningTriggered(true);
      stopHum();
      BootSound.stopAll();
      setStage('activation');
      playActivationSequence()
        .catch(() => undefined)
        .then(() => {
          setStage('complete');
          onFinished?.();
        });
    }
  }, [awakeningTriggered, stepIndex, commandSequence.length, onFinished]);

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#02040A]">
      <motion.div className="absolute inset-0" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <RelicVisuals progress={visualsProgress} />
      </motion.div>

      <AnimatePresence>
        {stage === 'activation' && (
          <motion.div
            key="activation-mask"
            className="absolute inset-0 bg-black"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.8 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {stage !== 'intro' && stage !== 'complete' && (
          <motion.div
            key="terminal"
            className="absolute inset-x-0 bottom-0 flex w-full justify-center pb-12"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            <motion.div
              className={`terminal-shell w-full max-w-4xl rounded-2xl border border-emerald-200/20 bg-[#030508]/90 px-6 py-6 shadow-[0_0_35px_rgba(34,197,94,0.25)] ${
                errorPulse ? 'ring-2 ring-rose-400/60' : ''
              }`}
            >
              <div className="h-[45vh] overflow-y-auto pr-1 text-emerald-200">
                {consoleLines.map((line) => (
                  <motion.p
                    key={line.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`whitespace-pre-wrap text-sm leading-7 ${
                      line.tone === 'success'
                        ? 'text-emerald-100'
                        : line.tone === 'error'
                          ? 'text-rose-300'
                          : line.tone === 'help'
                            ? 'text-cyan-200'
                            : 'text-emerald-200'
                    }`}
                  >
                    {line.text}
                  </motion.p>
                ))}
              </div>

              <form onSubmit={handleSubmit} className="mt-4 flex items-center text-sm text-emerald-200">
                <span className="mr-3 text-emerald-400">{'>'}</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(event) => setInputValue(event.target.value)}
                  disabled={stage !== 'installing'}
                  spellCheck={false}
                  autoComplete="off"
                  className="flex-1 bg-transparent text-emerald-100 outline-none placeholder:text-emerald-500"
                  placeholder={
                    bootReady && expectedStep ? `Next: ${expectedStep.command}` : 'Initializing…'
                  }
                />
                <span className="ml-3 cursor-glow" />
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <LoreFeed step={lastLoreStep} />

      <div className="pointer-events-none absolute left-1/2 top-8 -translate-x-1/2 text-center text-xs uppercase tracking-[0.4em] text-emerald-200/60">
        {archMode && stage === 'installing'
          ? 'ARCH INSTALLATION RITUAL IN PROGRESS'
          : stage === 'intro'
            ? 'Stabilizing relic signature…'
            : stage === 'activation'
              ? 'Archon activation sequence complete'
              : `Ritual Progress ${Math.round(visualsProgress)}%`}
      </div>
    </div>
  );
};

export default RelicBoot;
