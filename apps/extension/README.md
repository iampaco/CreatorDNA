# CreatorDNA Extension

WXT + TypeScript Chrome extension (Manifest V3) for Douyin Web.

## Scripts

```bash
pnpm dev    # from apps/extension or: pnpm --filter extension dev
pnpm build  # production build
```

## Load in Chrome

After `pnpm build` or `pnpm dev`:

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. **Load unpacked** → select `.output/chrome-mv3` in this directory

## Entrypoints (Phase 0 stubs)

| Entry | Purpose |
|-------|---------|
| `content.ts` | Content script on `*.douyin.com` |
| `background.ts` | Service worker orchestration |
| `popup.html` | Toolbar popup |
| `sidepanel.html` | Side panel report UI |
| `offscreen/main.ts` | Offscreen document stub |
