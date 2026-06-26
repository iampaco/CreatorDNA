import type {
  CreatorProfile,
  CreatorVideoMeta,
  PlatformId,
  PlatformPageDetection,
} from "@creator-dna/shared-types";

export interface PlatformAdapter {
  readonly platform: PlatformId;
  detectPage(): PlatformPageDetection;
  extractCreatorProfile(): Promise<CreatorProfile | null>;
  extractVideoList(limit: number): Promise<CreatorVideoMeta[]>;
  extractCurrentVideo(): Promise<CreatorVideoMeta | null>;
}
