import React from 'react';
import CountUpModule from 'react-countup';

const CountUp = (CountUpModule as any).default || CountUpModule;
import { motion } from 'framer-motion';

interface CountUpMetricProps {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  label: string;
  delay?: number;
}

export const CountUpMetric: React.FC<CountUpMetricProps> = ({
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
  duration = 2.5,
  label,
  delay = 0,
}) => {
  return (
    <motion.div 
      className="flex flex-col items-center justify-center p-4 bg-bg-secondary rounded-lg border border-border hover:border-accent-primary transition-colors"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
    >
      <div className="text-sm text-text-secondary font-mono mb-2 uppercase tracking-wider text-center">
        {label}
      </div>
      <div className="text-3xl font-bold text-accent-primary font-mono drop-shadow-[0_0_8px_rgba(79,70,229,0.2)]">
        <CountUp
          start={0}
          end={value}
          decimals={decimals}
          duration={duration}
          separator=","
          prefix={prefix}
          suffix={suffix}
          useEasing={true}
          delay={delay}
        />
      </div>
    </motion.div>
  );
};
