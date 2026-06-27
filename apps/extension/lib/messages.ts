import type {
  AnalysisTask,
  CreatorProfile,
  CreatorReport,
  CreatorVideoMeta,
  PlatformPageDetection,
  VideoStyleAnalysis,
  VisualAnalysis,
} from "@creator-dna/shared-types";

export type AnalysisState =
  | "idle"
  | "capturing"
  | "uploading"
  | "processing"
  | "done"
  | "error";

export type AnalysisMode = "single" | "batch";

export interface BatchVideoItem {
  videoId: string;
  videoUrl: string;
  platformVideoId?: string;
  title?: string;
  status?: "pending" | "capturing" | "uploading" | "processing" | "done" | "failed";
}

export interface AnalysisSession {
  mode?: AnalysisMode;
  state: AnalysisState;
  pageDetection?: PlatformPageDetection;
  videoMeta?: CreatorVideoMeta;
  creatorProfile?: CreatorProfile;
  videoList?: CreatorVideoMeta[];
  sampleSize?: number;
  taskId?: string;
  videoId?: string;
  creatorId?: string;
  batchVideos?: BatchVideoItem[];
  currentVideoIndex?: number;
  progress?: number;
  currentStep?: string;
  finishedVideos?: number;
  totalVideos?: number;
  errorCode?: string;
  errorMessage?: string;
  analysis?: VideoStyleAnalysis;
  visualAnalysis?: VisualAnalysis;
  creatorReport?: CreatorReport;
  captureStartedAt?: string;
  updatedAt: string;
}

export type ExtensionMessage =
  | {
      type: "content:page-update";
      detection: PlatformPageDetection;
      videoMeta: CreatorVideoMeta | null;
      creatorProfile?: CreatorProfile | null;
      videoList?: CreatorVideoMeta[] | null;
    }
  | { type: "content:extract-videos"; limit: number }
  | { type: "sidepanel:get-session" }
  | { type: "sidepanel:start-analysis" }
  | { type: "sidepanel:start-batch"; sampleSize: number }
  | { type: "sidepanel:set-sample-size"; sampleSize: number }
  | { type: "sidepanel:reset" }
  | { type: "offscreen:start-capture"; streamId: string; maxDurationMs: number }
  | { type: "offscreen:stop-capture" }
  | { type: "offscreen:capture-complete"; data: ArrayBuffer; mimeType: string; durationMs: number }
  | { type: "offscreen:capture-error"; code: string; message: string };

export type ExtensionResponse =
  | { ok: true; session: AnalysisSession }
  | { ok: true; task?: AnalysisTask }
  | { ok: false; error: string; code?: string };
