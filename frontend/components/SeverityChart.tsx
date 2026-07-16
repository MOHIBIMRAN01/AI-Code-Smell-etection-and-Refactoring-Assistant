/**
 * Severity distribution chart component
 */

'use client';

import { Card, CardContent, CardHeader } from './Card';
import type { Finding } from '@/types';

interface SeverityChartProps {
  findings: Finding[];
}

export function SeverityChart({ findings }: SeverityChartProps) {
  const counts = {
    critical: findings.filter((f) => f.severity === 'critical').length,
    high: findings.filter((f) => f.severity === 'high').length,
    medium: findings.filter((f) => f.severity === 'medium').length,
    low: findings.filter((f) => f.severity === 'low').length,
  };

  const total = findings.length;
  const maxCount = Math.max(...Object.values(counts), 1);

  const severities = [
    { name: 'Critical', count: counts.critical, color: 'bg-coral', lightColor: 'bg-coral/15' },
    { name: 'High', count: counts.high, color: 'bg-yellow-400', lightColor: 'bg-yellow-950/40' },
    { name: 'Medium', count: counts.medium, color: 'bg-blue-400', lightColor: 'bg-blue-950/40' },
    { name: 'Low', count: counts.low, color: 'bg-green-400', lightColor: 'bg-green-950/40' },
  ];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-cream">Severity Distribution</h3>
      </CardHeader>
      <CardContent className="space-y-4">
        {severities.map(({ name, count, color, lightColor }) => {
          const percentage = total > 0 ? (count / total) * 100 : 0;
          const barWidth = total > 0 ? (count / maxCount) * 100 : 0;

          return (
            <div key={name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700 dark:text-cream-90">{name}</span>
                <span className="text-sm font-semibold text-gray-900 dark:text-cream">
                  {count} ({percentage.toFixed(1)}%)
                </span>
              </div>
              <div className={`w-full h-2 rounded-full ${lightColor} overflow-hidden border border-gray-100 dark:border-dark-border`}>
                <div className={`h-full ${color} transition-all duration-300`} style={{ width: `${barWidth}%` }} />
              </div>
            </div>
          );
        })}

        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-dark-border">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {severities.map(({ name, count }) => (
              <div key={name} className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-cream">{count}</p>
                <p className="text-xs text-gray-500 dark:text-cream-50 mt-1">{name}</p>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
