export type ApiErrorCode =
  | "unsupported_platform"
  | "no_videos_found"
  | "capture_denied"
  | "upload_failed"
  | "asr_failed"
  | "vision_failed"
  | "llm_parse_failed"
  | "rate_limited"
  | "unauthorized";

export interface ApiError {
  error: ApiErrorCode | string;
  message: string;
}
