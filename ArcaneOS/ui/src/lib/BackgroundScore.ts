let scoreAudio: HTMLAudioElement | null = null;
let isPlaying = false;
let targetVolume = 0.07;
let fadeRAF: number | undefined;

const BASE_VOLUME = 0.05;
const MIN_VOLUME = 0.0001;

const clearFade = () => {
  if (fadeRAF !== undefined) {
    cancelAnimationFrame(fadeRAF);
    fadeRAF = undefined;
  }
};

const getAudio = () => {
  if (!scoreAudio) {
    scoreAudio = new Audio(`${process.env.PUBLIC_URL || ''}/audio/instrumental.wav`);
    scoreAudio.loop = true;
    scoreAudio.volume = MIN_VOLUME;
  }
  return scoreAudio;
};

const fadeVolume = (to: number, duration = 600): Promise<void> => {
  const audio = getAudio();
  if (duration <= 0) {
    audio.volume = to;
    return Promise.resolve();
  }
  clearFade();
  const start = audio.volume;
  const startTime = performance.now();
  return new Promise((resolve) => {
    const step = (now: number) => {
      const elapsed = now - startTime;
      const ratio = Math.min(elapsed / duration, 1);
      audio.volume = start + (to - start) * ratio;
      if (ratio < 1) {
        fadeRAF = requestAnimationFrame(step);
      } else {
        fadeRAF = undefined;
        resolve();
      }
    };
    fadeRAF = requestAnimationFrame(step);
  });
};

export const startBackgroundScore = async () => {
  if (typeof window === 'undefined') return;
  const audio = getAudio();
  if (isPlaying) {
    if (audio.paused) {
      try {
        await audio.play();
      } catch (error) {
        // ignore autoplay errors
      }
    }
    return;
  }
  try {
    await audio.play();
    isPlaying = true;
    targetVolume = BASE_VOLUME;
    await fadeVolume(targetVolume, 1500);
  } catch (error) {
    // ignore; browser may block until user interaction
  }
};

export const stopBackgroundScore = () => {
  if (!scoreAudio) return;
  clearFade();
  fadeVolume(MIN_VOLUME, 600).finally(() => {
    if (!scoreAudio) return;
    try {
      scoreAudio.pause();
      scoreAudio.currentTime = 0;
    } catch (error) {
      // ignore pause errors
    }
    isPlaying = false;
  });
};

export const setBackgroundScoreVolume = (volume: number, duration = 500) => {
  targetVolume = Math.max(MIN_VOLUME, Math.min(volume, 1));
  return fadeVolume(targetVolume, duration);
};

export const duckBackgroundScore = async (attenuation = 0.5, duration = 300) => {
  if (!isPlaying) {
    return async () => {};
  }
  const previousTarget = targetVolume;
  const duckTarget = Math.max(MIN_VOLUME, BASE_VOLUME * attenuation);
  await setBackgroundScoreVolume(duckTarget, duration);
  return () => setBackgroundScoreVolume(previousTarget, 600);
};

const BackgroundScore = {
  startBackgroundScore,
  stopBackgroundScore,
  setBackgroundScoreVolume,
  duckBackgroundScore,
};

export default BackgroundScore;
