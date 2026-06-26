import { getAdapterForHostname } from "../platform-adapters";

export default defineContentScript({
  matches: ["*://*.douyin.com/*"],
  main() {
    const adapter = getAdapterForHostname(window.location.hostname);
    if (!adapter) return;

    const publishPageState = async () => {
      const detection = adapter.detectPage();
      const videoMeta =
        detection.pageType === "video" ? await adapter.extractCurrentVideo() : null;

      void browser.runtime
        .sendMessage({
          type: "content:page-update",
          detection,
          videoMeta,
        })
        .catch(() => {
          // Background may not be ready yet.
        });
    };

    void publishPageState();

    const observer = new MutationObserver(() => {
      void publishPageState();
    });
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    window.addEventListener("popstate", () => {
      void publishPageState();
    });
  },
});
