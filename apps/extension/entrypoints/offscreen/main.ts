import "./style.css";

import type { ExtensionMessage } from "../../lib/messages";

let mediaRecorder: MediaRecorder | undefined;
let captureStream: MediaStream | undefined;
let stopTimer: ReturnType<typeof setTimeout> | undefined;
const chunks: BlobPart[] = [];

function cleanupCapture(): void {
  if (stopTimer) {
    clearTimeout(stopTimer);
    stopTimer = undefined;
  }
  mediaRecorder?.stop();
  mediaRecorder = undefined;
  captureStream?.getTracks().forEach((track) => track.stop());
  captureStream = undefined;
  chunks.length = 0;
}

async function startCapture(streamId: string, maxDurationMs: number): Promise<void> {
  cleanupCapture();

  captureStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      mandatory: {
        chromeMediaSource: "tab",
        chromeMediaSourceId: streamId,
      },
    } as MediaTrackConstraints,
    video: {
      mandatory: {
        chromeMediaSource: "tab",
        chromeMediaSourceId: streamId,
      },
    } as MediaTrackConstraints,
  });

  mediaRecorder = new MediaRecorder(captureStream, {
    mimeType: MediaRecorder.isTypeSupported("video/webm;codecs=vp9,opus")
      ? "video/webm;codecs=vp9,opus"
      : "video/webm",
  });

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) chunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: mediaRecorder?.mimeType || "video/webm" });
    const mimeType = blob.type;
    cleanupCapture();
    const reader = new FileReader();
    reader.onload = () => {
      void browser.runtime
        .sendMessage({
          type: "offscreen:capture-complete",
          data: reader.result as ArrayBuffer,
          mimeType,
          durationMs: maxDurationMs,
        } satisfies ExtensionMessage)
        .catch(() => undefined);
    };
    reader.readAsArrayBuffer(blob);
  };

  mediaRecorder.onerror = () => {
    void browser.runtime.sendMessage({
      type: "offscreen:capture-error",
      code: "capture_denied",
      message: "MediaRecorder failed",
    } satisfies ExtensionMessage);
    cleanupCapture();
  };

  mediaRecorder.start(1_000);
  stopTimer = setTimeout(() => {
    if (mediaRecorder?.state === "recording") {
      mediaRecorder.stop();
    }
  }, maxDurationMs);
}

browser.runtime.onMessage.addListener((message: ExtensionMessage) => {
  if (message.type === "offscreen:start-capture") {
    void startCapture(message.streamId, message.maxDurationMs).catch((error: unknown) => {
      void browser.runtime.sendMessage({
        type: "offscreen:capture-error",
        code: "capture_denied",
        message: error instanceof Error ? error.message : "Capture failed",
      } satisfies ExtensionMessage);
      cleanupCapture();
    });
    return true;
  }

  if (message.type === "offscreen:stop-capture") {
    if (mediaRecorder?.state === "recording") {
      mediaRecorder.stop();
    }
    return true;
  }

  return false;
});
