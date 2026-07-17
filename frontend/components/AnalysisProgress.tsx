/**
 * Analysis Progress Component
 * Shows real-time feedback during long-running analysis
 */

'use client';

import { useState, useEffect } from 'react';

interface AnalysisProgressProps {
  isLoading: boolean;
  startTime?: number;
}

export function AnalysisProgress({ isLoading, startTime }: AnalysisProgressProps) {
  const [elapsed, setElapsed] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState('2-5 minutes');

  useEffect(() => {
    if (!isLoading) {
      setElapsed(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);

      // Update estimated time based on elapsed time
      if (elapsed > 120) {
        setEstimatedTime('Large repo - may take 5-10 minutes');
      } else if (elapsed > 60) {
        setEstimatedTime('3-5 minutes for large repo');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isLoading, elapsed]);

  if (!isLoading) return null;

  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  const progress = Math.min((elapsed / 300) * 100, 90); // Assume max 5 minutes normally

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-2xl p-8 max-w-md">
        <div className="text-center">
          {/* Loading Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 border-4 border-gray-200 dark:border-slate-700 border-t-blue-600 rounded-full animate-spin" />
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Analyzing Repository
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            This may take a few minutes for large repositories
          </p>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="bg-gray-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Time Display */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-950/20 rounded-lg p-3">
              <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold">
                ELAPSED TIME
              </p>
              <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
                {minutes}:{seconds.toString().padStart(2, '0')}
              </p>
            </div>
            <div className="bg-amber-50 dark:bg-amber-950/20 rounded-lg p-3">
              <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold">
                ESTIMATED
              </p>
              <p className="text-sm font-bold text-gray-900 dark:text-white mt-1">
                {estimatedTime}
              </p>
            </div>
          </div>

          {/* Status Messages */}
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Cloning repository</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Parsing Java files</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={elapsed > 30 ? 'text-green-500' : 'text-gray-400'}>
                {elapsed > 30 ? '✓' : '○'}
              </span>
              <span>Extracting metrics</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={elapsed > 60 ? 'text-green-500' : 'text-gray-400'}>
                {elapsed > 60 ? '✓' : '○'}
              </span>
              <span>Analyzing with AI</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={elapsed > 120 ? 'text-green-500' : 'text-gray-400'}>
                {elapsed > 120 ? '✓' : '○'}
              </span>
              <span>Generating report</span>
            </div>
          </div>

          {/* Tip */}
          <div className="mt-6 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              💡 Tip: Don't close this tab. Large repositories may take up to 10 minutes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
