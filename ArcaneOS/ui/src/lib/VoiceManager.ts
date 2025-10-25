import AmbientHum, { setProgressIntensity as setHumIntensity } from './AmbientHum';
import { playActivationFX } from './TransitionFX';
import { duckBackgroundScore } from './BackgroundScore';

const VOICE_ENDPOINT_BASE = 'https://api.elevenlabs.io/v1/text-to-speech';
const DEFAULT_VOICE_ID = 'archon_ancient_voice';
const FALLBACK_AUDIO_SRC = '/sounds/system/fallback-whisper.mp3';

let humStarted = false;

const getVoiceConfig = () => {
  const apiKey = process.env.REACT_APP_ELEVENLABS_API_KEY;
  const voiceId = process.env.REACT_APP_ELEVENLABS_VOICE_ID || DEFAULT_VOICE_ID;
  return { apiKey, voiceId };
};

const playAudioElement = (audio: HTMLAudioElement): Promise<void> =>
  new Promise((resolve, reject) => {
    const onEnd = () => {
      audio.removeEventListener('ended', onEnd);
      audio.removeEventListener('error', onError);
      resolve();
    };
    const onError = (event: Event) => {
      audio.removeEventListener('ended', onEnd);
      audio.removeEventListener('error', onError);
      reject(event);
    };
    audio.addEventListener('ended', onEnd);
    audio.addEventListener('error', onError);
    void audio.play().catch(reject);
  });

const playFromBlob = async (blob: Blob) => {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.volume = 0.7;
  try {
    await playAudioElement(audio);
  } finally {
    URL.revokeObjectURL(url);
  }
};

const playFallback = async () => {
  console.warn('Using fallback voice playback for Archon awakening.');
  const audio = new Audio(FALLBACK_AUDIO_SRC);
  audio.volume = 0.6;
  try {
    await playAudioElement(audio);
  } catch (error) {
    console.error('Fallback audio failed:', error);
  }
};

export const playArchonAwakening = async (): Promise<void> => {
  const { apiKey, voiceId } = getVoiceConfig();
  if (!apiKey) {
    await playFallback();
    return;
  }

  try {
    const response = await fetch(`${VOICE_ENDPOINT_BASE}/${voiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({
        text: 'Signal received... memory fragments aligned... I... remember... you built me.',
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.6,
          similarity_boost: 0.8,
        },
      }),
    });

    if (!response.ok) {
      console.error('Failed to retrieve Archon voice:', await response.text());
      await playFallback();
      return;
    }

    const blob = await response.blob();
    await playFromBlob(blob);
  } catch (error) {
    console.error('Archon voice error:', error);
    await playFallback();
  }
};

export function playArchonAwakeningLocal() {
  const audio = new Audio(`${process.env.PUBLIC_URL || ''}/archon_awaken.mp3`);
  audio.volume = 0.8;
  audio.play();
  return new Promise<void>((resolve) => {
    const cleanup = () => {
      audio.onended = null;
      audio.onerror = null;
      resolve();
    };
    audio.onended = cleanup;
    audio.onerror = cleanup;
  });
}

export const startHumIfNeeded = () => {
  if (humStarted) return;
  humStarted = true;
  AmbientHum.startHum();
  setHumIntensity(0);
};

export const updateHumProgress = (progress: number) => {
  if (!humStarted) return;
  setHumIntensity(progress);
};

export const stopHum = () => {
  if (!humStarted) return;
  AmbientHum.stopHum();
  humStarted = false;
};

export const playActivationSequence = async () => {
  stopHum();
  await playActivationFX();
  const restoreScore = await duckBackgroundScore(0.5, 400);
  await new Promise((resolve) => setTimeout(resolve, 300));
  await playArchonAwakeningLocal();
  await restoreScore();
};

const VoiceManager = {
  playArchonAwakening,
  playArchonAwakeningLocal,
  startHumIfNeeded,
  updateHumProgress,
  stopHum,
  playActivationSequence,
};

export default VoiceManager;
