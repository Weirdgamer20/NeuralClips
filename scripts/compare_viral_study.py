"""Perform statistical analysis and comparison across:
1) 100 GTA 6 Clips (100k - 1M views)
2) 100 GTA 6 Clips (1M+ views)
3) Our 101 Published NeuralClips Shorts
"""

import json
import os
import re
import statistics
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIRAL_DATASET = os.path.join(BASE_DIR, "storage", "gta6_viral_dataset.json")
OUR_DATASET = os.path.join(BASE_DIR, "storage", "our_100_shorts_analysis.json")
REPORT_OUTPUT = os.path.join(BASE_DIR, "storage", "viral_comparison_report.json")

HOOK_PATTERNS = [
    r"\b(wait|wait for it)\b",
    r"\b(bro|he|she|they)\b",
    r"\b(no way|actually|literally)\b",
    r"\b(police|cops|wanted)\b",
    r"\b(physics|realism|details|graphics)\b",
    r"\b(secret|easter egg|hidden)\b",
    r"\b(fail|clutch|insane|crazy)\b",
    r"\b(lucia|jason)\b",
    r"\b(vs|compared to)\b",
    r"\b(gta 5|gta v|fivem)\b",
]

def analyze_group(clips: list) -> dict:
    durations = [c["duration"] for c in clips if c.get("duration") and c["duration"] > 0]
    views = [c["views"] for c in clips if c.get("views")]
    title_lengths = [len(c["title"]) for c in clips if c.get("title")]
    word_counts = [len(c["title"].split()) for c in clips if c.get("title")]

    emojis_found = []
    caps_words = []
    question_marks = 0
    exclamation_marks = 0
    hook_matches = Counter()

    for c in clips:
        t = c.get("title", "")
        # Find emojis
        found = re.findall(r"[\U00010000-\U0010ffff]", t)
        emojis_found.extend(found)
        if "?" in t:
            question_marks += 1
        if "!" in t:
            exclamation_marks += 1
        words = t.split()
        for w in words:
            clean_w = re.sub(r"[^\w]", "", w)
            if clean_w.isupper() and len(clean_w) > 1 and clean_w != "GTA":
                caps_words.append(clean_w)
        for pat in HOOK_PATTERNS:
            if re.search(pat, t, re.IGNORECASE):
                hook_matches[pat] += 1

    return {
        "count": len(clips),
        "views_mean": round(statistics.mean(views), 0) if views else 0,
        "views_median": round(statistics.median(views), 0) if views else 0,
        "views_min": min(views) if views else 0,
        "views_max": max(views) if views else 0,
        "duration_mean": round(statistics.mean(durations), 1) if durations else 0,
        "duration_median": round(statistics.median(durations), 1) if durations else 0,
        "duration_distribution": {
            "under_15s": len([d for d in durations if d < 15]),
            "15s_to_30s": len([d for d in durations if 15 <= d <= 30]),
            "30s_to_45s": len([d for d in durations if 30 < d <= 45]),
            "over_45s": len([d for d in durations if d > 45]),
        },
        "title_length_mean": round(statistics.mean(title_lengths), 1) if title_lengths else 0,
        "title_length_median": round(statistics.median(title_lengths), 1) if title_lengths else 0,
        "word_count_mean": round(statistics.mean(word_counts), 1) if word_counts else 0,
        "emoji_frequency_pct": round(len([c for c in clips if re.search(r'[\U00010000-\U0010ffff]', c.get('title', ''))]) / len(clips) * 100, 1) if clips else 0,
        "top_emojis": Counter(emojis_found).most_common(8),
        "caps_word_frequency": len(caps_words),
        "question_mark_pct": round(question_marks / len(clips) * 100, 1) if clips else 0,
        "exclamation_pct": round(exclamation_marks / len(clips) * 100, 1) if clips else 0,
        "hook_patterns": dict(hook_matches),
        "sample_top_titles": [c["title"] for c in sorted(clips, key=lambda x: x.get("views", 0), reverse=True)[:10]],
    }

def main():
    with open(VIRAL_DATASET, "r", encoding="utf-8") as f:
        viral = json.load(f)

    with open(OUR_DATASET, "r", encoding="utf-8") as f:
        ours = json.load(f)

    c_100k = viral["clips_100k_to_1m"]
    c_1m = viral["clips_1m_plus"]
    c_ours = ours["clips"]
    # Normalize our clips fields
    for o in c_ours:
        o["views"] = 100 # baseline
        o["duration"] = o.get("duration", 30.0)

    analysis_100k = analyze_group(c_100k)
    analysis_1m = analyze_group(c_1m)
    analysis_ours = analyze_group(c_ours)

    report = {
        "group_100k_to_1m": analysis_100k,
        "group_1m_plus": analysis_1m,
        "group_ours": analysis_ours,
    }

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to {REPORT_OUTPUT}")
    print("\n=== COMPARISON SUMMARY ===")
    print(f"100k-1M Avg Duration: {analysis_100k['duration_mean']}s | Median: {analysis_100k['duration_median']}s")
    print(f"1M+ Avg Duration:     {analysis_1m['duration_mean']}s | Median: {analysis_1m['duration_median']}s")
    print(f"Our Avg Duration:     {analysis_ours['duration_mean']}s | Median: {analysis_ours['duration_median']}s")
    print(f"100k-1M Title Length: {analysis_100k['title_length_mean']} chars")
    print(f"1M+ Title Length:     {analysis_1m['title_length_mean']} chars")
    print(f"Our Title Length:     {analysis_ours['title_length_mean']} chars")
    print(f"1M+ Top Emojis:       {analysis_1m['top_emojis']}")
    print(f"1M+ Top Hooks:        {analysis_1m['hook_patterns']}")

if __name__ == "__main__":
    main()
