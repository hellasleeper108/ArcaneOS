type HumState = {
  ctx: AudioContext;
  master: GainNode;
  toneGain: GainNode;
  noiseGain: GainNode;
  oscillators: OscillatorNode[];
  lfo: OscillatorNode;
  lfoGain: GainNode;
  baseLevel: ConstantSourceNode;
  noiseSource: AudioBufferSourceNode;
  shimmerOsc?: OscillatorNode;
  shimmerGain?: GainNode;
  shimmerFilter?: BiquadFilterNode;
  shimmerFadeTimeout?: number;
  shimmerStopTimeout?: number;
  shimmerFilterTimeout?: number;
};

let state: HumState | null = null;

const BASE_GAIN = 0.2;
const RAMP_TIME = 1.2;

const createAudioContext = () => {
  const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
  return new AudioCtx();
};

const createNoiseBuffer = (ctx: AudioContext) => {
  const duration = 2;
  const channels = 1;
  const sampleRate = ctx.sampleRate;
  const frameCount = sampleRate * duration;
  const buffer = ctx.createBuffer(channels, frameCount, sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < frameCount; i += 1) {
    data[i] = (Math.random() * 2 - 1) * 0.3;
  }
  return buffer;
};

export const startHum = () => {
  if (typeof window === 'undefined') return;
  if (state) {
    const { ctx, master } = state;
    if (ctx.state === 'suspended') void ctx.resume();
    const now = ctx.currentTime;
    master.gain.cancelScheduledValues(now);
    master.gain.setValueAtTime(master.gain.value, now);
    master.gain.linearRampToValueAtTime(BASE_GAIN, now + RAMP_TIME);
    return;
  }

  const ctx = createAudioContext();
  const master = ctx.createGain();
  master.gain.value = 0;
  master.connect(ctx.destination);

  const toneGain = ctx.createGain();
  toneGain.gain.value = 0;
  toneGain.connect(master);

  const baseLevel = ctx.createConstantSource();
  baseLevel.offset.value = 0.08;
  baseLevel.connect(toneGain.gain);
  baseLevel.start();

  const lfo = ctx.createOscillator();
  lfo.frequency.value = 0.12;
  const lfoGain = ctx.createGain();
  lfoGain.gain.value = 0.025;
  lfo.connect(lfoGain);
  lfoGain.connect(toneGain.gain);
  lfo.start();

  const oscillators: OscillatorNode[] = [
    ctx.createOscillator(),
    ctx.createOscillator(),
  ];
  oscillators[0].type = 'sine';
  oscillators[0].frequency.value = 55;
  oscillators[0].detune.value = -5;
  oscillators[0].connect(toneGain);
  oscillators[0].start();

  oscillators[1].type = 'sine';
  oscillators[1].frequency.value = 110;
  oscillators[1].detune.value = 7;
  oscillators[1].connect(toneGain);
  oscillators[1].start();

  const noiseBuffer = createNoiseBuffer(ctx);
  const noiseSource = ctx.createBufferSource();
  noiseSource.buffer = noiseBuffer;
  noiseSource.loop = true;
  const noiseGain = ctx.createGain();
  noiseGain.gain.value = 0.015;
  noiseSource.connect(noiseGain);
  noiseGain.connect(master);
  noiseSource.start();

  state = {
    ctx,
    master,
    toneGain,
    noiseGain,
    oscillators,
    lfo,
    lfoGain,
    baseLevel,
    noiseSource,
    shimmerOsc: undefined,
    shimmerGain: undefined,
    shimmerFilter: undefined,
    shimmerFadeTimeout: undefined,
    shimmerStopTimeout: undefined,
    shimmerFilterTimeout: undefined,
  };

  const now = ctx.currentTime;
  master.gain.setValueAtTime(0, now);
  master.gain.linearRampToValueAtTime(BASE_GAIN, now + RAMP_TIME);
};

export const stopHum = () => {
  if (!state) return;
  const { ctx, master, oscillators, lfo, noiseSource, baseLevel, toneGain, noiseGain, shimmerGain, shimmerOsc, shimmerFilter, shimmerFadeTimeout, shimmerStopTimeout, shimmerFilterTimeout } = state;
  const now = ctx.currentTime;
  master.gain.cancelScheduledValues(now);
  master.gain.setValueAtTime(master.gain.value, now);
  master.gain.linearRampToValueAtTime(0.0001, now + 1);

  if (shimmerGain) {
    shimmerGain.gain.cancelScheduledValues(now);
    shimmerGain.gain.setValueAtTime(shimmerGain.gain.value, now);
    shimmerGain.gain.linearRampToValueAtTime(0.0001, now + 0.6);
  }
  if (typeof shimmerFadeTimeout === 'number') {
    clearTimeout(shimmerFadeTimeout);
  }
  if (typeof shimmerStopTimeout === 'number') {
    clearTimeout(shimmerStopTimeout);
  }
  if (typeof shimmerFilterTimeout === 'number') {
    clearTimeout(shimmerFilterTimeout);
  }

  const cleanup = () => {
    oscillators.forEach((osc) => {
      try {
        osc.stop();
        osc.disconnect();
      } catch (error) {
        // ignore stop errors
      }
    });
    try {
      lfo.stop();
      lfo.disconnect();
    } catch (error) {
      /* ignore */
    }
    try {
      noiseSource.stop();
      noiseSource.disconnect();
    } catch (error) {
      /* ignore */
    }
    try {
      baseLevel.stop();
      baseLevel.disconnect();
    } catch (error) {
      /* ignore */
    }
    if (shimmerOsc) {
      try {
        shimmerOsc.stop();
        shimmerOsc.disconnect();
      } catch (error) {
        /* ignore */
      }
    }
    if (shimmerGain) {
      try {
        shimmerGain.disconnect();
      } catch (error) {
        /* ignore */
      }
    }
    if (shimmerFilter) {
      try {
        shimmerFilter.disconnect();
      } catch (error) {
        /* ignore */
      }
    }
    try {
      toneGain.disconnect();
      noiseGain.disconnect();
      master.disconnect();
    } catch (error) {
      /* ignore */
    }
    state = null;
  };

  setTimeout(cleanup, 1200);
};

