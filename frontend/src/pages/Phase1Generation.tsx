import React, { useState } from 'react';
import { Send, RotateCcw, Zap, AlertCircle } from 'lucide-react';
import { TextType, ClickSpark, StarBorder } from '../components/animations';
import { useAppStore } from '../store/useAppStore';
import { motion } from 'framer-motion';

interface GeneratorState {
  backbone: string;
  leftGroup: string;
  rightGroup: string;
  dielectricConstant: number;
  tg: number;
  density: number;
  thickness: number;
  voltage: number;
  temperature: number;
}

const BACKBONES = [
  { id: 'PE', label: 'PE (Polyethylene)', eps: 2.2, tg: -120, density: 0.92 },
  { id: 'PP', label: 'PP (Polypropylene)', eps: 2.2, tg: -10, density: 0.90 },
  { id: 'PVC', label: 'PVC', eps: 3.5, tg: 80, density: 1.40 },
  { id: 'PTFE', label: 'PTFE (Teflon)', eps: 2.1, tg: 115, density: 2.20 },
  { id: 'PVDF', label: 'PVDF', eps: 12.0, tg: -35, density: 1.78 },
  { id: 'PS', label: 'Polystyrene', eps: 2.5, tg: 100, density: 1.05 },
  { id: 'PMMA', label: 'PMMA (Acrylic)', eps: 3.0, tg: 105, density: 1.18 },
  { id: 'PC', label: 'Polycarbonate', eps: 2.9, tg: 145, density: 1.20 },
  { id: 'PET', label: 'PET (Polyester)', eps: 3.3, tg: 75, density: 1.38 },
  { id: 'PA6', label: 'Nylon-6', eps: 3.5, tg: 47, density: 1.14 },
];

const FUNCTIONAL_GROUPS = ['C', 'CC', 'CCC', 'FC(F)(F)', 'Cl', 'CO', 'CC(=O)', 'c1ccccc1', 'N'];

interface Phase1GenerationProps {
  onGenerate?: (data: GeneratorState) => void;
}

