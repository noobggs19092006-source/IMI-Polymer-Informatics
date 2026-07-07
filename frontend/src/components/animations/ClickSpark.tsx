import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Spark {
  id: number;
  x: number;
  y: number;
}

interface ClickSparkProps {
  children: React.ReactNode;
  color?: string;
}

export const ClickSpark: React.FC<ClickSparkProps> = ({ 
  children, 
  color = '#00D9FF' // Default to accent-primary
}) => {
  const [sparks, setSparks] = useState<Spark[]>([]);

  const handleClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newSpark = { id: Date.now(), x, y };
    setSparks((prev) => [...prev, newSpark]);
  }, []);

  // Clean up sparks after animation
  useEffect(() => {
    if (sparks.length > 0) {
      const timer = setTimeout(() => {
        setSparks((prev) => prev.slice(1));
      }, 600); // slightly longer than animation duration
      return () => clearTimeout(timer);
    }
  }, [sparks]);

  return (
    <div className="relative inline-block" onClick={handleClick}>
      {children}
      <AnimatePresence>
        {sparks.map((spark) => (
          <div
            key={spark.id}
            className="absolute pointer-events-none"
            style={{ left: spark.x, top: spark.y }}
          >
            {[...Array(12)].map((_, i) => {
              const angle = (i * 30 * Math.PI) / 180;
              const radius = 60 + Math.random() * 40; // 60-100px spread
              const targetX = Math.cos(angle) * radius;
              const targetY = Math.sin(angle) * radius;

              return (
                <motion.div
                  key={i}
                  className="absolute rounded-full"
                  style={{
                    backgroundColor: color,
                    width: Math.random() * 3 + 2 + 'px',
                    height: Math.random() * 3 + 2 + 'px',
                    boxShadow: `0 0 8px ${color}`,
                  }}
                  initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
                  animate={{ 
                    x: targetX, 
                    y: targetY, 
                    opacity: 0, 
                    scale: 0 
                  }}
                  transition={{ 
                    duration: 0.4 + Math.random() * 0.2, 
                    ease: "easeOut" 
                  }}
                />
              );
            })}
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
};
