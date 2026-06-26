import type { PlatformAdapter } from "@creator-dna/platform-core";

import { createDouyinWebAdapter } from "./douyin-web.adapter";

export function getAdapterForHostname(hostname: string): PlatformAdapter | null {
  if (hostname.endsWith("douyin.com")) {
    return createDouyinWebAdapter();
  }
  return null;
}
