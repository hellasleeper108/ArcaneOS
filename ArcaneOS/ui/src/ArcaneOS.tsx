import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Terminal } from './components/Terminal';
import { LogPane } from './components/LogPane';
import { ArchonSigil } from './components/ArchonSigil';
import './ArcaneOS.css';

const ArcaneOS: React.FC = () => {
  const [isFantasyMode, setIsFantasyMode] = useState(true);

  return (
    <div className="arcane-container">
      <ArchonSigil isFantasyMode={isFantasyMode} />

      <button
        className="mode-toggle"
        onClick={() => setIsFantasyMode((mode) => !mode)}
      >
        {isFantasyMode ? 'Enter Dev Mode' : 'Awaken Fantasy'}
      </button>

      <AnimatePresence>
        {isFantasyMode ? <Terminal key="fantasy" /> : <LogPane key="dev" />}
      </AnimatePresence>
    </div>
  );
};

export default ArcaneOS;
