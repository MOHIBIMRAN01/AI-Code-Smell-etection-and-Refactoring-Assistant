/**
 * Home page
 */

'use client';

import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/Button';
import { Card, CardContent } from '@/components/Card';
import { FiSearch, FiBarChart2 } from 'react-icons/fi';
import { LuLightbulb, LuRocket } from 'react-icons/lu';

export default function Home() {
  const features = [
    {
      icon: <FiSearch className="text-coral" />,
      title: 'Intelligent Detection',
      description: 'AI-powered analysis to detect code smells and anti-patterns in Java repositories',
    },
    {
      icon: <LuLightbulb className="text-coral" />,
      title: 'Smart Suggestions',
      description: 'Get personalized refactoring recommendations based on your code',
    },
    {
      icon: <FiBarChart2 className="text-coral" />,
      title: 'Detailed Reports',
      description: 'Comprehensive analysis with metrics, severity ratings, and confidence scores',
    },
    {
      icon: <LuRocket className="text-coral" />,
      title: 'Quick Analysis',
      description: 'Fast repository scanning with support for large codebases',
    },
  ];

  const smellTypes = [
    'Long Method',
    'Large Class',
    'Feature Envy',
    'Data Clumps',
    'Primitive Obsession',
    'Switch Statements',
    'Parallel Inheritance',
    'Lazy Class',
  ];

  return (
    <>
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-12 sm:py-16 lg:py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-cream mb-6">
                Detect Code Smells
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-coral dark:to-cream bg-clip-text text-transparent">
                  with AI
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-gray-600 dark:text-cream-50 max-w-2xl mx-auto mb-8">
                Analyze your Java repositories to detect code smells, receive intelligent refactoring
                suggestions, and improve your code quality using advanced AI technology.
              </p>
              <Link href="/analyze">
                <Button size="lg" className="px-8">
                  Start Analyzing →
                </Button>
              </Link>
            </div>

            {/* Demo Stats */}
            <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-4xl font-bold text-blue-600 dark:text-coral">10k+</p>
                <p className="text-gray-600 dark:text-cream-50 mt-2">Repositories Analyzed</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-blue-600 dark:text-coral">1M+</p>
                <p className="text-gray-600 dark:text-cream-50 mt-2">Code Smells Detected</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-blue-600 dark:text-coral">95%</p>
                <p className="text-gray-600 dark:text-cream-50 mt-2">Detection Accuracy</p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-12 sm:py-16 lg:py-20 bg-gray-50 border-y border-gray-200 dark:bg-dark-card/30 dark:border-dark-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-cream">
                Powerful Features
              </h2>
              <p className="text-gray-600 dark:text-cream-50 mt-4 text-lg">
                Everything you need to improve code quality
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature, i) => (
                <Card key={i} variant="elevated">
                  <CardContent className="pt-6">
                    <div className="text-4xl mb-4">{feature.icon}</div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-cream mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 dark:text-cream-50">{feature.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Detectable Smells Section */}
        <section className="py-12 sm:py-16 lg:py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-cream">
                Detectable Code Smells
              </h2>
              <p className="text-gray-600 dark:text-cream-50 mt-4 text-lg">
                Our AI can identify a wide range of code smell patterns
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {smellTypes.map((smell, i) => (
                <Card key={i} className="text-center hover:border-gray-300 dark:hover:border-cream-30 hover:bg-gray-50/50 dark:hover:bg-dark-card/45 transition-all">
                  <CardContent className="py-4">
                    <p className="font-medium text-gray-800 dark:text-cream-90">{smell}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-12 sm:py-16 lg:py-20 bg-gradient-to-r from-blue-50 via-slate-100 to-blue-50 dark:from-coral/10 dark:via-dark-card dark:to-coral/10 border-t border-gray-200 dark:border-dark-border">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-cream mb-6">
              Ready to improve your code quality?
            </h2>
            <p className="text-gray-600 dark:text-cream-50 text-lg mb-8">
              Analyze your first repository now and get actionable insights
            </p>
            <Link href="/analyze">
              <Button variant="secondary" size="lg" className="px-8">
                Analyze Your Repository
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}