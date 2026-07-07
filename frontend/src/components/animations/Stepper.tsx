import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

export interface Phase {
  id: number;
  label: string;
}

interface StepperProps {
  phases: Phase[];
  currentPhase: number;
  onPhaseClick?: (phaseId: number) => void;
}

export const Stepper: React.FC<StepperProps> = ({ phases, currentPhase, onPhaseClick }) => {
  return (
    <div className="w-full flex items-center justify-between relative px-4">
      {/* Background connecting line */}
      <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-200 -translate-y-1/2 z-0" />

      {/* Animated active connecting line */}
      <motion.div
        className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-[#7342E2] to-[#06B6D4] -translate-y-1/2 z-0"
        initial={{ width: '0%' }}
        animate={{ width: `${(currentPhase / (phases.length - 1)) * 100}%` }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
      />

      {phases.map((phase, index) => {
        const isCompleted = currentPhase > index;
        const isActive = currentPhase === index;
        const isUpcoming = currentPhase < index;

        return (
          <div key={phase.id} className="relative z-10 flex flex-col items-center group">
            <motion.button
              onClick={() => onPhaseClick && onPhaseClick(phase.id)}
              disabled={isUpcoming && !onPhaseClick}
              className={`w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors duration-300 cursor-pointer ${
                isActive
                  ? 'bg-white border-[#7342E2] text-[#7342E2] shadow-[0_0_15px_rgba(115,66,226,0.25)]'
                  : isCompleted
                  ? 'bg-[#10B981] border-[#10B981] text-white shadow-sm shadow-emerald-100'
                  : 'bg-[#F8FAFC] border-slate-200 text-slate-400 hover:border-slate-300'
              }`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              whileHover={{ scale: isUpcoming ? 1 : 1.1 }}
              whileTap={{ scale: isUpcoming ? 1 : 0.95 }}
            >
              {isCompleted ? <Check size={20} strokeWidth={3} /> : phase.id + 1}
            </motion.button>
            
            {/* Active pulse effect */}
            {isActive && (
              <motion.div
                className="absolute w-12 h-12 rounded-full border-2 border-[#7342E2]"
                animate={{ scale: [1, 1.5], opacity: [0.8, 0] }}
                transition={{ repeat: Infinity, duration: 1.5, ease: 'easeOut' }}
              />
            )}

            <motion.span
              className={`absolute top-14 text-xs whitespace-nowrap font-mono transition-colors duration-300 ${
                isActive ? 'text-[#7342E2] font-bold' : isCompleted ? 'text-slate-700' : 'text-slate-400'
              }`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 + 0.2 }}
            >
              {phase.label}
            </motion.span>
          </div>
        );
      })}
    </div>
  );
};
