import type { AnalysisSession } from "./messages";

const STORAGE_KEY = "analysisSession";

export function createEmptySession(): AnalysisSession {
  return {
    state: "idle",
    updatedAt: new Date().toISOString(),
  };
}

export async function loadSession(): Promise<AnalysisSession> {
  const stored = await browser.storage.local.get(STORAGE_KEY);
  return (stored[STORAGE_KEY] as AnalysisSession | undefined) ?? createEmptySession();
}

export async function saveSession(session: AnalysisSession): Promise<void> {
  await browser.storage.local.set({
    [STORAGE_KEY]: {
      ...session,
      updatedAt: new Date().toISOString(),
    },
  });
}

export async function patchSession(patch: Partial<AnalysisSession>): Promise<AnalysisSession> {
  const current = await loadSession();
  const next = { ...current, ...patch, updatedAt: new Date().toISOString() };
  await saveSession(next);
  return next;
}
