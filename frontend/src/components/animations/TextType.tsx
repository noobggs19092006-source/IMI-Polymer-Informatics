import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TextTypeProps {
  text: string;
  speed?: number; // ms per character
  delay?: number; // ms before starting
  className?: string;
  onComplete?: () => void;
  showCursor?: boolean;
}

export const TextType: React.FC<TextTypeProps> = ({
  text,
  speed = 50,
  delay = 0,
  className = '',
  onComplete,
  showCursor = true,
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    setDisplayedText('');
    setIsTyping(false);
    setHasStarted(false);

    let timeoutId: number;
    let intervalId: number;

    timeoutId = window.setTimeout(() => {
      setHasStarted(true);
      setIsTyping(true);
      
      let currentIndex = 0;
      intervalId = window.setInterval(() => {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;

        if (currentIndex >= text.length) {
          clearInterval(intervalId);
          setIsTyping(false);
          if (onComplete) onComplete();
        }
      }, speed);
    }, delay);

    return () => {
      clearTimeout(timeoutId);
      clearInterval(intervalId);
    };
  }, [text, speed, delay]);

  return (
    <span className={`inline-block ${className}`}>
      {displayedText}
      {showCursor && (isTyping || !hasStarted) && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 0] }}
          transition={{ repeat: Infinity, duration: 0.8 }}
          className="inline-block ml-1 w-[0.5em] h-[1em] align-middle bg-accent-primary"
          style={{ width: '2px', height: '1em' }}
        />
      )}
    </span>
  );
};
