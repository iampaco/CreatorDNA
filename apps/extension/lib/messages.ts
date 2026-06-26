import type {
  AnalysisTask,
  CreatorVideoMeta,
  PlatformPageDetection,
  VideoStyleAnalysis,
} from "@creator-dna/shared-types";

export type AnalysisState =
  | "idle"
  | "capturing"
  | "uploading"
  | "processing"
  | "done"
  | "error";

export interface AnalysisSession {
  state: AnalysisState;
  pageDetection?: PlatformPageDetection;
  videoMeta?: CreatorVideoMeta;
  taskId?: string;
  videoId?: string;
  progress?: number;
  currentStep?: string;
  errorCode?: string;
  errorMessage?: string;
  analysis?: VideoStyleAnalysis;
  updatedAt: string;
}

export type ExtensionMessage =
  | { type: "content:page-update"; detection: PlatformPageDetection; videoMeta: CreatorVideoMeta | null }
  | { type: "sidepanel:get-session" }
  | { type: "sidepanel:start-analysis" }
  | { type: "sidepanel:reset" }
  | { type: "offscreen:start-capture"; streamId: string; maxDurationMs: number }
  | { type: "offscreen:stop-capture" }
  | { type: "offscreen:capture-complete"; data: ArrayBuffer; mimeType: string; durationMs: number }
  | { type: "offscreen:capture-error"; code: string; message: string };

export type ExtensionResponse =
  | { ok: true; session: AnalysisSession }
  | { ok: true; task?: AnalysisTask }
  | { ok: false; error: string; code?: string };
