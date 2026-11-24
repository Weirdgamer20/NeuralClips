import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = Path("d:/vidclip/storage/review_cuts")

# Test Techno Gamerz (Facecam at x:0, y:760, w:380, h:320 -> bottom 40%; Gameplay center -> top 60%)
# In 1920x1080 input:
# Gameplay: crop 608:1080:656:0 -> scale to 1080:1152
# Facecam: crop 360:300:20:760 -> scale to 1080:768
# vstack the two!
cmd_techno = [
    ffmpeg, "-y",
    "-ss", "70",
    "-i", "d:/vidclip/storage/review_cuts/indian_techno_gamerz.mp4",
    "-t", "5",
    "-filter_complex",
    "[0:v]crop=800:1080:560:0,scale=1080:1152:flags=lanczos[top];"
    "[0:v]crop=380:300:0:780,scale=1080:768:flags=lanczos[bot];"
    "[top][bot]vstack[v]",
    "-map", "[v]",
    "-map", "0:a?",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-avoid_negative_ts", "make_zero", "-async", "1",
    "d:/vidclip/storage/review_cuts/test_techno_stack.mp4"
]

print("Rendering Techno test clip...")
subprocess.run(cmd_techno, check=True)
print("Techno test rendered!")

# Test CarryMinati (Facecam at x:0, y:620, w:360, h:380)
cmd_carry = [
    ffmpeg, "-y",
    "-ss", "50",
    "-i", "d:/vidclip/storage/review_cuts/indian_carryminati.mp4",
    "-t", "5",
    "-filter_complex",
    "[0:v]crop=800:1080:560:0,scale=1080:1152:flags=lanczos[top];"
    "[0:v]crop=360:360:0:640,scale=1080:768:flags=lanczos[bot];"
    "[top][bot]vstack[v]",
    "-map", "[v]",
    "-map", "0:a?",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-avoid_negative_ts", "make_zero", "-async", "1",
    "d:/vidclip/storage/review_cuts/test_carry_stack.mp4"
]

print("Rendering CarryMinati test clip...")
subprocess.run(cmd_carry, check=True)
print("Carry test rendered!")

# Test Triggered Insaan (Facecam at top-left x:0, y:0, w:360, h:280)
cmd_triggered = [
    ffmpeg, "-y",
    "-ss", "80",
    "-i", "d:/vidclip/storage/review_cuts/indian_triggered_insaan.mp4",
    "-t", "5",
    "-filter_complex",
    "[0:v]crop=800:1080:560:0,scale=1080:1152:flags=lanczos[top];"
    "[0:v]crop=360:280:0:0,scale=1080:768:flags=lanczos[bot];"
    "[top][bot]vstack[v]",
    "-map", "[v]",
    "-map", "0:a?",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-avoid_negative_ts", "make_zero", "-async", "1",
    "d:/vidclip/storage/review_cuts/test_triggered_stack.mp4"
]

print("Rendering Triggered Insaan test clip...")
subprocess.run(cmd_triggered, check=True)
print("Triggered test rendered!")
