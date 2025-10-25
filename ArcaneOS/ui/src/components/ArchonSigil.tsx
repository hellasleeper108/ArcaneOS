import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useArchonSocket } from '../lib/events';
import './Archon.css';

type ArchonSigilProps = {
  isFantasyMode: boolean;
};

export const ArchonSigil: React.FC<ArchonSigilProps> = ({ isFantasyMode }) => {
  const { archonState, message, clearMessage } = useArchonSocket();

  useEffect(() => {
    if (!message) return;
    const timer = window.setTimeout(() => clearMessage(), 4000);
    return () => window.clearTimeout(timer);
  }, [message, clearMessage]);

  return (
    <div className="archon-container">
      <div data-testid="archon-sigil" className={`archon-sigil ${archonState} ${isFantasyMode ? '' : 'wireframe'}`}>
        <div className="archon-runes">
          <span className="rune">ᛟ</span>
          <span className="rune">ᛝ</span>
          <span className="rune">ᛚ</span>
        </div>
        <div className="archon-eye">
          <div className="archon-iris" />
        </div>
      </div>

      <AnimatePresence>
        {message && (
          <motion.div
            className="archon-toast"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export const Archon = ArchonSigil;

export default ArchonSigil;
