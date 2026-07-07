import React, { useState } from 'react';
import { Download, FileJson, FileText, Share2, Trophy, Star } from 'lucide-react';
import { TextType, ClickSpark, CountUpMetric } from '../components/animations';
import { motion } from 'framer-motion';

interface ResultEntry {
  rank: number;
  polymer: string;
  target: number;
  predicted: number;
  error: number;
  errorPercent: number;
  material: string;
  thickness: number;
  smiles: string;
}

const MOCK_RESULTS: ResultEntry[] = [
  {
    rank: 1,
    polymer: 'PVDF-C3-C(F)(F)F',
    target: 200,
    predicted: 199.87,
    error: 0.13,
    errorPercent: 0.065,
    material: 'PVDF',
    thickness: 750,
    smiles: 'CCPC(F)(F)FCC(F)(F)',
  },
  {
    rank: 2,
    polymer: 'PVDF-CC-C(F)(F)F',
    target: 200,
    predicted: 200.34,
    error: 0.34,
    errorPercent: 0.170,
    material: 'PVDF',
    thickness: 725,
    smiles: 'CCPC(F)(F)FCC(F)(F)',
  },
  {
    rank: 3,
    polymer: 'PE-CC-Cl',
    target: 200,
    predicted: 198.92,
    error: 1.08,
    errorPercent: 0.540,
    material: 'PE',
    thickness: 1200,
    smiles: 'CCCCCCCL',
  },
  {
    rank: 4,
    polymer: 'PTFE-C-CC',
    target: 200,
    predicted: 201.45,
    error: 1.45,
    errorPercent: 0.725,
    material: 'PTFE',
    thickness: 680,
    smiles: 'C(F)(F)C(F)(F)CC',
  },
  {
    rank: 5,
    polymer: 'PVC-CCC-Cl',
    target: 200,
    predicted: 202.12,
    error: 2.12,
    errorPercent: 1.060,
    material: 'PVC',
    thickness: 1100,
    smiles: 'CCCCCL',
  },
  {
    rank: 6,
    polymer: 'PC-C-CC',
    target: 200,
    predicted: 197.34,
    error: 2.66,
    errorPercent: 1.330,
    material: 'PC',
    thickness: 900,
    smiles: 'CCCC',
  },
];

interface Phase5ResultsProps {
  onExport?: (format: string) => void;
}

