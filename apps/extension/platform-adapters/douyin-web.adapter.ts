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

    return {
      platform: this.platform,
      displayName:
        readMetaContent("og:title") ||
        readText(["[data-e2e='user-title']", "h1", ".user-title"]),
      username,
      profileUrl: detection.url.split("?")[0],
      avatarUrl: readMetaContent("og:image"),
    };
  }

  async extractVideoList(limit: number): Promise<CreatorVideoMeta[]> {
    const detection = this.detectPage();
    if (detection.pageType !== "creator") return [];

    const anchors = Array.from(document.querySelectorAll<HTMLAnchorElement>("a[href*='/video/']"));
    const seen = new Set<string>();
    const videos: CreatorVideoMeta[] = [];

    for (const anchor of anchors) {
      const href = anchor.href;
      const match = href.match(VIDEO_PATH);
      if (!match || seen.has(match[1])) continue;
      seen.add(match[1]);

      videos.push({
        platform: this.platform,
        videoUrl: href.split("?")[0],
        platformVideoId: match[1],
        title: anchor.getAttribute("title") || anchor.textContent?.trim() || undefined,
      });

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
