/**
 * Loading states components
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export function LoadingSpinner({ size = 'md', message }: LoadingSpinnerProps) {
  const sizeMap = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={cn(
          'border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin',
          sizeMap[size]
        )}
      />
      {message && <p className="text-gray-600 font-medium">{message}</p>}
    </div>
  );
}

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  count?: number;
  height?: string;
}

export function Skeleton({ count = 1, height = 'h-4', className, ...props }: SkeletonProps) {
  return (
    <div className="space-y-2" {...props}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn('bg-gray-200 rounded animate-pulse', height, className)}
        />
      ))}
    </div>
  );
}

interface ProgressBarProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  showLabel?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  showLabel = true,
  className,
  ...props
}: ProgressBarProps) {
  const percentage = (value / max) * 100;

  return (
    <div className={cn('w-full', className)} {...props}>
      <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="bg-blue-600 h-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && <p className="text-sm text-gray-600 mt-1">{Math.round(percentage)}%</p>}
    </div>
  );
}
