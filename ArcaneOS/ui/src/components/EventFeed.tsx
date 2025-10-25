import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

export type EventChannel = 'route' | 'stdout' | 'error';

export interface EventRecord {
  id: string;
  channel: EventChannel;
  text: string;
  timestamp: number;
  raw?: unknown;
}

interface EventFeedProps {
  events: EventRecord[];
}

const CHANNEL_LABEL: Record<EventChannel, string> = {
  route: 'Routing',
  stdout: 'Output',
  error: 'Errors',
};

const CHANNEL_COLOR: Record<EventChannel, string> = {
  route: 'text-teal-300',
  stdout: 'text-slate-100',
  error: 'text-red-300',
};

export const EventFeed: React.FC<EventFeedProps> = ({ events }) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [collapsed, setCollapsed] = useState<Record<EventChannel, boolean>>({
    route: false,
    stdout: false,
    error: false,
  });

  const grouped = useMemo(() => {
    return events.reduce<Record<EventChannel, EventRecord[]>>(
      (acc, event) => {
        acc[event.channel] = [...acc[event.channel], event];
        return acc;
      },
      { route: [], stdout: [], error: [] }
    );
  }, [events]);

  useEffect(() => {
    const node = scrollRef.current;
    if (!node) return;
    requestAnimationFrame(() => {
      node.scrollTop = node.scrollHeight;
    });
  }, [events]);

  const toggle = (channel: EventChannel) =>
    setCollapsed((prev) => ({ ...prev, [channel]: !prev[channel] }));

  return (
    <motion.aside
      initial={{ x: 360, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="pointer-events-auto fixed inset-y-0 right-0 z-30 w-[320px] bg-[#05080C]/85 backdrop-blur-lg border-l border-teal-800/30 flex flex-col"
    >
      <header className="px-5 py-4 border-b border-teal-900/30">
        <h2 className="text-sm font-semibold tracking-[0.2em] text-teal-200 uppercase">
          Event Feed
        </h2>
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {(Object.keys(CHANNEL_LABEL) as EventChannel[]).map((channel) => {
          const items = grouped[channel];
          const isCollapsed = collapsed[channel];
          return (
            <section key={channel} className="rounded-md border border-teal-900/30 bg-black/40">
              <button
                type="button"
                onClick={() => toggle(channel)}
                className="flex w-full items-center justify-between px-3 py-2 text-xs uppercase tracking-[0.2em] text-teal-200 hover:bg-teal-500/10 transition"
              >
                <span>{`${CHANNEL_LABEL[channel]} (${items.length})`}</span>
                <span>{isCollapsed ? '▸' : '▾'}</span>
              </button>

              <AnimatePresence initial={false}>
                {!isCollapsed && (
                  <motion.ul
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="max-h-64 overflow-y-auto space-y-1 px-3 py-2 text-[11px] leading-relaxed"
                  >
                    {items.length === 0 && (
                      <motion.li
                        key="empty"
                        className="text-slate-400 text-[10px] italic"
                      >
                        No events yet.
                      </motion.li>
                    )}
                    {items.map((event) => (
                      <motion.li
                        key={event.id}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -4 }}
                        transition={{ duration: 0.18 }}
                        className={`${CHANNEL_COLOR[channel]} whitespace-pre-wrap`}
                      >
                        <span className="text-[10px] text-slate-400 mr-2">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                        {event.text || JSON.stringify(event.raw)}
                      </motion.li>
                    ))}
                  </motion.ul>
                )}
              </AnimatePresence>
            </section>
          );
        })}
      </div>
    </motion.aside>
  );
};

export default EventFeed;
