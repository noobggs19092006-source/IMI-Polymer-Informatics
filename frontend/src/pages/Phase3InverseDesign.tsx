import React from 'react';
import { Play, Download, Eye, AlertCircle, Trophy } from 'lucide-react';
import { TextType, ClickSpark, StarBorder } from '../components/animations';
import { useAppStore } from '../store/useAppStore';
import { motion } from 'framer-motion';

interface SearchParams {
  targetCapacitance: number;
  librarySize: number;
  thicknessMin: number;
  thicknessMax: number;
  materials: string[];
  selectedModel: string;
}

const MATERIALS = ['PE', 'PP', 'PVC', 'PTFE', 'PVDF', 'PS', 'PMMA', 'PC', 'PET', 'PA6'];

export const Phase3InverseDesign: React.FC = () => {
  const { discoveryResults, discoveryLoading, runDiscovery, error, setError, selectedModel } = useAppStore();
  const [params, setParams] = React.useState<SearchParams>({
    targetCapacitance: 200,
    librarySize: 10000,
    thicknessMin: 500,
    thicknessMax: 3000,
    materials: MATERIALS,
    selectedModel: 'ensemble',
  });

  const [searchComplete, setSearchComplete] = React.useState(false);

  const handleSearch = async () => {
    setError(null);
    setSearchComplete(false);
    
    const searchParams = {
      targetCapacitance: params.targetCapacitance,
      librarySize: params.librarySize,
      materials: params.materials,
      model: selectedModel,
    };

    await runDiscovery(searchParams);
    
    setTimeout(() => {
      setSearchComplete(true);
    }, 2600);
  };

  const toggleMaterial = (material: string) => {
    setParams(prev => ({
      ...prev,
      materials: prev.materials.includes(material)
        ? prev.materials.filter(m => m !== material)
        : [...prev.materials, material],
    }));
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
          <TextType text="Phase 3: Inverse Design Discovery" speed={40} />
        </h1>
        <p className="text-text-secondary">
          <TextType 
            text="Define target capacitance and constraints. The system will screen a virtual library to find optimal polymer candidates."
            speed={20}
            delay={500}
          />
        </p>
      </motion.div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-600/50 rounded-lg flex items-start gap-3">
          <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-1" />
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <motion.div 
          variants={itemVariants}
          className="lg:col-span-1 p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-6 h-fit shadow-md shadow-indigo-100/5"
        >
          <h2 className="font-bold text-accent-primary font-mono">Search Parameters</h2>

          {/* Target Capacitance */}
          <div className="space-y-3">
            <label className="text-xs font-mono font-bold text-text-secondary">
              Target Capacitance (pF/m)
            </label>
            <input
              type="number"
              min="10"
              max="2000"
              value={params.targetCapacitance}
              onChange={(e) => setParams(prev => ({ ...prev, targetCapacitance: parseFloat(e.target.value) }))}
              className="w-full px-3 py-2 bg-white/40 border border-slate-200/85 rounded-lg text-text-primary font-mono text-sm focus:border-accent-primary focus:bg-white focus:outline-none transition-all"
            />
          </div>

          {/* Library Size */}
          <div className="space-y-3">
            <label className="text-xs font-mono font-bold text-text-secondary">
              Virtual Library Size: {params.librarySize.toLocaleString()}
            </label>
            <input
              type="range"
              min="1000"
              max="25000"
              step="1000"
              value={params.librarySize}
              onChange={(e) => setParams(prev => ({ ...prev, librarySize: parseInt(e.target.value) }))}
              className="w-full"
            />
          </div>

          {/* Thickness Range */}
          <div className="space-y-3 pb-4 border-b border-border">
            <label className="text-xs font-mono font-bold text-text-secondary">
              Thickness Range (nm)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                min="100"
                max="5000"
                value={params.thicknessMin}
                onChange={(e) => setParams(prev => ({ ...prev, thicknessMin: parseInt(e.target.value) }))}
                className="flex-1 px-2 py-2 bg-white/40 border border-slate-200/85 rounded text-text-primary font-mono text-xs focus:border-accent-primary focus:bg-white focus:outline-none transition-all"
              />
              <span className="text-text-secondary px-2 py-2">→</span>
              <input
                type="number"
                min="100"
                max="5000"
                value={params.thicknessMax}
                onChange={(e) => setParams(prev => ({ ...prev, thicknessMax: parseInt(e.target.value) }))}
                className="flex-1 px-2 py-2 bg-white/40 border border-slate-200/85 rounded text-text-primary font-mono text-xs focus:border-accent-primary focus:bg-white focus:outline-none transition-all"
              />
            </div>
          </div>

          {/* Material Filters */}
          <div className="space-y-3">
            <label className="text-xs font-mono font-bold text-text-secondary">
              Materials ({params.materials.length}/{MATERIALS.length})
            </label>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {MATERIALS.map(material => (
                <button
                  key={material}
                  onClick={() => toggleMaterial(material)}
                  className={`w-full text-left px-3 py-2 rounded text-sm font-mono transition-all cursor-pointer ${
                    params.materials.includes(material)
                      ? 'bg-accent-primary text-white shadow-sm shadow-accent-primary/20'
                      : 'bg-bg-secondary border border-border text-text-secondary hover:border-accent-primary/50'
                  }`}
                >
                  {params.materials.includes(material) ? '✓' : '○'} {material}
                </button>
              ))}
            </div>
          </div>

          {/* Search Button */}
          <ClickSpark>
            <button
              onClick={handleSearch}
              disabled={discoveryLoading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-accent-primary hover:bg-accent-primary/90 disabled:opacity-50 text-white font-bold rounded-lg transition-all mt-6 cursor-pointer"
            >
              {discoveryLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Play size={18} />
                  Run Discovery
                </>
              )}
            </button>
          </ClickSpark>
        </motion.div>

        {/* Right Results Panel */}
        <motion.div 
          variants={itemVariants}
          className="lg:col-span-3 space-y-6"
        >
          {discoveryLoading && (
            <div className="p-8 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl text-center space-y-4 shadow-sm">
              <div className="flex justify-center">
                <div className="w-16 h-16 border-4 border-slate-200 rounded-full border-t-accent-primary animate-spin" />
              </div>
              <p className="text-text-secondary font-mono">
                Screening {params.librarySize.toLocaleString()} candidates...
              </p>
              <p className="text-xs text-text-secondary/50 font-mono">This typically takes 2-3 seconds</p>
            </div>
          )}

          {searchComplete && discoveryResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="p-4 bg-white/60 backdrop-blur-md border border-accent-primary/20 rounded-xl shadow-sm">
                <p className="text-sm font-mono text-text-secondary">
                  ✓ <strong>Search Complete!</strong> Found {discoveryResults.length} top candidates.
                  Best match error: <strong className="text-accent-primary">{discoveryResults[0].error.toFixed(2)} pF/m</strong>
                </p>
              </div>

              {/* Results Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {discoveryResults.map((result) => (
                  <ClickSpark key={result.rank}>
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: result.rank * 0.1 }}
                    >
                      <StarBorder 
                        isActive={result.rank === 1}
                        colorStart="#4F46E5"
                        colorEnd="#06B6D4"
                        className="h-full"
                      >
                        <div className="space-y-4">
                          {/* Rank Badge */}
                          <div className="flex items-start justify-between">
                            <div className="px-3 py-1 bg-accent-primary text-white rounded-full font-bold text-xs font-mono">
                              #{result.rank}
                            </div>
                            {result.rank === 1 && (
                              <Trophy size={18} className="text-accent-secondary" />
                            )}
                          </div>

                          {/* Predicted Value */}
                          <div>
                            <p className="text-xs text-text-secondary font-mono mb-1">Predicted Capacitance</p>
                            <p className="text-2xl font-bold text-accent-primary">
                              {result.predicted.toFixed(1)} pF/m
                            </p>
                          </div>

                          <div className="p-3 bg-white/50 backdrop-blur-sm rounded border border-white/80 shadow-sm">
                            <p className="text-xs text-text-secondary font-mono mb-1">Error from Target</p>
                            <p className="text-lg font-bold">
                              <span className="text-accent-primary">{result.error.toFixed(2)}</span>
                              <span className="text-text-secondary text-xs ml-1">pF/m</span>
                            </p>
                          </div>

                          {/* Properties */}
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-text-secondary">Material:</span>
                              <span className="font-mono font-bold text-accent-primary">{result.material}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-text-secondary">Thickness:</span>
                              <span className="font-mono font-bold text-accent-primary">{result.thickness.toFixed(0)} nm</span>
                            </div>
                          </div>

                          {/* SMILES */}
                          <div className="pt-3 border-t border-border/50">
                            <p className="text-xs text-text-secondary font-mono mb-2">SMILES</p>
                            <p className="text-xs font-mono text-accent-primary break-all bg-white/40 p-2 rounded border border-white/80">
                              {result.smiles}
                            </p>
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2 pt-3">
                            <button className="flex-1 px-2 py-2 text-xs font-mono bg-accent-primary hover:bg-accent-primary/90 text-white rounded transition-all cursor-pointer">
                              <Eye size={14} className="inline mr-1" /> View
                            </button>
                            <button className="flex-1 px-2 py-2 text-xs font-mono bg-bg-secondary border border-border text-text-primary hover:border-accent-primary rounded transition-all cursor-pointer">
                              <Download size={14} className="inline mr-1" /> Export
                            </button>
                          </div>
                        </div>
                      </StarBorder>
                    </motion.div>
                  </ClickSpark>
                ))}
              </div>
            </motion.div>
          )}

          {!discoveryLoading && !searchComplete && (
            <div className="p-8 bg-white/40 backdrop-blur-sm border-2 border-dashed border-slate-200 rounded-xl text-center shadow-sm">
              <p className="text-text-secondary font-mono">
                Configure search parameters and click <strong>"Run Discovery"</strong> to begin screening
              </p>
            </div>
          )}
        </motion.div>
      </div>

      <motion.div variants={itemVariants} className="p-4 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl shadow-sm">
        <p className="text-xs text-text-secondary font-mono">
          <strong>Virtual High-Throughput Screening (vHTS):</strong> Configure search parameters and run discovery. The system generates a virtual library of polymer candidates, predicts their properties using the selected ML model, and ranks them by proximity to your target capacitance.
        </p>
      </motion.div>
    </motion.div>
  );
};
