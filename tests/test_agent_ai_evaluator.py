"""Tests for Antigravity Agent AI Evaluator."""

from ai.agent_evaluator import AgentEvaluator


def test_agent_evaluator():
    evaluator = AgentEvaluator()

    # Test short segment (< 30s) -> should be rejected
    res_short = evaluator.evaluate_segment("src_test", "seg_01", 0.0, 20.0)
    assert len(res_short) == 0

    # Test 60s segment -> should produce candidate with score >= 75 and 30-60s duration
    res = evaluator.evaluate_segment("src_test", "seg_02", 120.0, 60.0)
    assert len(res) == 1
    cand = res[0]

    assert cand["score"] >= 75
    assert cand["suggested_duration"] in [30, 45, 60]
    dur = cand["end_timestamp"] - cand["start_timestamp"]
    assert 30.0 <= dur <= 60.0
    assert len(cand["transcript"]) > 0
    assert len(cand["suggested_title"]) > 0
    assert cand["category"] in [
        "kills_eliminations", "clutch", "multi_kill", "unexpected_victory",
        "funny_gameplay", "funny_reaction", "high_skill_play", "impressive_movement",
        "rare_event", "exciting_fight", "unexpected_failure", "memorable_interaction",
        "dramatic_comeback", "unusual_moment", "engaging_gameplay"
    ]
