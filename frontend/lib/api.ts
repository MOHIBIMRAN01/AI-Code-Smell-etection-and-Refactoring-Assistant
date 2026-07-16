/**
 * API client for communicating with the backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  AnalyzeRepositoryRequest,
  AnalysisResponse,
  HealthCheckResponse,
  ReportLinks,
  ApiError,
} from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private backendUrl: string;

  constructor() {
    this.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

    this.client = axios.create({
      baseURL: this.backendUrl,
      timeout: parseInt(process.env.NEXT_PUBLIC_REQUEST_TIMEOUT || '600000'),
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach client X-User-ID header
    this.client.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          let userId = localStorage.getItem('user_id');
          if (!userId) {
            userId = crypto.randomUUID();
            localStorage.setItem('user_id', userId);
          }
          if (config.headers) {
            config.headers['X-User-ID'] = userId;
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add error interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error)
    );
  }

  private handleError(error: AxiosError<ApiError>): never {
    const errorMessage = error.response?.data?.detail || error.message || 'An unknown error occurred';
    const errorStatus = error.response?.status || 500;

    const customError = new Error(errorMessage) as Error & { status?: number };
    customError.status = errorStatus;

    throw customError;
  }

  /**
   * Get all past analyses for this client UUID
   */
  async getAnalyses(): Promise<AnalysisResponse[]> {
    try {
      const response = await this.client.get<AnalysisResponse[]>('/api/analyses');
      return response.data;
    } catch (error) {
      console.error('Failed to get user analyses:', error);
      throw error;
    }
  }

  /**
   * Check if the backend is healthy
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.client.get<HealthCheckResponse>('/api/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Analyze a repository for code smells
   */
  async analyzeRepository(request: AnalyzeRepositoryRequest): Promise<AnalysisResponse> {
    try {
      const response = await this.client.post<AnalysisResponse>('/api/analyze', request);
      return response.data;
    } catch (error) {
      console.error('Analysis request failed:', error);
      throw error;
    }
  }

  /**
   * Get report download links for an analysis
   */
  async getReportLinks(analysisId: string): Promise<ReportLinks> {
    try {
      const response = await this.client.get<ReportLinks>(`/api/reports/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get report links:', error);
      throw error;
    }
  }

  /**
   * Get the full analysis data from the database
   */
  async getReportData(analysisId: string): Promise<AnalysisResponse> {
    try {
      const response = await this.client.get<AnalysisResponse>(`/api/reports/${analysisId}/data`);
      return response.data;
    } catch (error) {
      console.error('Failed to get report data:', error);
      throw error;
    }
  }

  /**
   * Download JSON report
   */
  async downloadJsonReport(analysisId: string): Promise<void> {
    try {
      const response = await this.client.get(`/api/reports/${analysisId}/json`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report-${analysisId}.json`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error('Failed to download JSON report:', error);
      throw error;
    }
  }

  /**
   * Download PDF report
   */
  async downloadPdfReport(analysisId: string): Promise<void> {
    try {
      const response = await this.client.get(`/api/reports/${analysisId}/pdf`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report-${analysisId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error('Failed to download PDF report:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
