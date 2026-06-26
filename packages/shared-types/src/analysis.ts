export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface Transcript {
  videoId: string;
  language: string;
  fullText: string;
  segments: TranscriptSegment[];
  words: unknown[];
  asrModel: string;
}

export interface ContentStructurePart {
  part: string;
  description: string;
}

export interface VideoStyleAnalysis {
  videoId?: string;
  hookType: string;
  hookText: string;
  topicCategory: string;
  targetAudience: string[];
  contentStructure: ContentStructurePart[];
  emotionalTone: string;
  commonPhrases: string[];
  endingType: string;
  shootingStyle: string;
  reusableTemplate: string;
  subtitlePosition?: string;
  subtitleStyle?: string;
  subtitleConsistency?: string;
}

export interface FrameAnalysis {
  frameTime: number;
  shotType?: string;
  cameraAngle?: string;
  composition?: string;
  background?: string;
  subtitleVisible?: boolean;
  subtitlePosition?: string;
  subtitleStyle?: string;
  visualElements?: string[];
  bRoll?: boolean;
}

export interface VisualAnalysis {
  videoId?: string;
  frames: FrameAnalysis[];
  summary: Record<string, unknown>;
  visionModel: string;
}
