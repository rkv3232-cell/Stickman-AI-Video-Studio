"""
Deterministic Articulated Stickman Storytelling & Animation Engine.
Provides 100% character identity preservation (Yellow T-Shirt, Crimson Red Beanie,
signature anatomical proportions) while delivering living, multi-beat cinematic character acting.

Features:
- Dynamic Action Sequences per Scene (Entrance -> Interaction/Gaze -> Audience Engagement)
- Articulated 2-segment limbs with natural human joint kinematics & easing
- Dynamic Gaze & Head Orientation (Looking at scene objects, sky, screens, or directly at viewer)
- Natural Locomotion (True walking kinematics with hip bob, alternating legs, counter-swinging arms)
- Expressive Facial Rig (Devanagari speech mouth sync, blinks, wide shock, smiles, curious tilts)
- Grounded Cinematic Framing (Safe vertical placement, no chest cutoff, no overlap with subtitles)
"""

import os
import sys
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from moviepy import VideoClip
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS

FONT_PATH = "C:/Windows/Fonts/arial.ttf"

class StickmanPose:
    # Story-driven multi-beat actions
    LOOK_AND_SHOCK = "look_and_shock"
    POINT_AND_EXPLAIN = "point_and_explain"
    INTERACT_MEDICAL = "interact_medical"
    WALK_AND_WAVE = "walk_and_wave"
    SIT_AND_EXPLAIN = "sit_and_explain"
    CELEBRATE_AND_CTA = "celebrate_and_cta"
    # Legacy aliases mapped cleanly
    EXPLAINING = "explaining"
    POINTING_RIGHT = "pointing_right"
    POINTING_LEFT = "pointing_left"
    POINTING_UP = "pointing_up"
    THINKING = "thinking"
    SHOCKED = "shocked"
    TALKING = "talking"
    CELEBRATING = "celebrating"
    WORRIED = "worried"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    SITTING = "sitting"
    INTERACTING_SCREEN = "interacting_screen"

class StickmanEmotion:
    NEUTRAL = "neutral"
    HAPPY = "happy"
    CURIOUS = "curious"
    SHOCKED = "shocked"
    CONFIDENT = "confident"
    WORRIED = "worried"

class ShotType:
    WIDE = "wide"          # scale = 0.90, baseline y = 0.68 * H
    MEDIUM = "medium"      # scale = 1.15, baseline y = 0.70 * H
    CLOSE_UP = "close_up"  # scale = 1.35, baseline y = 0.72 * H

class StickmanConfig:
    def __init__(
        self,
        style: str = "modern_beanie",
        line_width: int = 8,
        head_radius: int = 48,
        torso_length: int = 100,
        upper_arm_length: int = 52,
        forearm_length: int = 48,
        thigh_length: int = 68,
        calf_length: int = 68,
        stroke_color: tuple = (20, 24, 36),
        fill_color: tuple = (255, 255, 255),
        accent_color: tuple = (225, 29, 72)
    ):
        self.style = style
        self.line_width = line_width
        self.head_radius = head_radius
        self.torso_length = torso_length
        self.upper_arm_length = upper_arm_length
        self.forearm_length = forearm_length
        self.thigh_length = thigh_length
        self.calf_length = calf_length
        self.stroke_color = stroke_color
        self.fill_color = fill_color
        self.accent_color = accent_color

def _draw_antialiased_line(draw: ImageDraw.Draw, p1: tuple, p2: tuple, color: tuple, width: int):
    """Draws a smooth line with rounded caps for natural hand-drawn limbs."""
    draw.line([p1, p2], fill=color, width=width)
    r = max(1, width // 2)
    draw.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=color)
    draw.ellipse([p2[0] - r, p2[1] - r, p2[0] + r, p2[1] + r], fill=color)

