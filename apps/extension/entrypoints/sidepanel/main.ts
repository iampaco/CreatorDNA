import type { AnalysisSession, BatchVideoItem, ExtensionMessage, ExtensionResponse } from "../../lib/messages";
import {
  createReportExport,
  downloadExportFile,
  pollExportUntilReady,
} from "../../lib/api-client";
import { downloadJson, downloadText } from "../../lib/download";
import "./style.css";

const CAPTURE_MAX_SECONDS = 60;
const STORAGE_SESSION_KEY = "analysisSession";

const USER_ERROR_MESSAGES: Record<string, string> = {
  capture_denied: "录制权限被拒绝。请在浏览器提示中允许标签页捕获后重试。",
  asr_failed: "语音转写失败。请确认视频有清晰旁白后重试。",
  vision_failed: "视觉分析失败。请确认视频画面可见后重试。",
  llm_parse_failed: "结构分析结果无效。请稍后重试。",
  upload_failed: "上传失败。请检查 API 服务是否运行。",
  unsupported_platform: "当前页面不支持分析。请打开抖音视频页或创作者主页。",
};

const BATCH_STATUS_LABELS: Record<NonNullable<BatchVideoItem["status"]>, string> = {
  pending: "等待",
  capturing: "录制中",
  uploading: "上传中",
  processing: "分析中",
  done: "完成",
  failed: "失败",
};

const SAMPLE_SIZES = [10, 20, 50] as const;

let lastRenderedAt: string | undefined;
let countdownTimer: ReturnType<typeof setInterval> | undefined;
let apiKeySaveTimer: ReturnType<typeof setTimeout> | undefined;
let subtitleEl: HTMLParagraphElement | undefined;

function getErrorMessage(session: AnalysisSession): string {
  if (session.errorMessage) return session.errorMessage;
  if (session.errorCode && USER_ERROR_MESSAGES[session.errorCode]) {
    return USER_ERROR_MESSAGES[session.errorCode];
  }
  return "分析失败，请重试。";
}

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function showFeedback(message: string, type: "error" | "info" = "error"): void {
  const banner = document.getElementById("feedback-banner");
  if (!banner) return;
  banner.textContent = message;
  banner.className = `feedback-banner ${type}`;
  banner.hidden = false;
}

function clearFeedback(): void {
  const banner = document.getElementById("feedback-banner");
  if (!banner) return;
  banner.textContent = "";
  banner.hidden = true;
  banner.className = "feedback-banner";
}

async function runAction(message: ExtensionMessage): Promise<ExtensionResponse | undefined> {
  try {
    const response = (await browser.runtime.sendMessage(message)) as ExtensionResponse | undefined;
    if (response && "ok" in response && !response.ok) {
      showFeedback(response.error, "error");
    } else if (response?.ok) {
      clearFeedback();
    }
    return response;
  } catch {
    showFeedback("操作失败，请确认扩展后台正在运行。", "error");
    return undefined;
  }
}

function clearCountdown(): void {
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = undefined;
  }
}

function syncCountdown(session: AnalysisSession): void {
  clearCountdown();
  if (session.state !== "capturing" || !session.captureStartedAt) return;

  const countdownEl = document.getElementById("recording-countdown");
  if (!countdownEl) return;

  const startedAt = Date.parse(session.captureStartedAt);
  const tick = () => {
    const left = Math.max(0, CAPTURE_MAX_SECONDS - (Date.now() - startedAt) / 1000);
    countdownEl.textContent = `${Math.ceil(left)}s`;
    if (left <= 0) clearCountdown();
  };

  tick();
  countdownTimer = setInterval(tick, 500);
}

function renderReportSection(title: string, value: string): HTMLElement | null {
  if (!value) return null;
  const block = el("div", "report-block");
  block.append(el("h3", undefined, title), el("p", undefined, value));
  return block;
}

