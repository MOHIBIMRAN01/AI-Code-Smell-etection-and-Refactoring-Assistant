/**
 * Error notification display component
 */

'use client';

import { useErrorContext } from '@/context';
import { Alert } from './Alert';

export function ErrorNotification() {
  const { errors, removeError } = useErrorContext();

  if (errors.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md pointer-events-auto">
      {errors.map((error) => (
        <Alert
          key={error.id}
          variant={error.type === 'error' ? 'error' : error.type === 'success' ? 'success' : error.type === 'warning' ? 'warning' : 'info'}
          onClose={() => removeError(error.id)}
          className="shadow-lg"
        >
          {error.message}
        </Alert>
      ))}
    </div>
  );
}