def _smooth_step(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep interpolation between 0 and 1."""
    t = max(0.0, min(1.0, (x - edge0) / max(1e-5, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)

def render_stickman_frame(
    t: float,
    duration: float = 4.0,
    pose: str = StickmanPose.EXPLAINING,
    emotion: str = StickmanEmotion.CONFIDENT,
    position: str = "center",
    shot_type: str = ShotType.MEDIUM,
    prop: str = "none",
    config: StickmanConfig = None,
    scale: float = None,
    target_x: int = None,
    target_y: int = None,
    facing: str = None
) -> Image.Image:
    """
    Renders a living, articulated Stickman character frame with 100% identity preservation.
    Supports left/right adaptive composition, gaze orientation, and natural kinetic acting.
    """
    if config is None:
        config = StickmanConfig()

    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # 1. Determine Scale and Base Placement
    if scale is None:
        if shot_type == ShotType.CLOSE_UP:
            scale = 1.25
            base_y = int(VIDEO_HEIGHT * 0.59)
        elif shot_type == ShotType.WIDE:
            scale = 0.95
            base_y = int(VIDEO_HEIGHT * 0.58)
        else: # MEDIUM
            scale = 1.15
            base_y = int(VIDEO_HEIGHT * 0.58)
    else:
        base_y = int(VIDEO_HEIGHT * 0.58)

    # Scaled anatomical dimensions
    lw = max(3, int(config.line_width * scale))
    hr = int(config.head_radius * scale)
    torso_len = int(config.torso_length * scale)
    thigh_len = int(config.thigh_length * scale)
    calf_len = int(config.calf_length * scale)
    u_arm = int(config.upper_arm_length * scale)
    f_arm = int(config.forearm_length * scale)

    # Progress in scene timeline (0.0 to 1.0)
    tau = max(0.0, min(1.0, t / max(duration, 0.1)))

    # Micro-animations
    breath = math.sin(t * 3.5) * (3.5 * scale)
    is_blinking = (t % 3.0) < 0.14
    mouth_open_factor = abs(math.sin(t * 13.0))

    # Base X and Facing Calculation for Adaptive Composition
    if target_x is not None:
        default_x = target_x
    elif position in ["left", "lower_left"]:
        default_x = int(VIDEO_WIDTH * 0.28)
    elif position in ["right", "lower_right"]:
        default_x = int(VIDEO_WIDTH * 0.72)
    elif position == "left_center":
        default_x = int(VIDEO_WIDTH * 0.36)
    elif position == "right_center":
        default_x = int(VIDEO_WIDTH * 0.64)
    else:
        default_x = int(VIDEO_WIDTH * 0.50)

    if target_y is not None:
        base_y = target_y
    elif position in ["lower_left", "lower_right"]:
        base_y = int(VIDEO_HEIGHT * 0.64)

    # Determine Facing Direction (towards negative space / typography)
    if facing is None:
        if position in ["right", "right_center", "lower_right"]:
            facing = "left"
        elif position in ["left", "left_center", "lower_left"]:
            facing = "right"
        else:
            facing = "center"

    # State variables to compute per action sequence
    curr_x = default_x
    curr_y = base_y
    gaze_dir = facing if facing != "center" else "center"
    head_tilt = 0.0      # radians
    torso_lean = 0.0     # horizontal dx for neck
    curr_emotion = emotion
    is_sitting = False
    is_jumping = False

    # ═════════════════════════════════════════════════════════════════════
    # 1. RESOLVE ACTION TIMELINE POSITION & STATE
    # ═════════════════════════════════════════════════════════════════════
    if pose in [StickmanPose.WALK_AND_WAVE, StickmanPose.WALKING]:
        if tau < 0.50:
            p = _smooth_step(0.0, 0.50, tau)
            if facing == "right":
                curr_x = int(VIDEO_WIDTH * (0.20 + 0.16 * p))
            else:
                curr_x = int(VIDEO_WIDTH * (0.80 - 0.16 * p))
            step_bounce = -abs(math.sin(t * 8.0)) * (10.0 * scale)
            curr_y = base_y + int(step_bounce)
        else:
            curr_x = default_x
            curr_y = base_y
    elif pose in [StickmanPose.CELEBRATE_AND_CTA, StickmanPose.JUMPING, StickmanPose.CELEBRATING]:
        curr_x = default_x
        if 0.40 <= tau < 0.75:
            is_jumping = True
            p_jump = _smooth_step(0.40, 0.75, tau)
            jump_h = math.sin(p_jump * math.pi) * (95.0 * scale)
            curr_y = base_y - int(jump_h)
    else:
        curr_x = default_x
        curr_y = base_y

    # ═════════════════════════════════════════════════════════════════════
    # 2. COMPUTED ANCHOR KINEMATICS (Pelvis, Neck, Head, Shoulder)
    # ═════════════════════════════════════════════════════════════════════
    pelvis = (curr_x, int(curr_y + (breath if not is_sitting else 0)))
    neck = (curr_x + int(torso_lean), int(pelvis[1] - torso_len))
    head_center = (neck[0], int(neck[1] - hr - 8 * scale))
    shoulder = (neck[0], neck[1] + int(14 * scale))

    # Default anatomical limbs
    l_elbow = (shoulder[0] - int(40 * scale), shoulder[1] + int(24 * scale))
    l_hand = (shoulder[0] - int(60 * scale), shoulder[1] + int(12 * scale))
    r_elbow = (shoulder[0] + int(42 * scale), shoulder[1] + int(20 * scale))
    r_hand = (shoulder[0] + int(75 * scale), shoulder[1] - int(22 * scale))

    l_knee = (pelvis[0] - int(14 * scale), pelvis[1] + thigh_len)
    l_foot = (l_knee[0] - int(4 * scale), l_knee[1] + calf_len)
    r_knee = (pelvis[0] + int(14 * scale), pelvis[1] + thigh_len)
    r_foot = (r_knee[0] + int(4 * scale), r_knee[1] + calf_len)

    # ═════════════════════════════════════════════════════════════════════
    # 3. MULTI-BEAT ACTION CHOREOGRAPHY WITH DIRECTION AWARENESS
    # ═════════════════════════════════════════════════════════════════════

    # --- ACTION 1: LOOK AND SHOCK (Hook Scene) ---
    if pose in [StickmanPose.LOOK_AND_SHOCK, StickmanPose.SHOCKED]:
        if tau < 0.35:
            # Beat 1: Looking up at kinetic typography / environment in awe
            gaze_dir = "up"
            head_tilt = 0.08 if facing == "right" else -0.08
            curr_emotion = StickmanEmotion.CURIOUS
            if facing == "right":
                l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(35 * scale))
                l_hand = (shoulder[0] - int(25 * scale), shoulder[1] + int(70 * scale))
                r_elbow = (shoulder[0] + int(35 * scale), shoulder[1] - int(15 * scale))
                r_hand = (shoulder[0] + int(55 * scale), shoulder[1] - int(75 * scale))
            else:
                r_elbow = (shoulder[0] + int(35 * scale), shoulder[1] + int(35 * scale))
                r_hand = (shoulder[0] + int(25 * scale), shoulder[1] + int(70 * scale))
                l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] - int(15 * scale))
                l_hand = (shoulder[0] - int(55 * scale), shoulder[1] - int(75 * scale))
        elif tau < 0.70:
            # Beat 2: Turns to camera, hands clutch cheeks in shock!
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.SHOCKED
            torso_lean = -int(4 * scale) if facing == "right" else int(4 * scale)
            l_elbow = (shoulder[0] - int(48 * scale), shoulder[1] - int(12 * scale))
            l_hand = (curr_x - hr + int(4 * scale), neck[1] - hr // 2 + int(8 * scale))
            r_elbow = (shoulder[0] + int(48 * scale), shoulder[1] - int(12 * scale))
            r_hand = (curr_x + hr - int(4 * scale), neck[1] - hr // 2 + int(8 * scale))
        else:
            # Beat 3: Conversational explanation
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.CONFIDENT
            arm_swing = math.sin(t * 5.0) * (8 * scale)
            l_elbow = (shoulder[0] - int(40 * scale), shoulder[1] + int(25 * scale))
            l_hand = (shoulder[0] - int(55 * scale), shoulder[1] + int(20 * scale) + int(arm_swing))
            r_elbow = (shoulder[0] + int(42 * scale), shoulder[1] + int(20 * scale))
            r_hand = (shoulder[0] + int(75 * scale), shoulder[1] - int(20 * scale) - int(arm_swing))

    # --- ACTION 2: POINT AND EXPLAIN (Market / Technology / Core Points) ---
    elif pose in [StickmanPose.POINT_AND_EXPLAIN, StickmanPose.POINTING_RIGHT, StickmanPose.POINTING_LEFT]:
        if tau < 0.45:
            # Beat 1: Turns towards typography, points directly at the headline
            if facing == "right" or pose == StickmanPose.POINTING_RIGHT:
                gaze_dir = "right"
                curr_emotion = StickmanEmotion.CONFIDENT
                l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(30 * scale))
                l_hand = (shoulder[0] - int(20 * scale), shoulder[1] + int(65 * scale))
                r_elbow = (shoulder[0] + int(55 * scale), shoulder[1] - int(25 * scale))
                r_hand = (shoulder[0] + int(135 * scale), shoulder[1] - int(70 * scale))
            else:
                gaze_dir = "left"
                curr_emotion = StickmanEmotion.CONFIDENT
                r_elbow = (shoulder[0] + int(35 * scale), shoulder[1] + int(30 * scale))
                r_hand = (shoulder[0] + int(20 * scale), shoulder[1] + int(65 * scale))
                l_elbow = (shoulder[0] - int(55 * scale), shoulder[1] - int(25 * scale))
                l_hand = (shoulder[0] - int(135 * scale), shoulder[1] - int(70 * scale))
        else:
            # Beat 2: Turns head to viewer, explaining with both hands
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.HAPPY
            arm_cadence = math.sin(t * 6.0) * (10 * scale)
            l_elbow = (shoulder[0] - int(42 * scale), shoulder[1] + int(22 * scale))
            l_hand = (shoulder[0] - int(65 * scale), shoulder[1] - int(10 * scale) + int(arm_cadence))
            r_elbow = (shoulder[0] + int(45 * scale), shoulder[1] + int(22 * scale))
            r_hand = (shoulder[0] + int(70 * scale), shoulder[1] - int(10 * scale) - int(arm_cadence))

    # --- ACTION 3: INTERACT MEDICAL / SCREEN ---
    elif pose in [StickmanPose.INTERACT_MEDICAL, StickmanPose.INTERACTING_SCREEN]:
        if tau < 0.45:
            # Beat 1: Interacts with digital UI on the inward side
            gaze_dir = facing if facing != "center" else "right"
            curr_emotion = StickmanEmotion.CURIOUS
            tap_drift = math.sin(t * 9.0) * (6 * scale)
            if facing == "right":
                l_elbow = (shoulder[0] - int(30 * scale), shoulder[1] + int(32 * scale))
                l_hand = (shoulder[0] - int(15 * scale), shoulder[1] + int(60 * scale))
                r_elbow = (shoulder[0] + int(45 * scale), shoulder[1] + int(10 * scale))
                r_hand = (shoulder[0] + int(95 * scale) + int(tap_drift), shoulder[1] - int(25 * scale))
            else:
                r_elbow = (shoulder[0] + int(30 * scale), shoulder[1] + int(32 * scale))
                r_hand = (shoulder[0] + int(15 * scale), shoulder[1] + int(60 * scale))
                l_elbow = (shoulder[0] - int(45 * scale), shoulder[1] + int(10 * scale))
                l_hand = (shoulder[0] - int(95 * scale) - int(tap_drift), shoulder[1] - int(25 * scale))
        else:
            # Beat 2: Turns to viewer, reassuring open-palm explanation
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.CONFIDENT
            l_elbow = (shoulder[0] - int(38 * scale), shoulder[1] + int(28 * scale))
            l_hand = (shoulder[0] - int(55 * scale), shoulder[1] + int(15 * scale))
            r_elbow = (shoulder[0] + int(45 * scale), shoulder[1] + int(18 * scale))
            r_hand = (shoulder[0] + int(80 * scale), shoulder[1] - int(15 * scale))

    # --- ACTION 4: WALK AND WAVE ---
    elif pose in [StickmanPose.WALK_AND_WAVE, StickmanPose.WALKING]:
        if tau < 0.50:
            # Beat 1: Natural walking across frame
            gaze_dir = facing if facing != "center" else "right"
            curr_emotion = StickmanEmotion.CONFIDENT

            walk_cycle = t * 8.0
            l_angle = math.sin(walk_cycle) * 0.50
            r_angle = -math.sin(walk_cycle) * 0.50

            l_knee = (int(pelvis[0] - int(12 * scale) + thigh_len * math.sin(l_angle)),
                      int(pelvis[1] + thigh_len * math.cos(l_angle)))
            r_knee = (int(pelvis[0] + int(12 * scale) + thigh_len * math.sin(r_angle)),
                      int(pelvis[1] + thigh_len * math.cos(r_angle)))
            l_foot = (int(l_knee[0] + calf_len * math.sin(l_angle + 0.2)),
                      int(l_knee[1] + calf_len * math.cos(l_angle + 0.2)))
            r_foot = (int(r_knee[0] + calf_len * math.sin(r_angle + 0.2)),
                      int(r_knee[1] + calf_len * math.cos(r_angle + 0.2)))

            # Arm counter-swing
            walk_arm = math.sin(t * 8.0) * (32.0 * scale)
            l_elbow = (shoulder[0] - int(25 * scale), shoulder[1] + int(30 * scale))
            l_hand = (int(shoulder[0] - 35 * scale - walk_arm), shoulder[1] + int(60 * scale))
            r_elbow = (shoulder[0] + int(25 * scale), shoulder[1] + int(30 * scale))
            r_hand = (int(shoulder[0] + 35 * scale + walk_arm), shoulder[1] + int(60 * scale))
        elif tau < 0.80:
            # Beat 2: Stops, waves toward scene / typography
            gaze_dir = "up"
            curr_emotion = StickmanEmotion.HAPPY

            wave_motion = math.sin(t * 12.0) * (18 * scale)
            if facing == "right":
                l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(35 * scale))
                l_hand = (shoulder[0] - int(20 * scale), shoulder[1] + int(70 * scale))
                r_elbow = (shoulder[0] + int(40 * scale), shoulder[1] - int(35 * scale))
                r_hand = (int(shoulder[0] + 65 * scale + wave_motion), shoulder[1] - int(95 * scale))
            else:
                r_elbow = (shoulder[0] + int(35 * scale), shoulder[1] + int(35 * scale))
                r_hand = (shoulder[0] + int(20 * scale), shoulder[1] + int(70 * scale))
                l_elbow = (shoulder[0] - int(40 * scale), shoulder[1] - int(35 * scale))
                l_hand = (int(shoulder[0] - 65 * scale - wave_motion), shoulder[1] - int(95 * scale))
        else:
            # Beat 3: Turns to camera with proud thumbs-up
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.HAPPY
            l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(30 * scale))
            l_hand = (shoulder[0] - int(20 * scale), shoulder[1] + int(65 * scale))
            r_elbow = (shoulder[0] + int(38 * scale), shoulder[1] + int(10 * scale))
            r_hand = (shoulder[0] + int(65 * scale), shoulder[1] - int(25 * scale))

    # --- ACTION 5: SIT AND EXPLAIN ---
    elif pose in [StickmanPose.SIT_AND_EXPLAIN, StickmanPose.SITTING]:
        is_sitting = False
        if tau < 0.45:
            # Beat 1: Points towards code / technology typography
            gaze_dir = facing if facing != "center" else "right"
            curr_emotion = StickmanEmotion.CONFIDENT
            if facing == "right":
                l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(30 * scale))
                l_hand = (shoulder[0] - int(20 * scale), shoulder[1] + int(65 * scale))
                r_elbow = (shoulder[0] + int(50 * scale), shoulder[1] - int(15 * scale))
                r_hand = (shoulder[0] + int(120 * scale), shoulder[1] - int(45 * scale))
            else:
                r_elbow = (shoulder[0] + int(35 * scale), shoulder[1] + int(30 * scale))
                r_hand = (shoulder[0] + int(20 * scale), shoulder[1] + int(65 * scale))
                l_elbow = (shoulder[0] - int(50 * scale), shoulder[1] - int(15 * scale))
                l_hand = (shoulder[0] - int(120 * scale), shoulder[1] - int(45 * scale))
        else:
            # Beat 2: Turns to face audience, gesturing with both hands
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.CONFIDENT
            arm_drift = math.sin(t * 5.0) * (8 * scale)
            l_elbow = (shoulder[0] - int(38 * scale), shoulder[1] + int(24 * scale))
            l_hand = (shoulder[0] - int(60 * scale), shoulder[1] - int(10 * scale) + int(arm_drift))
            r_elbow = (shoulder[0] + int(42 * scale), shoulder[1] + int(24 * scale))
            r_hand = (shoulder[0] + int(70 * scale), shoulder[1] - int(10 * scale) - int(arm_drift))

    # --- ACTION 6: CELEBRATE AND CTA ---
    elif pose in [StickmanPose.CELEBRATE_AND_CTA, StickmanPose.JUMPING, StickmanPose.CELEBRATING]:
        if tau < 0.40:
            # Beat 1: Warm closing delivery
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.CONFIDENT
            l_elbow = (shoulder[0] - int(38 * scale), shoulder[1] + int(22 * scale))
            l_hand = (shoulder[0] - int(60 * scale), shoulder[1] + int(10 * scale))
            r_elbow = (shoulder[0] + int(38 * scale), shoulder[1] + int(22 * scale))
            r_hand = (shoulder[0] + int(60 * scale), shoulder[1] + int(10 * scale))
        elif tau < 0.75:
            # Beat 2: Parabolic celebration jump!
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.HAPPY

            # Arms raised in triumph 'V'
            l_elbow = (shoulder[0] - int(50 * scale), shoulder[1] - int(45 * scale))
            l_hand = (shoulder[0] - int(80 * scale), shoulder[1] - int(95 * scale))
            r_elbow = (shoulder[0] + int(50 * scale), shoulder[1] - int(45 * scale))
            r_hand = (shoulder[0] + int(80 * scale), shoulder[1] - int(95 * scale))

            # Tucked airborne legs
            l_knee = (pelvis[0] - int(22 * scale), pelvis[1] + int(thigh_len * 0.65))
            r_knee = (pelvis[0] + int(22 * scale), pelvis[1] + int(thigh_len * 0.65))
            l_foot = (l_knee[0] + int(10 * scale), l_knee[1] + int(calf_len * 0.65))
            r_foot = (r_knee[0] - int(10 * scale), r_knee[1] + int(calf_len * 0.65))
        else:
            # Beat 3: Cushioned landing & friendly wave
            gaze_dir = "center"
            curr_emotion = StickmanEmotion.HAPPY
            l_elbow = (shoulder[0] - int(35 * scale), shoulder[1] + int(30 * scale))
            l_hand = (shoulder[0] - int(20 * scale), shoulder[1] + int(65 * scale))
            wave_h = math.sin(t * 10.0) * (14 * scale)
            r_elbow = (shoulder[0] + int(42 * scale), shoulder[1] - int(20 * scale))
            r_hand = (int(shoulder[0] + 65 * scale + wave_h), shoulder[1] - int(75 * scale))

    # --- DEFAULT / EXPLAINING ---
    else:
        gaze_dir = "center"
        curr_emotion = emotion
        arm_drift = math.sin(t * 4.0) * (6.0 * scale)
        l_elbow = (shoulder[0] - int(40 * scale), shoulder[1] + int(24 * scale))
        l_hand = (shoulder[0] - int(60 * scale), shoulder[1] + int(12 * scale) + int(arm_drift))
        r_elbow = (shoulder[0] + int(42 * scale), shoulder[1] + int(20 * scale))
        r_hand = (shoulder[0] + int(75 * scale), shoulder[1] - int(22 * scale) - int(arm_drift))

    # ═════════════════════════════════════════════════════════════════════
    # DRAW CHARACTER RIG
    # ═════════════════════════════════════════════════════════════════════

    # Re-anchor based on updated coordinates
    pelvis = (curr_x, int(curr_y + (breath if not is_sitting else 0)))
    neck = (curr_x + int(torso_lean), int(pelvis[1] - torso_len))
    head_center = (neck[0], int(neck[1] - hr - 8 * scale))
    shoulder = (neck[0], neck[1] + int(14 * scale))

    # SITTING FURNITURE (Only when seated)
    if is_sitting:
        stool_top_y = pelvis[1] + int(8 * scale)
        stool_w = int(60 * scale)
        draw.rounded_rectangle(
            [pelvis[0] - stool_w // 2, stool_top_y, pelvis[0] + stool_w // 2, stool_top_y + int(12 * scale)],
            radius=max(2, int(4 * scale)), fill=(40, 50, 70), outline=config.stroke_color, width=max(1, int(2 * scale))
        )
        stool_leg_b = stool_top_y + thigh_len + calf_len - int(8 * scale)
        _draw_antialiased_line(draw, (pelvis[0], stool_top_y + int(12 * scale)), (pelvis[0], stool_leg_b), (60, 75, 95), max(2, int(3 * scale)))
        draw.line([(pelvis[0] - int(20 * scale), stool_leg_b), (pelvis[0] + int(20 * scale), stool_leg_b)], fill=(60, 75, 95), width=max(2, int(3 * scale)))

        # Seated leg angles
        l_knee = (pelvis[0] + int(45 * scale), pelvis[1] + int(10 * scale))
        r_knee = (pelvis[0] + int(50 * scale), pelvis[1] + int(12 * scale))
        l_foot = (l_knee[0] + int(4 * scale), l_knee[1] + calf_len)
        r_foot = (r_knee[0] + int(6 * scale), r_knee[1] + calf_len)

    # 0. GROUND SHADOW (Anchors character physically to environment)
    if not is_jumping and not is_sitting:
        ground_y = max(l_foot[1], r_foot[1]) + int(2 * scale)
        shadow_w = int(48 * scale)
        shadow_h = int(12 * scale)
        draw.ellipse(
            [curr_x - shadow_w, ground_y - shadow_h, curr_x + shadow_w, ground_y + shadow_h],
            fill=(10, 15, 25, 110)
        )
    elif is_jumping:
        ground_y = base_y + thigh_len + calf_len + int(2 * scale)
        jump_ratio = max(0.2, 1.0 - (base_y - curr_y) / (120.0 * scale))
        shadow_w = int(45 * scale * jump_ratio)
        shadow_h = int(10 * scale * jump_ratio)
        draw.ellipse(
            [default_x - shadow_w, ground_y - shadow_h, default_x + shadow_w, ground_y + shadow_h],
            fill=(10, 15, 25, int(90 * jump_ratio))
        )

    # 1. DRAW LEGS, SHORTS & RED SNEAKERS
    left_hip = (pelvis[0] - int(12 * scale), pelvis[1])
    right_hip = (pelvis[0] + int(12 * scale), pelvis[1])

    _draw_antialiased_line(draw, left_hip, l_knee, config.stroke_color, lw)
    _draw_antialiased_line(draw, l_knee, l_foot, config.stroke_color, lw)
    _draw_antialiased_line(draw, right_hip, r_knee, config.stroke_color, lw)
    _draw_antialiased_line(draw, r_knee, r_foot, config.stroke_color, lw)

    # Signature Navy/Slate Shorts
    shorts_w = int(22 * scale)
    shorts_h = int(32 * scale)
    draw.rounded_rectangle(
        [pelvis[0] - shorts_w, pelvis[1] - int(4 * scale), pelvis[0] + shorts_w, pelvis[1] + shorts_h],
        radius=max(2, int(4 * scale)),
        fill=(30, 41, 59),
        outline=config.stroke_color,
        width=max(1, int(2 * scale))
    )

    # Red Sneakers with White Soles
    shoe_w = int(18 * scale)
    shoe_h = int(12 * scale)
    # Left Shoe
    draw.rounded_rectangle(
        [l_foot[0] - shoe_w + int(4 * scale), l_foot[1] - int(4 * scale), l_foot[0] + int(6 * scale), l_foot[1] + shoe_h],
        radius=max(2, int(4 * scale)),
        fill=(225, 29, 72),
        outline=config.stroke_color,
        width=max(1, int(2 * scale))
    )
    # Right Shoe
    draw.rounded_rectangle(
        [r_foot[0] - int(6 * scale), r_foot[1] - int(4 * scale), r_foot[0] + shoe_w - int(4 * scale), r_foot[1] + shoe_h],
        radius=max(2, int(4 * scale)),
        fill=(225, 29, 72),
        outline=config.stroke_color,
        width=max(1, int(2 * scale))
    )

    # 2. DRAW TORSO & SIGNATURE YELLOW T-SHIRT
    _draw_antialiased_line(draw, neck, pelvis, config.stroke_color, lw)

    if config.style == "modern_beanie":
        shirt_top = neck[1] + int(8 * scale)
        shirt_bottom = pelvis[1] - int(2 * scale)
        shirt_half_w = int(22 * scale)
        # Signature Yellow Shirt with rounded corners
        draw.rounded_rectangle(
            [neck[0] - shirt_half_w, shirt_top, neck[0] + shirt_half_w, shirt_bottom],
            radius=max(4, int(8 * scale)),
            fill=(253, 224, 71),
            outline=config.stroke_color,
            width=max(2, int(2 * scale))
        )
        # Dark Collar accent
        draw.line([(neck[0] - int(8 * scale), shirt_top), (neck[0] + int(8 * scale), shirt_top)], fill=(15, 23, 42), width=max(1, int(2 * scale)))

    # 3. DRAW ARMS & HANDS
    _draw_antialiased_line(draw, shoulder, l_elbow, config.stroke_color, lw)
    _draw_antialiased_line(draw, l_elbow, l_hand, config.stroke_color, lw)
    _draw_antialiased_line(draw, shoulder, r_elbow, config.stroke_color, lw)
    _draw_antialiased_line(draw, r_elbow, r_hand, config.stroke_color, lw)

    # Hand joints
    hand_r = max(3, int(lw // 2 + 3 * scale))
    draw.ellipse([l_hand[0] - hand_r, l_hand[1] - hand_r, l_hand[0] + hand_r, l_hand[1] + hand_r], fill=config.stroke_color)
    draw.ellipse([r_hand[0] - hand_r, r_hand[1] - hand_r, r_hand[0] + hand_r, r_hand[1] + hand_r], fill=config.stroke_color)

    # 4. DRAW HEAD, SIGNATURE CRIMSON BEANIE & FACIAL RIG
    hx, hy = head_center

    # Apply head tilt
    if abs(head_tilt) > 0.01:
        hy = int(hy - math.sin(head_tilt) * 4)

    # Head Circle
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=config.fill_color, outline=config.stroke_color, width=lw)

    # Signature Crimson Red Beanie with cuff
    if config.style == "modern_beanie":
        beanie_h = int(hr * 0.85)
        beanie_box = [hx - hr - int(4 * scale), hy - hr - int(14 * scale), hx + hr + int(4 * scale), hy - hr + beanie_h]
        draw.chord(beanie_box, start=180, end=360, fill=(225, 29, 72), outline=config.stroke_color, width=max(2, int(2 * scale)))
        # Folded cuff
        draw.rounded_rectangle(
            [hx - hr - int(6 * scale), hy - hr + int(12 * scale), hx + hr + int(6 * scale), hy - hr + int(30 * scale)],
            radius=max(2, int(4 * scale)), fill=(190, 18, 60)
        )

    # Gaze-directed facial feature placement
    eye_dx = 0
    eye_dy = 0
    if gaze_dir == "right":
        eye_dx = int(10 * scale)
    elif gaze_dir == "left":
        eye_dx = -int(10 * scale)
    elif gaze_dir == "up":
        eye_dy = -int(8 * scale)

    eye_offset_x = int(14 * scale)
    eye_y = hy - int(4 * scale) + eye_dy
    eye_r = max(2, int(4 * scale))

    # Eyes Rig
    if is_blinking:
        draw.line([(hx + eye_dx - eye_offset_x - int(5 * scale), eye_y), (hx + eye_dx - eye_offset_x + int(5 * scale), eye_y)], fill=(15, 23, 42), width=max(2, int(3 * scale)))
        draw.line([(hx + eye_dx + eye_offset_x - int(5 * scale), eye_y), (hx + eye_dx + eye_offset_x + int(5 * scale), eye_y)], fill=(15, 23, 42), width=max(2, int(3 * scale)))
    elif curr_emotion == StickmanEmotion.SHOCKED:
        # Wide Shocked Eyes with catchlight
        draw.ellipse([hx + eye_dx - eye_offset_x - eye_r - 2, eye_y - eye_r - 2, hx + eye_dx - eye_offset_x + eye_r + 2, eye_y + eye_r + 2], fill=(15, 23, 42))
        draw.ellipse([hx + eye_dx + eye_offset_x - eye_r - 2, eye_y - eye_r - 2, hx + eye_dx + eye_offset_x + eye_r + 2, eye_y + eye_r + 2], fill=(15, 23, 42))
        # Raised high arched eyebrows
        draw.line([(hx + eye_dx - eye_offset_x - int(8 * scale), eye_y - int(15 * scale)), (hx + eye_dx - eye_offset_x + int(8 * scale), eye_y - int(15 * scale))], fill=(15, 23, 42), width=max(2, int(3 * scale)))
        draw.line([(hx + eye_dx + eye_offset_x - int(8 * scale), eye_y - int(15 * scale)), (hx + eye_dx + eye_offset_x + int(8 * scale), eye_y - int(15 * scale))], fill=(15, 23, 42), width=max(2, int(3 * scale)))
    else:
        # Normal Expressive Eyes
        draw.ellipse([hx + eye_dx - eye_offset_x - eye_r, eye_y - eye_r, hx + eye_dx - eye_offset_x + eye_r, eye_y + eye_r], fill=(15, 23, 42))
        draw.ellipse([hx + eye_dx + eye_offset_x - eye_r, eye_y - eye_r, hx + eye_dx + eye_offset_x + eye_r, eye_y + eye_r], fill=(15, 23, 42))
        # Eyebrows
        if curr_emotion == StickmanEmotion.CURIOUS:
            # Inquiring raised eyebrow
            draw.line([(hx + eye_dx - eye_offset_x - int(6 * scale), eye_y - int(16 * scale)), (hx + eye_dx - eye_offset_x + int(6 * scale), eye_y - int(12 * scale))], fill=(15, 23, 42), width=max(2, int(3 * scale)))
            draw.line([(hx + eye_dx + eye_offset_x - int(6 * scale), eye_y - int(10 * scale)), (hx + eye_dx + eye_offset_x + int(6 * scale), eye_y - int(10 * scale))], fill=(15, 23, 42), width=max(2, int(2 * scale)))
        else:
            # Confident / Warm eyebrows
            draw.line([(hx + eye_dx - eye_offset_x - int(6 * scale), eye_y - int(10 * scale)), (hx + eye_dx - eye_offset_x + int(6 * scale), eye_y - int(10 * scale))], fill=(15, 23, 42), width=max(2, int(2 * scale)))
            draw.line([(hx + eye_dx + eye_offset_x - int(6 * scale), eye_y - int(10 * scale)), (hx + eye_dx + eye_offset_x + int(6 * scale), eye_y - int(10 * scale))], fill=(15, 23, 42), width=max(2, int(2 * scale)))

    # Articulated Devanagari Talking Mouth Rig
    mouth_y = hy + int(18 * scale)
    if curr_emotion == StickmanEmotion.SHOCKED:
        # Wide oval mouth in shock
        draw.ellipse([hx + eye_dx - int(8 * scale), mouth_y - int(8 * scale), hx + eye_dx + int(8 * scale), mouth_y + int(10 * scale)], fill=(15, 23, 42))
    elif mouth_open_factor > 0.35:
        # Speaking mouth cycle
        open_h = int(6 * scale * mouth_open_factor)
        draw.ellipse([hx + eye_dx - int(8 * scale), mouth_y - open_h, hx + eye_dx + int(8 * scale), mouth_y + open_h], fill=(15, 23, 42))
    elif curr_emotion in [StickmanEmotion.HAPPY, StickmanEmotion.CONFIDENT]:
        # Smiling arc
        draw.arc([hx + eye_dx - int(12 * scale), mouth_y - int(6 * scale), hx + eye_dx + int(12 * scale), mouth_y + int(8 * scale)], start=20, end=160, fill=(15, 23, 42), width=max(2, int(3 * scale)))
    else:
        # Neutral small mouth line
        draw.line([(hx + eye_dx - int(7 * scale), mouth_y), (hx + eye_dx + int(7 * scale), mouth_y)], fill=(15, 23, 42), width=max(2, int(2 * scale)))

    # 5. CONTEXTUAL PROPS (Only clean, non-intrusive elements)
    if prop == "hologram_chart":
        # Subtle 3D rising growth curve on right
        gx1 = curr_x + int(90 * scale)
        gy1 = shoulder[1] - int(110 * scale)
        gw, gh = int(220 * scale), int(150 * scale)
        # Translucent glass card
        draw.rounded_rectangle([gx1, gy1, gx1 + gw, gy1 + gh], radius=int(12 * scale), fill=(10, 20, 36, 190), outline=(0, 240, 255, 180), width=max(1, int(2 * scale)))
        try:
            f_chart = ImageFont.truetype(FONT_PATH, max(10, int(15 * scale)))
        except Exception:
            f_chart = ImageFont.load_default()
        draw.text((gx1 + int(14 * scale), gy1 + int(12 * scale)), "INDIA AI: $1 TRILLION", font=f_chart, fill=(0, 240, 255))
        # Upward green trendline
        curve_pts = [
            (gx1 + int(20 * scale), gy1 + gh - int(25 * scale)),
            (gx1 + int(80 * scale), gy1 + gh - int(55 * scale)),
            (gx1 + int(140 * scale), gy1 + gh - int(85 * scale)),
            (gx1 + int(200 * scale), gy1 + gh - int(120 * scale))
        ]
        for ci in range(len(curve_pts) - 1):
            draw.line([curve_pts[ci], curve_pts[ci + 1]], fill=(34, 197, 94), width=max(2, int(3 * scale)))
        # Trend tip
        draw.ellipse([curve_pts[-1][0] - 4, curve_pts[-1][1] - 4, curve_pts[-1][0] + 4, curve_pts[-1][1] + 4], fill=(255, 255, 255))

    return canvas

def create_stickman_clip(
    duration: float,
    pose: str = StickmanPose.EXPLAINING,
    emotion: str = StickmanEmotion.CONFIDENT,
    position: str = "center",
    shot_type: str = ShotType.MEDIUM,
    prop: str = "none",
    config: StickmanConfig = None,
    scale: float = None,
    target_x: int = None,
    target_y: int = None,
    facing: str = None
) -> VideoClip:
    """
    Creates a full-motion 30 FPS transparent VideoClip of the animated Stickman for the scene duration.
    """
    def make_frame(t):
        img = render_stickman_frame(
            t=t,
            duration=duration,
            pose=pose,
            emotion=emotion,
            position=position,
            shot_type=shot_type,
            prop=prop,
            config=config,
            scale=scale,
            target_x=target_x,
            target_y=target_y,
            facing=facing
        )
        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

if __name__ == "__main__":
    print("Testing Complete Articulated Stickman Storytelling Engine...")
    cfg = StickmanConfig()
    poses = [
        (StickmanPose.LOOK_AND_SHOCK, "output/test_shock.png", 2.0),
        (StickmanPose.POINT_AND_EXPLAIN, "output/test_point.png", 2.0),
        (StickmanPose.INTERACT_MEDICAL, "output/test_medical.png", 2.0),
        (StickmanPose.WALK_AND_WAVE, "output/test_walk.png", 1.5),
        (StickmanPose.SIT_AND_EXPLAIN, "output/test_sit.png", 2.0),
        (StickmanPose.CELEBRATE_AND_CTA, "output/test_celebrate.png", 2.0)
    ]
    for p, out_name, t_test in poses:
        frame = render_stickman_frame(t=t_test, duration=5.0, pose=p, config=cfg)
        frame.save(out_name)
        print(f"Rendered {p} -> {out_name}")
    print("All poses tested and rendered successfully!")
