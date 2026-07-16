/**
 * Custom hook for managing analysis state and API calls
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import type { AnalyzeRepositoryRequest, AnalysisResponse } from '@/types';

interface UseAnalysisState {
  data: AnalysisResponse | null;
  loading: boolean;
  error: Error | null;
}

export function useAnalysis() {
  const [state, setState] = useState<UseAnalysisState>({
    data: null,
    loading: false,
    error: null,
  });

  const analyze = useCallback(
    async (request: AnalyzeRepositoryRequest) => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await apiClient.analyzeRepository(request);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Analysis failed');
        setState({ data: null, loading: false, error });
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    analyze,
    reset,
  };
}
