/**
 * Application Header component with real-time backend status
 */

'use client';

import Link from 'next/link';
import { useHealthCheck } from '@/lib/hooks';
import { FiSearch } from 'react-icons/fi';
import { useState, useEffect } from 'react';

export function Header() {
  const [statusDisplay, setStatusDisplay] = useState<'offline' | 'connecting' | 'online'>('offline');
  
  const { isHealthy, checked, isWakingUp, manualRetry } = useHealthCheck(
    30000,
    true,
    (healthy) => {
      // Real-time callback when backend status changes
      setStatusDisplay(healthy ? 'online' : 'offline');
    }
  );

  useEffect(() => {
    // Update display based on current state
    if (isWakingUp) {
      setStatusDisplay('connecting');
    } else if (isHealthy) {
      setStatusDisplay('online');
    } else if (checked) {
      setStatusDisplay('offline');
    }
  }, [isHealthy, isWakingUp, checked]);

  const getStatusBadge = () => {
    switch (statusDisplay) {
      case 'online':
        return {
          bg: 'bg-green-100 dark:bg-green-950/40',
          border: 'border-green-200 dark:border-green-900/60',
          text: 'text-green-800 dark:text-green-400',
          dot: 'bg-green-500 dark:bg-green-400',
          label: 'Connected',
          icon: '●',
        };
      case 'connecting':
        return {
          bg: 'bg-amber-100 dark:bg-amber-950/40',
          border: 'border-amber-200 dark:border-amber-900/60',
          text: 'text-amber-800 dark:text-amber-400',
          dot: 'bg-amber-500 dark:bg-amber-400 animate-pulse',
          label: 'Connecting...',
          icon: '⟳',
        };
      case 'offline':
      default:
        return {
          bg: 'bg-red-100 dark:bg-red-950/40',
          border: 'border-red-200 dark:border-red-900/60',
          text: 'text-red-800 dark:text-red-400',
          dot: 'bg-red-500 dark:bg-red-400',
          label: 'Offline',
          icon: '●',
        };
    }
  };

  const status = getStatusBadge();

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 border-b border-gray-100 dark:border-gray-800 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 group">
              <FiSearch className="text-2xl text-blue-600 dark:text-blue-400 transition-transform group-hover:scale-110" />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                CodeSmell AI
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link href="/" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors font-medium">
              Home
            </Link>
            <Link href="/analyze" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors font-medium">
              Analyze
            </Link>
          </nav>

          {/* Status Badge */}
          <div className="flex items-center gap-3">
            {checked && (
              <button
                onClick={statusDisplay === 'offline' ? manualRetry : undefined}
                disabled={statusDisplay === 'connecting'}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                  status.bg
                } ${status.border} ${status.text} ${
                  statusDisplay === 'offline' && !isWakingUp
                    ? 'cursor-pointer hover:opacity-80'
                    : 'cursor-default'
                }`}
                title={statusDisplay === 'offline' ? 'Click to retry' : undefined}
              >
                <span className={`w-2 h-2 rounded-full ${status.dot}`} />
                {statusDisplay === 'connecting' && (
                  <span className="animate-spin inline-block">⟳</span>
                )}
                {status.label}
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
