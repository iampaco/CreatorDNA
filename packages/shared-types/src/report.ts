export interface ReportJson {
  positioning: string;
  hookPatterns: unknown[];
  speechStyle: Record<string, unknown>;
  shootingStyle: Record<string, unknown>;
  reusableTemplates: unknown[];
  [key: string]: unknown;
}

export interface CreatorReport {
  creatorId: string;
  sampleVideoCount: number;
  reportMarkdown: string;
  reportJson: ReportJson;
}
