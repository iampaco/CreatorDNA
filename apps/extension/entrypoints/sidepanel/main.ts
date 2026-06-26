import type { AnalysisSession } from "../../lib/messages";
import "./style.css";

const USER_ERROR_MESSAGES: Record<string, string> = {
  capture_denied: "录制权限被拒绝。请在浏览器提示中允许标签页捕获后重试。",
  asr_failed: "语音转写失败。请确认视频有清晰旁白后重试。",
  vision_failed: "视觉分析失败。请确认视频画面可见后重试。",
  llm_parse_failed: "结构分析结果无效。请稍后重试。",
  upload_failed: "上传失败。请检查 API 服务是否运行。",
  unsupported_platform: "当前页面不支持分析。请打开抖音视频页或创作者主页。",
};

const SAMPLE_SIZES = [10, 20, 50] as const;

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
    group.append(btn);
  }
  wrap.append(group);
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
    const summary = el("summary", undefined, "查看完整 Markdown 报告");
    const pre = el("pre", "markdown-preview", report.reportMarkdown);
    details.append(summary, pre);
    card.append(details);
  }

  return card;
}

function render(session: AnalysisSession): void {
  const root = document.getElementById("root");
  if (!root) return;
  root.replaceChildren();

  const panel = el("main", "panel");
  const header = el("header", "header");
  header.append(
    el("h1", undefined, "CreatorDNA"),
    el("p", "subtitle", session.mode === "batch" ? "抖音创作者批量分析" : "抖音单视频结构分析"),
  );
  panel.append(header);

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
      el("p", "meta-title", session.creatorProfile?.displayName || session.creatorProfile?.username || "（未读取到名称）"),
    );
    const count = session.videoList?.length ?? 0;
    pageCard.append(el("p", "meta-count", `已发现 ${count} 个视频链接`));
  } else if (isVideoPage) {
    pageCard.append(el("p", "status-ok", "已识别视频页"));
    pageCard.append(el("p", "meta-title", session.videoMeta?.title || "（未读取到标题）"));
  } else {
    pageCard.append(el("p", "status-warn", "请在抖音视频页或创作者主页打开本侧边栏"));
  }
  panel.append(pageCard);

  if (isCreatorPage) {
    const batchCard = el("section", "card");
    batchCard.append(el("h2", undefined, "批量分析"));
    const selectedSize = session.sampleSize ?? 10;
    const selector = renderSampleSizeSelector(selectedSize, isWorking);
    batchCard.append(selector);

    if (session.videoList?.length) {
      const preview = el("ul", "video-preview");
      for (const video of session.videoList.slice(0, selectedSize)) {
        const item = el("li", undefined, video.title || video.videoUrl);
        preview.append(item);
      }
      batchCard.append(preview);
    }

    const batchBtn = el("button", undefined, isWorking ? "批量分析中…" : "开始批量分析") as HTMLButtonElement;
    batchBtn.disabled = !canBatchAnalyze || isWorking;
    batchBtn.addEventListener("click", () => {
      const active = selector.querySelector<HTMLButtonElement>(".sample.active");
      const size = Number(active?.dataset.size || selectedSize);
      void browser.runtime.sendMessage({ type: "sidepanel:start-batch", sampleSize: size });
    });

    selector.querySelectorAll<HTMLButtonElement>(".sample").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (isWorking) return;
        selector.querySelectorAll(".sample").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });

    batchCard.append(batchBtn);
    panel.append(batchCard);
  }

  if (isVideoPage) {
    const actions = el("section", "card actions");
    const analyzeBtn = el("button", undefined, isWorking ? "分析中…" : "开始分析") as HTMLButtonElement;
    analyzeBtn.disabled = !canSingleAnalyze || isWorking;
    analyzeBtn.addEventListener("click", () => {
      void browser.runtime.sendMessage({ type: "sidepanel:start-analysis" });
    });
    actions.append(analyzeBtn);

    if (session.state === "done" || session.state === "error") {
      const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
      resetBtn.addEventListener("click", () => {
        void browser.runtime.sendMessage({ type: "sidepanel:reset" });
      });
      actions.append(resetBtn);
    }
    panel.append(actions);
  }

  if (isWorking || (session.mode === "batch" && session.state === "done")) {
    const progressCard = el("section", "card");
    progressCard.append(el("h2", undefined, "进度"));
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
    panel.append(progressCard);
  }

  if (session.state === "error") {
    const errorCard = el("section", "card error");
    errorCard.append(el("h2", undefined, "错误"), el("p", undefined, getErrorMessage(session)));
    const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
    resetBtn.addEventListener("click", () => {
      void browser.runtime.sendMessage({ type: "sidepanel:reset" });
    });
    errorCard.append(resetBtn);
    panel.append(errorCard);
  }

  if (session.state === "done" && session.mode === "batch" && session.creatorReport) {
    panel.append(renderCreatorReport(session));
    const resetCard = el("section", "card actions");
    const resetBtn = el("button", "secondary", "重新开始") as HTMLButtonElement;
    resetBtn.addEventListener("click", () => {
      void browser.runtime.sendMessage({ type: "sidepanel:reset" });
    });
    resetCard.append(resetBtn);
    panel.append(resetCard);
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
    panel.append(reportCard);
  }

  root.append(panel);
}

async function refresh(): Promise<void> {
  const response = await browser.runtime.sendMessage({ type: "sidepanel:get-session" });
  if (response?.ok) render(response.session);
}

void refresh();
browser.storage.onChanged.addListener(() => {
  void refresh();
});
setInterval(() => {
  void refresh();
}, 1_500);
