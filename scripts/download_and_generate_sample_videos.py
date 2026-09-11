import os
import math
import cv2
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

EXERCISES = [
    ("01_squatting", "Squatting - Bilateral Knee & Hip Deep Mechanics", "squatting"),
    ("02_lunging", "Lunges & Split Squats - Single-Leg Stability", "lunging"),
    ("03_deadlift", "Deadlift & Hinging - Posterior Chain Mechanics", "deadlift"),
    ("04_running", "Running & Gait - Cadence & Stride Mechanics", "running"),
    ("05_sprinting", "Sprinting - Max Velocity Mechanics", "sprinting"),
    ("06_jumping", "Jumping - Vertical Propulsion & Takeoff", "jumping"),
    ("07_landing", "Landing - Deceleration & Impact Attenuation", "landing"),
    ("08_cutting", "Cutting & Change-of-Direction - Lateral Shear", "cutting"),
    ("09_throwing", "Throwing & Overhead Serving - Kinetic Chain", "throwing"),
    ("10_upper_body_push", "Upper Body Press - Shoulder & Elbow Mechanics", "upper_body_push"),
    ("11_agility_drills", "Agility Ladder & Shuttle - Fast Footwork", "agility_drills"),
    ("12_single_leg_balance", "Single-Leg Balance - Dynamic Postural Control", "single_leg_balance"),
    ("13_plyometrics", "Plyometrics & Box Jumps - Explosive Power", "plyometrics"),
    ("14_swimming_rowing", "Swimming & Rowing - Kinematic Coordination", "swimming_rowing"),
    ("15_sport_specific_drills", "Sport-Specific Drills - Agility & Joint Integrity", "sport_specific_drills"),
]

WIDTH, HEIGHT = 640, 480
FPS = 30
DURATION_SEC = 5
TOTAL_FRAMES = FPS * DURATION_SEC

def draw_grid(img):
    for x in range(0, WIDTH, 40):
        cv2.line(img, (x, 0), (x, HEIGHT), (40, 40, 50), 1)
    for y in range(0, HEIGHT, 40):
        cv2.line(img, (0, y), (WIDTH, y), (40, 40, 50), 1)

