# Secrets Management

All production secrets must live outside the repository.

## Required Secrets

| Variable | Used by | Notes |
|----------|---------|-------|
| `API_SECRET_KEY` | API, Extension | Bearer token for extension → API calls |
| `DATABASE_URL` | API, Workers | Postgres connection string with TLS in prod |
| `REDIS_URL` | API, Workers | Celery broker + rate limit + AI quota |
| `LLM_API_KEY` | Workers | Text LLM for video structure and creator report generation |
| `LLM_BASE_URL` | Workers | OpenAI-compatible LLM endpoint, e.g. DeepSeek |
| `LLM_CHAT_MODEL` | Workers | Text LLM model name |
| `OPENAI_API_KEY` | Workers | OpenAI ASR and optional OpenAI vision |
| `STORAGE_ACCESS_KEY` | API, Workers | R2/S3/MinIO |
| `STORAGE_SECRET_KEY` | API, Workers | R2/S3/MinIO |
| `SENTRY_DSN` | API, Workers | Error monitoring (staging/prod) |

## Local Development

1. Copy `.env.example` to `.env`
2. Leave `API_SECRET_KEY` unset for auth-free local dev (`ENVIRONMENT=local`)
3. Set `LLM_API_KEY` for real DeepSeek text analysis, or leave it unset to use dev mock text outputs
4. Set `OPENAI_API_KEY` for real ASR/vision, or leave it unset to use dev mocks for those steps

## Staging / Production

1. Set `ENVIRONMENT=staging` or `production`
2. Set `API_SECRET_KEY` to a strong random value (32+ chars)
3. Set `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_CHAT_MODEL`
4. Set `OPENAI_API_KEY` unless ASR/vision are intentionally replaced or disabled
5. Distribute the same API key to extension users via secure onboarding
6. Store secrets in your platform secret manager (Fly secrets, AWS SSM, etc.)
7. Never log `Authorization` headers or raw keys

## Rotation

1. Generate new `API_SECRET_KEY`
2. Deploy API with new key
3. Update extension storage / redeploy extension build with new key
4. Revoke old key after grace period

## Extension Key Storage

The extension stores `apiKey` in `chrome.storage.local` (device-local). Users enter the key once in the side panel **连接设置** section.

## Related

- [security.md](./security.md)
- [deployment.md](./deployment.md)
- [.env.example](../../.env.example)
