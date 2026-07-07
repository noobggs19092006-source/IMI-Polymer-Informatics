import React from 'react';
import { motion } from 'framer-motion';
import { type LucideIcon } from 'lucide-react';

export interface MenuItem {
  id: string;
  label: string;
  icon?: LucideIcon;
}

interface StaggeredMenuProps {
  items: MenuItem[];
  activeId: string;
  onSelect: (id: string) => void;
}

const listVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { type: 'spring' as const, stiffness: 300, damping: 24 }
  },
};

export const StaggeredMenu: React.FC<StaggeredMenuProps> = ({ items, activeId, onSelect }) => {
  return (
    <motion.ul
      className="flex flex-col space-y-2"
      variants={listVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item) => {
        const isActive = activeId === item.id;
        const Icon = item.icon;

        return (
          <motion.li key={item.id} variants={itemVariants}>
            <button
              onClick={() => onSelect(item.id)}
              className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-all duration-200 group ${
                isActive
                  ? 'bg-bg-secondary text-accent-primary border border-border/80 shadow-[0_0_10px_rgba(79,70,229,0.1)]'
                  : 'text-text-secondary hover:bg-bg-secondary/55 hover:text-text-primary'
              }`}
            >
              {Icon && (
                <Icon
                  className={`mr-3 w-5 h-5 transition-colors ${
                    isActive ? 'text-accent-primary drop-shadow-[0_0_5px_rgba(79,70,229,0.3)]' : 'group-hover:text-accent-primary'
                  }`}
                />
              )}
              <span className="font-mono text-sm tracking-wide">{item.label}</span>
              
              {isActive && (
                <motion.div
                  layoutId="active-indicator"
                  className="ml-auto w-1.5 h-1.5 rounded-full bg-accent-primary drop-shadow-[0_0_5px_rgba(79,70,229,0.8)]"
                />
              )}
            </button>
          </motion.li>
        );
      })}
    </motion.ul>
  );
};
