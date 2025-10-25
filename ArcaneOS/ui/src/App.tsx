import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import ArchonSigil from './components/ArchonSigil';
import ParticleField from './components/ParticleField';
import ArchonConsole from './components/ArchonConsole';
import VeilToggle from './components/VeilToggle';
import RelicBoot from './components/RelicBoot';
import { startBackgroundScore, stopBackgroundScore } from './lib/BackgroundScore';

const INIT_COMPLETE_CUE = '/sounds/system/init-complete.mp3';

const App: React.FC = () => {
  const initialActivated = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem('archonActivated') === 'true';
  }, []);

  const [veil, setVeil] = useState(true);
  const [activated, setActivated] = useState(initialActivated);
  const [bootVisible, setBootVisible] = useState(!initialActivated);

  const handleFinished = useCallback(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('archonActivated', 'true');
    }
    setActivated(true);

    // Only play audio if enabled
    const audioEnabled = process.env.REACT_APP_ENABLE_AUDIO === 'true';
    if (audioEnabled) {
      try {
        const cue = new Audio(INIT_COMPLETE_CUE);
        cue.volume = 0.55;
        void cue.play().catch(() => {});
      } catch {
        /* ignore cue errors */
      }
    }

    setTimeout(() => setBootVisible(false), 1000);
  }, []);

  useEffect(() => {
    if (!bootVisible && !activated) {
      setBootVisible(true);
    }
  }, [activated, bootVisible]);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    const { body } = document;
    if (bootVisible) body.classList.add('relic-boot-active');
    else body.classList.remove('relic-boot-active');
    return () => {
      body.classList.remove('relic-boot-active');
    };
  }, [bootVisible]);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    const { body } = document;
    if (veil) body.classList.add('veil-enabled');
    else body.classList.remove('veil-enabled');
    return () => {
      body.classList.remove('veil-enabled');
    };
  }, [veil]);

  useEffect(() => {
    // Disable background audio in production (audio files not in repo)
    const audioEnabled = process.env.REACT_APP_ENABLE_AUDIO === 'true';
    if (!audioEnabled) {
      console.log('Background audio disabled (REACT_APP_ENABLE_AUDIO not set)');
      return;
    }

    let interactionHandler: (() => void) | undefined;
    const start = () => {
      startBackgroundScore().catch(() => undefined);
    };
    start();
    if (typeof document !== 'undefined') {
      interactionHandler = () => {
        startBackgroundScore().catch(() => undefined);
      };
      document.addEventListener('pointerdown', interactionHandler, { once: true });
    }
    return () => {
      if (interactionHandler) {
        document.removeEventListener('pointerdown', interactionHandler);
      }
      stopBackgroundScore();
    };
  }, []);

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#03060C] text-teal-100">
      <div className="grain-overlay" />
      <AnimatePresence>
        {bootVisible && (
          <motion.div
            key="relic-boot"
            className="absolute inset-0 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <RelicBoot onFinished={handleFinished} />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {activated && (
          <motion.div
            key="arcaneos-main"
            className="relative z-10 min-h-screen w-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={veil ? 'fantasy' : 'dev'}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: 'easeInOut' }}
                className={`absolute inset-0 ${
                  veil
                    ? 'bg-[radial-gradient(circle_at_center,#12233f_0%,#05080C_65%,#010203_100%)]'
                    : 'bg-[radial-gradient(circle_at_center,#0f172a_0%,#05060a_65%,#02030a_100%)]'
                }`}
              />
            </AnimatePresence>

            {veil && <ParticleField veil={veil} />}

            <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 py-12">
              <ArchonSigil isFantasyMode={veil} />
              <ArchonConsole />
            </div>

            <VeilToggle veilEnabled={veil} onToggle={(next) => setVeil(next)} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
