"""Aggregate video-level structured analyses into creator-level statistics."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _counter_to_ranked(counter: Counter[str], limit: int = 10) -> list[dict[str, Any]]:
    return [{"value": key, "count": count} for key, count in counter.most_common(limit)]


def aggregate_video_analyses(analyses: list[dict[str, Any]]) -> dict[str, Any]:
    """Build statistics from video-level style + visual analyses — no raw transcripts."""
    if not analyses:
        return {
            "sampleVideoCount": 0,
            "hookTypeDistribution": [],
            "topicCategoryDistribution": [],
            "endingTypeDistribution": [],
            "emotionalToneDistribution": [],
            "shootingStyleDistribution": [],
            "shotTypeDistribution": [],
            "subtitlePositionDistribution": [],
            "subtitleStyleDistribution": [],
            "subtitleConsistencyDistribution": [],
            "bRollUsageDistribution": [],
            "visualDensityDistribution": [],
            "commonPhrases": [],
            "reusableTemplates": [],
            "targetAudience": [],
            "contentStructurePatterns": [],
            "videoSummaries": [],
        }

    hook_types: Counter[str] = Counter()
    topics: Counter[str] = Counter()
    endings: Counter[str] = Counter()
    tones: Counter[str] = Counter()
    shooting: Counter[str] = Counter()
    shot_types: Counter[str] = Counter()
    subtitle_positions: Counter[str] = Counter()
    subtitle_styles: Counter[str] = Counter()
    subtitle_consistency: Counter[str] = Counter()
    b_roll_usage: Counter[str] = Counter()
    visual_density: Counter[str] = Counter()
    phrases: Counter[str] = Counter()
    templates: Counter[str] = Counter()
    audiences: Counter[str] = Counter()
    structure_parts: Counter[str] = Counter()
    summaries: list[dict[str, str]] = []

    for item in analyses:
        if hook := item.get("hookType"):
            hook_types[str(hook)] += 1
        if topic := item.get("topicCategory"):
            topics[str(topic)] += 1
        if ending := item.get("endingType"):
            endings[str(ending)] += 1
        if tone := item.get("emotionalTone"):
            tones[str(tone)] += 1
        if style := item.get("shootingStyle"):
            shooting[str(style)] += 1
        if template := item.get("reusableTemplate"):
            templates[str(template)] += 1
        if shot := item.get("dominantShotType"):
            shot_types[str(shot)] += 1
        if position := item.get("dominantSubtitlePosition"):
            subtitle_positions[str(position)] += 1
        if sub_style := item.get("dominantSubtitleStyle"):
            subtitle_styles[str(sub_style)] += 1
        if consistency := item.get("subtitleConsistency"):
            subtitle_consistency[str(consistency)] += 1
        if b_roll := item.get("bRollUsage"):
            b_roll_usage[str(b_roll)] += 1
        if density := item.get("visualDensity"):
            visual_density[str(density)] += 1

        for phrase in item.get("commonPhrases") or []:
            if phrase:
                phrases[str(phrase)] += 1
        for audience in item.get("targetAudience") or []:
            if audience:
                audiences[str(audience)] += 1
        for part in item.get("contentStructure") or []:
            if isinstance(part, dict) and part.get("part"):
                structure_parts[str(part["part"])] += 1

        summaries.append(
            {
                "hookType": str(item.get("hookType") or ""),
                "hookText": str(item.get("hookText") or "")[:80],
                "topicCategory": str(item.get("topicCategory") or ""),
                "reusableTemplate": str(item.get("reusableTemplate") or "")[:120],
                "shootingStyle": str(item.get("shootingStyle") or "")[:80],
                "subtitlePosition": str(item.get("dominantSubtitlePosition") or ""),
            }
        )

    return {
        "sampleVideoCount": len(analyses),
        "hookTypeDistribution": _counter_to_ranked(hook_types),
        "topicCategoryDistribution": _counter_to_ranked(topics),
        "endingTypeDistribution": _counter_to_ranked(endings),
        "emotionalToneDistribution": _counter_to_ranked(tones),
        "shootingStyleDistribution": _counter_to_ranked(shooting),
        "shotTypeDistribution": _counter_to_ranked(shot_types),
        "subtitlePositionDistribution": _counter_to_ranked(subtitle_positions),
        "subtitleStyleDistribution": _counter_to_ranked(subtitle_styles),
        "subtitleConsistencyDistribution": _counter_to_ranked(subtitle_consistency),
        "bRollUsageDistribution": _counter_to_ranked(b_roll_usage),
        "visualDensityDistribution": _counter_to_ranked(visual_density),
        "commonPhrases": _counter_to_ranked(phrases, 20),
        "reusableTemplates": _counter_to_ranked(templates, 10),
        "targetAudience": _counter_to_ranked(audiences, 15),
        "contentStructurePatterns": _counter_to_ranked(structure_parts),
        "videoSummaries": summaries,
    }
