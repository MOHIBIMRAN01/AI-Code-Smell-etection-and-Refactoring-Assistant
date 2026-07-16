/**
 * Application Header component
 */

'use client';

import Link from 'next/link';
import { useHealthCheck } from '@/lib/hooks';
import { FiSearch, FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from '@/context';

export function Header() {
  const { isHealthy, checked } = useHealthCheck(30000);
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 bg-white/95 text-gray-900 border-b border-gray-100 dark:bg-dark-card/90 dark:text-cream dark:border-dark-border backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 group">
              <FiSearch className="text-2xl text-blue-600 dark:text-coral transition-transform group-hover:scale-110" />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-coral dark:to-cream bg-clip-text text-transparent">
                CodeSmell AI
              </span>
            </Link>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            <Link href="/" className="text-gray-600 hover:text-blue-600 dark:text-cream-50 dark:hover:text-coral transition-colors font-medium">
              Home
            </Link>
            <Link href="/analyze" className="text-gray-600 hover:text-blue-600 dark:text-cream-50 dark:hover:text-coral transition-colors font-medium">
              Analyze
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            {checked && (
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${
                isHealthy
                  ? 'bg-green-100 text-green-800 border-green-200 dark:bg-green-950/40 dark:text-green-400 dark:border-green-900/60'
                  : 'bg-red-100 text-red-800 border-red-200 dark:bg-coral/10 dark:text-coral dark:border-coral/30'
              }`}>
                <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500 dark:bg-green-400' : 'bg-red-500 dark:bg-coral'}`} />
                {isHealthy ? 'Connected' : 'Offline'}
              </div>
            )}

            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:border-dark-border dark:text-cream-50 dark:hover:bg-cream-10/40 dark:hover:text-cream transition-colors"
              aria-label="Toggle Theme"
            >
              {theme === 'light' ? <FiMoon className="text-lg" /> : <FiSun className="text-lg" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
