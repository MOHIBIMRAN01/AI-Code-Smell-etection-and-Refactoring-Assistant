/**
 * Reusable Alert component
 */

import { cn } from '@/lib/utils';
import React from 'react';
import { FiInfo, FiCheckCircle, FiAlertTriangle, FiXCircle } from 'react-icons/fi';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  onClose?: () => void;
}

export function Alert({
  variant = 'info',
  title,
  onClose,
  className,
  children,
  ...props
}: AlertProps) {
  const baseStyles = 'rounded-lg p-4 border';

  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950/30 dark:border-blue-900/50 dark:text-blue-300',
    success: 'bg-green-50 border-green-200 text-green-900 dark:bg-green-950/30 dark:border-green-900/50 dark:text-green-300',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-950/30 dark:border-yellow-900/50 dark:text-yellow-300',
    error: 'bg-red-50 border-red-200 text-red-900 dark:bg-coral/10 dark:border-coral/30 dark:text-coral',
  };

  const IconComponent = {
    info: FiInfo,
    success: FiCheckCircle,
    warning: FiAlertTriangle,
    error: FiXCircle,
  }[variant];

  return (
    <div className={cn(baseStyles, variants[variant], className)} {...props}>
      <div className="flex items-start gap-3">
        <IconComponent className="text-xl mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          {title && <h4 className="font-semibold mb-1">{title}</h4>}
          {children}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 text-lg hover:opacity-70 transition-opacity"
            aria-label="Close alert"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