export const Phase1Generation: React.FC<Phase1GenerationProps> = ({ onGenerate }) => {
  const { generatePolymer, generatorLoading, error, setError } = useAppStore();
  const [state, setState] = useState<GeneratorState>({
    backbone: 'PE',
    leftGroup: 'C',
    rightGroup: 'C',
    dielectricConstant: 2.2,
    tg: -120,
    density: 0.92,
    thickness: 500,
    voltage: 100,
    temperature: 25,
  });

  const [smiles, setSMILES] = useState<string>('');

  const backboneData = BACKBONES.find(b => b.id === state.backbone) || BACKBONES[0];

  // Auto-generate SMILES when backbone/groups change
  const generateSMILES = () => {
    // Simplified SMILES generation - replace with actual backend call
    const generatedSMILES = `${state.leftGroup}C${backboneData.id}C${state.rightGroup}`;
    setSMILES(generatedSMILES);
  };

  const handleBackboneChange = (backboneId: string) => {
    const backbone = BACKBONES.find(b => b.id === backboneId);
    if (backbone) {
      setState(prev => ({
        ...prev,
        backbone: backboneId,
        dielectricConstant: backbone.eps,
        tg: backbone.tg,
        density: backbone.density,
      }));
    }
  };

  const handleReset = () => {
    setState({
      backbone: 'PE',
      leftGroup: 'C',
      rightGroup: 'C',
      dielectricConstant: 2.2,
      tg: -120,
      density: 0.92,
      thickness: 500,
      voltage: 100,
      temperature: 25,
    });
    setSMILES('');
  };

  const handleGenerate = async () => {
    setError(null);
    setSMILES('');
    await generatePolymer(state);
    setTimeout(() => {
      generateSMILES();
      if (onGenerate) {
        onGenerate(state);
      }
    }, 900);
  };

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
          <TextType text="Phase 1: Polymer Configuration" speed={40} />
        </h1>
        <p className="text-text-secondary">
          <TextType 
            text="Select a backbone, functional groups, and physical parameters to configure your polymer."
            speed={20}
            delay={500}
          />
        </p>
      </motion.div>

      {/* Backbone Selection */}
      <motion.div variants={itemVariants} className="space-y-4">
        <div>
          <label className="text-sm font-bold text-accent-primary font-mono">Polymer Backbone</label>
          <p className="text-xs text-text-secondary mb-3">Choose from 10 industrial polymer families</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {BACKBONES.map(backbone => (
            <button
              key={backbone.id}
              onClick={() => handleBackboneChange(backbone.id)}
              className={`p-3 rounded-lg text-sm font-mono font-bold transition-all cursor-pointer ${
                state.backbone === backbone.id
                  ? 'bg-accent-primary text-white border border-accent-primary shadow-sm shadow-accent-primary/20'
                  : 'bg-bg-secondary border border-border hover:border-accent-primary/50 text-text-primary'
              }`}
            >
              {backbone.id}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Functional Groups */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Group */}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-bold text-accent-primary font-mono">Left Functional Group</label>
            <p className="text-xs text-text-secondary mb-3">Modify left terminus</p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {FUNCTIONAL_GROUPS.map(group => (
              <button
                key={`left-${group}`}
                onClick={() => setState(prev => ({ ...prev, leftGroup: group }))}
                className={`p-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  state.leftGroup === group
                    ? 'bg-accent-secondary text-white border border-accent-secondary shadow-sm shadow-accent-secondary/20'
                    : 'bg-bg-secondary border border-border hover:border-accent-secondary/50 text-text-primary'
                }`}
              >
                {group}
              </button>
            ))}
          </div>
        </div>

        {/* Right Group */}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-bold text-accent-primary font-mono">Right Functional Group</label>
            <p className="text-xs text-text-secondary mb-3">Modify right terminus</p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {FUNCTIONAL_GROUPS.map(group => (
              <button
                key={`right-${group}`}
                onClick={() => setState(prev => ({ ...prev, rightGroup: group }))}
                className={`p-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  state.rightGroup === group
                    ? 'bg-accent-secondary text-white border border-accent-secondary shadow-sm shadow-accent-secondary/20'
                    : 'bg-bg-secondary border border-border hover:border-accent-secondary/50 text-text-primary'
                }`}
              >
                {group}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Physical Parameters */}
      <motion.div variants={itemVariants} className="space-y-6 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl p-6 shadow-sm">
        <h3 className="font-bold text-accent-primary font-mono">Physical Parameters</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {/* Dielectric Constant */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Dielectric Constant (ε)
            </label>
            <input
              type="range"
              min="1"
              max="15"
              step="0.1"
              value={state.dielectricConstant}
              onChange={(e) => setState(prev => ({ ...prev, dielectricConstant: parseFloat(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.dielectricConstant.toFixed(1)}</div>
          </div>

          {/* Tg (Glass Transition) */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Tg (Glass Transition) °C
            </label>
            <input
              type="range"
              min="-150"
              max="200"
              step="1"
              value={state.tg}
              onChange={(e) => setState(prev => ({ ...prev, tg: parseInt(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.tg}°C</div>
          </div>

          {/* Density */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Density (g/cm³)
            </label>
            <input
              type="range"
              min="0.5"
              max="2.5"
              step="0.01"
              value={state.density}
              onChange={(e) => setState(prev => ({ ...prev, density: parseFloat(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.density.toFixed(2)}</div>
          </div>

          {/* Thickness */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Thickness (nm)
            </label>
            <input
              type="range"
              min="100"
              max="5000"
              step="100"
              value={state.thickness}
              onChange={(e) => setState(prev => ({ ...prev, thickness: parseInt(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.thickness} nm</div>
          </div>

          {/* Applied Voltage */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Applied Voltage (V)
            </label>
            <input
              type="range"
              min="10"
              max="500"
              step="10"
              value={state.voltage}
              onChange={(e) => setState(prev => ({ ...prev, voltage: parseInt(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.voltage} V</div>
          </div>

          {/* Temperature */}
          <div>
            <label className="text-xs font-mono font-bold text-text-secondary">
              Temperature (°C)
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="1"
              value={state.temperature}
              onChange={(e) => setState(prev => ({ ...prev, temperature: parseInt(e.target.value) }))}
              className="w-full mt-2"
            />
            <div className="text-sm font-mono text-accent-primary mt-1">{state.temperature}°C</div>
          </div>
        </div>
      </motion.div>

      {/* SMILES Display */}
      {smiles && (
        <motion.div 
          variants={itemVariants}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-4 bg-white/60 backdrop-blur-md border border-accent-primary/20 rounded-xl shadow-sm"
        >
          <p className="text-xs font-mono text-text-secondary mb-2">Generated SMILES String</p>
          <StarBorder isActive colorStart="#4F46E5" colorEnd="#06B6D4">
            <p className="font-mono text-sm text-accent-primary break-all">{smiles}</p>
          </StarBorder>
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div variants={itemVariants} className="flex gap-4 pt-4">
        {error && (
          <div className="w-full p-4 bg-red-900/30 border border-red-600/50 rounded-lg flex items-start gap-3 mb-4">
            <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-1" />
            <p className="text-sm text-red-200">{error}</p>
          </div>
        )}
        <ClickSpark>
          <button
            onClick={handleGenerate}
            disabled={generatorLoading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 disabled:opacity-50 text-white font-bold rounded-lg transition-all cursor-pointer"
          >
            {generatorLoading ? (
              <>
                <Zap size={20} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Send size={20} />
                Generate Polymer
              </>
            )}
          </button>
        </ClickSpark>

        <ClickSpark>
          <button
            onClick={handleReset}
            className="px-6 py-3 bg-bg-secondary hover:bg-bg-secondary/80 border border-border text-text-primary font-bold rounded-lg transition-all cursor-pointer"
          >
            <RotateCcw size={20} />
          </button>
        </ClickSpark>
      </motion.div>

      <motion.div variants={itemVariants} className="p-4 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl shadow-sm">
        <p className="text-xs text-text-secondary font-mono">
          <strong>Tip:</strong> Configure polymer backbone, functional groups, and physical parameters. The system will generate a unique SMILES string and prepare it for ML prediction. Each configuration represents a unique polymer candidate in the virtual library.
        </p>
      </motion.div>
    </motion.div>
  );
};