function renderSampleSizeSelector(selected: number, disabled: boolean): HTMLElement {
  const wrap = el("div", "sample-size");
  wrap.append(el("p", "sample-label", "样本数量"));
  const group = el("div", "sample-buttons");
  for (const size of SAMPLE_SIZES) {
    const btn = el("button", size === selected ? "sample active" : "sample", String(size)) as HTMLButtonElement;
    btn.type = "button";
    btn.disabled = disabled;
    btn.dataset.size = String(size);
    btn.addEventListener("click", () => {
      if (disabled) return;
      void runAction({ type: "sidepanel:set-sample-size", sampleSize: size });
    });
    group.append(btn);
  }
  wrap.append(group);
  return wrap;
}

function renderBatchVideoList(session: AnalysisSession): HTMLElement | null {
  if (!session.batchVideos?.length) return null;

  const list = el("ul", "batch-video-list");
  session.batchVideos.forEach((video, index) => {
    const item = el("li", "batch-item");
    if (index === session.currentVideoIndex) item.classList.add("batch-item-active");

    const title = el("span", "batch-item-title", video.title || video.videoUrl);
    const status = el(
      "span",
      "batch-item-status",
      BATCH_STATUS_LABELS[video.status ?? "pending"],
    );
    item.append(title, status);
    list.append(item);
  });

  return list;
}

function renderRecordingBanner(): HTMLElement {
  const banner = el("div", "recording-banner");
  const countdown = el("span", "recording-countdown", `${CAPTURE_MAX_SECONDS}s`);
  countdown.id = "recording-countdown";
  banner.append(
    el("span", "recording-pulse"),
    el("span", undefined, "正在录制标签页音频/视频，请勿切换窗口"),
    countdown,
  );
  return banner;
}

function renderExportActions(session: AnalysisSession): HTMLElement {
  const wrap = el("div", "export-actions");
  wrap.append(el("p", "export-label", "导出报告"));

  const report = session.creatorReport;
  const creatorId = session.creatorId || report?.creatorId;
  let exporting = false;

  const setExporting = (value: boolean) => {
    exporting = value;
    for (const btn of wrap.querySelectorAll<HTMLButtonElement>("button.export")) {
      btn.disabled = value;
    }
  };

  const showExportError = (message: string) => {
    const existing = wrap.querySelector(".export-error");
    existing?.remove();
    wrap.append(el("p", "export-error", message));
  };

  const mdBtn = el("button", "export secondary", "Markdown") as HTMLButtonElement;
  mdBtn.type = "button";
  mdBtn.addEventListener("click", () => {
    if (!report?.reportMarkdown || exporting) return;
    downloadText(`creator-report-${creatorId || "export"}.md`, report.reportMarkdown, "text/markdown;charset=utf-8");
  });

  const jsonBtn = el("button", "export secondary", "JSON") as HTMLButtonElement;
  jsonBtn.type = "button";
  jsonBtn.addEventListener("click", () => {
    if (!report || exporting) return;
    downloadJson(`creator-report-${creatorId || "export"}.json`, {
      creatorId: report.creatorId,
      sampleVideoCount: report.sampleVideoCount,
      reportJson: report.reportJson,
    });
  });

  const pdfBtn = el("button", "export", "PDF") as HTMLButtonElement;
  pdfBtn.type = "button";
  pdfBtn.addEventListener("click", () => {
    if (!creatorId || exporting) return;
    setExporting(true);
    void (async () => {
      try {
        const created = await createReportExport(creatorId, "pdf");
        await pollExportUntilReady(created.taskId);
        await downloadExportFile(created.taskId, `creator-report-${creatorId}.pdf`);
      } catch (error) {
        showExportError(error instanceof Error ? error.message : "PDF 导出失败");
      } finally {
        setExporting(false);
      }
    })();
  });

  wrap.append(mdBtn, jsonBtn, pdfBtn);
  return wrap;
}

