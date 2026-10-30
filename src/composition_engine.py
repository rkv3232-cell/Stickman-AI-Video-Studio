"""
Adaptive Composition Engine for Stickman AI Video Production Studio.
Calculates dynamic character framing, negative space regions, kinetic typography zones,
and collision-free bounding boxes on a 1080x1920 portrait canvas.

Enforces:
- Rule of Thirds framing (Left / Right character zones).
- Opposite negative-space positioning for high-impact kinetic typography.
- Subtitle safe zone preservation (Y: 1480-1720).
- Channel header safe zone preservation (Y: 0-180).
- Bounding box collision detection & resolution before rendering.
"""

from typing import Dict, Any, Tuple, Optional
from config import VIDEO_WIDTH, VIDEO_HEIGHT

class CompositionPreset:
    LEFT_STICKMAN_RIGHT_TYPO = "left_stickman_right_typo"
    RIGHT_STICKMAN_LEFT_TYPO = "right_stickman_left_typo"
    CENTER_STICKMAN_TOP_TYPO = "center_stickman_top_typo"
    LOWER_LEFT_STICKMAN_RIGHT_TYPO = "lower_left_stickman_right_typo"
    LOWER_RIGHT_STICKMAN_LEFT_TYPO = "lower_right_stickman_left_typo"

# Screen Layout Boundaries
SAFE_TOP = 190          # Below channel header badge
SAFE_BOTTOM = 1460      # Above word-highlight subtitles
SUBTITLE_Y = 1530       # Center of word-highlight captions
SAFE_MARGIN_X = 60      # Horizontal edge padding

