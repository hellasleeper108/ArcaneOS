import React from 'react';
import { motion } from 'framer-motion';

interface DaemonAvatarProps {
  name: string;
  color: string;
  auraColor: string;
  mode: 'fantasy' | 'developer';
}

const DaemonAvatar: React.FC<DaemonAvatarProps> = ({ name, color, auraColor, mode }) => {
  if (mode === 'developer') {
    return (
      <div className="flex items-center gap-3 rounded-md border border-slate-700/80 bg-slate-900/60 px-3 py-2 text-left">
        <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-300">{name}</span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="relative flex h-24 w-24 items-center justify-center rounded-full"
      style={{ filter: 'drop-shadow(0 0 12px rgba(255,255,255,0.45))' }}
    >
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{ background: `radial-gradient(circle, ${auraColor} 0%, transparent 70%)` }}
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.75, 0.55, 0.75],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="relative z-10 h-16 w-16 rounded-full bg-slate-950/70 backdrop-blur-md border border-white/40 flex items-center justify-center">
        <span className="text-xs font-semibold tracking-[0.3em] text-white/90 uppercase">{name}</span>
      </div>
    </motion.div>
  );
};

export default DaemonAvatar;
