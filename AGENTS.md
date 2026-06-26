# AGENTS.md

## Project Name

**CreatorDNA**

## Project Overview

CreatorDNA is a browser-extension-based creator intelligence system for short-video platforms such as Douyin Web, TikTok Web, YouTube Shorts, Bilibili, and other web-based video platforms.

The product helps users analyze a specific creator's publicly visible short videos and generate a structured report about the creator's:

- Content positioning
- Topic selection patterns
- Hook formulas
- Speaking style
- Video structure
- Shooting and editing style
- Subtitle and visual presentation style
- Reusable content templates
- High-performing video patterns

The project should be understood as a **creator style intelligence tool**, not as a video downloading, scraping, or content-copying tool.

The core principle is:

> Analyze publicly visible content that the user can already access in the browser, summarize structural patterns, and help users learn content strategy in an original and compliant way.

---

## Product Positioning

CreatorDNA is designed for:

- Individual creators who want to learn from successful short-video accounts
- MCN teams that need to analyze creator style and content strategy
- Brand teams that need to evaluate creator fit before collaboration
- Startup founders and marketers researching short-video distribution methods
- Content strategists studying topic, hook, script, and visual patterns

CreatorDNA should avoid presenting itself as a tool for copying another creator's exact content. The system should focus on extracting **structure, pattern, style, and method**, then helping users create original content.

Preferred product description:

> CreatorDNA analyzes publicly visible short-video content through a browser extension and AI pipeline, then summarizes a creator's content structure, speaking style, shooting method, and reusable creative patterns.

---

## Core User Flow

1. User opens a creator profile page on a supported video platform.
2. Browser extension detects the current platform and creator page.
3. Extension extracts visible public metadata, such as creator name, video links, titles, descriptions, covers, and interaction metrics if available.
4. User chooses a sample size, such as 10, 20, or 50 videos.
5. Extension starts an analysis task after explicit user action.
6. For each selected video, the system collects available text, audio, and visual information from the user's active browsing session.
7. Backend workers process audio, transcript, frames, metadata, and page context.
8. AI pipeline generates video-level structured analyses.
9. Aggregation layer generates creator-level style report.
10. User views the report in the extension side panel or web dashboard.
11. User can export the report as Markdown, PDF, or structured JSON.

---

## High-Level Architecture

```txt
Browser Extension
  ↓
Platform Adapter Layer
  ↓
API Gateway
  ↓
Task Queue
  ↓
AI Processing Workers
  ├── Metadata Pipeline
  ├── Audio / ASR Pipeline
  ├── Vision Pipeline
  ├── Video Structure Analysis Pipeline
  └── Creator Report Pipeline
  ↓
Database + Object Storage
  ↓
Web Dashboard / Extension Side Panel
```

The architecture should keep browser-side logic, backend orchestration, and AI workers clearly separated.

---

## Recommended Monorepo Structure

```txt
creator-dna/
├── apps/
│   ├── extension/
│   │   ├── entrypoints/
│   │   │   ├── content.ts
│   │   │   ├── background.ts
│   │   │   ├── popup/
│   │   │   ├── sidepanel/
│   │   │   └── offscreen/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── platform-adapters/
│   │   └── wxt.config.ts
│   │
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── styles/
│   │
│   └── api/
│       ├── main.py
│       ├── routers/
│       ├── services/
│       ├── schemas/
│       └── config/
│
├── workers/
│   ├── video_preprocess_worker.py
│   ├── asr_worker.py
│   ├── vision_worker.py
│   ├── style_analysis_worker.py
│   └── report_worker.py
│
├── packages/
│   ├── shared-types/
│   ├── prompts/
│   ├── ai-clients/
│   ├── platform-core/
│   └── utils/
│
├── infra/
│   ├── docker-compose.yml
│   ├── postgres/
│   ├── redis/
│   └── storage/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── ai-pipeline.md
│   └── compliance.md
│
├── AGENTS.md
├── README.md
├── package.json
└── pnpm-workspace.yaml
```

---

## Technology Stack

### Browser Extension

Use the following stack unless there is a strong reason to change it:

- **WXT** as the browser extension framework
- **React** for popup and side panel UI
- **TypeScript** for all extension code
- **Manifest V3** as the default Chrome extension target
- **Chrome Side Panel API** for report viewing when available
- **Chrome tabCapture API** for user-initiated tab media capture
- **Offscreen Document** for media recording tasks that cannot run directly inside the service worker

