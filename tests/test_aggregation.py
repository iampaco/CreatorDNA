from workers.services.aggregation import aggregate_video_analyses


def test_aggregate_empty() -> None:
    result = aggregate_video_analyses([])
    assert result["sampleVideoCount"] == 0
    assert result["hookTypeDistribution"] == []
    assert result["subtitlePositionDistribution"] == []


def test_aggregate_hook_distribution() -> None:
    analyses = [
        {"hookType": "反常识开头", "topicCategory": "创业", "commonPhrases": ["本质上"]},
        {"hookType": "反常识开头", "topicCategory": "内容创作", "commonPhrases": ["你会发现"]},
        {"hookType": "提问开头", "topicCategory": "创业", "commonPhrases": ["本质上"]},
    ]
    result = aggregate_video_analyses(analyses)
    assert result["sampleVideoCount"] == 3
    assert result["hookTypeDistribution"][0]["value"] == "反常识开头"
    assert result["hookTypeDistribution"][0]["count"] == 2
    assert result["topicCategoryDistribution"][0]["count"] == 2
    phrases = {p["value"]: p["count"] for p in result["commonPhrases"]}
    assert phrases["本质上"] == 2


def test_aggregate_visual_patterns() -> None:
    analyses = [
        {
            "hookType": "反常识开头",
            "dominantSubtitlePosition": "底部居中",
            "dominantSubtitleStyle": "白色大字",
            "dominantShotType": "真人口播",
            "subtitleConsistency": "全程一致",
            "bRollUsage": "无B-roll",
        },
        {
            "hookType": "反常识开头",
            "dominantSubtitlePosition": "底部居中",
            "dominantSubtitleStyle": "白色大字",
            "dominantShotType": "真人口播",
            "subtitleConsistency": "全程一致",
            "bRollUsage": "少量穿插",
        },
        {
            "hookType": "提问开头",
            "dominantSubtitlePosition": "顶部",
            "dominantSubtitleStyle": "黄色描边",
            "dominantShotType": "混剪",
            "subtitleConsistency": "部分出现",
            "bRollUsage": "频繁切换",
        },
    ]
    result = aggregate_video_analyses(analyses)
    assert result["subtitlePositionDistribution"][0]["value"] == "底部居中"
    assert result["subtitlePositionDistribution"][0]["count"] == 2
    assert result["shotTypeDistribution"][0]["value"] == "真人口播"
    assert result["shotTypeDistribution"][0]["count"] == 2
