/**
 * Application Footer component
 */

export function Footer() {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 text-gray-300 dark:bg-dark-card dark:border-dark-border dark:text-cream-90 py-8 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-bold mb-4 text-white dark:text-cream">CodeSmell AI</h3>
            <p className="text-gray-400 dark:text-cream-50 text-sm">
              Detect and refactor code smells in Java repositories using AI-powered analysis.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4 text-white dark:text-cream">Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/" className="text-gray-400 hover:text-blue-500 dark:text-cream-50 dark:hover:text-coral transition-colors">
                  Home
                </a>
              </li>
              <li>
                <a href="/analyze" className="text-gray-400 hover:text-blue-500 dark:text-cream-50 dark:hover:text-coral transition-colors">
                  Analyze Repository
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4 text-white dark:text-cream">Support</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="text-gray-400 hover:text-blue-500 dark:text-cream-50 dark:hover:text-coral transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-blue-500 dark:text-cream-50 dark:hover:text-coral transition-colors">
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 dark:border-dark-border mt-8 pt-8 text-center text-gray-400 dark:text-cream-50 text-sm">
          <p>&copy; 2026 CodeSmell AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
