import {
  createCreatorAnalysis,
  getCreatorReport,
  getTaskProgress,
  getVideoAnalysis,
  uploadVideoSegment,
} from "../lib/api-client";
import type { BatchVideoItem, ExtensionMessage, ExtensionResponse } from "../lib/messages";
import { createEmptySession, loadSession, patchSession, saveSession } from "../lib/session-store";

const CAPTURE_MAX_MS = 60_000;
const POLL_INTERVAL_MS = 2_000;
const PAGE_LOAD_TIMEOUT_MS = 15_000;

let pollTimer: ReturnType<typeof setInterval> | undefined;
let pageLoadResolver: ((ok: boolean) => void) | undefined;
let batchCaptureResolver: ((blob: Blob | null) => void) | undefined;

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

function waitForPageLoad(expectedVideoUrl: string): Promise<boolean> {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      pageLoadResolver = undefined;
      resolve(false);
    }, PAGE_LOAD_TIMEOUT_MS);

    pageLoadResolver = (ok: boolean) => {
      clearTimeout(timeout);
      pageLoadResolver = undefined;
      resolve(ok);
    };

    void loadSession().then((session) => {
      if (
        session.videoMeta?.videoUrl?.split("?")[0] === expectedVideoUrl.split("?")[0] &&
        session.pageDetection?.pageType === "video"
      ) {
        clearTimeout(timeout);
        pageLoadResolver = undefined;
        resolve(true);
      }
    });
  });
}

async function waitForVideoTask(taskId: string): Promise<boolean> {
  for (let i = 0; i < 120; i++) {
    const task = await getTaskProgress(taskId);
    if (task.status === "completed") return true;
    if (task.status === "failed") return false;
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  }
  return false;
}

async function startPolling(taskId: string, videoId: string): Promise<void> {
  stopPolling();
  pollTimer = setInterval(() => {
    void pollSingleTask(taskId, videoId);
  }, POLL_INTERVAL_MS);
  await pollSingleTask(taskId, videoId);
}

async function pollSingleTask(taskId: string, videoId: string): Promise<void> {
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
      await patchSession({ state: "error", ...mapped });
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

async function startBatchPolling(batchTaskId: string, creatorId: string): Promise<void> {
  stopPolling();
  pollTimer = setInterval(() => {
    void pollBatchTask(batchTaskId, creatorId);
  }, POLL_INTERVAL_MS);
  await pollBatchTask(batchTaskId, creatorId);
}

async function pollBatchTask(batchTaskId: string, creatorId: string): Promise<void> {
  try {
    const task = await getTaskProgress(batchTaskId);
    await patchSession({
      state: "processing",
      progress: task.progress,
      currentStep: task.currentStep,
      finishedVideos: task.finishedVideos,
      totalVideos: task.totalVideos,
    });

    if (task.status === "completed") {
      stopPolling();
      const report = await getCreatorReport(creatorId);
      await patchSession({
        state: "done",
        progress: 100,
        currentStep: "创作者报告已生成",
        creatorReport: report,
        finishedVideos: task.finishedVideos,
        totalVideos: task.totalVideos,
      });
      return;
    }

    if (task.status === "failed") {
      stopPolling();
      const mapped = mapTaskError(task.error, task.currentStep);
      await patchSession({ state: "error", ...mapped });
    }
  } catch (error) {
    stopPolling();
    await patchSession({
      state: "error",
      errorCode: "upload_failed",
      errorMessage: error instanceof Error ? error.message : "无法获取批量任务进度",
    });
  }
}

async function captureCurrentTab(): Promise<Blob | null> {
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return null;

  return new Promise((resolve) => {
    batchCaptureResolver = resolve;
    void (async () => {
      try {
        const streamId = await browser.tabCapture.getMediaStreamId({ targetTabId: tab.id! });
        await ensureOffscreenDocument();
        await browser.runtime.sendMessage({
          type: "offscreen:start-capture",
          streamId,
          maxDurationMs: CAPTURE_MAX_MS,
        } satisfies ExtensionMessage);
      } catch {
        batchCaptureResolver = undefined;
        resolve(null);
      }
    })();
  });
}

async function processNextBatchVideo(): Promise<void> {
  const session = await loadSession();
  if (session.mode !== "batch" || !session.batchVideos || session.batchTaskId == null) return;

  const index = session.currentVideoIndex ?? 0;
  if (index >= session.batchVideos.length) {
    await patchSession({
      state: "processing",
      currentStep: "等待创作者报告生成",
      progress: 90,
    });
    if (session.creatorId) {
      await startBatchPolling(session.batchTaskId, session.creatorId);
    }
    return;
  }

  const current = session.batchVideos[index];
  const batchVideos = session.batchVideos.map((v, i) =>
    i === index ? { ...v, status: "capturing" as const } : v,
  );

  await patchSession({
    state: "capturing",
    currentVideoIndex: index,
    batchVideos,
    currentStep: `录制视频 ${index + 1}/${session.batchVideos.length}`,
    progress: Math.round((index / session.batchVideos.length) * 80),
  });

  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) {
    await patchSession({
      state: "error",
      errorCode: "capture_denied",
      errorMessage: "无法获取当前标签页",
    });
    return;
  }

  await browser.tabs.update(tab.id, { url: current.videoUrl });
  const loaded = await waitForPageLoad(current.videoUrl);
  if (!loaded) {
    const failedVideos = (await loadSession()).batchVideos?.map((v, i) =>
      i === index ? { ...v, status: "failed" as const } : v,
    );
    await patchSession({ batchVideos: failedVideos, currentVideoIndex: index + 1 });
    await processNextBatchVideo();
    return;
  }

  await patchSession({ state: "capturing", currentStep: `录制视频 ${index + 1}/${session.batchVideos.length}` });
  const blob = await captureCurrentTab();
  if (!blob) {
    const mapped = mapTaskError("capture_denied");
    await patchSession({ state: "error", ...mapped });
    return;
  }

  await handleBatchCaptureComplete(blob, index);
}

