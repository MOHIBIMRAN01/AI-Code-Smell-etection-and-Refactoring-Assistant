/**
 * Utility functions for the application
 */

import clsx, { type ClassValue } from 'clsx';
import React from 'react';
import { 
  FiAlertTriangle, 
  FiAlertCircle, 
  FiInfo, 
  FiCheckCircle,
  FiEye,
  FiBox,
  FiHash,
  FiGitBranch,
  FiLink,
  FiMoon,
  FiCompass,
  FiFileText,
  FiLayers,
  FiUsers,
  FiLock,
  FiRefreshCw,
  FiBookOpen,
  FiDatabase,
  FiXCircle,
  FiMessageSquare,
  FiSearch
} from 'react-icons/fi';
import { LuRuler } from 'react-icons/lu';
import { FaRegBuilding } from 'react-icons/fa6';

/**
 * Merge classnames safely
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Format a date string to a readable format
 */
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}

/**
 * Get severity badge color
 */
export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-red-100 text-red-800 border border-red-300';
    case 'high':
      return 'bg-orange-100 text-orange-800 border border-orange-300';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
    case 'low':
      return 'bg-green-100 text-green-800 border border-green-300';
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-300';
  }
}

/**
 * Get badge variant from severity
 */
export function getBadgeVariant(severity: string): 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'danger';
    case 'high':
      return 'warning';
    case 'medium':
      return 'primary';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
}

/**
 * Get severity icon component
 */
export function getSeverityIcon(severity: string): React.ReactNode {
  switch (severity.toLowerCase()) {
    case 'critical':
      return <FiAlertTriangle className="inline mr-1 text-coral text-sm" />;
    case 'high':
      return <FiAlertCircle className="inline mr-1 text-yellow-400 text-sm" />;
    case 'medium':
      return <FiInfo className="inline mr-1 text-blue-400 text-sm" />;
    case 'low':
      return <FiCheckCircle className="inline mr-1 text-green-400 text-sm" />;
    default:
      return <FiInfo className="inline mr-1 text-sm" />;
  }
}

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Extract repository name from URL
 */
export function extractRepoName(url: string): string {
  try {
    const match = url.match(/\/([^/]+)(\.git)?$/);
    return match ? match[1] : url;
  } catch {
    return url;
  }
}

/**
 * Validate GitHub repository URL
 */
export function isValidGitHubUrl(url: string): boolean {
  const githubRegex = /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+(\.git)?$/i;
  return githubRegex.test(url);
}

/**
 * Format confidence as percentage
 */
export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(0)}%`;
}

/**
 * Get smell type icon/emoji component
 */
export function getSmellTypeIcon(smellType: string): React.ReactNode {
  const icons: Record<string, React.ReactNode> = {
    'Long Method': <LuRuler className="inline text-coral" />,
    'Large Class': <FaRegBuilding className="inline text-coral" />,
    'Feature Envy': <FiEye className="inline text-coral" />,
    'Data Clumps': <FiBox className="inline text-coral" />,
    'Primitive Obsession': <FiHash className="inline text-coral" />,
    'Switch Statements': <FiGitBranch className="inline text-coral" />,
    'Parallel Inheritance': <FiLink className="inline text-coral" />,
    'Lazy Class': <FiMoon className="inline text-coral" />,
    'Speculative Generality': <FiCompass className="inline text-coral" />,
    'Temporary Field': <FiFileText className="inline text-coral" />,
    'Message Chains': <FiLayers className="inline text-coral" />,
    'Middle Man': <FiUsers className="inline text-coral" />,
    'Inappropriate Intimacy': <FiLock className="inline text-coral" />,
    'Alternative Classes': <FiRefreshCw className="inline text-coral" />,
    'Incomplete Library Classes': <FiBookOpen className="inline text-coral" />,
    'Data Classes': <FiDatabase className="inline text-coral" />,
    'Refused Bequest': <FiXCircle className="inline text-coral" />,
    'Comments': <FiMessageSquare className="inline text-coral" />,
  };

  return icons[smellType] || <FiSearch className="inline text-coral" />;
}

/**
 * Calculate statistics from findings
 */
export function calculateStats(findings: any[]) {
  return {
    total: findings.length,
    critical: findings.filter((f) => f.severity === 'critical').length,
    high: findings.filter((f) => f.severity === 'high').length,
    medium: findings.filter((f) => f.severity === 'medium').length,
    low: findings.filter((f) => f.severity === 'low').length,
    avgConfidence:
      findings.length > 0
        ? (findings.reduce((sum, f) => sum + f.confidence, 0) / findings.length * 100).toFixed(1)
        : 0,
  };
}

/**
 * Delay execution (for testing/demo purposes)
 */
export async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
