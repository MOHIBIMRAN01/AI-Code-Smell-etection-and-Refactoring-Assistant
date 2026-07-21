import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ErrorProvider, AnalysisProvider, ThemeProvider } from '@/context';
import { ErrorNotification } from '@/components/ErrorNotification';
import { BackendWakeup } from '@/components/BackendWakeup';

export const metadata: Metadata = {
  title: 'Code Smell Detector - AI-Powered Analysis',
  description: 'Detect and refactor code smells in Java repositories using AI',
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-slate-50 to-slate-100 text-gray-900 dark:bg-none dark:bg-dark dark:text-cream antialiased">
        <ThemeProvider>
          <ErrorProvider>
            <AnalysisProvider>
              <div className="min-h-screen flex flex-col">
                <BackendWakeup />
                {children}
                <ErrorNotification />
              </div>
            </AnalysisProvider>
          </ErrorProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
