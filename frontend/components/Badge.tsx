/**
 * Reusable Badge component
 */

import { cn } from '@/lib/utils';
import React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export function Badge({
  variant = 'default',
  size = 'md',
  className,
  children,
  ...props
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center font-semibold rounded-full';

  const variants = {
    default: 'bg-gray-100 text-gray-800 dark:bg-cream-10 dark:text-cream-90 dark:border dark:border-dark-border',
    primary: 'bg-blue-100 text-blue-800 dark:bg-cream-30/20 dark:text-cream-90 dark:border dark:border-cream-30/40',
    success: 'bg-green-100 text-green-800 dark:bg-green-950/40 dark:text-green-400 dark:border dark:border-green-900/60',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/40 dark:text-yellow-400 dark:border dark:border-yellow-900/60',
    danger: 'bg-red-100 text-red-800 dark:bg-coral/10 dark:text-coral dark:border dark:border-coral/30',
    info: 'bg-cyan-100 text-cyan-800 dark:bg-blue-950/40 dark:text-blue-400 dark:border dark:border-blue-900/60',
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
}
