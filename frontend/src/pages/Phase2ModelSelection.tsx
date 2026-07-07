import React, { useState } from 'react';
import { CheckCircle2, Brain, Zap, Database } from 'lucide-react';
import { TextType, ClickSpark, StarBorder } from '../components/animations';
import { motion } from 'framer-motion';

interface Model {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  r2: number;
  cv: number;
  rmse: number;
  mae: number;
  features: string[];
  specs: string[];
}

const MODELS: Model[] = [
  {
    id: 'ensemble',
    name: '3-Way Ensemble',
    description: 'MLP + Gradient Boosting + XGBoost',
    icon: <Zap className="w-8 h-8" />,
    r2: 0.9558,
    cv: 0.9073,
    rmse: 12.34,
    mae: 8.76,
    features: ['512 Morgan bits', '6 physical props', 'PCA reduced to 64D'],
    specs: [
      'Multi-model voting',
      'Robust to outliers',
      'Fast inference',
      'Stable performance',
    ],
  },
  {
    id: 'gnn',
    name: 'Graph Neural Network',
    description: 'Graph-based molecular representation',
    icon: <Brain className="w-8 h-8" />,
    r2: 0.9528,
    cv: 0.9301,
    rmse: 13.12,
    mae: 9.34,
    features: ['Graph topology', 'Atom embeddings', 'Bond features'],
    specs: [
      'Molecular structure aware',
      'Interpretable graphs',
      'Transfer learning capable',
      'Higher CV robustness',
    ],
  },
  {
    id: 'vae',
    name: 'Variational Autoencoder',
    description: 'Generative model for discovery',
    icon: <Database className="w-8 h-8" />,
    r2: 0.8945,
    cv: 0.8712,
    rmse: 18.56,
    mae: 14.23,
    features: ['128D latent space', 'Reconstruction loss', 'KL divergence'],
    specs: [
      'Generative discovery',
      'Latent space exploration',
      'Novel polymers synthesis',
      'Uncertainty quantification',
    ],
  },
];

interface Phase2ModelSelectionProps {
  onSelectModel?: (modelId: string) => void;
}

