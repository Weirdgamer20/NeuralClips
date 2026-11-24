import yt_dlp

ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    res = ydl.extract_info("ytsearch8:GTA 6 4K 60FPS gameplay stunts explosions", download=False)
    for e in res.get("entries", []):
        dur = e.get("duration") or 0
        if 180 <= dur <= 1200:
            print(f"{e.get('id')} | {dur}s | {e.get('title')}")
