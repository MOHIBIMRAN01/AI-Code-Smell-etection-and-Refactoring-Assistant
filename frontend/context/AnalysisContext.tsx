/**
 * Analysis Context for global state management
 */

'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { AnalysisResponse } from '@/types';

interface AnalysisContextType {
  currentAnalysis: AnalysisResponse | null;
  setCurrentAnalysis: (analysis: AnalysisResponse | null) => void;
  analysisHistory: AnalysisResponse[];
  addToHistory: (analysis: AnalysisResponse) => void;
  clearHistory: () => void;
  removeFromHistory: (id: string) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResponse[]>([]);

  const addToHistory = useCallback((analysis: AnalysisResponse) => {
    setAnalysisHistory((prev) => {
      const filtered = prev.filter((a) => a.analysis_id !== analysis.analysis_id);
      return [analysis, ...filtered].slice(0, 10); // Keep last 10
    });
  }, []);

  const clearHistory = useCallback(() => {
    setAnalysisHistory([]);
  }, []);

  const removeFromHistory = useCallback((id: string) => {
    setAnalysisHistory((prev) => prev.filter((a) => a.analysis_id !== id));
  }, []);

  return (
    <AnalysisContext.Provider
      value={{
        currentAnalysis,
        setCurrentAnalysis,
        analysisHistory,
        addToHistory,
        clearHistory,
        removeFromHistory,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysisContext() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysisContext must be used within AnalysisProvider');
  }
  return context;
}
