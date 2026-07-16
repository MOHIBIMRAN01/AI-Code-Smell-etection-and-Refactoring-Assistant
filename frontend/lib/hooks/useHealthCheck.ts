/**
 * Custom hook for checking backend health
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api';

interface UseHealthCheckState {
  isHealthy: boolean;
  checked: boolean;
  error: Error | null;
}

export function useHealthCheck(interval: number = 30000) {
  const [state, setState] = useState<UseHealthCheckState>({
    isHealthy: false,
    checked: false,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    try {
      await apiClient.healthCheck();
      setState({ isHealthy: true, checked: true, error: null });
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Health check failed');
      setState({ isHealthy: false, checked: true, error });
    }
  }, []);

  useEffect(() => {
    // Check immediately
    checkHealth();

    // Set up interval
    const intervalId = setInterval(checkHealth, interval);

    return () => clearInterval(intervalId);
  }, [checkHealth, interval]);

  return state;
}