export const Phase2ModelSelection: React.FC<Phase2ModelSelectionProps> = ({ onSelectModel }) => {
  const [selectedModel, setSelectedModel] = useState<string>('ensemble');

  const handleSelectModel = (modelId: string) => {
    setSelectedModel(modelId);
    if (onSelectModel) {
      onSelectModel(modelId);
    }
  };

  const currentModel = MODELS.find(m => m.id === selectedModel) || MODELS[0];

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
          <TextType text="Phase 2: ML Model Selection" speed={40} />
        </h1>
        <p className="text-text-secondary">
          <TextType 
            text="Choose from multiple pre-trained models for polymer property prediction. Each model has unique strengths in accuracy, robustness, and interpretability."
            speed={20}
            delay={500}
          />
        </p>
      </motion.div>

      {/* Model Cards Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {MODELS.map((model) => (
          <ClickSpark key={model.id}>
            <motion.button
              onClick={() => handleSelectModel(model.id)}
              className={`h-full text-left transition-all rounded-xl overflow-hidden cursor-pointer ${
                selectedModel === model.id
                  ? 'ring-2 ring-accent-primary shadow-md shadow-accent-primary/20'
                  : 'hover:ring-2 hover:ring-accent-primary/50'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <StarBorder 
                isActive={selectedModel === model.id}
                className="w-full h-full"
                colorStart="#4F46E5"
                colorEnd="#06B6D4"
              >
                <div className="h-full space-y-4">
                  {/* Header */}
                  <div>
                    <div className="flex items-start justify-between mb-3">
                      <div className="text-accent-primary">{model.icon}</div>
                      {selectedModel === model.id && (
                        <CheckCircle2 size={20} className="text-accent-primary" />
                      )}
                    </div>
                    <h3 className="text-lg font-bold text-text-primary">{model.name}</h3>
                    <p className="text-xs text-text-secondary mt-1">{model.description}</p>
                  </div>

                  {/* Key Metrics */}
                  <div className="grid grid-cols-2 gap-3 pt-3 border-t border-border/50">
                    <div>
                      <p className="text-xs text-text-secondary font-mono">R² Score</p>
                      <p className="text-sm font-bold text-accent-primary">{model.r2.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary font-mono">CV Score</p>
                      <p className="text-sm font-bold text-accent-primary">{model.cv.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary font-mono">RMSE</p>
                      <p className="text-sm font-bold text-accent-primary">{model.rmse.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary font-mono">MAE</p>
                      <p className="text-sm font-bold text-accent-primary">{model.mae.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="pt-3 border-t border-border/50">
                    <p className="text-xs font-mono text-text-secondary mb-2">Features</p>
                    <div className="space-y-1">
                      {model.features.map((feat, i) => (
                        <p key={i} className="text-xs text-text-secondary">• {feat}</p>
                      ))}
                    </div>
                  </div>
                </div>
              </StarBorder>
            </motion.button>
          </ClickSpark>
        ))}
      </motion.div>

      {/* Selected Model Details */}
      {selectedModel && (
        <motion.div
          variants={itemVariants}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-6 bg-white/70 backdrop-blur-xl border border-white/80 rounded-xl space-y-6 shadow-md shadow-indigo-100/5"
        >
          <div>
            <h3 className="text-xl font-bold mb-4 font-mono flex items-center gap-2">
              <CheckCircle2 size={20} className="text-accent-primary" />
              {currentModel.name} - Detailed Specifications
            </h3>
          </div>

          {/* Specifications Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-mono font-bold text-accent-primary mb-3">Key Features</h4>
              <ul className="space-y-2">
                {currentModel.features.map((feat, i) => (
                  <li key={i} className="text-sm text-text-secondary flex items-start gap-2">
                    <span className="text-accent-primary mt-1">→</span>
                    {feat}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-mono font-bold text-accent-primary mb-3">Capabilities</h4>
              <ul className="space-y-2">
                {currentModel.specs.map((spec, i) => (
                  <li key={i} className="text-sm text-text-secondary flex items-start gap-2">
                    <span className="text-accent-primary mt-1">→</span>
                    {spec}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Detailed Metrics */}
          <div className="pt-4 border-t border-border/50">
            <h4 className="font-mono font-bold text-accent-primary mb-4">Performance Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 bg-white/50 backdrop-blur-sm rounded-lg border border-white/80 shadow-sm">
                <p className="text-xs text-text-secondary font-mono mb-2">R² Score</p>
                <p className="text-2xl font-bold text-accent-primary">
                  {(currentModel.r2 * 100).toFixed(2)}%
                </p>
              </div>
              <div className="p-3 bg-white/50 backdrop-blur-sm rounded-lg border border-white/80 shadow-sm">
                <p className="text-xs text-text-secondary font-mono mb-2">CV Score</p>
                <p className="text-2xl font-bold text-accent-primary">
                  {(currentModel.cv * 100).toFixed(2)}%
                </p>
              </div>
              <div className="p-3 bg-white/50 backdrop-blur-sm rounded-lg border border-white/80 shadow-sm">
                <p className="text-xs text-text-secondary font-mono mb-2">RMSE</p>
                <p className="text-2xl font-bold text-accent-primary">
                  {currentModel.rmse.toFixed(1)}
                </p>
              </div>
              <div className="p-3 bg-white/50 backdrop-blur-sm rounded-lg border border-white/80 shadow-sm">
                <p className="text-xs text-text-secondary font-mono mb-2">MAE</p>
                <p className="text-2xl font-bold text-accent-primary">
                  {currentModel.mae.toFixed(1)}
                </p>
              </div>
            </div>
          </div>

          <div className="p-3 bg-white/40 backdrop-blur-sm rounded-lg border border-white/80 shadow-sm">
            <p className="text-xs text-text-secondary font-mono">
              <strong>Note:</strong> The selected model will be used for all subsequent predictions in the inverse design phase. Choose based on your accuracy requirements and use case (ensemble for robustness, GNN for interpretability, VAE for generative discovery).
            </p>
          </div>
        </motion.div>
      )}

      {/* Comparison Table */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-bold font-mono text-accent-primary">Model Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 px-3 font-mono text-xs text-text-secondary">Model</th>
                <th className="text-right py-2 px-3 font-mono text-xs text-text-secondary">R²</th>
                <th className="text-right py-2 px-3 font-mono text-xs text-text-secondary">CV</th>
                <th className="text-right py-2 px-3 font-mono text-xs text-text-secondary">RMSE</th>
                <th className="text-right py-2 px-3 font-mono text-xs text-text-secondary">MAE</th>
              </tr>
            </thead>
            <tbody>
              {MODELS.map(model => (
                <tr 
                  key={model.id}
                  className={`border-b border-border/50 transition-all cursor-pointer ${
                    selectedModel === model.id
                      ? 'bg-accent-primary/10 border-l-2 border-l-accent-primary font-bold'
                      : 'hover:bg-bg-primary/60'
                  }`}
                >
                  <td className="py-3 px-3 font-mono text-text-primary">{model.name}</td>
                  <td className="text-right py-3 px-3 text-accent-primary font-bold">{model.r2.toFixed(4)}</td>
                  <td className="text-right py-3 px-3 text-accent-primary font-bold">{model.cv.toFixed(4)}</td>
                  <td className="text-right py-3 px-3 text-accent-primary font-bold">{model.rmse.toFixed(2)}</td>
                  <td className="text-right py-3 px-3 text-accent-primary font-bold">{model.mae.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="p-4 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl shadow-sm">
        <p className="text-xs text-text-secondary font-mono">
          <strong>All models trained on 551 successful ANSYS simulations</strong> with 10-fold cross-validation. Click on a model card to see details and use it for predictions in the Inverse Design phase.
        </p>
      </motion.div>
    </motion.div>
  );
};
