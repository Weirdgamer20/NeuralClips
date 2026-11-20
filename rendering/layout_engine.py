"""FFmpeg Filtergraph Layout Engine for Split-Screen 9:16 Video (2K / 1080p)."""

import os
from typing import Any, Dict, Optional


class LayoutEngine:
    """Builds FFmpeg filtergraphs for 2K (1440x2560) or 1080p (1080x1920) vertical split-screen rendering."""

    # 2K Resolution by default for premium YouTube VP9/AV1 encoding quality
    IS_2K = os.getenv("OUTPUT_RESOLUTION", "2K").upper() == "2K"

    if IS_2K:
        CANVAS_WIDTH = 1440
        CANVAS_HEIGHT = 2560
        FACECAM_HEIGHT = 1024   # 40% of 2560
        GAMEPLAY_HEIGHT = 1536  # 60% of 2560
    else:
        CANVAS_WIDTH = 1080
        CANVAS_HEIGHT = 1920
        FACECAM_HEIGHT = 768    # 40% of 1920
        GAMEPLAY_HEIGHT = 1152  # 60% of 1920

    @classmethod
    def generate_split_screen_filter(
        cls,
        crop_config: Dict[str, Any],
        ass_subtitle_path: Optional[str] = None,
    ) -> str:
        """Constructs an FFmpeg complex filter string.

        Layout:
        - Gameplay top 60% (e.g. 1440x1536 in 2K or 1080x1152 in 1080p)
        - Facecam bottom 40% (e.g. 1440x1024 in 2K or 1080x768 in 1080p)
        - Stacked vertically to 9:16
        """
        fc = crop_config["facecam"]
        gp = crop_config["gameplay"]

        # 1. Facecam crop and scale (bottom 40%)
        fc_filter = (
            f"[0:v]crop={fc['width']}:{fc['height']}:{fc['x']}:{fc['y']},"
            f"scale={cls.CANVAS_WIDTH}:{cls.FACECAM_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={cls.CANVAS_WIDTH}:{cls.FACECAM_HEIGHT}[facecam]"
        )

        # 2. Gameplay crop and scale (top 60%)
        gp_filter = (
            f"[0:v]crop={gp['width']}:{gp['height']}:{gp['x']}:{gp['y']},"
            f"scale={cls.CANVAS_WIDTH}:{cls.GAMEPLAY_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={cls.CANVAS_WIDTH}:{cls.GAMEPLAY_HEIGHT}[gameplay]"
        )

        # 3. Vertical stack: Gameplay on top, Facecam on bottom
        stack_filter = f"[gameplay][facecam]vstack=inputs=2[stacked]"

        filters = [fc_filter, gp_filter, stack_filter]

        # 4. Optional ASS subtitle overlay
        if ass_subtitle_path:
            clean_ass = ass_subtitle_path.replace("\\", "/").replace(":", "\\:")
            filters.append(f"[stacked]ass='{clean_ass}'[v_out]")
        else:
            filters.append("[stacked]null[v_out]")

        return ";".join(filters)
