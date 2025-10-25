import React from 'react';

interface VeilToggleProps {
  veilEnabled: boolean;
  onToggle: (value: boolean) => void;
  loading?: boolean;
}

const VeilToggle: React.FC<VeilToggleProps> = ({ veilEnabled, onToggle, loading }) => {
  return (
    <button
      className={`rounded-full px-6 py-2 text-sm font-semibold transition-colors duration-300 focus:outline-none focus:ring ${veilEnabled ? 'bg-purple-600/80 text-purple-50 hover:bg-purple-500/90 focus:ring-purple-400/60' : 'bg-slate-700 text-slate-200 hover:bg-slate-600 focus:ring-slate-400/50'}`}
      onClick={() => onToggle(!veilEnabled)}
      disabled={loading}
    >
      {loading ? 'Shifting Veil...' : veilEnabled ? 'Fantasy Mode' : 'Developer Mode'}
    </button>
  );
};

export default VeilToggle;
