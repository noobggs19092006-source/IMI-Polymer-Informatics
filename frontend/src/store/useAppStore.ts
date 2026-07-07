import { create } from 'zustand';
import { apiService } from '../services/api';

interface DiscoveryResult {
  rank: number;
  smiles: string;
  predicted: number;
  error: number;
  material: string;
  thickness: number;
}

interface AppState {
  // Phase state
  currentPhase: number;
  setCurrentPhase: (phase: number) => void;

  // Generation state
  generatedSmiles: string | null;
  setGeneratedSmiles: (smiles: string | null) => void;
  generatorLoading: boolean;
  setGeneratorLoading: (loading: boolean) => void;

  // Model state
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  models: any[];
  setModels: (models: any[]) => void;
  loadingModels: boolean;
  setLoadingModels: (loading: boolean) => void;

  // Discovery state
  discoveryResults: DiscoveryResult[];
  setDiscoveryResults: (results: DiscoveryResult[]) => void;
  discoveryLoading: boolean;
  setDiscoveryLoading: (loading: boolean) => void;
  discoveryParams: any;
  setDiscoveryParams: (params: any) => void;

  // Metrics
  metrics: any;
  setMetrics: (metrics: any) => void;

  // Error handling
  error: string | null;
  setError: (error: string | null) => void;

  // Actions
  fetchModels: () => Promise<void>;
  generatePolymer: (config: any) => Promise<void>;
  runDiscovery: (params: any) => Promise<void>;
  exportResults: (format: 'csv' | 'json' | 'pdf') => Promise<void>;
  reset: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  currentPhase: 0,
  setCurrentPhase: (phase) => set({ currentPhase: phase }),

  generatedSmiles: null,
  setGeneratedSmiles: (smiles) => set({ generatedSmiles: smiles }),
  generatorLoading: false,
  setGeneratorLoading: (loading) => set({ generatorLoading: loading }),

  selectedModel: 'ensemble',
  setSelectedModel: (model) => set({ selectedModel: model }),
  models: [],
  setModels: (models) => set({ models }),
  loadingModels: false,
  setLoadingModels: (loading) => set({ loadingModels: loading }),

  discoveryResults: [],
  setDiscoveryResults: (results) => set({ discoveryResults: results }),
  discoveryLoading: false,
  setDiscoveryLoading: (loading) => set({ discoveryLoading: loading }),
  discoveryParams: null,
  setDiscoveryParams: (params) => set({ discoveryParams: params }),

  metrics: null,
  setMetrics: (metrics) => set({ metrics }),

  error: null,
  setError: (error) => set({ error }),

  // Async actions
  fetchModels: async () => {
    try {
      set({ loadingModels: true, error: null });
      const models = await apiService.getModels();
      set({ models });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch models' });
    } finally {
      set({ loadingModels: false });
    }
  },

  generatePolymer: async (config) => {
    try {
      set({ generatorLoading: true, error: null });
      const result = await apiService.generatePolymer(config);
      set({ generatedSmiles: result.smiles });
    } catch (err: any) {
      set({ error: err.message || 'Failed to generate polymer' });
    } finally {
      set({ generatorLoading: false });
    }
  },

  runDiscovery: async (params) => {
    try {
      set({ discoveryLoading: true, error: null, discoveryParams: params });
      const result = await apiService.searchPolymers({
        targetCapacitance: params.targetCapacitance,
        librarySize: params.librarySize,
        materials: params.materials,
        model: params.selectedModel || 'ensemble',
      });
      set({ discoveryResults: result.results });
    } catch (err: any) {
      set({ error: err.message || 'Failed to run discovery' });
    } finally {
      set({ discoveryLoading: false });
    }
  },

  exportResults: async (format) => {
    try {
      set({ error: null });
      const state = get();
      if (state.discoveryResults.length === 0) {
        set({ error: 'No results to export' });
        return;
      }
      const blob = await apiService.exportResults(format, state.discoveryResults);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `results.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      set({ error: err.message || 'Failed to export results' });
    }
  },

  reset: () => {
    set({
      currentPhase: 0,
      generatedSmiles: null,
      generatorLoading: false,
      selectedModel: 'ensemble',
      models: [],
      loadingModels: false,
      discoveryResults: [],
      discoveryLoading: false,
      discoveryParams: null,
      metrics: null,
      error: null,
    });
  },
}));
