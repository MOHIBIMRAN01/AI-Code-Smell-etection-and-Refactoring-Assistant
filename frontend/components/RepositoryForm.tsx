/**
 * Repository analysis form component
 */

'use client';

import React, { useState } from 'react';
import { Button } from './Button';
import { Alert } from './Alert';
import { isValidGitHubUrl } from '@/lib/utils';

interface RepositoryFormProps {
  onSubmit: (data: { repository_url: string; branch?: string; analysis_label?: string }) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}

export function RepositoryForm({ onSubmit, isLoading, error }: RepositoryFormProps) {
  const [repoUrl, setRepoUrl] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    // Validate URL
    if (!repoUrl.trim()) {
      setFormError('Repository URL is required');
      return;
    }

    if (!isValidGitHubUrl(repoUrl)) {
      setFormError('Please enter a valid GitHub repository URL');
      return;
    }

    try {
      await onSubmit({
        repository_url: repoUrl.trim(),
      });

      // Clear form on success
      setRepoUrl('');
    } catch (err) {
      // Error is handled by parent component
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {(error || formError) && (
        <Alert variant="error" title="Error">
          {error?.message || formError}
        </Alert>
      )}

      <div>
        <label htmlFor="repo-url" className="block text-sm font-semibold text-gray-700 dark:text-cream-90 mb-2">
          Repository URL <span className="text-red-500 dark:text-coral">*</span>
        </label>
        <input
          id="repo-url"
          type="url"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          disabled={isLoading}
          placeholder="https://github.com/username/repository"
          className="w-full px-4 py-3 border border-gray-300 bg-white text-gray-900 placeholder-gray-450 dark:border-dark-border dark:bg-dark/40 dark:text-cream dark:placeholder-cream-50/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-coral disabled:bg-gray-100 dark:disabled:bg-dark-card/30 disabled:cursor-not-allowed transition-all"
          required
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-cream-50">
          Enter the GitHub repository URL you want to analyze
        </p>
      </div>

      <Button
        type="submit"
        size="lg"
        isLoading={isLoading}
        disabled={isLoading}
        className="w-full"
      >
        {isLoading ? 'Analyzing Repository...' : 'Start Analysis'}
      </Button>

      <p className="text-xs text-gray-500 dark:text-cream-50 text-center">
        Analysis may take a few minutes depending on repository size
      </p>
    </form>
  );
}
