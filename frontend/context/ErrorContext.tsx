/**
 * Error Context for global error handling and notifications
 */

'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

export interface AppError {
  id: string;
  message: string;
  type: 'error' | 'warning' | 'info' | 'success';
  duration?: number; // ms, undefined means persistent
}

interface ErrorContextType {
  errors: AppError[];
  addError: (message: string, type?: AppError['type'], duration?: number) => void;
  removeError: (id: string) => void;
  clearErrors: () => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export function ErrorProvider({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<AppError[]>([]);

  const addError = useCallback(
    (message: string, type: AppError['type'] = 'error', duration = 5000) => {
      const id = `${Date.now()}-${Math.random()}`;
      const error: AppError = { id, message, type, duration };

      setErrors((prev) => [...prev, error]);

      // Auto-remove after duration
      if (duration) {
        setTimeout(() => removeError(id), duration);
      }

      return id;
    },
    []
  );

  const removeError = useCallback((id: string) => {
    setErrors((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  return (
    <ErrorContext.Provider value={{ errors, addError, removeError, clearErrors }}>
      {children}
    </ErrorContext.Provider>
  );
}

export function useErrorContext() {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useErrorContext must be used within ErrorProvider');
  }
  return context;
}