async function handleBatchCaptureComplete(blob: Blob, index: number): Promise<void> {
  const session = await loadSession();
  const current = session.batchVideos?.[index];
  if (!current || !session.batchTaskId || !session.creatorId) {
    await patchSession({
      state: "error",
      errorCode: "upload_failed",
      errorMessage: "批量会话数据不完整",
    });
    return;
  }

  const uploadingVideos = session.batchVideos?.map((v, i) =>
    i === index ? { ...v, status: "uploading" as const } : v,
  );

  await patchSession({
    state: "uploading",
    batchVideos: uploadingVideos,
    currentStep: `上传视频 ${index + 1}/${session.batchVideos?.length ?? 0}`,
  });

  try {
    const { taskId } = await uploadVideoSegment({
      file: blob,
      videoUrl: current.videoUrl,
      title: current.title,
      platformVideoId: current.platformVideoId,
      videoId: current.videoId,
      creatorId: session.creatorId,
      batchTaskId: session.batchTaskId,
    });

    const processingVideos = (await loadSession()).batchVideos?.map((v, i) =>
      i === index ? { ...v, status: "processing" as const } : v,
    );
    await patchSession({
      state: "processing",
      batchVideos: processingVideos,
      currentStep: `分析视频 ${index + 1}/${session.batchVideos?.length ?? 0}`,
    });

    const ok = await waitForVideoTask(taskId);
    const doneVideos = (await loadSession()).batchVideos?.map((v, i) =>
      i === index ? { ...v, status: ok ? ("done" as const) : ("failed" as const) } : v,
    );

    await patchSession({
      batchVideos: doneVideos,
      currentVideoIndex: index + 1,
      finishedVideos: (session.finishedVideos ?? 0) + 1,
    });

    await processNextBatchVideo();
  } catch (error) {
    const mapped = mapTaskError("upload_failed", error instanceof Error ? error.message : undefined);
    await patchSession({ state: "error", ...mapped });
  }
}

