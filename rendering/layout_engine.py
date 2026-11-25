"""FFmpeg Filtergraph Layout Engine for Split-Screen 9:16 Video (2K / 1080p)."""

import os
from typing import Any, Dict, Optional


class LayoutEngine:
    """Builds FFmpeg filtergraphs for 2K (1440x2560) or 1080p (1080x1920) vertical split-screen rendering."""

    # Output resolution: 4K (2160x3840), 2K (1440x2560), or 1080p (1080x1920)
    RES_MODE = os.getenv("OUTPUT_RESOLUTION", "4K").upper()
    IS_4K = RES_MODE == "4K"
    IS_2K = RES_MODE == "2K"

    if IS_4K:
        CANVAS_WIDTH = 2160
        CANVAS_HEIGHT = 3840
        DIVIDER_HEIGHT = 10     # Sleek neon border divider
        FACECAM_HEIGHT = 1530   # ~40% of 3840
        GAMEPLAY_HEIGHT = 2300  # 2300 + 10 + 1530 = 3840 exact 4K canvas
    elif IS_2K:
        CANVAS_WIDTH = 1440
        CANVAS_HEIGHT = 2560
        DIVIDER_HEIGHT = 6      # Sleek neon border divider between windows
        FACECAM_HEIGHT = 1024   # 40% of 2560
        GAMEPLAY_HEIGHT = 1530  # 1530 + 6 + 1024 = 2560 exact canvas
    else:
        CANVAS_WIDTH = 1080
        CANVAS_HEIGHT = 1920
        DIVIDER_HEIGHT = 4
        FACECAM_HEIGHT = 768    # 40% of 1920
        GAMEPLAY_HEIGHT = 1148  # 1148 + 4 + 768 = 1920 exact canvas

    DIVIDER_COLOR = "0x00F0FF"  # High-energy electric cyan accent border

    @classmethod
    def generate_split_screen_filter(
        cls,
        crop_config: Dict[str, Any],
        ass_subtitle_path: Optional[str] = None,
    ) -> str:
        """Constructs an FFmpeg complex filter string.

        Layout:
        - Gameplay top ~60% (1440x1530 in 2K) with color pop
        - Electric divider bar (1440x6 in 2K)
        - Facecam bottom 40% (1440x1024 in 2K) with facial contrast enhancement
        - Stacked vertically to exact 9:16 (1440x2560)
        """
        fc = crop_config["facecam"]
        gp = crop_config["gameplay"]

        # 1. Facecam crop, scale, and color balance (bottom 40%)
        fc_filter = (
            f"[0:v]crop={fc['width']}:{fc['height']}:{fc['x']}:{fc['y']},"
            f"scale={cls.CANVAS_WIDTH}:{cls.FACECAM_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={cls.CANVAS_WIDTH}:{cls.FACECAM_HEIGHT},"
            f"eq=contrast=1.05:brightness=0.01:saturation=1.10[facecam]"
        )

        # 2. Gameplay crop, scale, and dynamic vibrance (top 60%)
        gp_filter = (
            f"[0:v]crop={gp['width']}:{gp['height']}:{gp['x']}:{gp['y']},"
            f"scale={cls.CANVAS_WIDTH}:{cls.GAMEPLAY_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={cls.CANVAS_WIDTH}:{cls.GAMEPLAY_HEIGHT},"
            f"eq=contrast=1.08:brightness=0.01:saturation=1.15[gameplay]"
        )

        # 3. High-energy neon divider line
        divider_filter = f"color=c={cls.DIVIDER_COLOR}:s={cls.CANVAS_WIDTH}x{cls.DIVIDER_HEIGHT}[divider]"

        # 4. Vertical 3-way stack: Gameplay on top, Divider in middle, Facecam on bottom
        stack_filter = f"[gameplay][divider][facecam]vstack=inputs=3[stacked]"

        filters = [fc_filter, gp_filter, divider_filter, stack_filter]

        # 4. Optional ASS subtitle overlay
        if ass_subtitle_path:
            clean_ass = ass_subtitle_path.replace("\\", "/").replace(":", "\\:")
            filters.append(f"[stacked]ass='{clean_ass}'[v_out]")
        else:
            filters.append("[stacked]null[v_out]")

        return ";".join(filters)
