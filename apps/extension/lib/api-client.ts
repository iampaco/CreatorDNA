import type {
  AnalysisTask,
  CreatorReport,
  CreatorVideoMeta,
  ExportFormat,
  VideoStyleAnalysis,
  VisualAnalysis,
} from "@creator-dna/shared-types";

const DEFAULT_API_BASE = "http://localhost:8000";

export async function getApiBaseUrl(): Promise<string> {
  const stored = await browser.storage.local.get("apiBaseUrl");
  return (stored.apiBaseUrl as string | undefined) || DEFAULT_API_BASE;
}

export async function uploadVideoSegment(params: {
  file: Blob;
  videoUrl: string;
  title?: string;
  platformVideoId?: string;
  videoId?: string;
  creatorId?: string;
  batchTaskId?: string;
}): Promise<{ videoId: string; taskId: string }> {
  const apiBase = await getApiBaseUrl();
  const form = new FormData();
  form.append("file", params.file, "capture.webm");
  form.append("videoUrl", params.videoUrl);
  if (params.title) form.append("title", params.title);
  if (params.platformVideoId) form.append("platformVideoId", params.platformVideoId);
  if (params.videoId) form.append("videoId", params.videoId);
  if (params.creatorId) form.append("creatorId", params.creatorId);
  if (params.batchTaskId) form.append("batchTaskId", params.batchTaskId);

  const response = await fetch(`${apiBase}/api/videos/upload`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { error?: string; message?: string } | null;
    throw new Error(body?.message || `Upload failed (${response.status})`);
  }

  return response.json() as Promise<{ videoId: string; taskId: string }>;
}

export async function getTaskProgress(taskId: string): Promise<AnalysisTask> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/tasks/${taskId}`);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(body?.message || `Task fetch failed (${response.status})`);
  }
  return response.json() as Promise<AnalysisTask>;
}

export async function getVideoAnalysis(videoId: string): Promise<{
  videoId: string;
  transcript?: { fullText: string; language: string };
  analysis?: VideoStyleAnalysis;
  visualAnalysis?: VisualAnalysis;
}> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/videos/${videoId}/analysis`);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(body?.message || `Analysis fetch failed (${response.status})`);
  }
  return response.json() as Promise<{
    videoId: string;
    transcript?: { fullText: string; language: string };
    analysis?: VideoStyleAnalysis;
    visualAnalysis?: VisualAnalysis;
  }>;
}

export async function createCreatorAnalysis(params: {
  creatorUrl: string;
  creatorProfile?: {
    platform: string;
    displayName?: string;
    username?: string;
    profileUrl: string;
    avatarUrl?: string;
  };
  videos: CreatorVideoMeta[];
  sampleSize: number;
}): Promise<{
  taskId: string;
  creatorId: string;
  status: string;
  totalVideos: number;
  videos: Array<{ videoId: string; videoUrl: string; platformVideoId?: string; title?: string }>;
}> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/creator-analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      platform: "douyin",
      creatorUrl: params.creatorUrl,
      creatorProfile: params.creatorProfile,
      videos: params.videos.map((v) => ({
        videoUrl: v.videoUrl,
        platformVideoId: v.platformVideoId,
        title: v.title,
        description: v.description,
        likeCount: v.likeCount,
        commentCount: v.commentCount,
        collectCount: v.collectCount,
      })),
      sampleSize: params.sampleSize,
    }),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: { message?: string } } | null;
    throw new Error(body?.detail?.message || `Creator analysis failed (${response.status})`);
  }
  return response.json();
}

export async function getCreatorReport(creatorId: string): Promise<CreatorReport> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/reports/${creatorId}`);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: { message?: string } } | null;
    throw new Error(body?.detail?.message || `Report fetch failed (${response.status})`);
  }
  return response.json() as Promise<CreatorReport>;
}

export async function createReportExport(
  creatorId: string,
  format: ExportFormat,
): Promise<{ taskId: string; status: string; format: ExportFormat }> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/reports/${creatorId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ format }),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: { message?: string } } | null;
    throw new Error(body?.detail?.message || `Export failed (${response.status})`);
  }
  return response.json() as Promise<{ taskId: string; status: string; format: ExportFormat }>;
}

export async function downloadExportFile(taskId: string, filename: string): Promise<void> {
  const apiBase = await getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/exports/${taskId}/download`);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: { message?: string } } | null;
    throw new Error(body?.detail?.message || `Download failed (${response.status})`);
  }
  const blob = await response.blob();
  const { downloadBlob } = await import("./download");
  downloadBlob(filename, blob);
}

export async function pollExportUntilReady(
  taskId: string,
  onProgress?: (task: AnalysisTask) => void,
): Promise<AnalysisTask> {
  const maxAttempts = 60;
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const task = await getTaskProgress(taskId);
    onProgress?.(task);
    if (task.status === "completed") return task;
    if (task.status === "failed") {
      throw new Error(task.error || "导出失败");
    }
    await new Promise((resolve) => setTimeout(resolve, 1_000));
  }
  throw new Error("导出超时，请稍后重试");
}
