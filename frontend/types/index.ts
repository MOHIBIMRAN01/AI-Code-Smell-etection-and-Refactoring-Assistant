/**
 * Type definitions for the Code Smell Detection application
 */

export interface Metric {
  [key: string]: string | number | boolean;
}

export interface Finding {
  file_path: string;
  class_name: string;
  smell_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  rationale: string;
  metrics: Metric;
  refactoring_suggestions: string[];
  similar_examples: Record<string, unknown>[];
  llm_provider: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  repository_url: string;
  repository_name: string;
  repository_path: string;
  total_java_files: number;
  analyzed_classes: number;
  findings: Finding[];
  summary: string;
  json_report_path: string | null;
  pdf_report_path: string | null;
  created_at: string;
}

export interface AnalyzeRepositoryRequest {
  repository_url: string;
  branch?: string;
  analysis_label?: string;
}

export interface ReportLinks {
  json_url: string;
  pdf_url: string;
}

export interface HealthCheckResponse {
  status: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginatedFinding {
  finding: Finding;
  index: number;
}
