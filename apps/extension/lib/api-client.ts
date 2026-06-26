import type { AnalysisTask, VideoStyleAnalysis } from "@creator-dna/shared-types";

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
}): Promise<{ videoId: string; taskId: string }> {
  const apiBase = await getApiBaseUrl();
  const form = new FormData();
  form.append("file", params.file, "capture.webm");
  form.append("videoUrl", params.videoUrl);
  if (params.title) form.append("title", params.title);
  if (params.platformVideoId) form.append("platformVideoId", params.platformVideoId);

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
  }>;
}
