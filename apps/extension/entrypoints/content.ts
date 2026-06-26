export default defineContentScript({
  matches: ["*://*.douyin.com/*"],
  main() {
    console.log("[CreatorDNA] content script loaded");
    void browser.runtime.sendMessage({ type: "content:ping" }).catch(() => {
      // Background may not be ready yet.
    });
  },
});