def generate_video(filename, title, ex_type):
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, FPS, (WIDTH, HEIGHT))

    for frame_idx in range(TOTAL_FRAMES):
        t = (frame_idx / FPS) * 2 * math.pi
        
        # Dark tech background
        img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        img[:] = (20, 18, 30) # Dark purple background
        draw_grid(img)

        # Header HUD
        cv2.rectangle(img, (0, 0), (WIDTH, 50), (35, 28, 55), -1)
        cv2.line(img, (0, 50), (WIDTH, 50), (124, 58, 237), 2)
        cv2.putText(img, "MOTION IQ - OPTICAL MOVEMENT ANALYSIS", (15, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (167, 139, 250), 1, cv2.LINE_AA)
        cv2.putText(img, f"EXERCISE: {title.upper()}", (15, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        # Telemetry HUD right corner
        fps_text = f"FRAME: {frame_idx+1}/{TOTAL_FRAMES} | 30 FPS"
        cv2.putText(img, fps_text, (WIDTH - 220, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (52, 211, 153), 1, cv2.LINE_AA)

        # Kinematic Skeleton Math
        center_x = WIDTH // 2
        hip_y = 240

        if ex_type in ["squatting", "deadlift", "plyometrics"]:
            depth = math.sin(t)
            hip_y = int(240 + depth * 50)
            knee_flexion = int(90 + depth * 45)
            trunk_angle = int(15 + depth * 15)
            
            hip_x = center_x
            knee_x = hip_x - 30
            knee_y = hip_y + 70
            ankle_x = knee_x + 10
            ankle_y = knee_y + 80
            
            neck_x = hip_x + int(math.sin(math.radians(trunk_angle)) * 70)
            neck_y = hip_y - int(math.cos(math.radians(trunk_angle)) * 70)
            head_x = neck_x
            head_y = neck_y - 25

        elif ex_type in ["running", "sprinting", "agility_drills"]:
            stride = math.sin(t * 2)
            hip_y = 220 + int(abs(stride) * 15)
            hip_x = center_x
            
            knee_x = hip_x + int(stride * 50)
            knee_y = hip_y + 65
            ankle_x = knee_x - int(stride * 30)
            ankle_y = knee_y + 70
            
            neck_x = hip_x - 10
            neck_y = hip_y - 75
            head_x = neck_x
            head_y = neck_y - 25

        elif ex_type in ["jumping", "landing"]:
            jump_h = math.sin(t)
            hip_y = int(250 - jump_h * 70)
            hip_x = center_x
            
            knee_x = hip_x - int(jump_h * 20)
            knee_y = hip_y + 70
            ankle_x = knee_x + 10
            ankle_y = knee_y + 70
            
            neck_x = hip_x
            neck_y = hip_y - 75
            head_x = neck_x
            head_y = neck_y - 25

        else: # Default throwing, balance, lunging, etc.
            motion = math.sin(t)
            hip_y = int(230 + motion * 20)
            hip_x = center_x
            
            knee_x = hip_x + int(motion * 35)
            knee_y = hip_y + 70
            ankle_x = knee_x - int(motion * 20)
            ankle_y = knee_y + 70
            
            neck_x = hip_x + int(motion * 15)
            neck_y = hip_y - 75
            head_x = neck_x
            head_y = neck_y - 25

        # Draw Skeleton Landmarks & Limbs
        # Head
        cv2.circle(img, (head_x, head_y), 18, (248, 250, 252), 2)
        cv2.circle(img, (head_x, head_y), 6, (124, 58, 237), -1)

        # Spine
        cv2.line(img, (neck_x, neck_y), (hip_x, hip_y), (56, 189, 248), 4)

        # Legs
        cv2.line(img, (hip_x, hip_y), (knee_x, knee_y), (52, 211, 153), 4)
        cv2.line(img, (knee_x, knee_y), (ankle_x, ankle_y), (251, 191, 36), 4)

        # Arms
        elbow_x = neck_x + 35
        elbow_y = neck_y + 35
        wrist_x = elbow_x + 20
        wrist_y = elbow_y + 30
        cv2.line(img, (neck_x, neck_y), (elbow_x, elbow_y), (129, 140, 248), 3)
        cv2.line(img, (elbow_x, elbow_y), (wrist_x, wrist_y), (167, 139, 250), 3)

        # Joint Keypoint Nodes
        joints = [
            ((neck_x, neck_y), (56, 189, 248), "Neck"),
            ((hip_x, hip_y), (56, 189, 248), "Hip"),
            ((knee_x, knee_y), (52, 211, 153), "Knee"),
            ((ankle_x, ankle_y), (251, 191, 36), "Ankle"),
            ((elbow_x, elbow_y), (129, 140, 248), "Elbow")
        ]

        for (pt, col, name) in joints:
            cv2.circle(img, pt, 7, col, -1)
            cv2.circle(img, pt, 9, (255, 255, 255), 1)

        # Bottom Status Banner
        cv2.rectangle(img, (0, HEIGHT - 40), (WIDTH, HEIGHT), (15, 12, 25), -1)
        cv2.line(img, (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), (52, 211, 153), 1)
        cv2.putText(img, "✓ MediaPipe 33 Skeletal Keypoints Tracked | Status: Optimal", (15, HEIGHT - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (203, 213, 225), 1, cv2.LINE_AA)

        out.write(img)

    out.release()
    print(f"Generated sample video: {filename}.mp4 ({os.path.getsize(filepath)} bytes)")

def main():
    print("Generating 15 exercise sample videos...")
    for fn, title, ex_type in EXERCISES:
        generate_video(fn, title, ex_type)
    print(f"\nAll 15 sample exercise videos successfully created in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
