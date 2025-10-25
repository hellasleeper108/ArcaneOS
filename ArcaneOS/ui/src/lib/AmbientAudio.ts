let humAudio: HTMLAudioElement | null = null;
let whisperAudio: HTMLAudioElement | null = null;

const HUM_SRC = '/sounds/ambience/arcane-hum.mp3';
const WHISPER_SRC = '/sounds/voice/archon-remembers.mp3';

export const startHum = () => {
  try {
    if (!humAudio) {
      humAudio = new Audio(HUM_SRC);
      humAudio.loop = true;
      humAudio.volume = 0.18;
    }
    humAudio.currentTime = 0;
    void humAudio.play().catch(() => {});
  } catch {
    humAudio = null;
  }
};

export const stopHum = () => {
  if (!humAudio) return;
  try {
    humAudio.pause();
  } catch {
    /* ignore pause errors */
  }
};

export const playWhisper = () => {
  stopHum();
  try {
    if (!whisperAudio) {
      whisperAudio = new Audio(WHISPER_SRC);
      whisperAudio.volume = 0.45;
    }
    whisperAudio.currentTime = 0;
    void whisperAudio.play().catch(() => {});
  } catch {
    whisperAudio = null;
  }
};

const AmbientAudio = {
  startHum,
  stopHum,
  playWhisper,
};

export default AmbientAudio;
