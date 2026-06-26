import { getAdapterForHostname } from "../platform-adapters";

const CREATOR_VIDEO_LIMIT = 50;

export default defineContentScript({
  matches: ["*://*.douyin.com/*"],
  main() {
    const adapter = getAdapterForHostname(window.location.hostname);
    if (!adapter) return;

    let creatorRefreshTimer: ReturnType<typeof setTimeout> | undefined;

    const publishPageState = async () => {
      const detection = adapter.detectPage();
      const videoMeta =
        detection.pageType === "video" ? await adapter.extractCurrentVideo() : null;
      const creatorProfile =
        detection.pageType === "creator" ? await adapter.extractCreatorProfile() : null;
      const videoList =
        detection.pageType === "creator"
          ? await adapter.extractVideoList(CREATOR_VIDEO_LIMIT)
          : null;

      void browser.runtime
        .sendMessage({
          type: "content:page-update",
          detection,
          videoMeta,
          creatorProfile,
          videoList,
        })
        .catch(() => {
          // Background may not be ready yet.
        });
    };

    const scheduleCreatorRefresh = () => {
      if (creatorRefreshTimer) clearTimeout(creatorRefreshTimer);
      creatorRefreshTimer = setTimeout(() => {
        void publishPageState();
      }, 500);
    };

    void publishPageState();

    const observer = new MutationObserver(() => {
      const detection = adapter.detectPage();
      if (detection.pageType === "creator") {
        scheduleCreatorRefresh();
      } else {
        void publishPageState();
      }
    });
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    window.addEventListener("popstate", () => {
      void publishPageState();
    });

    browser.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (message?.type === "content:extract-videos") {
        void (async () => {
          const limit = typeof message.limit === "number" ? message.limit : 10;
          const videos = await adapter.extractVideoList(limit);
          return { ok: true, videos };
        })().then(sendResponse);
        return true;
      }
      return undefined;
    });
  },
});
