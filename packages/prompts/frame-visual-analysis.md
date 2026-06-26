# Frame Visual Analysis

> Placeholder — full prompt content in Phase 3 (P3-02).

Analyze extracted video frames. Return **structured JSON only**.

## Per-frame fields

| Field | Type |
|-------|------|
| `frameTime` | number |
| `shotType` | string |
| `cameraAngle` | string |
| `composition` | string |
| `background` | string |
| `subtitleVisible` | boolean |
| `subtitlePosition` | string |
| `subtitleStyle` | string |
| `visualElements` | string[] |
| `bRoll` | boolean |

## Summary rollup

Aggregate shooting format, subtitle patterns, and visual density into a `summary` object.

See [AGENTS.md](../../AGENTS.md) for example frame JSON.
