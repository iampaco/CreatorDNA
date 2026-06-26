# Secrets Management

All production secrets must live outside the repository.

## Required Secrets

| Variable | Used by | Notes |
|----------|---------|-------|
| `API_SECRET_KEY` | API, Extension | Bearer token for extension → API calls |
| `DATABASE_URL` | API, Workers | Postgres connection string with TLS in prod |
| `REDIS_URL` | API, Workers | Celery broker + rate limit + AI quota |
| `OPENAI_API_KEY` | Workers | ASR + LLM + vision |
| `STORAGE_ACCESS_KEY` | API, Workers | R2/S3/MinIO |
| `STORAGE_SECRET_KEY` | API, Workers | R2/S3/MinIO |
| `SENTRY_DSN` | API, Workers | Error monitoring (staging/prod) |

## Local Development

1. Copy `.env.example` to `.env`
2. Leave `API_SECRET_KEY` unset for auth-free local dev (`ENVIRONMENT=local`)
3. Leave `OPENAI_API_KEY` unset to use dev mocks in workers

## Staging / Production

1. Set `ENVIRONMENT=staging` or `production`
2. Set `API_SECRET_KEY` to a strong random value (32+ chars)
3. Distribute the same key to extension users via secure onboarding
4. Store secrets in your platform secret manager (Fly secrets, AWS SSM, etc.)
5. Never log `Authorization` headers or raw keys

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
