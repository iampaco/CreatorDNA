export type TaskStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export interface AnalysisTask {
  taskId: string;
  status: TaskStatus;
  progress: number;
  currentStep?: string;
  finishedVideos?: number;
  totalVideos?: number;
  error?: string;
}

export type TaskProgress = AnalysisTask;
