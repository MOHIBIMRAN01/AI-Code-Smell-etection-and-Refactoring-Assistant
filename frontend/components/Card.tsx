/**
 * Reusable Card component
 */

import { cn } from '@/lib/utils';
import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
}

export function Card({
  variant = 'default',
  className,
  children,
  ...props
}: CardProps) {
  const baseStyles = 'rounded-lg transition-all duration-200';

  const variants = {
    default: 'bg-white shadow-md border border-gray-200 text-gray-900 dark:bg-dark-card dark:border-dark-border dark:text-cream',
    elevated: 'bg-white border border-gray-200 shadow-md hover:shadow-lg hover:border-gray-300 dark:bg-dark-card dark:border-dark-border dark:text-cream dark:hover:border-cream-30',
    outlined: 'bg-transparent border border-gray-200 text-gray-800 dark:border-dark-border dark:text-cream-90',
  };

  return (
    <div className={cn(baseStyles, variants[variant], className)} {...props}>
      {children}
    </div>
  );
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardHeader({ className, children, ...props }: CardHeaderProps) {
  return (
    <div className={cn('px-6 py-4 border-b border-gray-200 dark:border-dark-border', className)} {...props}>
      {children}
    </div>
  );
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardContent({ className, children, ...props }: CardContentProps) {
  return (
    <div className={cn('px-6 py-4', className)} {...props}>
      {children}
    </div>
  );
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardFooter({ className, children, ...props }: CardFooterProps) {
  return (
    <div className={cn('px-6 py-4 border-t border-gray-200 bg-gray-50 dark:border-dark-border dark:bg-dark-card/50 rounded-b-lg', className)} {...props}>
      {children}
    </div>
  );
}
