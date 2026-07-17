/**
 * Custom hook for managing analysis state and API calls
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import type { AnalyzeRepositoryRequest, AnalysisResponse } from '@/types';

interface UseAnalysisState {
  data: AnalysisResponse | null;
  loading: boolean;
  error: Error | null;
  jobId: string | null;
  jobStatus: 'pending' | 'running' | 'completed' | 'failed' | null;
  progress: string;
}

export function useAnalysis() {
  const [state, setState] = useState<UseAnalysisState>({
    data: null,
    loading: false,
    error: null,
    jobId: null,
    jobStatus: null,
    progress: '',
  });

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const pollJobStatus = useCallback(
    async (jobId: string) => {
      try {
        const statusResponse = await apiClient.getAnalysisStatus(jobId);

        setState((prev) => ({
          ...prev,
          jobStatus: statusResponse.status,
          progress: `Status: ${statusResponse.status}...`,
        }));

        if (statusResponse.status === 'completed' && statusResponse.result) {
          setState((prev) => ({
            ...prev,
            data: statusResponse.result,
            loading: false,
            error: null,
            jobStatus: 'completed',
            progress: 'Analysis complete!',
          }));
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          return true; // Stop polling
        } else if (statusResponse.status === 'failed') {
          const error = new Error(statusResponse.error || 'Analysis failed');
          setState((prev) => ({
            ...prev,
            data: null,
            loading: false,
            error,
            jobStatus: 'failed',
            progress: `Failed: ${statusResponse.error}`,
          }));
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          return true; // Stop polling
        }

        return false; // Continue polling
      } catch (err) {
        console.error('Error polling job status:', err);
        return false; // Continue polling on network errors
      }
    },
    []
  );

  const analyze = useCallback(
    async (request: AnalyzeRepositoryRequest) => {
      setState({
        data: null,
        loading: true,
        error: null,
        jobId: null,
        jobStatus: 'pending',
        progress: 'Submitting analysis job...',
      });

      try {
        // Submit async job
        const submitResponse = await apiClient.submitAsyncAnalysis(request);
        const jobId = submitResponse.job_id;

        setState((prev) => ({
          ...prev,
          jobId,
          jobStatus: 'pending',
          progress: 'Job submitted. Waiting for analysis to start...',
        }));

        // Start polling for status
        let pollCount = 0;
        const maxPolls = 3600; // 30 seconds * 120 = 1 hour max polling

        pollIntervalRef.current = setInterval(async () => {
          pollCount++;
          if (pollCount > maxPolls) {
            clearInterval(pollIntervalRef.current!);
            pollIntervalRef.current = null;
            setState((prev) => ({
              ...prev,
              loading: false,
              error: new Error('Polling timeout: analysis took too long'),
              jobStatus: 'failed',
              progress: 'Polling timeout',
            }));
            return;
          }

          const shouldStop = await pollJobStatus(jobId);
          if (shouldStop) {
            clearInterval(pollIntervalRef.current!);
            pollIntervalRef.current = null;
          }
        }, 30000); // Poll every 30 seconds

        // Also do an immediate poll
        await pollJobStatus(jobId);

        return submitResponse;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Analysis submission failed');
        setState({ data: null, loading: false, error, jobId: null, jobStatus: null, progress: '' });
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        throw error;
      }
    },
    [pollJobStatus]
  );

  const reset = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setState({
      data: null,
      loading: false,
      error: null,
      jobId: null,
      jobStatus: null,
      progress: '',
    });
  }, []);

  return {
    ...state,
    analyze,
    reset,
  };
}
