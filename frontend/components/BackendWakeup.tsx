/**
 * Backend Wake-up Component
 * Automatically wakes up sleeping backend when user visits the page
 * Shows real-time status changes without page reload
 */

'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface WakeupState {
  status: 'idle' | 'waking' | 'connected' | 'error';
  message: string;
  progress: number; // 0-100
  attempt: number;
}

export function BackendWakeup() {
  const [state, setState] = useState<WakeupState>({
    status: 'idle',
    message: 'Checking backend...',
    progress: 0,
    attempt: 0,
  });

  useEffect(() => {
    let isActive = true;
    let retryTimeout: NodeJS.Timeout;
    let maxAttempts = 5;
    let currentAttempt = 0;
    const delays = [500, 750, 1125, 1687, 2531]; // Exponential backoff

    const wakeupBackend = async () => {
      if (!isActive) return;

      try {
        setState((prev) => ({
          ...prev,
          status: 'waking',
          message: `Waking up backend... (Attempt ${currentAttempt + 1}/${maxAttempts})`,
          attempt: currentAttempt + 1,
          progress: ((currentAttempt + 1) / maxAttempts) * 100,
        }));

        // Send health check request
        const response = await Promise.race([
          apiClient.healthCheck(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Timeout')), 5000)
          ),
        ]);

        if (isActive) {
          setState({
            status: 'connected',
            message: 'Backend is now online!',
            progress: 100,
            attempt: currentAttempt + 1,
          });
        }
      } catch (error) {
        if (!isActive) return;

        currentAttempt++;

        if (currentAttempt < maxAttempts) {
          const delay = delays[currentAttempt - 1] || 3000;

          setState((prev) => ({
            ...prev,
            status: 'waking',
            message: `Backend sleeping... Retrying in ${delay}ms`,
            progress: (currentAttempt / maxAttempts) * 100,
            attempt: currentAttempt,
          }));

          retryTimeout = setTimeout(wakeupBackend, delay);
        } else {
          setState({
            status: 'error',
            message: 'Could not connect to backend. Trying again later...',
            progress: 100,
            attempt: currentAttempt,
          });
        }
      }
    };

    // Start wakeup on mount
    wakeupBackend();

    return () => {
      isActive = false;
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, []);

  // Only show if not connected yet
  if (state.status === 'connected') {
    return null;
  }

  return (
    <div className="fixed top-16 right-4 z-40 max-w-sm">
      <div
        className={`rounded-lg shadow-lg p-4 border transition-all duration-300 ${
          state.status === 'error'
            ? 'bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-900/40'
            : 'bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-900/40'
        }`}
      >
        <div className="flex items-start gap-3">
          <div
            className={`flex-shrink-0 ${
              state.status === 'error' ? 'text-red-500' : 'text-amber-500'
            }`}
          >
            {state.status === 'waking' ? (
              <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              <span className="text-xl">⚠️</span>
            )}
          </div>
          <div className="flex-1">
            <p
              className={`text-sm font-semibold ${
                state.status === 'error'
                  ? 'text-red-800 dark:text-red-300'
                  : 'text-amber-800 dark:text-amber-300'
              }`}
            >
              {state.message}
            </p>
            {state.status === 'waking' && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-amber-500 dark:bg-amber-400 h-full transition-all duration-500"
                    style={{ width: `${state.progress}%` }}
                  />
                </div>
                <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                  {Math.round(state.progress)}% - Attempt {state.attempt}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
