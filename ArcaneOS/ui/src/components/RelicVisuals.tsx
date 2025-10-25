import React, { useEffect, useMemo, useRef, useState } from 'react';
import { motion, useAnimationControls } from 'framer-motion';

interface RelicVisualsProps {
  progress: number;
  onFinished?: () => void;
}

const RUNE_SYMBOLS = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚺ', 'ᚾ'];
const clamp = (value: number, min = 0, max = 100) => Math.min(Math.max(value, min), max);

const Particles: React.FC<{ active: boolean; finale: boolean }> = ({ active, finale }) => {
  if (!active) return null;
  return (
    <motion.div
      className="absolute inset-0"
      initial={{ opacity: 0 }}
      animate={{ opacity: finale ? [0.8, 1, 0] : 0.8, scale: finale ? [1, 3, 0.5] : 1 }}
      transition={{ duration: finale ? 3.2 : 1, ease: finale ? 'easeOut' : 'linear', repeat: finale ? 0 : Infinity }}
    >
      {Array.from({ length: 40 }).map((_, idx) => {
        const angle = (idx / 40) * Math.PI * 2;
        const radius = 100 + (idx % 7) * 8;
        const baseDuration = 10 + (idx % 5);
        return (
          <motion.span
            key={`particle-${idx}`}
            className="absolute h-1 w-1 rounded-full bg-teal-100 shadow-[0_0_10px_rgba(56,189,248,0.75)]"
            style={{ top: '50%', left: '50%', marginTop: -0.5, marginLeft: -0.5 }}
            animate={{
              x: [
                radius * Math.cos(angle),
                radius * Math.cos(angle + Math.PI / 2),
                radius * Math.cos(angle + Math.PI),
                radius * Math.cos(angle + (3 * Math.PI) / 2),
                radius * Math.cos(angle * 2),
              ],
              y: [
                radius * Math.sin(angle),
                radius * Math.sin(angle + Math.PI / 2),
                radius * Math.sin(angle + Math.PI),
                radius * Math.sin(angle + (3 * Math.PI) / 2),
                radius * Math.sin(angle * 2),
              ],
              opacity: finale ? [0.8, 1, 0] : [0, 1, 0.2, 1, 0],
            }}
            transition={{
              duration: finale ? baseDuration / 2 : baseDuration,
              repeat: finale ? 0 : Infinity,
              ease: 'linear',
              delay: idx * 0.12,
            }}
          />
        );
      })}
    </motion.div>
  );
};

