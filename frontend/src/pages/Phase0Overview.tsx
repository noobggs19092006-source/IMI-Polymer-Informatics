import React from 'react';
import { ArrowRight, Zap, Database, Cpu, Search } from 'lucide-react';
import { TextType, ClickSpark } from '../components/animations';
import { motion } from 'framer-motion';

interface Phase0OverviewProps {
  onAdvance: () => void;
}

export const Phase0Overview: React.FC<Phase0OverviewProps> = ({ onAdvance }) => {
  const stats = [
    { label: 'Polymer Backbones', value: '10', icon: Database },
    { label: 'Functional Groups', value: '72', icon: Zap },
    { label: 'Total Configurations', value: '1440', icon: Cpu },
    { label: 'Successful Simulations', value: '551', icon: Search },
  ];

  const phases = [
    { num: 1, title: 'Data Generation', desc: 'Combinatorial polymer library creation' },
    { num: 2, title: 'ANSYS Simulation', desc: 'Maxwell 2D electrostatic analysis' },
    { num: 3, title: 'ML Training', desc: '3-Way Ensemble model training' },
    { num: 4, title: 'Inverse Design', desc: 'Virtual high-throughput screening' },
    { num: 5, title: 'Advanced Analytics', desc: 'Pareto & generative discovery' },
    { num: 6, title: 'Results Export', desc: 'Candidate polymer export' },
  ];

  return (
    <div className="space-y-12">
      {/* Welcome Section */}
      <div className="space-y-6">
        <div>
          <h1 className="text-5xl font-bold mb-4 font-mono">
            <TextType text="Polymer Informatics" speed={50} />
          </h1>
          <h2 className="text-2xl text-accent-primary mb-6 font-mono">
            <TextType text="ANSYS-Validated Materials Discovery" speed={40} delay={1000} />
          </h2>
        </div>

        <p className="text-lg text-text-secondary leading-relaxed max-w-3xl">
          <TextType 
            text="This platform combines ANSYS Maxwell 2D finite-element simulations with physics-informed machine learning and advanced optimization algorithms to discover novel polymer materials with target dielectric properties. Train, predict, and optimize in real-time."
            speed={15}
            delay={1500}
          />
        </p>
      </div>

      {/* Key Statistics */}
      <div>
        <h3 className="text-xl font-bold mb-6 font-mono text-accent-primary">Dataset Overview</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 + 2.5 }}
                className="p-5 bg-bg-primary/50 border border-border rounded-lg hover:border-accent-primary/50 transition-all"
              >
                <Icon size={24} className="text-accent-primary mb-3" />
                <div className="text-3xl font-bold text-accent-primary">{stat.value}</div>
                <div className="text-xs text-text-secondary mt-2 font-mono">{stat.label}</div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Pipeline Overview */}
      <div>
        <h3 className="text-xl font-bold mb-6 font-mono text-accent-primary">Complete Pipeline</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {phases.map((phase, i) => (
            <motion.div
              key={phase.num}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 + 3 }}
              className="p-4 bg-gradient-to-br from-accent-primary/10 to-accent-secondary/10 border border-border rounded-lg hover:border-accent-primary transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-accent-primary text-bg-primary flex items-center justify-center font-bold text-sm font-mono">
                  {phase.num}
                </div>
                <div>
                  <h4 className="font-bold text-text-primary">{phase.title}</h4>
                  <p className="text-sm text-text-secondary mt-1">{phase.desc}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Key Capabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-bg-primary/50 border border-border rounded-lg">
          <h4 className="font-bold text-accent-primary mb-3 font-mono flex items-center gap-2">
            <Cpu size={18} /> 3-Way ML Ensemble
          </h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>• MLP Neural Network</li>
            <li>• Gradient Boosting Regressor</li>
            <li>• XGBoost Ensemble</li>
            <li>• R² = 0.9558 | CV = 0.9073</li>
          </ul>
        </div>

        <div className="p-6 bg-bg-primary/50 border border-border rounded-lg">
          <h4 className="font-bold text-accent-primary mb-3 font-mono flex items-center gap-2">
            <Search size={18} /> Advanced Models
          </h4>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li>• Graph Neural Networks (GNN)</li>
            <li>• Variational Autoencoders (VAE)</li>
            <li>• Pareto Front Optimization</li>
            <li>• Generative Discovery</li>
          </ul>
        </div>
      </div>

      {/* CTA */}
      <div className="flex flex-col gap-4 pt-8 border-t border-border/50">
        <p className="text-sm text-text-secondary font-mono">Ready to begin polymer discovery?</p>
        <ClickSpark>
          <button 
            onClick={onAdvance}
            className="w-full flex items-center justify-center gap-3 px-8 py-4 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded-lg transition-all hover:scale-105 cursor-pointer"
          >
            <span>Begin Discovery Journey</span>
            <ArrowRight size={20} />
          </button>
        </ClickSpark>
      </div>
    </div>
  );
};
