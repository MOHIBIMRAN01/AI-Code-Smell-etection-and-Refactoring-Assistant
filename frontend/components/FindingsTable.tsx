/**
 * Findings table component
 */

'use client';

import { useState } from 'react';
import { Card, CardContent } from './Card';
import { Badge } from './Badge';
import { getBadgeVariant, getSeverityIcon, truncate, getSmellTypeIcon } from '@/lib/utils';
import type { Finding } from '@/types';

interface FindingsTableProps {
  findings: Finding[];
  onSelectFinding?: (finding: Finding, index: number) => void;
}

export function FindingsTable({ findings, onSelectFinding }: FindingsTableProps) {
  const [sortBy, setSortBy] = useState<'severity' | 'confidence' | 'file'>('severity');
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);

  const sortedFindings = [...findings].sort((a, b) => {
    switch (sortBy) {
      case 'severity': {
        const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        return (
          (severityOrder[a.severity as keyof typeof severityOrder] ?? 99) -
          (severityOrder[b.severity as keyof typeof severityOrder] ?? 99)
        );
      }
      case 'confidence':
        return b.confidence - a.confidence;
      case 'file':
        return a.file_path.localeCompare(b.file_path);
      default:
        return 0;
    }
  });

  const filteredFindings = filterSeverity
    ? sortedFindings.filter((f) => f.severity === filterSeverity)
    : sortedFindings;

  if (findings.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <p className="text-2xl mb-2">🎉</p>
          <p className="text-cream font-medium">No code smells detected!</p>
          <p className="text-cream-50 text-sm mt-1">
            Your code looks great according to the analysis.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterSeverity(null)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filterSeverity === null
                ? 'bg-blue-600 text-white dark:bg-coral dark:text-dark dark:font-bold'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-cream-10 dark:text-cream-90 dark:border dark:border-dark-border dark:hover:bg-cream-10/80'
            }`}
          >
            All ({findings.length})
          </button>
          {['critical', 'high', 'medium', 'low'].map((severity) => {
            const count = findings.filter((f) => f.severity === severity).length;
            if (count === 0) return null;
            return (
              <button
                key={severity}
                onClick={() => setFilterSeverity(severity)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  filterSeverity === severity
                    ? 'bg-blue-600 text-white dark:bg-coral dark:text-dark dark:font-bold'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-cream-10 dark:text-cream-90 dark:border dark:border-dark-border dark:hover:bg-cream-10/80'
                }`}
              >
                {severity.charAt(0).toUpperCase() + severity.slice(1)} ({count})
              </button>
            );
          })}
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="px-3 py-1.5 border border-gray-300 bg-white text-gray-900 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-card dark:text-cream dark:focus:ring-coral"
        >
          <option value="severity">Sort by Severity</option>
          <option value="confidence">Sort by Confidence</option>
          <option value="file">Sort by File</option>
        </select>
      </div>

      <div className="space-y-2">
        {filteredFindings.map((finding, index) => (
          <Card
            key={`${finding.file_path}-${finding.class_name}-${index}`}
            className="cursor-pointer hover:shadow-lg hover:border-blue-400 dark:hover:border-cream-30 transition-all"
            onClick={() => onSelectFinding?.(finding, index)}
          >
            <CardContent className="py-4">
              <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{getSmellTypeIcon(finding.smell_type)}</span>
                    <h3 className="font-semibold text-gray-900 dark:text-cream">{finding.smell_type}</h3>
                    <Badge variant={getBadgeVariant(finding.severity)} size="sm">
                      {getSeverityIcon(finding.severity)} {finding.severity.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="text-sm text-gray-600 dark:text-cream-50 mb-2">
                    <p>
                      <span className="font-medium text-gray-700 dark:text-cream-90">File:</span>{' '}
                      <code className="bg-slate-100 border border-slate-200 dark:bg-dark/45 dark:border-dark-border px-1.5 py-0.5 rounded font-mono text-xs text-gray-800 dark:text-cream-90">
                        {truncate(finding.file_path, 60)}
                      </code>
                    </p>
                    <p className="mt-1">
                      <span className="font-medium text-gray-700 dark:text-cream-90">Class:</span>{' '}
                      <code className="bg-slate-100 border border-slate-200 dark:bg-dark/45 dark:border-dark-border px-1.5 py-0.5 rounded font-mono text-xs text-gray-800 dark:text-cream-90">
                        {finding.class_name}
                      </code>
                    </p>
                  </div>

                  <p className="text-sm text-gray-700 dark:text-cream-50 line-clamp-2">
                    {truncate(finding.rationale, 100)}
                  </p>
                </div>

                <div className="flex flex-col items-end gap-2 sm:pt-0">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-coral">
                      {(finding.confidence * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-500 dark:text-cream-50">Confidence</p>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-cream-50 px-2 py-1 bg-slate-100 border border-slate-200 dark:bg-cream-10/10 dark:border-dark-border rounded">
                    {finding.llm_provider}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredFindings.length === 0 && (
        <Card>
          <CardContent className="text-center py-8 text-cream-50">
            No findings with severity: {filterSeverity}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
