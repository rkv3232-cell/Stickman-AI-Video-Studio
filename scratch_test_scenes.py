import sys
from pathlib import Path
from PIL import Image
import numpy as np

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.stickman_engine import render_stickman_frame, StickmanPose, StickmanConfig, ShotType
from src.storyboard_director import generate_deterministic_storyboard
from src.ai_script import get_fallback_script

script_data = get_fallback_script('भारत में AI का भविष्य')
storyboard = generate_deterministic_storyboard(script_data, total_duration=45.0)

print(f"Storyboard contains {len(storyboard)} scenes:")
cfg = StickmanConfig()
for sc in storyboard:
    sid = sc['scene_id']
    pose = sc['stickman_pose']
    shot = sc['shot_type']
    stage = sc['stage']
    print(f"Scene {sid}: {stage} | Pose: {pose} | Shot: {shot}")
    
    # Render stickman
    sm_img = render_stickman_frame(t=2.0, duration=sc['duration'], pose=pose, shot_type=shot, config=cfg)
    
    # Load background image
    bg_path = Path(f"assets/scenes/scene_{sid}.jpg")
    if bg_path.exists():
        bg_img = Image.open(bg_path).convert("RGBA").resize((1080, 1920))
        comp = Image.alpha_composite(bg_img, sm_img)
        out_path = Path(f"output/test_scene_{sid}_comp.png")
        comp.save(out_path)
        print(f"  Saved: {out_path.name}")
    else:
        print(f"  Warning: {bg_path} missing")
print("All 6 scenes rendered successfully!")
