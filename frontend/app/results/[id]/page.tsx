/**
 * Analysis results page
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/Button';
import { Card, CardContent } from '@/components/Card';
import { Alert } from '@/components/Alert';
import { LoadingSpinner } from '@/components/Loading';
import { FindingsTable } from '@/components/FindingsTable';
import { FindingDetail } from '@/components/FindingDetail';
import { SeverityChart } from '@/components/SeverityChart';
import { StatCard } from '@/components/StatCard';
import { apiClient } from '@/lib/api';
import { calculateStats, formatDate } from '@/lib/utils';
import type { AnalysisResponse, Finding } from '@/types';
import { 
  FiDownload, 
  FiTarget, 
  FiAlertTriangle, 
  FiAlertCircle, 
  FiInfo, 
  FiCheckCircle, 
  FiBarChart2 
} from 'react-icons/fi';
import { LuLightbulb } from 'react-icons/lu';

interface ResultsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ResultsPage({ params: _params }: ResultsPageProps) {
  const routerParams = useParams();
  const id = routerParams.id as string;
  
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  useEffect(() => {
    if (id) {
      setLoading(true);
      setError(null);
      apiClient.getReportData(id)
        .then((data) => {
          setAnalysis(data);
        })
        .catch((err) => {
          setError(err instanceof Error ? err : new Error('Failed to load analysis results'));
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [id]);

  const handleSelectFinding = (finding: Finding, index: number) => {
    setSelectedFinding(finding);
    setSelectedIndex(index);
  };

  const handleNextFinding = () => {
    if (analysis && selectedIndex < analysis.findings.length - 1) {
      const nextFinding = analysis.findings[selectedIndex + 1];
      setSelectedFinding(nextFinding);
      setSelectedIndex(selectedIndex + 1);
    }
  };

  const handlePreviousFinding = () => {
    if (analysis && selectedIndex > 0) {
      const prevFinding = analysis.findings[selectedIndex - 1];
      setSelectedFinding(prevFinding);
      setSelectedIndex(selectedIndex - 1);
    }
  };

  const handleDownloadJson = async () => {
    if (!analysis?.analysis_id) return;
    try {
      await apiClient.downloadJsonReport(analysis.analysis_id);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Download failed'));
    }
  };

  const handleDownloadPdf = async () => {
    if (!analysis?.analysis_id) return;
    try {
      await apiClient.downloadPdfReport(analysis.analysis_id);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Download failed'));
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex justify-center">
            <LoadingSpinner size="lg" message="Loading analysis results..." />
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (!analysis) {
    return (
      <>
        <Header />
        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Card className="max-w-md mx-auto">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FiBarChart2 className="text-5xl text-gray-400 dark:text-cream-30 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-cream">Analysis Not Found</h2>
              <p className="text-gray-600 dark:text-cream-50 mt-2 text-center">
                The analysis results could not be loaded. It may have expired.
              </p>
              <Link href="/analyze" className="mt-6">
                <Button>Start New Analysis</Button>
              </Link>
            </CardContent>
          </Card>
        </main>
        <Footer />
      </>
    );
  }

  const stats = calculateStats(analysis.findings);

  return (
    <>
      <Header />

      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          {error && (
            <Alert variant="error" title="Error" onClose={() => setError(null)}>
              {error.message}
            </Alert>
          )}

          {/* Header Section */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-cream">
                  Analysis Results
                </h1>
                <p className="text-gray-600 dark:text-cream-50 mt-2">
                  Repository: <span className="font-semibold">{analysis.repository_name}</span>
                </p>
                <p className="text-sm text-gray-500 dark:text-cream-50 mt-1">
                  Analyzed on {formatDate(analysis.created_at)}
                </p>
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button variant="secondary" onClick={handleDownloadJson} className="gap-2">
                  <FiDownload className="text-sm" /> JSON Report
                </Button>
                <Button variant="secondary" onClick={handleDownloadPdf} className="gap-2">
                  <FiDownload className="text-sm" /> PDF Report
                </Button>
                <Link href="/analyze">
                  <Button>New Analysis</Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Summary Section */}
          {analysis.summary && (
            <Card className="mb-8 bg-blue-50 border border-blue-200 dark:bg-cream-10/5 dark:border-dark-border">
              <CardContent className="pt-6">
                <h2 className="font-semibold text-blue-900 dark:text-coral mb-2">Summary</h2>
                <p className="text-blue-800 dark:text-cream-90">{analysis.summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Stats Section */}
          <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
            <StatCard
              title="Total Findings"
              value={stats.total}
              icon={<FiTarget />}
              variant="default"
            />
            <StatCard
              title="Critical"
              value={stats.critical}
              icon={<FiAlertTriangle className="text-red-650 dark:text-coral" />}
              variant="critical"
            />
            <StatCard
              title="High"
              value={stats.high}
              icon={<FiAlertCircle className="text-orange-500 dark:text-yellow-400" />}
              variant="high"
            />
            <StatCard
              title="Medium"
              value={stats.medium}
              icon={<FiInfo className="text-yellow-600 dark:text-blue-400" />}
              variant="medium"
            />
            <StatCard
              title="Low"
              value={stats.low}
              icon={<FiCheckCircle className="text-green-600 dark:text-green-400" />}
              variant="low"
            />
          </div>

          {/* Repository Info Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-gray-500 dark:text-cream-50 font-semibold">JAVA FILES</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-cream mt-2">
                  {analysis.total_java_files}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-gray-500 dark:text-cream-50 font-semibold">CLASSES ANALYZED</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-cream mt-2">
                  {analysis.analyzed_classes}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-gray-500 dark:text-cream-50 font-semibold">AVG CONFIDENCE</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-cream mt-2">
                  {stats.avgConfidence}%
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Findings List */}
            <div className="lg:col-span-2">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-cream mb-6">Code Smells</h2>
              <FindingsTable
                findings={analysis.findings}
                onSelectFinding={handleSelectFinding}
              />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Severity Chart */}
              <SeverityChart findings={analysis.findings} />

              {/* Selected Finding Detail */}
              {selectedFinding && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-cream mb-4">
                    Finding Details
                  </h3>
                  <FindingDetail
                    finding={selectedFinding}
                    index={selectedIndex}
                    onNext={
                      selectedIndex < analysis.findings.length - 1
                        ? handleNextFinding
                        : undefined
                    }
                    onPrevious={selectedIndex > 0 ? handlePreviousFinding : undefined}
                    totalFindings={analysis.findings.length}
                    onClose={() => setSelectedFinding(null)}
                  />
                </div>
              )}

              {/* Info Card */}
              {!selectedFinding && (
                <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 dark:bg-cream-10/5 dark:border-dark-border">
                  <CardContent className="pt-6">
                    <p className="text-sm text-gray-600 dark:text-cream font-semibold flex items-center gap-2 mb-2">
                      <LuLightbulb className="text-purple-600 dark:text-coral text-lg" /> Tip
                    </p>
                    <p className="text-sm text-gray-700 dark:text-cream-50">
                      Click on any code smell in the list to view detailed information,
                      metrics, and refactoring suggestions.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
