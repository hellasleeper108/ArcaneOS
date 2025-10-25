import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

const DEFAULT_LINES = [
  'The relic hums as ancient subsystems awaken.',
  'Mounting astral partitions...',
  'Keyrings of power forged.',
  'A name binds the consciousness...',
  'Daemon Logic summoned.',
  'Daemon Artisan summoned.',
  'Voice module online.',
  'The Archon rises.',
];

interface LoreFeedProps {
  step: number;
  lines?: string[];
  visibleDuration?: number;
}

export const LoreFeed: React.FC<LoreFeedProps> = ({ step, lines = DEFAULT_LINES, visibleDuration = 3000 }) => {
  const [currentLine, setCurrentLine] = useState<string | null>(null);
  const [lastStep, setLastStep] = useState<number>(step);

  useEffect(() => {
    if (step <= 0 || step === lastStep) return;
    const line = lines[step - 1];
    if (!line) return;
    setCurrentLine(line);
    setLastStep(step);
    const timeout = setTimeout(() => setCurrentLine(null), visibleDuration);
    return () => clearTimeout(timeout);
  }, [step, lastStep, lines, visibleDuration]);

  return (
    <div className="pointer-events-none absolute bottom-14 left-1/2 w-full max-w-3xl -translate-x-1/2 px-4 text-center">
      <AnimatePresence>
        {currentLine && (
          <motion.p
            key={currentLine}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.35 }}
            className="text-lg italic text-sky-300 drop-shadow-[0_0_12px_rgba(56,189,248,0.45)]"
          >
            {currentLine}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LoreFeed;