export const Phase5Results: React.FC<Phase5ResultsProps> = ({ onExport }) => {
  const [sortBy, setSortBy] = useState<'error' | 'rank'>('error');
  const [filterMaterial, setFilterMaterial] = useState<string | null>(null);

  const materials = [...new Set(MOCK_RESULTS.map(r => r.material))];
  const sortedResults = [...MOCK_RESULTS]
    .sort((a, b) => sortBy === 'error' ? a.error - b.error : a.rank - b.rank)
    .filter(r => !filterMaterial || r.material === filterMaterial);

  const handleExport = (format: string) => {
    if (onExport) {
      onExport(format);
    }
    alert(`Exporting as ${format}...`);
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
          <TextType text="Phase 5: Discovery Results" speed={40} />
        </h1>
        <p className="text-text-secondary">
          <TextType 
            text="Review discovered polymers, compare predictions, and export results for further analysis."
            speed={20}
            delay={500}
          />
        </p>
      </motion.div>

      {/* Summary Statistics */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <CountUpMetric 
          label="Total Screened"
          value={25000}
          duration={2.5}
        />
        <CountUpMetric 
          label="Qualified Matches"
          value={127}
          duration={2.8}
        />
        <CountUpMetric 
          label="Best Match Accuracy"
          value={99.935}
          decimals={2}
          suffix="%"
          duration={3}
        />
        <CountUpMetric 
          label="Avg Prediction Error"
          value={1.3}
          decimals={1}
          suffix=" pF/m"
          duration={2.3}
        />
      </motion.div>

      {/* Results Table with Filters & Controls */}
      <motion.div variants={itemVariants} className="space-y-4">
        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex gap-4 flex-wrap">
            <div>
              <label className="text-xs font-mono text-text-secondary block mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'error' | 'rank')}
                className="px-3 py-2 bg-bg-primary border border-border rounded text-text-primary font-mono text-sm focus:border-accent-primary focus:outline-none"
              >
                <option value="error">Error (Lowest First)</option>
                <option value="rank">Rank</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-mono text-text-secondary block mb-2">Material Filter</label>
              <select
                value={filterMaterial || ''}
                onChange={(e) => setFilterMaterial(e.target.value || null)}
                className="px-3 py-2 bg-bg-primary border border-border rounded text-text-primary font-mono text-sm focus:border-accent-primary focus:outline-none"
              >
                <option value="">All Materials</option>
                {materials.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="flex gap-2">
            <ClickSpark>
              <button
                onClick={() => handleExport('csv')}
                className="flex items-center gap-2 px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded text-sm transition-all cursor-pointer"
              >
                <Download size={16} />
                CSV
              </button>
            </ClickSpark>
            <ClickSpark>
              <button
                onClick={() => handleExport('json')}
                className="flex items-center gap-2 px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded text-sm transition-all cursor-pointer"
              >
                <FileJson size={16} />
                JSON
              </button>
            </ClickSpark>
            <ClickSpark>
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center gap-2 px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded text-sm transition-all cursor-pointer"
              >
                <FileText size={16} />
                PDF
              </button>
            </ClickSpark>
          </div>
        </div>

        <div className="overflow-x-auto border border-white/80 rounded-xl bg-white/40 backdrop-blur-sm shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200/80 bg-white/60">
                <th className="text-left px-4 py-3 font-mono font-bold text-xs text-text-secondary">#</th>
                <th className="text-left px-4 py-3 font-mono font-bold text-xs text-text-secondary">Polymer</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Target</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Predicted</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Error</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Error %</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Material</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Thickness</th>
                <th className="text-center px-4 py-3 font-mono font-bold text-xs text-text-secondary">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedResults.map((result, idx) => (
                <motion.tr
                  key={result.rank}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`border-b border-border/50 hover:bg-bg-primary/30 transition-all ${
                    result.rank === 1 ? 'bg-accent-primary/5' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    <span className="font-bold text-accent-primary">#{result.rank}</span>
                    {result.rank === 1 && <Trophy size={14} className="inline ml-2 text-accent-secondary" />}
                  </td>
                  <td className="px-4 py-3 font-mono text-sm text-text-primary">{result.polymer}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm">{result.target.toFixed(1)}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-accent-primary font-bold">
                    {result.predicted.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-accent-primary">
                    {result.error.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-accent-primary">
                    {result.errorPercent.toFixed(3)}%
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-text-secondary">
                    {result.material}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-text-secondary">
                    {result.thickness} nm
                  </td>
                  <td className="px-4 py-3 text-center">
                    <ClickSpark>
                      <button className="px-3 py-1 bg-accent-primary/20 hover:bg-accent-primary/40 text-accent-primary font-mono text-xs rounded transition-all cursor-pointer">
                        View
                      </button>
                    </ClickSpark>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Top Candidate Card */}
      <motion.div 
        variants={itemVariants}
        className="p-6 bg-gradient-to-br from-white/70 to-indigo-50/50 backdrop-blur-xl border border-accent-primary/40 rounded-xl space-y-4 shadow-lg shadow-indigo-100/10"
      >
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold font-mono flex items-center gap-2">
            <Trophy className="text-accent-secondary" /> Top Candidate
          </h3>
          <Star size={24} className="text-accent-secondary fill-accent-secondary animate-pulse" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-xs text-text-secondary font-mono mb-2">Polymer Name</p>
            <p className="text-lg font-bold text-text-primary">{MOCK_RESULTS[0].polymer}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary font-mono mb-2">Predicted Capacitance</p>
            <p className="text-lg font-bold text-accent-primary">{MOCK_RESULTS[0].predicted.toFixed(2)} pF/m</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary font-mono mb-2">Error from Target</p>
            <p className="text-lg font-bold text-accent-primary">{MOCK_RESULTS[0].error.toFixed(3)} pF/m ({MOCK_RESULTS[0].errorPercent.toFixed(3)}%)</p>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-200/60">
          <p className="text-xs text-text-secondary font-mono mb-2">SMILES String</p>
          <div className="p-3 bg-white/50 backdrop-blur-sm rounded border border-white/80 shadow-sm">
            <p className="font-mono text-sm text-accent-primary break-all">{MOCK_RESULTS[0].smiles}</p>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <ClickSpark>
            <button className="flex-1 px-4 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white font-bold rounded transition-all cursor-pointer">
              <Download size={16} className="inline mr-2" />
              Export Candidate
            </button>
          </ClickSpark>
          <ClickSpark>
            <button className="flex-1 px-4 py-3 bg-bg-secondary border border-border text-text-primary hover:border-accent-primary font-bold rounded transition-all cursor-pointer">
              <Share2 size={16} className="inline mr-2" />
              Share
            </button>
          </ClickSpark>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5">
          <h3 className="font-bold text-accent-primary font-mono">Discovery Statistics</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Total Candidates Screened</span>
              <span className="text-accent-primary font-bold">25,000</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Qualified Matches (&lt; 5% error)</span>
              <span className="text-accent-primary font-bold">127</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Success Rate</span>
              <span className="text-accent-primary font-bold">0.51%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Avg Prediction Error</span>
              <span className="text-accent-primary font-bold">1.30 pF/m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Best Error</span>
              <span className="text-accent-primary font-bold">0.065 pF/m</span>
            </div>
          </div>
        </div>

        <div className="p-6 bg-white/60 backdrop-blur-md border border-white/80 rounded-xl space-y-4 shadow-md shadow-indigo-100/5">
          <h3 className="font-bold text-accent-primary font-mono">Material Distribution</h3>
          <div className="space-y-3">
            {materials.map(material => {
              const count = MOCK_RESULTS.filter(r => r.material === material).length;
              const percentage = (count / MOCK_RESULTS.length) * 100;
              return (
                <div key={material}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-secondary">{material}</span>
                    <span className="text-accent-primary font-bold">{count} ({percentage.toFixed(0)}%)</span>
                  </div>
                  <div className="w-full h-2 bg-white/50 rounded overflow-hidden border border-white/80">
                    <div
                      className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="p-4 bg-white/50 backdrop-blur-md border border-white/80 rounded-xl shadow-sm">
        <p className="text-xs text-text-secondary font-mono">
          <strong>Results Export:</strong> Download your discovery results in CSV, JSON, or PDF formats. CSV is ideal for spreadsheet analysis, JSON for data integration, and PDF for reports and presentations. All results include SMILES strings for further validation with ANSYS or experimental synthesis.
        </p>
      </motion.div>
    </motion.div>
  );
};