def get_composition_layout(
    scene_index: int,
    stickman_pos: str = "auto",
    typography_pos: str = "auto",
    shot_type: str = "medium",
    primary_text: str = "",
    secondary_text: str = ""
) -> Dict[str, Any]:
    """
    Intelligently determines and resolves scene layout, character positioning,
    typography zone, and safe boundaries.
    """
    # 1. Determine Character Side if "auto"
    if stickman_pos == "auto":
        # Alternate naturally across scenes to create editorial rhythm
        # Even scenes (0, 2, 4...) -> Left; Odd scenes (1, 3, 5...) -> Right
        if scene_index % 2 == 0:
            stickman_pos = "left"
        else:
            stickman_pos = "right"

    # 2. Derive Typography Placement opposite to Stickman
    if typography_pos == "auto":
        if stickman_pos in ["left", "left_center", "lower_left"]:
            typography_pos = "right"
        elif stickman_pos in ["right", "right_center", "lower_right"]:
            typography_pos = "left"
        else:
            typography_pos = "top"

    # 3. Calculate Stickman Coordinates & Dimensions
    # Based on 1080x1920 canvas
    if stickman_pos == "left":
        char_x = int(VIDEO_WIDTH * 0.28)    # ~302px
        char_y = int(VIDEO_HEIGHT * 0.58)   # ~1113px
        facing = "right"                    # Face towards typography on right
        char_scale = 1.15
        char_bbox = (char_x - 170, char_y - 420, char_x + 170, char_y + 240)
    elif stickman_pos == "right":
        char_x = int(VIDEO_WIDTH * 0.72)    # ~778px
        char_y = int(VIDEO_HEIGHT * 0.58)   # ~1113px
        facing = "left"                     # Face towards typography on left
        char_scale = 1.15
        char_bbox = (char_x - 170, char_y - 420, char_x + 170, char_y + 240)
    elif stickman_pos == "left_center":
        char_x = int(VIDEO_WIDTH * 0.36)
        char_y = int(VIDEO_HEIGHT * 0.58)
        facing = "right"
        char_scale = 1.12
        char_bbox = (char_x - 160, char_y - 410, char_x + 160, char_y + 230)
    elif stickman_pos == "right_center":
        char_x = int(VIDEO_WIDTH * 0.64)
        char_y = int(VIDEO_HEIGHT * 0.58)
        facing = "left"
        char_scale = 1.12
        char_bbox = (char_x - 160, char_y - 410, char_x + 160, char_y + 230)
    elif stickman_pos == "lower_left":
        char_x = int(VIDEO_WIDTH * 0.24)
        char_y = int(VIDEO_HEIGHT * 0.64)
        facing = "right"
        char_scale = 1.05
        char_bbox = (char_x - 150, char_y - 380, char_x + 150, char_y + 220)
    elif stickman_pos == "lower_right":
        char_x = int(VIDEO_WIDTH * 0.76)
        char_y = int(VIDEO_HEIGHT * 0.64)
        facing = "left"
        char_scale = 1.05
        char_bbox = (char_x - 150, char_y - 380, char_x + 150, char_y + 220)
    else: # center
        char_x = int(VIDEO_WIDTH * 0.50)
        char_y = int(VIDEO_HEIGHT * 0.62)
        facing = "center"
        char_scale = 1.05
        char_bbox = (char_x - 180, char_y - 410, char_x + 180, char_y + 230)

    # Adjust for shot type framing
    if shot_type == "close_up":
        char_scale *= 1.18
    elif shot_type == "wide":
        char_scale *= 0.88

    # 4. Calculate Kinetic Typography Box & Anchors
    if typography_pos == "right":
        typo_x1 = int(VIDEO_WIDTH * 0.48)
        typo_x2 = VIDEO_WIDTH - SAFE_MARGIN_X
        typo_center_x = (typo_x1 + typo_x2) // 2
        typo_center_y = int(VIDEO_HEIGHT * 0.38) # ~730px
        typo_align = "left"
        max_typo_w = typo_x2 - typo_x1
    elif typography_pos == "left":
        typo_x1 = SAFE_MARGIN_X
        typo_x2 = int(VIDEO_WIDTH * 0.52)
        typo_center_x = (typo_x1 + typo_x2) // 2
        typo_center_y = int(VIDEO_HEIGHT * 0.38) # ~730px
        typo_align = "left"
        max_typo_w = typo_x2 - typo_x1
    else: # top / center
        typo_x1 = SAFE_MARGIN_X
        typo_x2 = VIDEO_WIDTH - SAFE_MARGIN_X
        typo_center_x = VIDEO_WIDTH // 2
        typo_center_y = int(VIDEO_HEIGHT * 0.28) # ~537px
        typo_align = "center"
        max_typo_w = typo_x2 - typo_x1

    typo_bbox = (
        typo_x1,
        typo_center_y - 200,
        typo_x2,
        typo_center_y + 200
    )

    # 5. Collision Check between Stickman and Typography
    collision = check_box_overlap(char_bbox, typo_bbox)
    if collision:
        # Resolve collision by nudging typography vertically or flipping
        if char_y < typo_center_y:
            typo_center_y = min(SAFE_BOTTOM - 200, char_bbox[3] + 120)
        else:
            typo_center_y = max(SAFE_TOP + 160, char_bbox[1] - 160)
        typo_bbox = (typo_x1, typo_center_y - 180, typo_x2, typo_center_y + 180)

    # 6. Subtitle Safe Zone Check
    sub_bbox = (SAFE_MARGIN_X, SUBTITLE_Y - 80, VIDEO_WIDTH - SAFE_MARGIN_X, SUBTITLE_Y + 120)
    sub_collision = check_box_overlap(typo_bbox, sub_bbox)
    if sub_collision:
        typo_center_y = min(typo_center_y, SUBTITLE_Y - 260)
        typo_bbox = (typo_x1, typo_center_y - 180, typo_x2, typo_center_y + 180)

    return {
        "preset": f"{stickman_pos}_stickman_{typography_pos}_typo",
        "stickman": {
            "position": stickman_pos,
            "x": char_x,
            "y": char_y,
            "scale": char_scale,
            "facing": facing,
            "bbox": char_bbox
        },
        "typography": {
            "position": typography_pos,
            "center_x": typo_center_x,
            "center_y": typo_center_y,
            "align": typo_align,
            "max_width": max_typo_w,
            "bbox": typo_bbox
        },
        "captions": {
            "center_x": VIDEO_WIDTH // 2,
            "center_y": SUBTITLE_Y,
            "max_width": VIDEO_WIDTH - (SAFE_MARGIN_X * 2),
            "bbox": sub_bbox
        }
    }

def check_box_overlap(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> bool:
    """Returns True if box1 (x1, y1, x2, y2) overlaps box2."""
    b1_x1, b1_y1, b1_x2, b1_y2 = box1
    b2_x1, b2_y1, b2_x2, b2_y2 = box2
    return not (b1_x2 < b2_x1 or b1_x1 > b2_x2 or b1_y2 < b2_y1 or b1_y1 > b2_y2)

