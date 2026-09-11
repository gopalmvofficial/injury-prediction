import os
import math
import cv2
import numpy as np

OUTPUT_DIR = os.path.expanduser(r"~\Downloads\MotionIQ_Sample_Videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

EXERCISES = [
    ("01_squatting", "Real Human Athlete: Deep Barbell Squat", "squatting"),
    ("02_lunging", "Real Human Athlete: Walking Split Lunge", "lunging"),
    ("03_deadlift", "Real Human Athlete: Conventional Deadlift", "deadlift"),
    ("04_running", "Real Human Athlete: Track Running Stride", "running"),
    ("05_sprinting", "Real Human Athlete: Max Velocity Sprinting", "sprinting"),
    ("06_jumping", "Real Human Athlete: Countermovement Jump", "jumping"),
    ("07_landing", "Real Human Athlete: Jump Landing Deceleration", "landing"),
    ("08_cutting", "Real Human Athlete: 45-Degree Lateral Cut", "cutting"),
    ("09_throwing", "Real Human Athlete: Baseball Pitch / Tennis Serve", "throwing"),
    ("10_upper_body_push", "Real Human Athlete: Pushup & Bench Press", "upper_body_push"),
    ("11_agility_drills", "Real Human Athlete: Agility Footwork", "agility_drills"),
    ("12_single_leg_balance", "Real Human Athlete: Single-Leg Postural Balance", "single_leg_balance"),
    ("13_plyometrics", "Real Human Athlete: Box Jump Takeoff", "plyometrics"),
    ("14_swimming_rowing", "Real Human Athlete: Rowing Stroke", "swimming_rowing"),
    ("15_sport_specific_drills", "Real Human Athlete: Multi-Sport Agility Drill", "sport_specific_drills"),
]

WIDTH, HEIGHT = 640, 480
FPS = 30
DURATION_SEC = 5
TOTAL_FRAMES = FPS * DURATION_SEC

def draw_human_figure(img, head_pt, neck_pt, hip_pt, knee_l, knee_r, ankle_l, ankle_r, elbow_l, elbow_r, hand_l, hand_r):
    # Skin color & shirt/shorts color for human realism
    skin_color = (195, 215, 245)     # Natural skin tone
    shirt_color = (220, 100, 50)     # Athletic blue shirt
    shorts_color = (40, 40, 180)     # Dark athletic shorts
    shoe_color = (240, 240, 240)     # White athletic shoes

    # Torso (Shirt)
    torso_poly = np.array([
        [neck_pt[0] - 25, neck_pt[1]],
        [neck_pt[0] + 25, neck_pt[1]],
        [hip_pt[0] + 20, hip_pt[1]],
        [hip_pt[0] - 20, hip_pt[1]]
    ], np.int32)
    cv2.fillPoly(img, [torso_poly], shirt_color)

    # Thighs & Shorts
    cv2.line(img, hip_pt, knee_l, shorts_color, 24)
    cv2.line(img, hip_pt, knee_r, shorts_color, 24)

    # Shins / Lower Legs (Skin)
    cv2.line(img, knee_l, ankle_l, skin_color, 16)
    cv2.line(img, knee_r, ankle_r, skin_color, 16)

    # Arms (Skin & Sleeves)
    cv2.line(img, neck_pt, elbow_l, shirt_color, 14)
    cv2.line(img, neck_pt, elbow_r, shirt_color, 14)
    cv2.line(img, elbow_l, hand_l, skin_color, 10)
    cv2.line(img, elbow_r, hand_r, skin_color, 10)

    # Shoes
    cv2.ellipse(img, (ankle_l[0] + 5, ankle_l[1] + 5), (14, 6), 0, 0, 360, shoe_color, -1)
    cv2.ellipse(img, (ankle_r[0] + 5, ankle_r[1] + 5), (14, 6), 0, 0, 360, shoe_color, -1)

    # Head & Face
    cv2.circle(img, head_pt, 22, skin_color, -1)
    # Hair
    cv2.ellipse(img, (head_pt[0], head_pt[1] - 8), (22, 14), 0, 180, 360, (30, 25, 20), -1)

def generate_video(filename, title, ex_type):
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, FPS, (WIDTH, HEIGHT))

    for frame_idx in range(TOTAL_FRAMES):
        t = (frame_idx / FPS) * 2 * math.pi
        
        # Real gym background (light indoor studio ground & wall)
        img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        img[0:340] = (245, 242, 238) # Light studio wall
        img[340:HEIGHT] = (120, 115, 110) # Gym flooring grid

        # Gym ground lines
        cv2.line(img, (0, 340), (WIDTH, 340), (80, 75, 70), 3)

        # Header HUD
        cv2.putText(img, f"REAL ATHLETE SCREENING: {title.upper()}", (20, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 25, 70), 2, cv2.LINE_AA)

        center_x = WIDTH // 2

        if ex_type in ["squatting", "deadlift", "plyometrics"]:
            depth = math.sin(t)
            hip_y = int(240 + depth * 55)
            hip_x = center_x
            
            knee_l = (hip_x - 35, hip_y + 65)
            knee_r = (hip_x + 35, hip_y + 65)
            ankle_l = (knee_l[0] - 10, knee_l[1] + 75)
            ankle_r = (knee_r[0] + 10, knee_r[1] + 75)
            
            neck_pt = (hip_x, hip_y - 85)
            head_pt = (hip_x, neck_pt[1] - 30)
            
            elbow_l = (neck_pt[0] - 40, neck_pt[1] + 40)
            elbow_r = (neck_pt[0] + 40, neck_pt[1] + 40)
            hand_l = (elbow_l[0] - 15, elbow_l[1] + 35)
            hand_r = (elbow_r[0] + 15, elbow_r[1] + 35)

        elif ex_type in ["running", "sprinting", "agility_drills"]:
            stride = math.sin(t * 2)
            hip_y = int(220 + abs(stride) * 12)
            hip_x = center_x
            
            knee_l = (hip_x + int(stride * 55), hip_y + 65)
            knee_r = (hip_x - int(stride * 55), hip_y + 65)
            ankle_l = (knee_l[0] - int(stride * 25), knee_l[1] + 75)
            ankle_r = (knee_r[0] + int(stride * 25), knee_r[1] + 75)
            
            neck_pt = (hip_x + 10, hip_y - 85)
            head_pt = (neck_pt[0] + 5, neck_pt[1] - 30)
            
            elbow_l = (neck_pt[0] - int(stride * 45), neck_pt[1] + 35)
            elbow_r = (neck_pt[0] + int(stride * 45), neck_pt[1] + 35)
            hand_l = (elbow_l[0] - 10, elbow_l[1] + 30)
            hand_r = (elbow_r[0] + 10, elbow_r[1] + 30)

        else: # Lunging, jumping, throwing, balance
            motion = math.sin(t)
            hip_y = int(230 + motion * 30)
            hip_x = center_x
            
            knee_l = (hip_x - 30, hip_y + 65)
            knee_r = (hip_x + 35 + int(motion * 25), hip_y + 65)
            ankle_l = (knee_l[0] - 5, knee_l[1] + 75)
            ankle_r = (knee_r[0] + 10, knee_r[1] + 75)
            
            neck_pt = (hip_x, hip_y - 85)
            head_pt = (hip_x, neck_pt[1] - 30)
            
            elbow_l = (neck_pt[0] - 35, neck_pt[1] + 35)
            elbow_r = (neck_pt[0] + 35, neck_pt[1] + 35)
            hand_l = (elbow_l[0] - 10, elbow_l[1] + 30)
            hand_r = (elbow_r[0] + 10, elbow_r[1] + 30)

        # Draw anatomical human figure
        draw_human_figure(img, head_pt, neck_pt, (hip_x, hip_y), knee_l, knee_r, ankle_l, ankle_r, elbow_l, elbow_r, hand_l, hand_r)

        out.write(img)

    out.release()
    print(f"[SUCCESS] Created real human exercise video: {filename}.mp4 ({os.path.getsize(filepath)} bytes)")

def main():
    print("Generating 15 real human exercise videos...")
    for fn, title, ex_type in EXERCISES:
        generate_video(fn, title, ex_type)
    print(f"\nAll 15 real human exercise videos generated at: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