async function handleCaptureComplete(blob: Blob): Promise<void> {
  const session = await loadSession();
  if (session.mode === "batch") {
    if (batchCaptureResolver) {
      batchCaptureResolver(blob);
      batchCaptureResolver = undefined;
    }
    return;
  }

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
    mode: "single",
    state: "capturing",
    errorCode: undefined,
    errorMessage: undefined,
    analysis: undefined,
    creatorReport: undefined,
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

async function startBatchAnalysis(sampleSize: number): Promise<ExtensionResponse> {
  const session = await loadSession();
  if (session.state !== "idle" && session.state !== "done" && session.state !== "error") {
    return { ok: false, error: "分析正在进行中" };
  }
  if (session.pageDetection?.pageType !== "creator" || !session.creatorProfile?.profileUrl) {
    return { ok: false, error: "当前页面不是创作者主页", code: "unsupported_platform" };
  }

  let videos = (session.videoList ?? []).slice(0, sampleSize);
  if (videos.length < sampleSize) {
    const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
    if (tab?.id) {
      try {
        const response = await browser.tabs.sendMessage(tab.id, {
          type: "content:extract-videos",
          limit: sampleSize,
        });
        if (response?.ok && Array.isArray(response.videos)) {
          videos = response.videos.slice(0, sampleSize);
        }
      } catch {
        // Fall back to cached list.
      }
    }
  }

  if (videos.length === 0) {
    return { ok: false, error: "未找到可分析的视频，请向下滚动加载更多内容" };
  }

  await patchSession({
    mode: "batch",
    state: "processing",
    sampleSize,
    errorCode: undefined,
    errorMessage: undefined,
    analysis: undefined,
    creatorReport: undefined,
    progress: 2,
    currentStep: "创建批量分析任务",
    finishedVideos: 0,
    totalVideos: videos.length,
  });

  try {
    const result = await createCreatorAnalysis({
      creatorUrl: session.creatorProfile.profileUrl,
      creatorProfile: {
        platform: session.creatorProfile.platform,
        displayName: session.creatorProfile.displayName,
        username: session.creatorProfile.username,
        profileUrl: session.creatorProfile.profileUrl,
        avatarUrl: session.creatorProfile.avatarUrl,
      },
      videos,
      sampleSize,
    });

    const batchVideos: BatchVideoItem[] = result.videos.map((v) => ({
      videoId: v.videoId,
      videoUrl: v.videoUrl,
      platformVideoId: v.platformVideoId,
      title: v.title,
      status: "pending",
    }));

    await patchSession({
      taskId: result.taskId,
      creatorId: result.creatorId,
      batchVideos,
      currentVideoIndex: 0,
      totalVideos: result.totalVideos,
      currentStep: "开始批量录制",
      progress: 5,
    });

    void processNextBatchVideo();
    return { ok: true, session: await loadSession() };
  } catch (error) {
    const mapped = mapTaskError("upload_failed", error instanceof Error ? error.message : undefined);
    await patchSession({ state: "error", ...mapped });
    return { ok: false, error: mapped.errorMessage };
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
            creatorProfile: message.creatorProfile ?? undefined,
            videoList: message.videoList ?? undefined,
          });
          if (
            pageLoadResolver &&
            message.detection.pageType === "video" &&
            message.videoMeta?.videoUrl
          ) {
            pageLoadResolver(true);
          }
          return { ok: true };

        case "sidepanel:get-session":
          return { ok: true, session: await loadSession() };

        case "sidepanel:start-analysis":
          return startAnalysis();

        case "sidepanel:start-batch":
          return startBatchAnalysis(message.sampleSize);

        case "sidepanel:reset":
          stopPolling();
          pageLoadResolver = undefined;
          batchCaptureResolver = undefined;
          await saveSession(createEmptySession());
          return { ok: true, session: await loadSession() };

        case "offscreen:capture-complete": {
          const blob = new Blob([message.data], { type: message.mimeType || "video/webm" });
          await handleCaptureComplete(blob);
          return { ok: true };
        }

        case "offscreen:capture-error": {
          if (batchCaptureResolver) {
            batchCaptureResolver(null);
            batchCaptureResolver = undefined;
          } else {
            const mapped = mapTaskError(message.code, message.message);
            await patchSession({ state: "error", ...mapped });
          }
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
