export type PlatformId = "douyin" | string;

export type PageType = "video" | "creator" | "unknown";

export interface PlatformPageDetection {
  platform: PlatformId;
  pageType: PageType;
  url: string;
}

export interface CreatorProfile {
  platform: string;
  displayName?: string;
  username?: string;
  profileUrl: string;
  avatarUrl?: string;
}

export interface CreatorVideoMeta {
  platform: string;
  videoUrl: string;
  platformVideoId?: string;
  title?: string;
  description?: string;
  coverUrl?: string;
  likeCount?: number;
  commentCount?: number;
  collectCount?: number;
  publishTime?: string;
  durationSeconds?: number;
}
