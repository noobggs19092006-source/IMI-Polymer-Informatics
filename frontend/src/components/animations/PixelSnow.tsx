import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  size: number;
  speedY: number;
  speedX: number;
  opacity: number;
}

export const PixelSnow: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    let particles: Particle[] = [];
    let animationFrameId: number;
    let width = window.innerWidth;
    let height = window.innerHeight;

    const initCanvas = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      initParticles();
    };

    const initParticles = () => {
      particles = [];
      const particleCount = Math.floor((width * height) / 15000); // Responsive density
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          size: Math.random() * 2 + 1, // 1-3px squares
          speedY: Math.random() * 0.5 + 0.1, // Slow falling
          speedX: (Math.random() - 0.5) * 0.3, // Slight drift
          opacity: Math.random() * 0.5 + 0.2, // 0.2-0.7 opacity
        });
      }
    };

    const draw = () => {
      // Clear with solid background for performance (no alpha blending on bg)
      ctx.fillStyle = '#0F1419';
      ctx.fillRect(0, 0, width, height);

      particles.forEach((p) => {
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
        // Draw square pixels
        ctx.fillRect(p.x, p.y, p.size, p.size);

        // Update position
        p.y += p.speedY;
        p.x += p.speedX;

        // Reset if out of bounds
        if (p.y > height) {
          p.y = -p.size;
          p.x = Math.random() * width;
        }
        if (p.x > width) {
          p.x = -p.size;
        } else if (p.x < -p.size) {
          p.x = width;
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', initCanvas);
    initCanvas();
    draw();

    return () => {
      window.removeEventListener('resize', initCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[-1]"
      style={{ background: '#0F1419' }}
    />
  );
};
