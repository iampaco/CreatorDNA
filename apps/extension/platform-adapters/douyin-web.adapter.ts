import type { PlatformAdapter } from "@creator-dna/platform-core";
import type {
  CreatorProfile,
  CreatorVideoMeta,
  PlatformPageDetection,
} from "@creator-dna/shared-types";

const VIDEO_PATH = /\/video\/(\d+)/;
const USER_PATH = /\/user\/([^/?#]+)/;

function parseCount(text: string | null | undefined): number | undefined {
  if (!text) return undefined;
  const normalized = text.trim().replace(/,/g, "");
  const match = normalized.match(/([\d.]+)\s*([万亿])?/);
  if (!match) return undefined;
  let value = parseFloat(match[1]);
  if (Number.isNaN(value)) return undefined;
  if (match[2] === "万") value *= 10_000;
  if (match[2] === "亿") value *= 100_000_000;
  return Math.round(value);
}

function readMetaContent(name: string): string | undefined {
  const element = document.querySelector(`meta[property="${name}"], meta[name="${name}"]`);
  return element?.getAttribute("content")?.trim() || undefined;
}

function readText(selectors: string[]): string | undefined {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    const text = element?.textContent?.trim();
    if (text) return text;
  }
  return undefined;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function scrollToLoadMore(targetCount: number): Promise<void> {
  let lastHeight = 0;
  let stableRounds = 0;

  for (let i = 0; i < 30; i++) {
    const anchors = document.querySelectorAll<HTMLAnchorElement>("a[href*='/video/']");
    const unique = new Set<string>();
    for (const anchor of anchors) {
      const match = anchor.href.match(VIDEO_PATH);
      if (match) unique.add(match[1]);
    }
    if (unique.size >= targetCount) return;

    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
    await sleep(600);

    const height = document.documentElement.scrollHeight;
    if (height === lastHeight) {
      stableRounds += 1;
      if (stableRounds >= 3) return;
    } else {
      stableRounds = 0;
      lastHeight = height;
    }
  }
}

function extractVideoFromAnchor(anchor: HTMLAnchorElement): CreatorVideoMeta | null {
  const href = anchor.href;
  const match = href.match(VIDEO_PATH);
  if (!match) return null;

  const card = anchor.closest("li, div");
  const title =
    anchor.getAttribute("title") ||
    anchor.getAttribute("aria-label") ||
    card?.querySelector("img")?.getAttribute("alt") ||
    anchor.textContent?.trim() ||
    undefined;

  const coverUrl = card?.querySelector("img")?.getAttribute("src") || undefined;
  const likeText = card ? readText(["[data-e2e='video-like-count']", ".count", ".like-count"]) : undefined;

  return {
    platform: "douyin",
    videoUrl: href.split("?")[0],
    platformVideoId: match[1],
    title: title || undefined,
    coverUrl: coverUrl || undefined,
    likeCount: parseCount(likeText),
  };
}

export class DouyinWebAdapter implements PlatformAdapter {
  readonly platform = "douyin" as const;

  detectPage(): PlatformPageDetection {
    const url = window.location.href;
    if (VIDEO_PATH.test(url)) {
      return { platform: this.platform, pageType: "video", url };
    }
    if (USER_PATH.test(url)) {
      return { platform: this.platform, pageType: "creator", url };
    }
    return { platform: this.platform, pageType: "unknown", url };
  }

  async extractCreatorProfile(): Promise<CreatorProfile | null> {
    const detection = this.detectPage();
    if (detection.pageType !== "creator") return null;

    const match = detection.url.match(USER_PATH);
    const username = match?.[1];
    const displayName =
      readText([
        "[data-e2e='user-title']",
        "[data-e2e='user-name']",
        "h1",
        ".user-title",
        ".nickname",
      ]) || readMetaContent("og:title");

    return {
      platform: this.platform,
      displayName: displayName?.replace(/的主页.*$/, "").trim() || displayName,
      username,
      profileUrl: detection.url.split("?")[0],
      avatarUrl:
        readMetaContent("og:image") ||
        document.querySelector<HTMLImageElement>("[data-e2e='user-avatar'] img, .avatar img")?.src,
    };
  }

  async extractVideoList(limit: number): Promise<CreatorVideoMeta[]> {
    const detection = this.detectPage();
    if (detection.pageType !== "creator") return [];

    if (limit > 0) {
      await scrollToLoadMore(limit);
    }

    const anchors = Array.from(document.querySelectorAll<HTMLAnchorElement>("a[href*='/video/']"));
    const seen = new Set<string>();
    const videos: CreatorVideoMeta[] = [];

    for (const anchor of anchors) {
      const meta = extractVideoFromAnchor(anchor);
      if (!meta?.platformVideoId || seen.has(meta.platformVideoId)) continue;
      seen.add(meta.platformVideoId);
      videos.push(meta);
      if (videos.length >= limit) break;
    }

    return videos;
  }

  async extractCurrentVideo(): Promise<CreatorVideoMeta | null> {
    const detection = this.detectPage();
    if (detection.pageType !== "video") return null;

    const match = detection.url.match(VIDEO_PATH);
    const platformVideoId = match?.[1];
    const title =
      readMetaContent("og:title") ||
      readMetaContent("title") ||
      readText([
        "[data-e2e='video-desc']",
        "h1",
        ".video-info-detail .title",
        "#video-info-wrap h1",
      ]);
    const description =
      readMetaContent("og:description") ||
      readText(["[data-e2e='video-desc']", ".video-info-detail .desc"]);

    const likeText = readText([
      "[data-e2e='like-count']",
      "[data-e2e='browse-like-count']",
      ".like-count",
    ]);
    const commentText = readText(["[data-e2e='comment-count']", ".comment-count"]);
    const collectText = readText(["[data-e2e='collect-count']", ".collect-count"]);

    return {
      platform: this.platform,
      videoUrl: detection.url.split("?")[0],
      platformVideoId,
      title,
      description,
      coverUrl: readMetaContent("og:image"),
      likeCount: parseCount(likeText),
      commentCount: parseCount(commentText),
      collectCount: parseCount(collectText),
    };
  }
}

export function createDouyinWebAdapter(): PlatformAdapter {
  return new DouyinWebAdapter();
}
