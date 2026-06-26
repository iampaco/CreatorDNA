from workers.services.aggregation import aggregate_video_analyses


def test_aggregate_empty() -> None:
    result = aggregate_video_analyses([])
    assert result["sampleVideoCount"] == 0
    assert result["hookTypeDistribution"] == []


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
