import json
from pathlib import Path

with open('d:/vidclip/storage/all_uploaded_clips_analytics_latest.json', 'r', encoding='utf-8') as f:
    records = json.load(f)

md_path = Path('C:/Users/thega/.gemini/antigravity/brain/cc9214c0-7f61-456a-b5aa-8cae3dbac8e4/all_uploaded_clips_analytics_table.md')

lines = []
lines.append('# 📊 Performance Analytics for All Uploaded Clips (Tabular Report)')
lines.append('')
lines.append(f'- **Total Clips Analyzed**: **{len(records)}**')
lines.append(f'- **Total Views Generated**: **{sum(r["views"] for r in records):,}**')
lines.append(f'- **Total Likes**: **{sum(r["likes"] for r in records):,}**')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 🔥 1. Top Performing Viral Clips (500+ Views)')
lines.append('')
lines.append('| Rank | Views | Likes | Published (IST) | Batch | Title | Watch Link |')
lines.append('| :---: | :---: | :---: | :---: | :--- | :--- | :---: |')

viral = [r for r in records if r['views'] >= 500]
for idx, r in enumerate(viral, 1):
    lines.append(f'| **#{idx}** | **{r["views"]}** | **{r["likes"]}** | {r["published_ist"]} | `{r["batch"]}` | *{r["title"]}* | [Watch Short]({r["url"]}) |')

lines.append('')
lines.append('---')
lines.append('')
lines.append('## 🎬 2. Batch 1: Initial 1:30 PM Review Cuts (5 Clips)')
lines.append('')
lines.append('| Rank | Views | Likes | Published (IST) | Title | Watch Link |')
lines.append('| :---: | :---: | :---: | :---: | :--- | :---: |')
b1_initial = [r for r in records if r['batch'] == '1:30 PM Review Cuts']
b1_initial.sort(key=lambda x: x['views'], reverse=True)
for idx, r in enumerate(b1_initial, 1):
    lines.append(f'| #{idx} | **{r["views"]}** | {r["likes"]} | {r["published_ist"]} | *{r["title"]}* | [Watch Short]({r["url"]}) |')

lines.append('')
lines.append('---')
lines.append('')
lines.append('## 🚀 3. Batch 1: 5:00 PM IST 2K Cuts (40 Clips)')
lines.append('')
lines.append('| Rank | Views | Likes | Published (IST) | Title | Watch Link |')
lines.append('| :---: | :---: | :---: | :---: | :--- | :---: |')
b1_5pm = [r for r in records if r['batch'] == '5:00 PM 2K Batch (Batch 1)']
b1_5pm.sort(key=lambda x: x['views'], reverse=True)
for idx, r in enumerate(b1_5pm, 1):
    lines.append(f'| #{idx} | **{r["views"]}** | {r["likes"]} | {r["published_ist"]} | *{r["title"]}* | [Watch Short]({r["url"]}) |')

lines.append('')
lines.append('---')
lines.append('')
lines.append('## 🌊 4. Batch 2: 3-Minute Interval Wave Cuts (40 Clips across 8 Waves)')
lines.append('')
lines.append('| Rank | Views | Likes | Wave | Published (IST) | Title | Watch Link |')
lines.append('| :---: | :---: | :---: | :---: | :---: | :--- | :---: |')
b2_waves = [r for r in records if 'Batch 2' in r['batch']]
b2_waves.sort(key=lambda x: x['views'], reverse=True)
for idx, r in enumerate(b2_waves, 1):
    lines.append(f'| #{idx} | **{r["views"]}** | {r["likes"]} | `{r["batch"]}` | {r["published_ist"]} | *{r["title"]}* | [Watch Short]({r["url"]}) |')

lines.append('')
lines.append('---')
lines.append('')
lines.append('## 🇮🇳 5. Indian Creators Batch (Techno Gamerz & CarryMinati)')
lines.append('')
lines.append('| Rank | Views | Likes | Creator | Published (IST) | Title | Watch Link |')
lines.append('| :---: | :---: | :---: | :---: | :---: | :--- | :---: |')
b_ind = [r for r in records if 'Indian Creators' in r['batch']]
b_ind.sort(key=lambda x: x['views'], reverse=True)
for idx, r in enumerate(b_ind, 1):
    lines.append(f'| #{idx} | **{r["views"]}** | {r["likes"]} | `{r["batch"]}` | {r["published_ist"]} | *{r["title"]}* | [Watch Short]({r["url"]}) |')

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Artifact created successfully!')
