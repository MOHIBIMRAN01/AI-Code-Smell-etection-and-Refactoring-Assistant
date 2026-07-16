/**
 * Detailed finding view component
 */

'use client';

import { Card, CardContent, CardHeader, CardFooter } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { getBadgeVariant, getSmellTypeIcon } from '@/lib/utils';
import type { Finding } from '@/types';

interface FindingDetailProps {
  finding: Finding;
  index: number;
  onClose?: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  totalFindings?: number;
}

export function FindingDetail({
  finding,
  index,
  onClose,
  onNext,
  onPrevious,
  totalFindings,
}: FindingDetailProps) {
  return (
    <Card className="bg-white border border-gray-200 dark:bg-dark-card dark:border-dark-border shadow-xl">
      <CardHeader className="border-b border-gray-200 bg-gray-50/50 dark:border-dark-border dark:bg-dark-card/50">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="text-3xl flex-shrink-0">{getSmellTypeIcon(finding.smell_type)}</div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-cream">{finding.smell_type}</h2>
            </div>
            <Badge variant={getBadgeVariant(finding.severity)} size="md" className="mt-2">
              {finding.severity.toUpperCase()}
            </Badge>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-2xl text-gray-400 hover:text-red-500 dark:text-cream-50 dark:hover:text-coral transition-colors"
            >
              ×
            </button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6 max-h-96 overflow-y-auto">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-slate-50 border border-gray-200 dark:bg-cream-10/10 dark:border-dark-border rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-cream-50 font-semibold">CONFIDENCE</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-coral">
              {(finding.confidence * 100).toFixed(0)}%
            </p>
          </div>
          <div className="bg-slate-50 border border-gray-200 dark:bg-cream-10/10 dark:border-dark-border rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-cream-50 font-semibold">SEVERITY</p>
            <p className="text-lg font-bold text-orange-650 dark:text-yellow-400 capitalize">
              {finding.severity}
            </p>
          </div>
          <div className="bg-slate-50 border border-gray-200 dark:bg-cream-10/10 dark:border-dark-border rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-cream-50 font-semibold">LLM PROVIDER</p>
            <p className="text-sm font-bold text-blue-600 dark:text-blue-400 truncate mt-1">{finding.llm_provider}</p>
          </div>
          <div className="bg-slate-50 border border-gray-200 dark:bg-cream-10/10 dark:border-dark-border rounded-lg p-3">
            <p className="text-xs text-gray-500 dark:text-cream-50 font-semibold">FINDING #</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-cream-90">
              {index + 1}
              {totalFindings && `/${totalFindings}`}
            </p>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 dark:text-cream mb-2">Location</h3>
          <div className="bg-slate-50 border border-gray-200 dark:bg-dark/45 dark:border-dark-border rounded-lg p-3 space-y-2">
            <p className="text-sm text-gray-650 dark:text-cream-50">
              <span className="font-medium text-gray-900 dark:text-cream-90">File:</span>{' '}
              <code className="bg-white border border-gray-250 dark:bg-dark-card dark:border-dark-border px-2 py-1 rounded font-mono text-xs break-all text-gray-800 dark:text-cream-90">
                {finding.file_path}
              </code>
            </p>
            <p className="text-sm text-gray-650 dark:text-cream-50">
              <span className="font-medium text-gray-900 dark:text-cream-90">Class:</span>{' '}
              <code className="bg-white border border-gray-250 dark:bg-dark-card dark:border-dark-border px-2 py-1 rounded font-mono text-xs text-gray-800 dark:text-cream-90">
                {finding.class_name}
              </code>
            </p>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 dark:text-cream mb-2">Rationale</h3>
          <p className="text-gray-700 dark:text-cream-90 leading-relaxed">{finding.rationale}</p>
        </div>

        {Object.keys(finding.metrics).length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-cream mb-3">Metrics</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(finding.metrics).map(([key, value]) => (
                <div key={key} className="bg-slate-50 border border-gray-200 dark:bg-cream-10/10 dark:border-dark-border rounded-lg p-3">
                  <p className="text-xs text-gray-500 dark:text-cream-50 font-semibold uppercase">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-lg font-bold text-gray-900 dark:text-cream mt-1">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {finding.refactoring_suggestions.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-cream mb-3">Refactoring Suggestions</h3>
            <ul className="space-y-2">
              {finding.refactoring_suggestions.map((suggestion, i) => (
                <li key={i} className="flex gap-2 text-gray-700 dark:text-cream-90">
                  <span className="text-blue-600 dark:text-coral font-bold flex-shrink-0">✓</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {finding.similar_examples.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-cream mb-3">Similar Examples</h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {finding.similar_examples.map((example, i) => (
                <div key={i} className="bg-slate-50 border border-gray-200 rounded-lg p-2 text-sm text-gray-700 dark:bg-dark/40 dark:border-dark-border dark:text-cream-90">
                  {typeof example === 'string' ? example : JSON.stringify(example)}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex gap-2 justify-end bg-gray-50 dark:bg-dark-card/50 border-t border-gray-200 dark:border-dark-border">
        {onPrevious && (
          <Button variant="secondary" onClick={onPrevious}>
            ← Previous
          </Button>
        )}
        {onNext && (
          <Button variant="secondary" onClick={onNext}>
            Next →
          </Button>
        )}
        {onClose && (
          <Button onClick={onClose}>Close</Button>
        )}
      </CardFooter>
    </Card>
  );
}

// Export as a function for use in modals
export const findingDetail = FindingDetail;
