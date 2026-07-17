/**
 * Custom hook for checking backend health with auto-wake functionality
 * Wakes up sleeping backend on page load and monitors status in real-time
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '@/lib/api';

interface UseHealthCheckState {
  isHealthy: boolean;
  checked: boolean;
  error: Error | null;
  isWakingUp: boolean;
  wakupProgress: number; // 0-100 percentage of wake attempts
}

export function useHealthCheck(
  interval: number = 30000,
  autoWake: boolean = true,
  onStatusChange?: (isHealthy: boolean) => void
) {
  const [state, setState] = useState<UseHealthCheckState>({
    isHealthy: false,
    checked: false,
    error: null,
    isWakingUp: false,
    wakupProgress: 0,
  });

  const wakeAttemptRef = useRef(0);
  const maxWakeAttempts = 5;
  const wakeDelayRef = useRef(500); // Start with 500ms delay
  const prevHealthyRef = useRef(false);

  const checkHealth = useCallback(
    async (isWakeupCall: boolean = false) => {
      try {
        if (isWakeupCall) {
          setState((prev) => ({
            ...prev,
            isWakingUp: true,
            wakupProgress: ((wakeAttemptRef.current + 1) / maxWakeAttempts) * 100,
          }));
        }

        await apiClient.healthCheck();

        const newState: UseHealthCheckState = {
          isHealthy: true,
          checked: true,
          error: null,
          isWakingUp: false,
          wakupProgress: 100,
        };

        setState(newState);

        // Trigger callback if status changed
        if (!prevHealthyRef.current && newState.isHealthy && onStatusChange) {
          onStatusChange(true);
        }
        prevHealthyRef.current = true;

        // Reset wake attempt counter on success
        wakeAttemptRef.current = 0;
        wakeDelayRef.current = 500;

        return true;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Health check failed');

        const newState: UseHealthCheckState = {
          isHealthy: false,
          checked: true,
          error,
          isWakingUp: isWakeupCall,
          wakupProgress: isWakeupCall
            ? ((wakeAttemptRef.current + 1) / maxWakeAttempts) * 100
            : state.wakupProgress,
        };

        setState(newState);

        // Trigger callback if status changed
        if (prevHealthyRef.current && !newState.isHealthy && onStatusChange) {
          onStatusChange(false);
        }
        prevHealthyRef.current = false;

        return false;
      }
    },
    [onStatusChange, state.wakupProgress]
  );

  // Wake up backend on initial load (like a cron job trigger)
  useEffect(() => {
    if (!autoWake) return;

    let timeoutId: NodeJS.Timeout;
    let isMounted = true;

    const attemptWakeup = async () => {
      if (!isMounted) return;

      const success = await checkHealth(true);

      // If failed and we have more attempts, retry with exponential backoff
      if (!success && wakeAttemptRef.current < maxWakeAttempts) {
        wakeAttemptRef.current += 1;
        // Exponential backoff: 500ms, 750ms, 1125ms, 1687ms, 2531ms (max 3s)
        wakeDelayRef.current = Math.min(wakeDelayRef.current * 1.5, 3000);

        timeoutId = setTimeout(attemptWakeup, wakeDelayRef.current);
      }
    };

    // Start wake-up immediately when component mounts
    attemptWakeup();

    return () => {
      isMounted = false;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [autoWake, checkHealth]);

  // Regular health checks after initial wake attempt
  useEffect(() => {
    // Wait a bit before starting regular checks to let wake-up complete
    const initialCheckTimeout = setTimeout(() => {
      if (!state.isWakingUp && state.checked) {
        checkHealth(false);
      }
    }, 2000);

    // Set up regular interval checks
    const intervalId = setInterval(() => {
      checkHealth(false);
    }, interval);

    return () => {
      clearTimeout(initialCheckTimeout);
      clearInterval(intervalId);
    };
  }, [checkHealth, interval, state.isWakingUp, state.checked]);

  // Manual retry function
  const manualRetry = useCallback(async () => {
    wakeAttemptRef.current = 0;
    wakeDelayRef.current = 500;
    setState((prev) => ({
      ...prev,
      isWakingUp: true,
      wakupProgress: 0,
    }));
    return checkHealth(true);
  }, [checkHealth]);

  return {
    ...state,
    manualRetry,
  };
}
