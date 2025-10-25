type EventType = 'success' | 'failure' | 'invoke';

type AudioSettings = {
  src: string;
  delay: number;
};

type AudioMap = Record<string, Record<string, string>>;

const audioMap: AudioMap = {
  archon: {
    invoke: '/sounds/archon/invoke.mp3',
    success: '/sounds/archon/success.mp3',
    failure: '/sounds/archon/failure.mp3',
    greeting: '/sounds/archon/greeting_01.mp3',
    code_hum: '/sounds/archon/code_hum_01.mp3',
  },
  claude: {
    invoke: '/sounds/claude/invoke.mp3',
    success: '/sounds/claude/success.mp3',
    failure: '/sounds/claude/failure.mp3',
  },
  gemini: {
    invoke: '/sounds/gemini/invoke.mp3',
    success: '/sounds/gemini/success.mp3',
    failure: '/sounds/gemini/failure.mp3',
  },
  system: {
    success: '/sounds/system/success-flare.mp3',
    failure: '/sounds/system/failure-dim.mp3',
  },
};

const getAudioSettings = (
  character: string,
  eventType?: string,
  messageKey?: string | null
): AudioSettings | null => {
  const char = (character || 'system').toLowerCase();
  const event = eventType?.toLowerCase() as EventType | undefined;

  let src: string | undefined;

  if (messageKey && audioMap[char]?.[messageKey]) {
    src = audioMap[char][messageKey];
  } else if (event && audioMap[char]?.[event]) {
    src = audioMap[char][event];
  } else if (event && audioMap.system[event]) {
    src = audioMap.system[event];
  }

  if (!src) return null;

  let delay = 150;

  switch (event) {
    case 'success':
      delay = 120;
      break;
    case 'failure':
      delay = 120;
      break;
    case 'invoke':
      delay = 150;
      break;
    default:
      delay = 150;
  }

  if (messageKey) {
    delay = 0;
  }

  return { src, delay };
};

const play = (character: string, eventType?: string, messageKey: string | null = null) => {
  const settings = getAudioSettings(character, eventType, messageKey);
  if (!settings) {
    console.warn(`AudioEngine: No audio for ${character}/${eventType}${messageKey ? `/${messageKey}` : ''}`);
    return;
  }

  window.setTimeout(() => {
    const audio = new Audio(settings.src);
    void audio.play().catch((error) => {
      console.error(`Failed to play audio: ${settings.src}`, error);
    });
  }, settings.delay);
};

export const AudioEngine = {
  play,
};
