import React from 'react';
import { motion } from 'framer-motion';

interface StarBorderProps {
  children: React.ReactNode;
  isActive?: boolean;
  colorStart?: string;
  colorEnd?: string;
  className?: string;
}

export const StarBorder: React.FC<StarBorderProps> = ({
  children,
  isActive = true,
  colorStart = '#4F46E5',
  colorEnd = '#06B6D4',
  className = '',
}) => {
  if (!isActive) {
    return <div className={`relative ${className}`}>{children}</div>;
  }

  return (
    <div className={`relative inline-block overflow-hidden rounded-xl p-[2px] ${className}`}>
      {/* Animated gradient background (the border) */}
      <motion.div
        className="absolute inset-[-100%] rounded-xl opacity-80"
        style={{
          background: `conic-gradient(from 0deg, transparent 0 340deg, ${colorStart} 360deg)`,
        }}
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          repeat: Infinity,
          duration: 3,
          ease: "linear",
        }}
      />
      <motion.div
        className="absolute inset-[-100%] rounded-xl opacity-80"
        style={{
          background: `conic-gradient(from 180deg, transparent 0 340deg, ${colorEnd} 360deg)`,
        }}
        animate={{
          rotate: [180, 540],
        }}
        transition={{
          repeat: Infinity,
          duration: 3,
          ease: "linear",
        }}
      />
      
      {/* Inner content wrapper blocking the center of the gradient */}
      <div className="relative h-full w-full rounded-[10px] bg-bg-secondary p-4 z-10">
        {children}
      </div>
    </div>
  );
};
