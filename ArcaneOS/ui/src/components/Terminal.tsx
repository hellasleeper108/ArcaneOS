import React from 'react';
import { motion } from 'framer-motion';

const Particle: React.FC = () => {
  const randomDuration = Math.random() * 3 + 2;
  const randomDelay = Math.random() * 3;
  const randomX = (Math.random() - 0.5) * 80;
  const randomY = (Math.random() - 0.5) * 80;

  return (
    <motion.div
      className="particle"
      style={{ top: `${Math.random() * 100}%`, left: `${Math.random() * 100}%` }}
      animate={{ opacity: [0, 0.7, 0.7, 0], x: [0, randomX, randomX, 0], y: [0, randomY, randomY, 0] }}
      transition={{ duration: randomDuration, delay: randomDelay, repeat: Infinity, ease: 'easeInOut' }}
    />
  );
};

export const Terminal: React.FC = () => {
  const particles = Array.from({ length: 30 });

  return (
    <motion.div
      className="fantasy-layer"
      initial={{ opacity: 0, filter: 'blur(0px) saturate(100%)' }}
      animate={{ opacity: 1, filter: 'blur(0px) saturate(100%)' }}
      exit={{ opacity: 0, filter: 'blur(2px) saturate(0%)' }}
      transition={{ duration: 1.0, ease: 'easeInOut' }}
    >
      <div className="particle-field-1">{particles.map((_, i) => <Particle key={`p1-${i}`} />)}</div>
      <div className="particle-field-2">{particles.map((_, i) => <Particle key={`p2-${i}`} />)}</div>

      <div className="fantasy-content">
        <h1 className="glow-text">ArcaneOS</h1>
        <p className="glow-text-secondary">The weave is stable.</p>

        <div className="daemon-grid">
          <div className="daemon-avatar">
            <div className="aura" />
            <div className="daemon-icon">❖</div>
            <span className="daemon-name">Ignis (Core)</span>
          </div>
          <div className="daemon-avatar">
            <div className="aura" />
            <div className="daemon-icon">♅</div>
            <span className="daemon-name">Aqua (Mem)</span>
          </div>
          <div className="daemon-avatar">
            <div className="aura" />
            <div className="daemon-icon">⚡︎</div>
            <span className="daemon-name">Fulgur (Net)</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Terminal;
