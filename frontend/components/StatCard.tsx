/**
 * Statistics card component
 */

import { Card, CardContent } from './Card';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low';
  subtitle?: string;
}

export function StatCard({
  title,
  value,
  icon,
  variant = 'default',
  subtitle,
}: StatCardProps) {
  const variants = {
    default: 'bg-blue-50 border-blue-100 text-blue-900 dark:bg-dark-card dark:border-dark-border dark:text-cream-90',
    critical: 'bg-red-50 border-red-100 text-red-900 dark:bg-coral/10 dark:border-coral/30 dark:text-coral',
    high: 'bg-orange-50 border-orange-100 text-orange-900 dark:bg-yellow-950/40 dark:border-yellow-900/60 dark:text-yellow-400',
    medium: 'bg-yellow-50 border-yellow-100 text-yellow-900 dark:bg-blue-950/40 dark:border-blue-900/60 dark:text-blue-400',
    low: 'bg-green-50 border-green-100 text-green-900 dark:bg-green-950/40 dark:border-green-900/60 dark:text-green-400',
  };

  const textColors = {
    default: 'text-blue-900 dark:text-cream-90',
    critical: 'text-red-950 dark:text-coral',
    high: 'text-orange-950 dark:text-yellow-400',
    medium: 'text-yellow-950 dark:text-blue-400',
    low: 'text-green-950 dark:text-green-400',
  };

  return (
    <Card className={cn('border', variants[variant])}>
      <CardContent className="flex items-start gap-4 pt-4">
        {icon && <span className="text-3xl flex-shrink-0">{icon}</span>}
        <div className="flex-1">
          <p className={cn('text-sm font-semibold', textColors[variant])}>
            {title}
          </p>
          <p className={cn('text-3xl font-bold mt-1', textColors[variant])}>
            {value}
          </p>
          {subtitle && (
            <p className={cn('text-xs mt-1', textColors[variant])}>
              {subtitle}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
