import type { AnalysisSession } from "../../lib/messages";
import "./style.css";

const USER_ERROR_MESSAGES: Record<string, string> = {
  capture_denied: "录制权限被拒绝。请在浏览器提示中允许标签页捕获后重试。",
  asr_failed: "语音转写失败。请确认视频有清晰旁白后重试。",
  llm_parse_failed: "结构分析结果无效。请稍后重试。",
  upload_failed: "上传失败。请检查 API 服务是否运行。",
  unsupported_platform: "当前页面不支持分析。请打开抖音视频页。",
};

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

function render(session: AnalysisSession): void {
  const root = document.getElementById("root");
  if (!root) return;
  root.replaceChildren();

  const panel = el("main", "panel");
  const header = el("header", "header");
  header.append(el("h1", undefined, "CreatorDNA"), el("p", "subtitle", "抖音单视频结构分析"));
  panel.append(header);

  const isVideoPage = session.pageDetection?.pageType === "video" && !!session.videoMeta?.videoUrl;
  const canAnalyze =
    isVideoPage && (session.state === "idle" || session.state === "done" || session.state === "error");
  const isWorking =
    session.state === "capturing" || session.state === "uploading" || session.state === "processing";

  const pageCard = el("section", "card");
  pageCard.append(el("h2", undefined, "页面状态"));
  if (isVideoPage) {
    pageCard.append(el("p", "status-ok", "已识别视频页"));
    pageCard.append(el("p", "meta-title", session.videoMeta?.title || "（未读取到标题）"));
  } else {
    pageCard.append(el("p", "status-warn", "请在抖音视频页打开本侧边栏"));
  }
  panel.append(pageCard);

  const actions = el("section", "card actions");
  const analyzeBtn = el("button", undefined, isWorking ? "分析中…" : "开始分析") as HTMLButtonElement;
  analyzeBtn.disabled = !canAnalyze || isWorking;
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

  if (isWorking) {
    const progressCard = el("section", "card");
    progressCard.append(el("h2", undefined, "进度"));
    const bar = el("div", "progress-bar");
    const fill = el("div", "progress-fill");
    fill.style.width = `${session.progress ?? 0}%`;
    bar.append(fill);
    progressCard.append(bar, el("p", undefined, session.currentStep || "处理中"));
    panel.append(progressCard);
  }

  if (session.state === "error") {
    const errorCard = el("section", "card error");
    errorCard.append(el("h2", undefined, "错误"), el("p", undefined, getErrorMessage(session)));
    panel.append(errorCard);
  }

  if (session.state === "done" && session.analysis) {
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