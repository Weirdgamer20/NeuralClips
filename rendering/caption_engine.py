"""Animated ASS Subtitle Generator for Vertical Gaming Videos."""

import os
from typing import Any, Dict, List, Optional


def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp format: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


class CaptionEngine:
    """Generates Advanced SubStation Alpha (.ass) files with word-level animated styling."""

    def __init__(
        self,
        font_family: str = "Arial Black",
        font_size: int = 24,
        primary_color: str = "&H00FFFFFF",     # White
        highlight_color: str = "&H0000FFFF",   # Vibrant Yellow
        outline_color: str = "&H00000000",     # Black outline
        outline_width: int = 5,
        margin_bottom: int = 340,
    ):
        self.font_family = font_family
        self.font_size = font_size
        self.primary_color = primary_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.margin_bottom = margin_bottom

    def generate_ass_script(
        self,
        timed_words: List[Dict[str, Any]],
        output_path: str,
        words_per_line: int = 4,
    ) -> str:
        """Writes an ASS subtitle file with animated word emphasis tags."""
        header = f"""[Script Info]
Title: NeuralClips Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1440
PlayResY: 2560

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.font_family},{self.font_size},{self.primary_color},{self.highlight_color},{self.outline_color},&H80000000,1,0,0,0,100,100,0,0,1,{self.outline_width},2,2,40,40,{self.margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []

        # Group words into short readable phrases
        chunks = [timed_words[i:i + words_per_line] for i in range(0, len(timed_words), words_per_line)]

        for chunk in chunks:
            if not chunk:
                continue
            line_start = chunk[0]["start"]
            line_end = chunk[-1]["end"]

            # For each word in this chunk, create a dialogue line with that word highlighted
            for i, target_word in enumerate(chunk):
                w_start = format_ass_time(target_word["start"])
                w_end = format_ass_time(target_word["end"])

                # Build line where the active word is enlarged and colored yellow
                styled_parts = []
                for j, w in enumerate(chunk):
                    if j == i:
                        styled_parts.append(f"{{\\c{self.highlight_color}\\fscx115\\fscy115}}{w['word']}{{\\r}}")
                    else:
                        styled_parts.append(f"{{\\c{self.primary_color}}}{w['word']}{{\\r}}")

                line_text = " ".join(styled_parts)
                events.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{line_text}")

        full_content = header + "\n".join(events) + "\n"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        return output_path
