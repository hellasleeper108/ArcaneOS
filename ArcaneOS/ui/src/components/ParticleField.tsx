import React, { useEffect, useRef } from 'react';

interface ParticleFieldProps {
  veil: boolean;
  count?: number;
}

type Particle = {
  x: number;
  y: number;
  radius: number;
  velocityX: number;
  velocityY: number;
  hue: number;
  alpha: number;
};

const clampCount = (count?: number) => {
  if (typeof count !== 'number') return 72;
  return Math.min(Math.max(Math.floor(count), 60), 80);
};

export const ParticleField: React.FC<ParticleFieldProps> = ({ veil, count }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null);
  const particlesRef = useRef<Particle[]>([]);

  const initParticles = (width: number, height: number) => {
    const particleCount = clampCount(count);
    particlesRef.current = Array.from({ length: particleCount }, () => {
      const hue = 160 + Math.random() * 30;
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        radius: 0.5 + Math.random() * 1.3,
        velocityX: (Math.random() - 0.5) * 0.12,
        velocityY: (Math.random() - 0.5) * 0.12,
        hue,
        alpha: 0.25 + Math.random() * 0.3,
      };
    });
  };

  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    const width = parent ? parent.clientWidth : window.innerWidth;
    const height = parent ? parent.clientHeight : window.innerHeight;
    const dpr = window.devicePixelRatio || 1;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);
    initParticles(width, height);
  };

  const drawFrame = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    ctx.globalCompositeOperation = 'lighter';

    particlesRef.current.forEach((particle) => {
      particle.x += particle.velocityX;
      particle.y += particle.velocityY;

      if (particle.x < -5) particle.x = width + 5;
      if (particle.x > width + 5) particle.x = -5;
      if (particle.y < -5) particle.y = height + 5;
      if (particle.y > height + 5) particle.y = -5;

      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${particle.hue}, 80%, 65%, ${particle.alpha})`;
      ctx.shadowColor = `hsla(${particle.hue}, 95%, 72%, 0.8)`;
      ctx.shadowBlur = 10;
      ctx.fill();
    });

    ctx.globalCompositeOperation = 'source-over';
    animationRef.current = requestAnimationFrame(drawFrame);
  };

  useEffect(() => {
    if (!veil) return;
    resizeCanvas();
    drawFrame();
    const handleResize = () => resizeCanvas();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [veil, count]);

  useEffect(() => {
    if (!veil && animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
  }, [veil]);

  if (!veil) return null;

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 z-10 opacity-90"
    />
  );
};

export default ParticleField;
