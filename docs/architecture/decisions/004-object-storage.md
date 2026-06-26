# ADR 004: Object Storage — MinIO (dev) / R2 or S3 (prod)

**Status:** Accepted  
**Date:** 2026-06-26  
**Deciders:** Engineering

## Context

Temporary media (captured webm, extracted audio, frame images) must be stored outside PostgreSQL. Compliance requires limited retention (delete after analysis TTL).

## Decision

| Environment | Storage |
|-------------|---------|
| Local / CI | **MinIO** in `infra/docker-compose.yml` (S3-compatible API) |
| Staging / Production | **Cloudflare R2** or **AWS S3** (S3-compatible SDK) |

- Single abstraction layer in API/workers using boto3 or compatible client
- Bucket paths: `media/{video_id}/`, `frames/{video_id}/`
- TTL cleanup job (P6-05) deletes objects after configurable retention

Environment variables (see `.env.example` at P6-06):

```txt
STORAGE_ENDPOINT=
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=
STORAGE_BUCKET=creator-dna
STORAGE_REGION=auto
```

## Consequences

**Positive**

- MinIO mirrors prod S3 API locally
- R2 offers lower egress cost vs. S3 for extension upload patterns
- Same code path across environments

**Negative**

- Must implement and test TTL cleanup for compliance
- Credential rotation required in production

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| Local filesystem only | Breaks multi-worker / multi-instance deployment |
| Postgres bytea | Poor fit for large blobs; backup bloat |
| R2 only everywhere | MinIO simplifies local dev without cloud dependency |

## References

- [deployment.md](../../operations/deployment.md)
- [security.md](../../operations/security.md)
- [compliance.md](../../compliance/compliance.md)