const RelicVisuals: React.FC<RelicVisualsProps> = ({ progress, onFinished }) => {
  const normalized = clamp(progress);
  const [finale, setFinale] = useState(false);
  const [flashOpacity, setFlashOpacity] = useState(0);
  const [particlesActive, setParticlesActive] = useState(true);

  const containerControls = useAnimationControls();
  const runeControls = useAnimationControls();
  const shimmerControls = useAnimationControls();

  const finaleRef = useRef<boolean>(false);
  const flashTimeoutRef = useRef<number | undefined>(undefined);
  const finishTimeoutRef = useRef<number | undefined>(undefined);

  const stage = useMemo(() => {
    if (normalized >= 100) return 'flare';
    if (normalized >= 90) return 'preflare';
    if (normalized >= 60) return 'swirl';
    if (normalized >= 30) return 'bright';
    return 'dim';
  }, [normalized]);

  useEffect(() => {
    if (normalized < 100) return;
    if (finaleRef.current) return;
    finaleRef.current = true;
    setFinale(true);
    containerControls.start({
      scale: [1, 1.4, 1.05, 1],
      opacity: [1, 0.92, 1],
      transition: { duration: 3.5, ease: 'easeInOut' },
    });

    runeControls.start({
      opacity: [1, 0.8, 0.4, 0],
      scale: [1, 0.85, 0.4, 0],
      transition: { duration: 2.6, ease: 'easeInOut' },
    });

    shimmerControls.start({
      opacity: [0.6, 1, 0],
      transition: { duration: 3.2, ease: 'easeInOut' },
    });

    setFlashOpacity(0.8);
    const flashTimeout = window.setTimeout(() => setFlashOpacity(0), 600);
    flashTimeoutRef.current = flashTimeout;

    const finishTimeout = window.setTimeout(() => {
      setParticlesActive(false);
      onFinished?.();
    }, 3500);
    finishTimeoutRef.current = finishTimeout;

    return () => {
      window.clearTimeout(flashTimeout);
      window.clearTimeout(finishTimeout);
    };
  }, [normalized, containerControls, runeControls, shimmerControls, onFinished]);

  useEffect(() => () => {
    if (flashTimeoutRef.current) window.clearTimeout(flashTimeoutRef.current);
    if (finishTimeoutRef.current) window.clearTimeout(finishTimeoutRef.current);
  }, []);

  const baseScale = useMemo(() => {
    switch (stage) {
      case 'bright':
        return 1.05;
      case 'swirl':
        return 1.08;
      case 'preflare':
        return 1.12;
      case 'flare':
        return 1;
      default:
        return 1;
    }
  }, [stage]);

  return (
    <div className="pointer-events-none relative flex h-full w-full items-center justify-center">
      <motion.div
        className="relative h-80 w-80 md:h-[24rem] md:w-[24rem]"
        animate={finale ? containerControls : { scale: baseScale }}
        transition={{
          duration: finale ? 3.5 : stage === 'dim' ? 0.6 : 14,
          ease: 'easeInOut',
          repeat: finale ? 0 : stage === 'dim' ? 0 : Infinity,
        }}
      >
        <motion.div
          className="absolute inset-0 rounded-full blur-3xl"
          animate={{
            backgroundColor: finale
              ? 'rgba(255,255,255,0.95)'
              : stage === 'dim'
                ? 'rgba(15,118,110,0.25)'
                : 'rgba(125,211,252,0.55)',
            opacity: finale ? [0.6, 1, 0.2] : stage === 'dim' ? 0.3 : 0.6,
          }}
          transition={{ duration: finale ? 3.5 : 0.8 }}
        />

        <motion.div className="absolute inset-0" animate={finale ? shimmerControls : { opacity: 0.4 }}>
          <motion.svg
            viewBox="0 0 400 400"
            className="absolute inset-0 h-full w-full"
            initial={{ opacity: 0.4 }}
            animate={{ opacity: finale ? [0.8, 0.3] : stage === 'flare' ? 1 : 0.8 }}
            transition={{ duration: finale ? 3.2 : 0.8 }}
          >
            <defs>
              <linearGradient id="relic-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22d3ee" />
                <stop offset="50%" stopColor="#a855f7" />
                <stop offset="100%" stopColor="#f472b6" />
              </linearGradient>
            </defs>
            <circle cx="200" cy="200" r="140" stroke="url(#relic-gradient)" strokeWidth="3" fill="none" />
            <circle
              cx="200"
              cy="200"
              r="70"
              stroke="rgba(180,220,255,0.6)"
              strokeWidth="2"
              fill="rgba(34,211,238,0.08)"
            />
            <motion.circle
              cx="200"
              cy="200"
              r="100"
              stroke="rgba(125,211,252,0.35)"
              strokeWidth="1.5"
              fill="none"
              animate={{ scale: finale ? [1, 1.4, 0.6] : [1, 1.08, 1] }}
              transition={{ duration: finale ? 3.2 : 8, repeat: finale ? 0 : Infinity, ease: 'easeInOut' }}
            />
          </motion.svg>

          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={
              finale
                ? runeControls
                : stage === 'flare'
                  ? { rotate: [0, 360] }
                  : stage === 'swirl' || stage === 'preflare'
                    ? { rotate: 360 }
                    : { rotate: 0 }
            }
            transition={{
              duration: finale ? 3.2 : stage === 'flare' ? 3 : stage === 'swirl' || stage === 'preflare' ? 22 : 0.1,
              ease: stage === 'swirl' || stage === 'preflare' ? 'linear' : 'easeInOut',
              repeat: finale ? 0 : stage === 'swirl' || stage === 'preflare' ? Infinity : 0,
            }}
          >
            {RUNE_SYMBOLS.map((rune, index) => {
              const angle = (index / RUNE_SYMBOLS.length) * Math.PI * 2;
              const radius = 140;
              const x = 200 + radius * Math.cos(angle);
              const y = 200 + radius * Math.sin(angle);
              return (
                <motion.span
                  key={rune}
                  className="absolute text-lg font-semibold text-cyan-200"
                  style={{ top: `calc(50% + ${(y - 200) / 2}px)`, left: `calc(50% + ${(x - 200) / 2}px)` }}
                  animate={
                    finale
                      ? undefined
                      : {
                          opacity: stage === 'dim' ? 0.2 : [0.4, 1, 0.4],
                          scale: stage === 'dim' ? 0.9 : [0.9, 1.1, 0.9],
                        }
                  }
                  transition={{ duration: finale ? 2.6 : 6 + index, repeat: finale ? 0 : Infinity, ease: 'easeInOut' }}
                >
                  {rune}
                </motion.span>
              );
            })}
          </motion.div>
        </motion.div>

        <Particles active={particlesActive} finale={finale} />
      </motion.div>

      <motion.div className="absolute inset-0 bg-white" animate={{ opacity: flashOpacity }} transition={{ duration: 0.5 }} />
    </div>
  );
};

export default RelicVisuals;
