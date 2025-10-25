import AmbientHum from './AmbientHum';

type FXState = {
  ctx: AudioContext;
  master: GainNode;
  active: boolean;
};

const ensureContext = (): FXState => {
  if (typeof window === 'undefined') {
    return {
      ctx: new AudioContext(),
      master: new GainNode(new AudioContext()),
      active: false,
    };
  }

  const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
  if (!globalState.ctx) {
    const ctx = new AudioCtx();
    const master = ctx.createGain();
    master.gain.value = 0.0001;
    master.connect(ctx.destination);
    globalState = { ctx, master, active: false };
  }
  if (globalState.ctx.state === 'suspended') {
    void globalState.ctx.resume();
  }
  return globalState;
};

let globalState: FXState = {
  ctx: null as unknown as AudioContext,
  master: null as unknown as GainNode,
  active: false,
};

const scheduleWhiteNoiseBurst = (ctx: AudioContext, master: GainNode, when: number) => {
  const duration = 0.4;
  const sampleRate = ctx.sampleRate;
  const frameCount = Math.floor(sampleRate * duration);
  const buffer = ctx.createBuffer(1, frameCount, sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < frameCount; i += 1) {
    data[i] = (Math.random() * 2 - 1) * (1 - i / frameCount);
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.05, when);
  gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
  noise.connect(gain).connect(master);
  noise.start(when);
  noise.stop(when + duration);
};

const scheduleRisingTone = (ctx: AudioContext, master: GainNode, startTime: number) => {
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(220, startTime);
  osc.frequency.linearRampToValueAtTime(880, startTime + 2.5);
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.02, startTime);
  gain.gain.linearRampToValueAtTime(0.08, startTime + 2.5);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 3.5);
  osc.connect(gain).connect(master);
  osc.start(startTime);
  osc.stop(startTime + 3.6);
};

const scheduleBellPing = (ctx: AudioContext, master: GainNode, when: number) => {
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(880, when);
  osc.frequency.exponentialRampToValueAtTime(1760, when + 0.8);
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.08, when);
  gain.gain.exponentialRampToValueAtTime(0.0001, when + 0.8);
  osc.connect(gain).connect(master);
  osc.start(when);
  osc.stop(when + 0.85);
};

export const playActivationFX = async () => {
  const { ctx, master, active } = ensureContext();
  if (active) return;
  globalState.active = true;

  AmbientHum.stopHum();

  const startTime = ctx.currentTime + 0.05;

  master.gain.cancelScheduledValues(ctx.currentTime);
  master.gain.setValueAtTime(master.gain.value || 0.0001, ctx.currentTime);
  master.gain.linearRampToValueAtTime(0.4, startTime + 0.5);

  scheduleRisingTone(ctx, master, startTime);
  scheduleWhiteNoiseBurst(ctx, master, startTime + 2);
  scheduleBellPing(ctx, master, startTime + 2.8);

  master.gain.exponentialRampToValueAtTime(0.0001, startTime + 3.5);

  await new Promise((resolve) => {
    setTimeout(() => {
      globalState.active = false;
      resolve(true);
    }, (startTime - ctx.currentTime + 3.6) * 1000);
  });
};

const dispatchFailureEvent = () => {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent('archon-failure'));
};

export const playFailureFX = async () => {
  const { ctx, master } = ensureContext();
  const start = ctx.currentTime + 0.02;

  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(440, start);
  osc.frequency.linearRampToValueAtTime(110, start + 0.6);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.05, start);
  gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.65);
  osc.connect(gain).connect(master);
  osc.start(start);
  osc.stop(start + 0.7);

  dispatchFailureEvent();
};

const TransitionFX = {
  playActivationFX,
  playFailureFX,
};

export default TransitionFX;