function renderCreatorReport(session: AnalysisSession): HTMLElement {
  const card = el("section", "card");
  card.append(el("h2", undefined, "创作者报告"));

  const report = session.creatorReport;
  if (!report) {
    card.append(el("p", undefined, "报告加载中…"));
    return card;
  }

  const json = report.reportJson;
  for (const section of [
    renderReportSection("内容定位", String(json.positioning || "")),
    renderReportSection(
      "Hook 模式",
      Array.isArray(json.hookPatterns)
        ? json.hookPatterns
            .slice(0, 5)
            .map((h: { value?: string; count?: number }) => `${h.value} (${h.count})`)
            .join("、")
        : "",
    ),
    renderReportSection(
      "表达风格",
      typeof json.speechStyle === "object" && json.speechStyle
        ? Object.entries(json.speechStyle as Record<string, unknown>)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join("、") : String(v)}`)
            .join("；")
        : "",
    ),
    renderReportSection(
      "拍摄风格",
      typeof json.shootingStyle === "object" && json.shootingStyle
        ? Object.entries(json.shootingStyle as Record<string, unknown>)
            .map(([k, v]) => `${k}: ${String(v)}`)
            .join("；")
        : "",
    ),
    renderReportSection(
      "字幕与剪辑",
      typeof json.subtitleEditingStyle === "object" && json.subtitleEditingStyle
        ? Object.entries(json.subtitleEditingStyle as Record<string, unknown>)
            .map(([k, v]) => `${k}: ${String(v)}`)
            .join("；")
        : "",
    ),
    renderReportSection(
      "可复用模板",
      Array.isArray(json.reusableTemplates) ? json.reusableTemplates.join("；") : "",
    ),
  ]) {
    if (section) card.append(section);
  }

  if (report.reportMarkdown) {
    const details = el("details", "report-markdown");
    details.append(
      el("summary", undefined, "查看完整 Markdown 报告"),
      el("pre", "markdown-preview", report.reportMarkdown),
    );
    card.append(details);
  }

  card.append(renderExportActions(session));
  return card;
}

function updateSubtitle(session: AnalysisSession): void {
  if (!subtitleEl) return;
  subtitleEl.textContent =
    session.mode === "batch" ? "抖音创作者批量分析" : "抖音单视频结构分析";
}

function renderDynamic(session: AnalysisSession): void {
  const dynamicRoot = document.getElementById("dynamic-root");
  if (!dynamicRoot) return;
  dynamicRoot.replaceChildren();

  updateSubtitle(session);

  const isVideoPage = session.pageDetection?.pageType === "video" && !!session.videoMeta?.videoUrl;
  const isCreatorPage =
    session.pageDetection?.pageType === "creator" && !!session.creatorProfile?.profileUrl;
  const isWorking =
    session.state === "capturing" || session.state === "uploading" || session.state === "processing";
  const canSingleAnalyze =
    isVideoPage && (session.state === "idle" || session.state === "done" || session.state === "error");
  const canBatchAnalyze =
    isCreatorPage && (session.state === "idle" || session.state === "done" || session.state === "error");

  const pageCard = el("section", "card");
  pageCard.append(el("h2", undefined, "页面状态"));

  if (isCreatorPage) {
    pageCard.append(el("p", "status-ok", "已识别创作者主页"));
    pageCard.append(
      el(
        "p",
        "meta-title",
        session.creatorProfile?.displayName || session.creatorProfile?.username || "（未读取到名称）",
      ),
    );
    pageCard.append(el("p", "meta-count", `已发现 ${session.videoList?.length ?? 0} 个视频链接`));
  } else if (isVideoPage) {
    pageCard.append(el("p", "status-ok", "已识别视频页"));
    pageCard.append(el("p", "meta-title", session.videoMeta?.title || "（未读取到标题）"));
  } else {
    pageCard.append(el("p", "status-warn", "请在抖音视频页或创作者主页打开本侧边栏"));
  }
  dynamicRoot.append(pageCard);

  if (isCreatorPage) {
    const batchCard = el("section", "card");
    batchCard.append(el("h2", undefined, "批量分析"));
    const selectedSize = session.sampleSize ?? 10;
    batchCard.append(renderSampleSizeSelector(selectedSize, isWorking));

    if (session.videoList?.length) {
      const preview = el("ul", "video-preview");
      for (const video of session.videoList.slice(0, selectedSize)) {
        preview.append(el("li", undefined, video.title || video.videoUrl));
      }
      batchCard.append(preview);
    }

    const batchBtn = el("button", undefined, isWorking ? "批量分析中…" : "开始批量分析") as HTMLButtonElement;
    batchBtn.type = "button";
    batchBtn.disabled = !canBatchAnalyze || isWorking;
    batchBtn.addEventListener("click", () => {
      const confirmed = confirm(
        "批量分析将自动切换当前标签页并依次录制各视频（约 60 秒/个）。\n\n请保持窗口在前台，不要手动切换标签页。\n\n是否继续？",
      );
      if (!confirmed) return;
      void runAction({ type: "sidepanel:start-batch", sampleSize: selectedSize });
    });
    batchCard.append(batchBtn);
    dynamicRoot.append(batchCard);
  }

  if (isVideoPage) {
    const actions = el("section", "card actions");
    const analyzeBtn = el("button", undefined, isWorking ? "分析中…" : "开始分析") as HTMLButtonElement;
    analyzeBtn.type = "button";
    analyzeBtn.disabled = !canSingleAnalyze || isWorking;
    analyzeBtn.addEventListener("click", () => {
      void runAction({ type: "sidepanel:start-analysis" });
    });
    actions.append(analyzeBtn);

    if (session.state === "done") {
      const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
      resetBtn.type = "button";
      resetBtn.addEventListener("click", () => {
        void runAction({ type: "sidepanel:reset" });
      });
      actions.append(resetBtn);
    }
    dynamicRoot.append(actions);
  }

  const showProgress =
    isWorking || (session.mode === "batch" && session.state === "done");
  const showBatchList =
    session.mode === "batch" && session.state !== "idle" && !!session.batchVideos?.length;

  if (showProgress || showBatchList) {
    const progressCard = el("section", "card");
    progressCard.append(el("h2", undefined, "进度"));

    if (session.state === "capturing") {
      progressCard.append(renderRecordingBanner());
    }

    if (showProgress) {
      const bar = el("div", "progress-bar");
      const fill = el("div", "progress-fill");
      fill.style.width = `${session.progress ?? 0}%`;
      bar.append(fill);
      progressCard.append(bar);

      if (session.mode === "batch" && session.totalVideos) {
        progressCard.append(
          el(
            "p",
            "batch-progress",
            `${session.finishedVideos ?? 0} / ${session.totalVideos} 个视频`,
          ),
        );
      }
      progressCard.append(el("p", undefined, session.currentStep || "处理中"));
    }

    const batchList = renderBatchVideoList(session);
    if (batchList) progressCard.append(batchList);

    dynamicRoot.append(progressCard);
  }

  if (session.state === "error") {
    const errorCard = el("section", "card error");
    errorCard.append(el("h2", undefined, "错误"), el("p", undefined, getErrorMessage(session)));
    const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
    resetBtn.type = "button";
    resetBtn.addEventListener("click", () => {
      void runAction({ type: "sidepanel:reset" });
    });
    errorCard.append(resetBtn);
    dynamicRoot.append(errorCard);
  }

  if (session.state === "done" && session.mode === "batch" && session.creatorReport) {
    dynamicRoot.append(renderCreatorReport(session));
    const resetCard = el("section", "card actions");
    const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
    resetBtn.type = "button";
    resetBtn.addEventListener("click", () => {
      void runAction({ type: "sidepanel:reset" });
    });
    resetCard.append(resetBtn);
    dynamicRoot.append(resetCard);
  }

  if (session.state === "done" && session.mode !== "batch" && session.analysis) {
    const reportCard = el("section", "card");
    reportCard.append(el("h2", undefined, "结构报告"));
    const analysis = session.analysis;
    for (const section of [
      renderReportSection("Hook 类型", analysis.hookType),
      renderReportSection("Hook 文案", analysis.hookText),
      renderReportSection("话题分类", analysis.topicCategory),
      renderReportSection("情绪基调", analysis.emotionalTone),
      renderReportSection("结尾类型", analysis.endingType),
      renderReportSection("拍摄风格", analysis.shootingStyle),
      renderReportSection("字幕位置", analysis.subtitlePosition || ""),
      renderReportSection("字幕样式", analysis.subtitleStyle || ""),
      renderReportSection("字幕一致性", analysis.subtitleConsistency || ""),
      renderReportSection("可复用模板", analysis.reusableTemplate),
      renderReportSection("目标受众", analysis.targetAudience?.join("、") || ""),
      renderReportSection("常用表达", analysis.commonPhrases?.join("、") || ""),
    ]) {
      if (section) reportCard.append(section);
    }
    if (analysis.contentStructure?.length) {
      const block = el("div", "report-block");
      block.append(el("h3", undefined, "内容结构"));
      const list = el("ul");
      for (const part of analysis.contentStructure) {
        const item = el("li");
        item.innerHTML = `<strong>${part.part}</strong>：${part.description}`;
        list.append(item);
      }
      block.append(list);
      reportCard.append(block);
    }
    dynamicRoot.append(reportCard);
  }

  syncCountdown(session);
}

function initShell(): void {
  const root = document.getElementById("root");
  if (!root) return;

  const panel = el("main", "panel");
  const header = el("header", "header");
  subtitleEl = el("p", "subtitle", "抖音单视频结构分析");
  header.append(el("h1", undefined, "CreatorDNA"), subtitleEl);
  panel.append(header);

  const settingsCard = el("section", "card settings");
  settingsCard.id = "settings-card";
  settingsCard.append(el("h2", undefined, "连接设置"));
  const apiKeyLabel = el("label", "settings-label", "API Key");
  apiKeyLabel.htmlFor = "api-key-input";
  const apiKeyInput = el("input", "settings-input") as HTMLInputElement;
  apiKeyInput.id = "api-key-input";
  apiKeyInput.type = "password";
  apiKeyInput.placeholder = "API Key（staging/production 必填）";
  apiKeyInput.autocomplete = "off";
  void browser.storage.local.get("apiKey").then((stored) => {
    apiKeyInput.value = (stored.apiKey as string | undefined) || "";
  });
  apiKeyInput.addEventListener("input", () => {
    if (apiKeySaveTimer) clearTimeout(apiKeySaveTimer);
    apiKeySaveTimer = setTimeout(() => {
      void browser.storage.local.set({ apiKey: apiKeyInput.value.trim() });
    }, 300);
  });
  settingsCard.append(apiKeyLabel, apiKeyInput);
  panel.append(settingsCard);

  const feedbackBanner = el("div", "feedback-banner");
  feedbackBanner.id = "feedback-banner";
  feedbackBanner.hidden = true;
  panel.append(feedbackBanner);

  const dynamicRoot = el("div");
  dynamicRoot.id = "dynamic-root";
  panel.append(dynamicRoot);

  root.append(panel);
}

function update(session: AnalysisSession): void {
  if (session.updatedAt === lastRenderedAt) return;
  lastRenderedAt = session.updatedAt;
  renderDynamic(session);
}

async function refresh(): Promise<void> {
  const response = await browser.runtime.sendMessage({ type: "sidepanel:get-session" });
  if (response?.ok) update(response.session);
}

initShell();
void refresh();

browser.storage.onChanged.addListener((changes, area) => {
  if (area !== "local") return;
  if (changes[STORAGE_SESSION_KEY]) {
    const next = changes[STORAGE_SESSION_KEY].newValue as AnalysisSession | undefined;
    if (next) update(next);
  }
});
