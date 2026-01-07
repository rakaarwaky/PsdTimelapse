/**
 * API Client for Timelapse Engine backend
 * Handles communication with the Python FastAPI server
 */

const API_BASE = 'http://localhost:8000';

export interface RenderRequest {
  psd_path: string;
  output_path?: string;
  width?: number;
  height?: number;
  fps?: number;
  strategy?: 'sequential' | 'parallel' | 'staggered';
}

export interface RenderResponse {
  status: string;
  message: string;
  job_id?: string;
  output_path?: string;
}

export interface ProgressResponse {
  state: string;
  current_frame: number;
  total_frames: number;
  progress_percent: number;
  message: string;
}

export interface HealthResponse {
  status: string;
  engine_state: string;
}

class TimelapseApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Check if the API server is healthy
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Upload a PSD file to the server
   */
  async uploadFile(file: File): Promise<{ path: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Start a render job
   */
  async startRender(request: RenderRequest): Promise<RenderResponse> {
    const response = await fetch(`${this.baseUrl}/render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Render failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get progress of a render job
   */
  async getProgress(jobId: string): Promise<ProgressResponse> {
    const response = await fetch(`${this.baseUrl}/progress/${jobId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get progress: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Poll progress until complete
   */
  async pollProgress(
    jobId: string,
    onProgress: (progress: ProgressResponse) => void,
    intervalMs: number = 500
  ): Promise<ProgressResponse> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const progress = await this.getProgress(jobId);
          onProgress(progress);

          if (progress.state === 'complete') {
            resolve(progress);
          } else if (progress.state === 'error') {
            reject(new Error(progress.message));
          } else {
            setTimeout(poll, intervalMs);
          }
        } catch (err) {
          reject(err);
        }
      };

      poll();
    });
  }
}

// Export singleton instance
export const apiClient = new TimelapseApiClient();
export default apiClient;
