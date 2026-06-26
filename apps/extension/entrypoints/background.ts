import { getVideoAnalysis, getTaskProgress, uploadVideoSegment } from "../lib/api-client";
import type { ExtensionMessage, ExtensionResponse } from "../lib/messages";
import { createEmptySession, loadSession, patchSession, saveSession } from "../lib/session-store";

const CAPTURE_MAX_MS = 60_000;
const POLL_INTERVAL_MS = 2_000;

let pollTimer: ReturnType<typeof setInterval> | undefined;

async function ensureOffscreenDocument(): Promise<void> {
  const existing = await browser.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
  });
  if (existing.length > 0) return;

  await browser.offscreen.createDocument({
    url: browser.runtime.getURL("/offscreen.html"),
    reasons: ["USER_MEDIA"],
    justification: "Record tab audio/video after explicit user action for analysis.",
  });
}

function stopPolling(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

function mapTaskError(code?: string, message?: string): { errorCode: string; errorMessage: string } {
  switch (code) {
    case "capture_denied":
      return {
        errorCode: code,
        errorMessage: "录制权限被拒绝。请在浏览器提示中允许标签页捕获后重试。",
      };
    case "asr_failed":
      return {
        errorCode: code,
        errorMessage: "语音转写失败。请确认视频有清晰旁白后重试。",
      };
    case "llm_parse_failed":
      return {
        errorCode: code,
        errorMessage: "结构分析结果无效。请稍后重试。",
      };
    case "upload_failed":
      return {
        errorCode: code,
        errorMessage: "上传失败。请检查 API 服务是否运行。",
      };
    default:
      return {
        errorCode: code || "unknown_error",
        errorMessage: message || "分析失败，请重试。",
      };
  }
}

async function startPolling(taskId: string, videoId: string): Promise<void> {
  stopPolling();
  pollTimer = setInterval(() => {
    void pollTask(taskId, videoId);
  }, POLL_INTERVAL_MS);
  await pollTask(taskId, videoId);
}

async function pollTask(taskId: string, videoId: string): Promise<void> {
  try {
    const task = await getTaskProgress(taskId);
    await patchSession({
      state: "processing",
      taskId,
      videoId,
      progress: task.progress,
      currentStep: task.currentStep,
    });

    if (task.status === "completed") {
      stopPolling();
      const result = await getVideoAnalysis(videoId);
      await patchSession({
        state: "done",
        progress: 100,
        currentStep: "分析完成",
        analysis: result.analysis,
      });
      return;
    }

    if (task.status === "failed") {
      stopPolling();
      const mapped = mapTaskError(task.error, task.currentStep);
      await patchSession({
        state: "error",
        ...mapped,
      });
    }
  } catch (error) {
    stopPolling();
    await patchSession({
      state: "error",
      errorCode: "upload_failed",
      errorMessage: error instanceof Error ? error.message : "无法获取任务进度",
    });
  }
}

async function startAnalysis(): Promise<ExtensionResponse> {
  const session = await loadSession();
  if (session.state !== "idle" && session.state !== "done" && session.state !== "error") {
    return { ok: false, error: "分析正在进行中" };
  }
  if (!session.videoMeta?.videoUrl || session.pageDetection?.pageType !== "video") {
    return { ok: false, error: "当前页面不是可分析的视频页", code: "unsupported_platform" };
  }

  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) {
    return { ok: false, error: "无法获取当前标签页" };
  }

  await patchSession({
    state: "capturing",
    errorCode: undefined,
    errorMessage: undefined,
    analysis: undefined,
    progress: 0,
    currentStep: "等待录制权限",
  });

  try {
    const streamId = await browser.tabCapture.getMediaStreamId({ targetTabId: tab.id });
    await ensureOffscreenDocument();
    await browser.runtime.sendMessage({
      type: "offscreen:start-capture",
      streamId,
      maxDurationMs: CAPTURE_MAX_MS,
    } satisfies ExtensionMessage);
    return { ok: true, session: await loadSession() };
  } catch (error) {
    const mapped = mapTaskError("capture_denied", error instanceof Error ? error.message : undefined);
    await patchSession({ state: "error", ...mapped });
    return { ok: false, error: mapped.errorMessage, code: mapped.errorCode };
  }
}

async function handleCaptureComplete(blob: Blob): Promise<void> {
  const session = await loadSession();
  if (!session.videoMeta) {
    await patchSession({
      state: "error",
      errorCode: "upload_failed",
      errorMessage: "缺少视频元数据，无法上传",
    });
    return;
  }

  await patchSession({
    state: "uploading",
    currentStep: "上传录制片段",
    progress: 10,
  });

  try {
    const { videoId, taskId } = await uploadVideoSegment({
      file: blob,
      videoUrl: session.videoMeta.videoUrl,
      title: session.videoMeta.title,
      platformVideoId: session.videoMeta.platformVideoId,
    });

    await patchSession({
      state: "processing",
      videoId,
      taskId,
      currentStep: "处理中",
      progress: 20,
    });
    await startPolling(taskId, videoId);
  } catch (error) {
    const mapped = mapTaskError("upload_failed", error instanceof Error ? error.message : undefined);
    await patchSession({ state: "error", ...mapped });
  }
}

export default defineBackground(() => {
  browser.runtime.onInstalled.addListener(() => {
    void browser.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
    void saveSession(createEmptySession());
  });

  browser.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
    const handle = async (): Promise<ExtensionResponse | { ok: true } | undefined> => {
      switch (message.type) {
        case "content:page-update":
          await patchSession({
            pageDetection: message.detection,
            videoMeta: message.videoMeta ?? undefined,
          });
          return { ok: true };

        case "sidepanel:get-session":
          return { ok: true, session: await loadSession() };

        case "sidepanel:start-analysis":
          return startAnalysis();

        case "sidepanel:reset":
          stopPolling();
          await saveSession(createEmptySession());
          return { ok: true, session: await loadSession() };

        case "offscreen:capture-complete": {
          const blob = new Blob([message.data], { type: message.mimeType || "video/webm" });
          await handleCaptureComplete(blob);
          return { ok: true };
        }

        case "offscreen:capture-error": {
          const mapped = mapTaskError(message.code, message.message);
          await patchSession({ state: "error", ...mapped });
          return { ok: true };
        }

        default:
          return undefined;
      }
    };

    void handle().then((result) => {
      if (result !== undefined) sendResponse(result);
    });
    return true;
  });
});
