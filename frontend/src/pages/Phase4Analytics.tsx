import React from 'react';
import { TrendingUp, Activity, Zap, LineChart } from 'lucide-react';
import { TextType, CountUpMetric } from '../components/animations';
import { motion } from 'framer-motion';

interface Phase4AnalyticsProps {
  onExport?: (format: string) => void;
}

export const Phase4Analytics: React.FC<Phase4AnalyticsProps> = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <motion.div 
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold mb-2 font-mono">
          <TextType text="Phase 4: Advanced Analytics" speed={40} />
        </h1>
        <p className="text-text-secondary">
          <TextType 
            text="Explore Pareto fronts, generative discovery, and advanced model comparison metrics."
            speed={20}
            delay={500}
          />
        </p>
      </motion.div>

      {/* Performance Metrics Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <CountUpMetric 
          label="R² Score"
          value={0.9558}
          decimals={4}
          duration={2.5}
        />
        <CountUpMetric 
          label="Accuracy"
          value={95.3}
          decimals={1}
          suffix="%"
          duration={3}
        />
        <CountUpMetric 
          label="Simulations"
          value={551}
          suffix=" / 1440"
          duration={2.5}
        />
        <CountUpMetric 
          label="MSE"
          value={0.0125}
          decimals={4}
          duration={2}
        />
      </motion.div>

      {/* Three-Column Analytics Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pareto Front Visualization */}
        <motion.div 
          variants={itemVariants}
          className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5"
        >
          <h3 className="font-bold text-accent-primary font-mono flex items-center gap-2">
            <TrendingUp size={18} /> Pareto Front Optimization
          </h3>
          <div className="space-y-3">
            <p className="text-sm text-text-secondary">
              Multi-objective optimization showing trade-off between model accuracy and inference speed.
            </p>
            <div className="h-48 bg-white/40 backdrop-blur-sm border border-white/80 rounded flex items-center justify-center shadow-sm">
              <div className="text-center space-y-2">
                <LineChart size={32} className="text-accent-primary mx-auto" />
                <p className="text-xs text-text-secondary font-mono">Pareto Front Visualization</p>
                <p className="text-xs text-text-secondary">(Scatter plot ready)</p>
              </div>
            </div>
            <ul className="text-xs text-text-secondary space-y-1">
              <li>• Ensemble: High accuracy, moderate speed</li>
              <li>• GNN: Balanced performance</li>
              <li>• VAE: Lower accuracy, faster inference</li>
            </ul>
          </div>
        </motion.div>

        {/* Generative Discovery (VAE) */}
        <motion.div 
          variants={itemVariants}
          className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5"
        >
          <h3 className="font-bold text-accent-primary font-mono flex items-center gap-2">
            <Zap size={18} /> Generative Discovery
          </h3>
          <div className="space-y-3">
            <p className="text-sm text-text-secondary">
              Explore the latent space of the VAE to generate novel polymer candidates.
            </p>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-mono text-text-secondary">Latent Dimension 1</label>
                <input 
                  type="range" 
                  min="-3" 
                  max="3" 
                  step="0.1" 
                  defaultValue="0"
                  className="w-full mt-2"
                />
              </div>
              <div>
                <label className="text-xs font-mono text-text-secondary">Latent Dimension 2</label>
                <input 
                  type="range" 
                  min="-3" 
                  max="3" 
                  step="0.1" 
                  defaultValue="0"
                  className="w-full mt-2"
                />
              </div>
            </div>
            <div className="h-32 bg-white/40 backdrop-blur-sm border border-white/80 rounded flex items-center justify-center shadow-sm">
              <p className="text-xs text-text-secondary font-mono">Molecule Preview</p>
            </div>
            <button className="w-full px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded text-sm transition-all cursor-pointer">
              Generate & Test
            </button>
          </div>
        </motion.div>

        {/* Model Comparison Dashboard */}
        <motion.div 
          variants={itemVariants}
          className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5"
        >
          <h3 className="font-bold text-accent-primary font-mono flex items-center gap-2">
            <Activity size={18} /> Model Comparison
          </h3>
          <div className="space-y-3">
            <table className="w-full text-xs">
              <tbody className="space-y-2">
                <tr className="border-b border-border pb-2">
                  <td className="text-text-secondary font-mono">Ensemble</td>
                  <td className="text-right text-accent-primary font-bold">0.9558</td>
                </tr>
                <tr className="border-b border-border pb-2">
                  <td className="text-text-secondary font-mono">GNN</td>
                  <td className="text-right text-accent-primary font-bold">0.9528</td>
                </tr>
                <tr>
                  <td className="text-text-secondary font-mono">VAE</td>
                  <td className="text-right text-accent-primary font-bold">0.8945</td>
                </tr>
              </tbody>
            </table>
            <div className="pt-3 border-t border-border">
              <p className="text-xs text-text-secondary mb-2">Cross-Validation Robustness</p>
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>Ensemble</span>
                    <span className="text-accent-primary">0.9073</span>
                  </div>
                  <div className="w-full h-2 bg-bg-primary rounded overflow-hidden">
                    <div className="h-full bg-accent-primary" style={{ width: '90.73%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>GNN</span>
                    <span className="text-accent-primary">0.9301</span>
                  </div>
                  <div className="w-full h-2 bg-bg-primary rounded overflow-hidden">
                    <div className="h-full bg-accent-primary" style={{ width: '93.01%' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Feature Importance */}
      <motion.div 
        variants={itemVariants}
        className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5"
      >
        <h3 className="font-bold text-accent-primary font-mono">Feature Importance Analysis</h3>
        <div className="space-y-3">
          <p className="text-sm text-text-secondary">Top contributing features to model predictions:</p>
          <div className="space-y-2">
            {[
              { name: 'Dielectric Constant', importance: 0.285 },
              { name: 'Thickness (nm)', importance: 0.241 },
              { name: 'Morgan Fingerprint #1', importance: 0.198 },
              { name: 'Applied Voltage', importance: 0.147 },
              { name: 'Temperature', importance: 0.089 },
              { name: 'Glass Transition (Tg)', importance: 0.040 },
            ].map((feat) => (
              <div key={feat.name} className="flex items-center gap-3">
                <span className="text-xs text-text-secondary flex-shrink-0 w-32">{feat.name}</span>
                <div className="flex-1 h-6 bg-bg-primary rounded overflow-hidden border border-border">
                  <motion.div
                    className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                    initial={{ width: 0 }}
                    animate={{ width: `${feat.importance * 100}%` }}
                    transition={{ duration: 1, delay: 0.2 }}
                  />
                </div>
                <span className="text-xs text-accent-primary font-bold w-12 text-right">
                  {(feat.importance * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Error Distribution */}
      <motion.div 
        variants={itemVariants}
        className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5"
      >
        <h3 className="font-bold text-accent-primary font-mono">Prediction Error Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-text-secondary mb-4">Error Distribution (Test Set)</p>
            <div className="h-40 bg-white/40 backdrop-blur-sm border border-white/80 rounded flex items-center justify-center shadow-sm">
              <p className="text-xs text-text-secondary font-mono">Histogram (Error density)</p>
            </div>
          </div>
          <div>
            <p className="text-sm text-text-secondary mb-4">Predicted vs Actual</p>
            <div className="h-40 bg-white/40 backdrop-blur-sm border border-white/80 rounded flex items-center justify-center shadow-sm">
              <p className="text-xs text-text-secondary font-mono">Scatter plot (R² = 0.9558)</p>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
          <div>
            <p className="text-xs text-text-secondary mb-2">Mean Error</p>
            <p className="text-2xl font-bold text-accent-primary">0.847 pF/m</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-2">Std Dev</p>
            <p className="text-2xl font-bold text-accent-primary">4.231 pF/m</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary mb-2">Max Error</p>
            <p className="text-2xl font-bold text-accent-primary">18.456 pF/m</p>
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="p-4 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl shadow-sm">
        <p className="text-xs text-text-secondary font-mono">
          <strong>Advanced Analytics:</strong> Explore model performance across multiple dimensions. The Pareto front shows accuracy-speed trade-offs, generative discovery enables novel polymer design, and error analysis helps understand model limitations.
        </p>
      </motion.div>
    </motion.div>
  );
};
