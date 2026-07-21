/**
 * Repository analysis page
 */

'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { RepositoryForm } from '@/components/RepositoryForm';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { Card, CardContent, CardHeader } from '@/components/Card';
import { useAnalysis } from '@/lib/hooks';
import type { AnalysisResponse } from '@/types';
import { LuLightbulb } from 'react-icons/lu';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function AnalyzePage() {
  const router = useRouter();
  const { loading, error, analyze } = useAnalysis();
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisResponse[]>([]);

  useEffect(() => {
    apiClient.getAnalyses()
      .then((data) => {
        setRecentAnalyses(data.slice(0, 5));
      })
      .catch((err) => console.error('Failed to load history:', err));
  }, []);

  const handleSubmit = async (formData: {
    repository_url: string;
    branch?: string;
    analysis_label?: string;
  }) => {
    try {
      const result = await analyze(formData);

      // Refresh history list
      const updated = await apiClient.getAnalyses();
      setRecentAnalyses(updated.slice(0, 5));

      // Redirect to results page
      router.push(`/results/${result.analysis_id}`);
    } catch (err) {
      // Error is handled by the hook and passed to the component
      console.error('Analysis failed:', err);
    }
  };

  return (
    <>
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <Card variant="elevated">
              <CardHeader>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-cream">
                  Analyze Repository
                </h1>
                <p className="text-gray-600 dark:text-cream-50 mt-2">
                  Enter your GitHub repository URL to scan for code smells
                </p>
              </CardHeader>
              <CardContent>
                <RepositoryForm
                  onSubmit={handleSubmit}
                  isLoading={loading}
                  error={error}
                />
                
                <AnalysisProgress isLoading={loading} />
              </CardContent>
            </Card>

            {/* Info Section */}
            <Card className="mt-8">
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-cream">How it works</h2>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 border border-blue-200 dark:bg-cream-10 dark:border-dark-border flex items-center justify-center font-semibold text-blue-600 dark:text-coral">
                    1
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-cream">Paste Repository URL</h3>
                    <p className="text-gray-600 dark:text-cream-50 text-sm mt-1">
                      Enter the GitHub repository URL you want to analyze
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 border border-blue-200 dark:bg-cream-10 dark:border-dark-border flex items-center justify-center font-semibold text-blue-600 dark:text-coral">
                    2
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-cream">AI Analysis</h3>
                    <p className="text-gray-600 dark:text-cream-50 text-sm mt-1">
                      Our AI engine scans the repository and identifies code smells
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 border border-blue-200 dark:bg-cream-10 dark:border-dark-border flex items-center justify-center font-semibold text-blue-600 dark:text-coral">
                    3
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-cream">Get Results</h3>
                    <p className="text-gray-600 dark:text-cream-50 text-sm mt-1">
                      View detailed findings with recommendations and metrics
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Analyses */}
            {recentAnalyses.length > 0 && (
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-cream">Recent Analyses</h3>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {recentAnalyses.map((analysis) => (
                      <Link
                        key={analysis.analysis_id}
                        href={`/results/${analysis.analysis_id}`}
                        className="block p-3 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-slate-50 dark:border-dark-border dark:hover:border-cream-30 dark:hover:bg-dark-card/50 transition-colors"
                      >
                        <p className="font-medium text-blue-600 dark:text-coral text-sm truncate">
                          {analysis.repository_name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-cream-50 mt-1">
                          {analysis.findings.length} findings
                        </p>
                      </Link>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tips */}
            <Card className="bg-blue-50/50 border border-blue-200/60 dark:bg-cream-10/10 dark:border-dark-border">
              <CardContent className="pt-6">
                <h3 className="font-semibold text-gray-900 dark:text-cream flex items-center gap-2 mb-3">
                  <LuLightbulb className="text-blue-600 dark:text-coral text-lg" /> Tips
                </h3>
                <ul className="space-y-2 text-sm text-gray-700 dark:text-cream-90">
                  <li className="flex gap-2">
                    <span className="text-blue-600 dark:text-coral">✓</span> Works best with Java repositories
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-600 dark:text-coral">✓</span> Public repositories recommended
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-600 dark:text-coral">✓</span> Analysis takes 1-5 minutes
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-600 dark:text-coral">✓</span> Results are saved for 30 days
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
