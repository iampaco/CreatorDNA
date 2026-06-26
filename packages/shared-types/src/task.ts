export type TaskStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export type ExportFormat = "markdown" | "json" | "pdf";

export interface AnalysisTask {
  taskId: string;
  status: TaskStatus;
  progress: number;
  currentStep?: string;
  finishedVideos?: number;
  totalVideos?: number;
  error?: string;
  downloadUrl?: string;
}

export type TaskProgress = AnalysisTask;
