let audioCtx: AudioContext | null = null;
let activeNodes: Array<{ oscillator: OscillatorNode | null; gain: GainNode }> = [];

const STEP_FREQUENCIES = [220, 440, 660, 880, 990, 1110, 1320];
const CHIME_FREQUENCIES = [660, 880, 1320];

const getContext = (): AudioContext => {
  if (!audioCtx) {
    audioCtx = new AudioContext();
  }
  return audioCtx;
};

const fadeOutAndDispose = (node: { oscillator: OscillatorNode | null; gain: GainNode }) => {
  const ctx = audioCtx;
  if (!ctx) return;
  const now = ctx.currentTime;
  node.gain.gain.cancelScheduledValues(now);
  node.gain.gain.setValueAtTime(node.gain.gain.value, now);
  node.gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);
  if (node.oscillator) {
    try {
      node.oscillator.stop(now + 0.22);
    } catch {
      /* ignore stop errors */
    }
  }
  setTimeout(() => {
    try {
      node.gain.disconnect();
      node.oscillator?.disconnect();
    } catch {
      /* ignore disconnect errors */
    }
  }, 320);
};

export const stopAll = () => {
  activeNodes.forEach(fadeOutAndDispose);
  activeNodes = [];
};

const playOscillator = (frequency: number, duration = 0.55) => {
  const ctx = getContext();
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();

  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);

  gain.gain.setValueAtTime(0.0001, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + 0.05);
  gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);

  oscillator.connect(gain).connect(ctx.destination);
  oscillator.start();
  oscillator.stop(ctx.currentTime + duration + 0.05);

  activeNodes.push({ oscillator, gain });

  oscillator.onended = () => fadeOutAndDispose({ oscillator: null, gain });
};

const playChime = () => {
  stopAll();
  const ctx = getContext();
  CHIME_FREQUENCIES.forEach((frequency, index) => {
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();

    oscillator.type = 'triangle';
    const startTime = ctx.currentTime + index * 0.05;
    oscillator.frequency.setValueAtTime(frequency, startTime);

    gain.gain.setValueAtTime(0.0001, startTime);
    gain.gain.linearRampToValueAtTime(0.35, startTime + 0.1);
    gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.65);

    oscillator.connect(gain).connect(ctx.destination);
    oscillator.start(startTime);
    oscillator.stop(startTime + 0.7);

    activeNodes.push({ oscillator, gain });

    oscillator.onended = () => fadeOutAndDispose({ oscillator: null, gain });
  });
};

export const playTone = (step: number) => {
  try {
    const ctx = getContext();
    if (ctx.state === 'suspended') {
      void ctx.resume();
    }
  } catch {
    return;
  }

  if (step >= STEP_FREQUENCIES.length) {
    playChime();
    return;
  }

  stopAll();
  const frequency = STEP_FREQUENCIES[step] ?? STEP_FREQUENCIES[STEP_FREQUENCIES.length - 1];
  playOscillator(frequency, 0.55);
};

const BootSound = {
  playTone,
  stopAll,
};

export default BootSound;
