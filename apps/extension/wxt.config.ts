import { defineConfig } from "wxt";

export default defineConfig({
  manifest: {
    name: "CreatorDNA",
    description: "Creator style intelligence for Douyin Web",
    permissions: ["sidePanel", "tabCapture", "storage", "offscreen"],
    host_permissions: ["*://*.douyin.com/*"],
    side_panel: {
      default_path: "sidepanel.html",
    },
  },
});
