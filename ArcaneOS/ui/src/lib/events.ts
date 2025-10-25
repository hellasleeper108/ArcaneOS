import { useEffect, useRef, useState } from 'react';
import { AudioEngine } from './audio';

type ArchonState = 'idle' | 'processing' | 'success' | 'failure';

const ARCHON_STATE: Record<string, ArchonState> = {
  IDLE: 'idle',
  PROCESSING: 'processing',
  SUCCESS: 'success',
  FAILURE: 'failure',
};

const resolveWebSocketUrl = (): string => {
  const envUrl = process.env.REACT_APP_ARCANE_WS_URL;
  if (envUrl) return envUrl;

  if (typeof window === 'undefined') {
    return 'ws://localhost:8000/ws/events';
  }

  const { protocol, hostname, port } = window.location;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
  const preferredPort =
    port && port !== '' && port !== '3000' && port !== '5173' ? port : '8000';

  return `${wsProtocol}//${hostname}:${preferredPort}/ws/events`;
};

export function useArchonSocket() {
  const [archonState, setArchonState] = useState<ArchonState>('idle');
  const [message, setMessage] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const resetTimerRef = useRef<number | null>(null);

  useEffect(() => {
    const url = resolveWebSocketUrl();
    const socket = new WebSocket(url);
    wsRef.current = socket;

    socket.onopen = () => {
      setMessage('I am awake.');
      setArchonState('idle');
      AudioEngine.play('archon', undefined, 'greeting');
    };

    socket.onclose = () => {
      setMessage('The link is broken...');
      setArchonState('failure');
      AudioEngine.play('archon', 'failure');
      resetTimerRef.current = window.setTimeout(() => {
        setArchonState('idle');
      }, 2000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as {
          event?: string;
          character?: string;
          message?: string;
          messageKey?: string;
        };

        const eventType = data.event?.toLowerCase();
        const character = (data.character || 'archon').toLowerCase();

        if (eventType && ARCHON_STATE[eventType.toUpperCase()]) {
          const newState = ARCHON_STATE[eventType.toUpperCase()];
          setArchonState(newState);

          if (newState === 'success' || newState === 'failure') {
            if (resetTimerRef.current) window.clearTimeout(resetTimerRef.current);
            resetTimerRef.current = window.setTimeout(() => {
              setArchonState('idle');
            }, 1500);
          }
        }

        if (data.message) {
          setMessage(data.message);
        }

        AudioEngine.play(character, eventType as string | undefined, data.messageKey ?? null);
      } catch (error) {
        console.error('Archon received unreadable runes:', error);
        setArchonState('failure');
        setMessage('The incantation is muddled.');
        AudioEngine.play('system', 'failure');
        resetTimerRef.current = window.setTimeout(() => {
          setArchonState('idle');
        }, 2000);
      }
    };

    return () => {
      if (resetTimerRef.current) {
        window.clearTimeout(resetTimerRef.current);
      }
      socket.close();
      wsRef.current = null;
    };
  }, []);

  const clearMessage = () => setMessage(null);

  return { archonState, message, clearMessage };
}
