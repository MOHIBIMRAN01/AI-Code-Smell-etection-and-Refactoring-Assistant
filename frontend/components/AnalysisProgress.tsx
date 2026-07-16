/**
 * Beautiful progress tracker overlay for code smell analysis
 */

'use client';

import { useState, useEffect } from 'react';
import { FiCloudLightning, FiCpu, FiCompass, FiAward, FiLoader } from 'react-icons/fi';

interface AnalysisProgressProps {
  isLoading: boolean;
}

export function AnalysisProgress({ isLoading }: AnalysisProgressProps) {
  const [secondsLeft, setSecondsLeft] = useState(65);
  const [progress, setProgress] = useState(0);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      // Reset values when not loading
      setSecondsLeft(65);
      setProgress(0);
      setActiveStep(0);
      return;
    }

    // Interval to countdown seconds and advance progress bar smoothly
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 3) return 3; // Keep it at 3 seconds minimum until backend finishes
        return prev - 1;
      });

      setProgress((prev) => {
        if (prev >= 98) return 98; // Hold at 98% until request resolves
        // Smoothly accelerate/decelerate progression rate
        const delta = prev < 30 ? 1.5 : prev < 75 ? 1.2 : 0.4;
        return Number((prev + delta).toFixed(1));
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isLoading]);

  // Determine current active stage based on progress/seconds
  useEffect(() => {
    if (progress < 25) {
      setActiveStep(0); // Cloning
    } else if (progress < 50) {
      setActiveStep(1); // Metrics Extraction
    } else if (progress < 65) {
      setActiveStep(2); // RAG Database
    } else if (progress < 90) {
      setActiveStep(3); // LLM Explanation
    } else {
      setActiveStep(4); // Finalizing
    }
  }, [progress]);

  if (!isLoading) return null;

  const steps = [
    { label: 'Cloning Repository', icon: FiCloudLightning, desc: 'Fetching git history & codebase...' },
    { label: 'Parsing Source Files', icon: FiCompass, desc: 'Calculating method metrics & smells...' },
    { label: 'Vector Store Query', icon: FiCpu, desc: 'Matching historical patterns via RAG...' },
    { label: 'AI Code Analysis', icon: FiAward, desc: 'Generating explaining recommendations...' },
    { label: 'Finalizing Report', icon: FiLoader, desc: 'Compiling findings and layout...' },
  ];

  return (
    <div className="mt-8 p-6 rounded-xl border border-gray-100 bg-white/50 dark:border-dark-border dark:bg-dark-card/45 backdrop-blur-md animate-fade-in">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-cream">
            Running Analysis Pipeline
          </h3>
          <p className="text-sm text-gray-600 dark:text-cream-50 mt-0.5">
            Our multi-stage pipeline is scanning your Java repository
          </p>
        </div>
        <div className="px-3.5 py-1.5 rounded-lg bg-blue-50 border border-blue-100 dark:bg-coral/10 dark:border-coral/20 flex flex-col items-end">
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-coral">
            Estimated remaining
          </span>
          <span className="text-xl font-extrabold text-blue-800 dark:text-coral font-mono leading-none mt-1">
            ~{secondsLeft}s
          </span>
        </div>
      </div>

      {/* Progress Bar Container */}
      <div className="relative w-full h-3.5 bg-gray-100 dark:bg-dark rounded-full overflow-hidden mb-8 border border-gray-200/40 dark:border-dark-border/40">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-coral dark:to-cream transition-all duration-1000 ease-out rounded-full"
          style={{ width: `${progress}%` }}
        />
        <div
          className="absolute inset-0 bg-shimmer bg-[length:200%_100%] animate-shimmer opacity-20 pointer-events-none"
        />
      </div>

      {/* Step Indicators */}
      <div className="grid grid-cols-1 gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = index < activeStep;
          const isActive = index === activeStep;

          return (
            <div
              key={step.label}
              className={`flex gap-4 p-3 rounded-lg border transition-all duration-300 ${
                isActive
                  ? 'bg-blue-50/70 border-blue-200 dark:bg-coral/10 dark:border-coral/30 shadow-sm'
                  : isCompleted
                  ? 'bg-gray-50/50 border-gray-150 dark:bg-dark-card/20 dark:border-dark-border/40 opacity-70'
                  : 'border-transparent opacity-40'
              }`}
            >
              <div
                className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center border transition-all ${
                  isActive
                    ? 'bg-blue-600 border-blue-400 text-white dark:bg-coral dark:border-coral/50'
                    : isCompleted
                    ? 'bg-green-100 border-green-200 text-green-600 dark:bg-green-950/40 dark:border-green-900/60 dark:text-green-400'
                    : 'bg-gray-100 border-gray-200 text-gray-500 dark:bg-dark dark:border-dark-border dark:text-cream-50/50'
                }`}
              >
                {isActive && index === 4 ? (
                  <Icon className="text-lg animate-spin" />
                ) : (
                  <Icon className="text-lg" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-sm text-gray-900 dark:text-cream truncate">
                    {step.label}
                  </h4>
                  {isCompleted && (
                    <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-bold uppercase dark:bg-green-950/60 dark:text-green-400">
                      Done
                    </span>
                  )}
                  {isActive && (
                    <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full font-bold uppercase animate-pulse dark:bg-coral/20 dark:text-coral">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-cream-50 mt-0.5 truncate">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