The extension must not silently record or capture browser content. Media capture must only happen after explicit user action.

### Web Dashboard

Recommended stack:

- **Next.js**
- **React**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** or a similarly clean component system
- **Markdown rendering** for reports
- Optional: **Tiptap** or **MDX editor** for editable reports

The web dashboard is optional for MVP. The side panel can be the first report UI.

### Backend API

Recommended stack:

- **FastAPI** for Python-based backend APIs
- **Pydantic** for schema validation
- **PostgreSQL** as primary relational database
- **SQLAlchemy** or **Prisma** depending on language choice
- **Redis** for caching and task queue coordination
- **Celery** or **BullMQ** for background jobs

If the team prefers a TypeScript backend, use:

- **Next.js API Routes** or **NestJS**
- **Prisma**
- **PostgreSQL**
- **Redis + BullMQ**

### AI / Media Processing

Core tools:

- **ffmpeg** for media preprocessing, audio extraction, frame extraction, duration detection, and format normalization
- **OpenAI Speech-to-Text**, **Whisper**, **faster-whisper**, or **WhisperX** for ASR
- **GPT-4o / GPT-5.5 Vision**, **Gemini Vision**, **Qwen-VL**, or **InternVL** for visual analysis
- **GPT-5.5**, **Claude**, **Gemini**, **DeepSeek**, or **Qwen** for text reasoning and report generation
- **PaddleOCR** or equivalent OCR model for low-cost subtitle extraction
- **pgvector** or **Qdrant** for optional embedding search and creator style comparison

### Storage

- **PostgreSQL** for structured data
- **Cloudflare R2**, **AWS S3**, or compatible object storage for temporary media, extracted audio, frames, and exported reports
- **Redis** for short-lived task state, progress updates, and caching

---

## Core Modules

### 1. Extension Content Script

Responsibilities:

- Detect the current platform and page type
- Identify creator profile pages and video pages
- Extract visible video links and metadata from DOM
- Listen for infinite-scroll updates with `MutationObserver`
- Send normalized data to background service worker

Do not hard-code fragile CSS class names as the only source of truth. Prefer a layered extraction strategy:

1. URL pattern recognition
2. Anchor link extraction
3. Semantic DOM text extraction
4. Platform-specific selectors as fallback
5. Manual user selection as last fallback

### 2. Extension Background Service Worker

Responsibilities:

- Manage extension state
- Coordinate between content script, side panel, popup, and offscreen document
- Start user-triggered analysis tasks
- Request tab capture stream ID when required
- Communicate with backend API
- Store lightweight local state in extension storage

The background worker should not contain heavy AI logic or media processing logic.

### 3. Offscreen Document

Responsibilities:

- Receive tab capture stream ID from background worker
- Use `navigator.mediaDevices.getUserMedia` when required
- Run `MediaRecorder`
- Chunk media data when possible
- Upload media blob to backend
- Stop recording safely when the user cancels or when the target duration is reached

Offscreen document must not be used for hidden or unauthorized capture.

### 4. Platform Adapter Layer

Create platform-specific adapters with a shared interface.

Example interface:

```ts
export interface PlatformAdapter {
  platform: string;
  detectPage(): PlatformPageDetection;
  extractCreatorProfile(): Promise<CreatorProfile | null>;
  extractVideoList(limit: number): Promise<CreatorVideoMeta[]>;
  extractCurrentVideo(): Promise<CreatorVideoMeta | null>;
}
```

Initial adapters:

- `douyin-web.adapter.ts`
- `tiktok-web.adapter.ts`
- `youtube-shorts.adapter.ts`
- `bilibili.adapter.ts`

The first MVP can focus on one platform only, but the architecture should support multiple adapters.

### 5. Backend API Gateway

Responsibilities:

- Accept analysis task creation requests
- Accept video or audio uploads
- Validate request schemas
- Store metadata in database
- Enqueue background jobs
- Provide task progress APIs
- Provide report retrieval APIs

### 6. Task Queue

Main job types:

```txt
ANALYZE_CREATOR
DISCOVER_VIDEOS
ANALYZE_VIDEO
EXTRACT_AUDIO
TRANSCRIBE_AUDIO
EXTRACT_FRAMES
ANALYZE_FRAMES
ANALYZE_VIDEO_STRUCTURE
GENERATE_CREATOR_REPORT
EXPORT_REPORT
```

Jobs should be idempotent where possible. Re-running a failed job should not duplicate database records.

### 7. AI Workers

Workers should be independent, observable, and replaceable.

Recommended workers:

- `video_preprocess_worker.py`
- `asr_worker.py`
- `vision_worker.py`
- `style_analysis_worker.py`
- `report_worker.py`

Each worker should:

- Accept a job payload
- Load required data from database or object storage
- Produce structured output
- Save results back to database
- Report progress and errors

---

## AI Pipeline Design

### Step 1: Metadata Extraction

Extract available public metadata:

- Platform
- Creator profile URL
- Creator display name
- Creator handle
- Video URL
- Video title
- Video description
- Cover image
- Like count
- Comment count
- Collect count
- Publish time
- Duration if available

### Step 2: Audio Processing

Use `ffmpeg` to normalize the audio:

```bash
ffmpeg -i input.webm -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

Then run ASR.

Expected transcript output:

```json
{
  "video_id": "video_001",
  "duration": 58.4,
  "language": "zh",
  "segments": [
    {
      "start": 0.0,
      "end": 3.2,
      "text": "很多人做内容最大的问题，不是不会拍，而是没有结构。"
    }
  ],
  "words": []
}
```

### Step 3: Speech Style Analysis

Compute or infer:

- Speaking speed
- Average sentence length
- Pause distribution
- Repeated phrases
- Hook sentence type
- Emotional tone
- Rhetorical style
- Teaching, storytelling, ranting, review, or documentary style

### Step 4: Visual Frame Extraction

Use sparse frame extraction:

```bash
ffmpeg -i input.webm -vf fps=1/3 frames/frame_%04d.jpg
```

For short videos, prioritize:

- First 0-5 seconds
- Middle section
- Final 3-5 seconds

### Step 5: Visual Understanding

Analyze extracted frames for:

- Main format: talking head, screen recording, vlog, mixed edit, product demo
- Camera angle
- Composition
- Background
- Subtitle visibility
- Subtitle position
- Subtitle style
- B-roll usage
- Visual density
- On-screen text
- Editing rhythm approximation

Expected frame-level output:

```json
{
  "frame_time": 3.0,
  "shot_type": "真人口播",
  "camera_angle": "正面",
  "composition": "半身近景",
  "background": "室内书桌",
  "subtitle_visible": true,
  "subtitle_position": "底部居中",
  "subtitle_style": "白色大字，黑色描边",
  "visual_elements": ["人物", "字幕", "桌面", "电脑"],
  "b_roll": false
}
```

### Step 6: Video-Level Structure Analysis

Each video should be converted into structured JSON before account-level aggregation.

Expected output:

```json
{
  "video_id": "video_001",
  "hook_type": "反常识开头",
  "hook_text": "很多人以为做内容靠灵感，其实靠结构。",
  "topic_category": "内容创作方法论",
  "target_audience": ["短视频创作者", "个人 IP", "创业者"],
  "content_structure": [
    {
      "part": "开头",
      "description": "提出常见误区并制造认知冲突"
    },
    {
      "part": "正文",
      "description": "解释爆款内容背后的结构规律"
    },
    {
      "part": "结尾",
      "description": "用一句方法论总结并引导关注"
    }
  ],
  "emotional_tone": "坚定、教学式、轻微制造焦虑",
  "common_phrases": ["本质上", "你会发现", "说白了"],
  "ending_type": "观点总结 + 关注引导",
  "shooting_style": "正面口播 + 大字幕",
  "reusable_template": "反常识判断 → 常见误区 → 方法解释 → 一句话总结"
}
```

### Step 7: Creator-Level Aggregation

Aggregate across multiple analyzed videos:

- Top topic categories
- Top hook types
- Common opening sentence patterns
- Average speech speed
- Common phrase library
- Common content structures
- Repeated visual style
- Subtitle style consistency
- High-performing video commonalities
- Low-performing video commonalities
- Reusable content templates

Do not directly send raw transcripts of dozens of videos to an LLM and ask for a summary. First produce video-level structured analysis, then aggregate statistics, then generate the final report.

### Step 8: Report Generation

The report should include:

1. Creator positioning
2. Target audience
3. Topic selection pattern
4. Title and hook formula
5. Video structure pattern
6. Speaking style
7. Shooting style
8. Subtitle and editing style
9. High-performing video pattern
10. Reusable content formula
11. Original script templates inspired by structure, not copied wording
12. Strategic recommendations

---

## Database Design

Use PostgreSQL with JSONB for flexible AI output.

### creators

```sql
CREATE TABLE creators (
  id UUID PRIMARY KEY,
  platform TEXT NOT NULL,
  platform_creator_id TEXT,
  username TEXT,
  display_name TEXT,
  profile_url TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### videos

```sql
CREATE TABLE videos (
  id UUID PRIMARY KEY,
  creator_id UUID REFERENCES creators(id),
  platform TEXT NOT NULL,
  platform_video_id TEXT,
  video_url TEXT NOT NULL,
  title TEXT,
  description TEXT,
  duration_seconds FLOAT,
  like_count INTEGER,
  comment_count INTEGER,
  collect_count INTEGER,
  publish_time TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### transcripts

```sql
CREATE TABLE transcripts (
  id UUID PRIMARY KEY,
  video_id UUID REFERENCES videos(id),
  language TEXT,
  full_text TEXT,
  segments JSONB,
  words JSONB,
  asr_model TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### visual_analyses

```sql
CREATE TABLE visual_analyses (
  id UUID PRIMARY KEY,
  video_id UUID REFERENCES videos(id),
  frames JSONB,
  summary JSONB,
  vision_model TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### video_style_analyses

```sql
CREATE TABLE video_style_analyses (
  id UUID PRIMARY KEY,
  video_id UUID REFERENCES videos(id),
  hook_type TEXT,
  topic_category TEXT,
  target_audience JSONB,
  content_structure JSONB,
  emotional_tone TEXT,
  common_phrases JSONB,
  ending_type TEXT,
  reusable_template TEXT,
  raw_analysis JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### creator_reports

```sql
CREATE TABLE creator_reports (
  id UUID PRIMARY KEY,
  creator_id UUID REFERENCES creators(id),
  sample_video_count INTEGER,
  report_markdown TEXT,
  report_json JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Design

### Create Creator Analysis Task

```http
POST /api/creator-analysis
```

Request:

```json
{
  "platform": "douyin",
  "creatorUrl": "https://www.douyin.com/user/example",
  "videoUrls": [
    "https://www.douyin.com/video/example_001",
    "https://www.douyin.com/video/example_002"
  ],
  "sampleSize": 20
}
```

Response:

```json
{
  "taskId": "task_123",
  "status": "queued"
}
```

### Upload Video Segment

```http
POST /api/videos/upload
```

Request:

```txt
multipart/form-data
file: video.webm
videoUrl: string
creatorId: string
```

Response:

```json
{
  "videoId": "video_123",
  "mediaUrl": "s3://bucket/video_123.webm",
  "status": "uploaded"
}
```

### Get Task Progress

```http
GET /api/tasks/:taskId
```

Response:

```json
{
  "taskId": "task_123",
  "status": "processing",
  "progress": 65,
  "currentStep": "Analyzing video frames",
  "finishedVideos": 13,
  "totalVideos": 20
}
```

### Get Creator Report

```http
GET /api/reports/:creatorId
```

Response:

```json
{
  "creatorId": "creator_123",
  "sampleVideoCount": 20,
  "reportMarkdown": "...",
  "reportJson": {
    "positioning": "AI 创业内容",
    "hookPatterns": [],
    "speechStyle": {},
    "shootingStyle": {},
    "reusableTemplates": []
  }
}
```

---

## Prompt Management

All prompts must be stored under:

```txt
packages/prompts/
```

Recommended files:

```txt
packages/prompts/
├── video-structure-analysis.md
├── frame-visual-analysis.md
├── creator-report-generation.md
├── script-template-generation.md
└── safety-rewrite.md
```

Prompts should request structured JSON where possible. Do not rely on unstructured prose for intermediate pipeline steps.

Final reports can be prose, but intermediate outputs should be typed and validated.

---

## Compliance and Safety Rules

This project must follow these constraints:

1. Do not bypass login, paywalls, privacy restrictions, DRM, or platform access controls.
2. Do not scrape private or non-public content.
3. Do not present the product as a video downloader.
4. Do not store full original videos longer than necessary for analysis.
5. Do not generate direct clones of a creator's exact scripts, catchphrases, or identity.
6. Do not encourage impersonation of specific creators.
7. Do not use hidden or silent recording.
8. Always require explicit user action before tab capture or media recording.
9. Prefer analyzing structure, style, and patterns over copying content.
10. Provide user-facing copy that frames output as learning and original creation support.

Recommended wording:

> CreatorDNA helps users understand public content patterns and generate original content strategies inspired by structural analysis.

Avoid wording such as:

> Copy this creator's exact style.

---

## Development Guidelines for AI Coding Agents

When modifying this project, follow these rules:

### General

- Keep modules small and composable.
- Prefer typed interfaces over loosely shaped objects.
- Do not mix extension UI logic with backend analysis logic.
- Do not hard-code platform-specific behavior in shared modules.
- Put platform-specific behavior in `platform-adapters`.
- Keep AI prompts versioned and easy to inspect.
- Validate all LLM JSON outputs before saving to database.
- Add graceful fallback behavior when page extraction fails.

### TypeScript

- Use strict TypeScript.
- Avoid `any` unless browser extension API typing makes it unavoidable.
- Define shared types in `packages/shared-types`.
- Use clear names for platform, creator, video, task, and report models.

### Python

- Use type hints.
- Use Pydantic models for request and worker payload schemas.
- Keep media processing functions deterministic and testable.
- Wrap external commands such as `ffmpeg` with proper error handling.
- Log processing duration and model used for each AI step.

### AI Output Handling

- Never trust raw LLM output directly.
- Parse, validate, and normalize JSON output.
- Store the model name, prompt version, and timestamp for each analysis.
- Keep raw analysis available for debugging, but expose cleaned report data to users.

### Error Handling

Every long-running job should handle:

- Unsupported platform
- No videos found
- Tab capture denied
- Media upload failure
- ASR failure
- Vision model failure
- LLM JSON parse failure
- Rate limit or quota error
- User cancellation

### Observability

Log at least:

- task_id
- creator_id
- video_id
- current step
- model provider
- processing duration
- error message
- retry count

---

## MVP Scope

The MVP should focus on one complete vertical slice:

1. Support one platform first, preferably Douyin Web or TikTok Web.
2. Detect creator profile page.
3. Extract visible video links and metadata.
4. Analyze one video through user-triggered tab capture.
5. Run ASR on captured audio.
6. Generate video-level structure analysis.
7. Display result in extension side panel.
8. Add creator-level aggregation only after single-video analysis works reliably.

Do not overbuild multi-platform support before the first end-to-end pipeline is stable.

---

## Future Roadmap

### Phase 1: Single Video Analysis

- Analyze current video page
- Capture 30-60 seconds of audio or video after user action
- Run ASR
- Generate hook, structure, and speaking style analysis
- Display result in side panel

### Phase 2: Creator Batch Analysis

- Detect creator profile
- Extract recent video list
- Analyze 10-20 videos
- Generate creator-level style report

### Phase 3: Visual Analysis

- Add frame extraction
- Analyze subtitle style, composition, shooting method, B-roll, and editing rhythm
- Merge visual analysis into video-level report

### Phase 4: Report and Export

- Add Markdown export
- Add PDF export
- Add JSON export for advanced users
- Add web dashboard

### Phase 5: Creator Intelligence Platform

- Multi-platform support
- Creator comparison
- Team workspace
- Brand-fit scoring
- Content opportunity discovery
- Original script generation based on structural templates

---

## Naming and Tone

Use the name **CreatorDNA** consistently in user-facing documentation unless the product name changes.

The tone should be:

- Technical
- Reliable
- Clean
- Serious
- Creator-friendly
- Compliance-aware

Avoid exaggerated marketing claims. The product should feel like an analytical infrastructure tool for creators, not a gimmick.

---

## Important Architectural Principle

Do not build the project as a fragile crawler.

Build it as:

> A browser-assisted, user-triggered, AI-powered analysis system for publicly visible short-video content.

The browser extension should observe and collect what the user can already see. The backend should transform that information into structured creator intelligence.
