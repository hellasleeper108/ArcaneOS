import React from 'react';
import { motion } from 'framer-motion';

export const LogPane: React.FC = () => {
  return (
    <motion.div
      className="dev-layer"
      initial={{ opacity: 0, filter: 'blur(2px) saturate(0%)' }}
      animate={{ opacity: 1, filter: 'blur(0px) saturate(100%)' }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.0, ease: 'easeInOut' }}
    >
      <div className="terminal">
        <pre>
          <code>
            [SYSTEM] Switching to Developer Mode...{"\n"}
            [INFO] Unloading 'fantasy-illusion-layer.vfx'... OK{"\n"}
            [INFO] Mounting 'core-debug.log'... OK{"\n"}
            [DAEMON_LOG] Ignis(Core): PID 4045 - Temp: 35.2C - Load: 12%{"\n"}
            [DAEMON_LOG] Aqua(Mem): PID 4046 - Usage: 4.8/16GB - Swap: 0%{"\n"}
            [DAEMON_LOG] Fulgur(Net): PID 4047 - Eth0: 1.2MB/s UP | 8.8MB/s DOWN{"\n"}
            [WARN] Aetheric flux detected in process 667 (mana_leak.exe). Monitoring...{"\n"}
            [SYSTEM] Awaiting input...<span className="cursor">_</span>
          </code>
        </pre>
      </div>
    </motion.div>
  );
};

export default LogPane;