export const setProgressIntensity = (percent: number) => {
  if (!state) return;
  if (typeof window === 'undefined') return;
  const { ctx, master } = state;
  const clamped = Math.max(0, Math.min(percent, 100));

  const computeGain = () => {
    if (clamped < 60) return 0.2;
    if (clamped < 90) {
      const t = (clamped - 60) / 30; // 0 to 1
      return 0.2 + t * (0.35 - 0.2);
    }
    const t = (clamped - 90) / 10;
    return 0.35 + t * (0.5 - 0.35);
  };

  const target = computeGain();
  const now = ctx.currentTime;
  master.gain.cancelScheduledValues(now);
  master.gain.setValueAtTime(master.gain.value, now);
  master.gain.linearRampToValueAtTime(target, now + 0.8);

  if (clamped >= 90) {
    if (typeof state.shimmerFadeTimeout === 'number') {
      clearTimeout(state.shimmerFadeTimeout);
      state.shimmerFadeTimeout = undefined;
    }
    if (typeof state.shimmerStopTimeout === 'number') {
      clearTimeout(state.shimmerStopTimeout);
      state.shimmerStopTimeout = undefined;
    }
    if (typeof state.shimmerFilterTimeout === 'number') {
      clearTimeout(state.shimmerFilterTimeout);
      state.shimmerFilterTimeout = undefined;
    }
    if (!state.shimmerOsc || !state.shimmerGain || !state.shimmerFilter) {
      const shimmerFilter = ctx.createBiquadFilter();
      shimmerFilter.type = 'bandpass';
      shimmerFilter.frequency.value = 1000;
      shimmerFilter.Q.value = 5;

      const shimmerGain = ctx.createGain();
      shimmerGain.gain.setValueAtTime(0, now);
      shimmerGain.connect(master);

      const shimmerOsc = ctx.createOscillator();
      shimmerOsc.type = 'triangle';
      shimmerOsc.frequency.value = 1000;
      shimmerOsc.detune.value = 10;
      shimmerOsc.connect(shimmerFilter);
      shimmerFilter.connect(shimmerGain);
      shimmerOsc.start();

      state.shimmerOsc = shimmerOsc;
      state.shimmerGain = shimmerGain;
      state.shimmerFilter = shimmerFilter;
    }
    const shimmerGainNode = state.shimmerGain;
    if (shimmerGainNode) {
      shimmerGainNode.gain.cancelScheduledValues(now);
      shimmerGainNode.gain.setValueAtTime(shimmerGainNode.gain.value, now);
      shimmerGainNode.gain.linearRampToValueAtTime(0.05, now + 0.5);
    }
  } else {
    if (state.shimmerGain) {
      const shimmerGainNode = state.shimmerGain;
      shimmerGainNode.gain.cancelScheduledValues(now);
      shimmerGainNode.gain.setValueAtTime(shimmerGainNode.gain.value, now);
      shimmerGainNode.gain.linearRampToValueAtTime(0.0001, now + 0.6);
    }
    if (state.shimmerOsc) {
      const osc = state.shimmerOsc;
      const stopTimeout = window.setTimeout(() => {
        try {
          osc.stop();
          osc.disconnect();
        } catch (error) {
          /* ignore */
        }
        if (state && state.shimmerOsc === osc) state.shimmerOsc = undefined;
        if (state) state.shimmerStopTimeout = undefined;
      }, 700);
      state.shimmerStopTimeout = stopTimeout;
    }
    if (state.shimmerGain) {
      const gain = state.shimmerGain;
      const fadeTimeout = window.setTimeout(() => {
        try {
          gain.disconnect();
        } catch (error) {
          /* ignore */
        }
        if (state && state.shimmerGain === gain) state.shimmerGain = undefined;
        if (state) state.shimmerFadeTimeout = undefined;
      }, 800);
      state.shimmerFadeTimeout = fadeTimeout;
    }
    if (state.shimmerFilter) {
      const filter = state.shimmerFilter;
      const filterTimeout = window.setTimeout(() => {
        try {
          filter.disconnect();
        } catch (error) {
          /* ignore */
        }
        if (state && state.shimmerFilter === filter) state.shimmerFilter = undefined;
        if (state) state.shimmerFilterTimeout = undefined;
      }, 800);
      state.shimmerFilterTimeout = filterTimeout;
    }
  }
};

const AmbientHumAPI = {
  startHum,
  stopHum,
  setProgressIntensity,
};

export default AmbientHumAPI;
