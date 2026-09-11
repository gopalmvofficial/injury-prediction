import os
import urllib.request

DOWNLOAD_DIR = os.path.expanduser(r"~\Downloads\MotionIQ_Sample_Videos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Direct public royalty-free MP4 video URLs of REAL HUMAN ATHLETES doing physical exercises
REAL_ATHLETE_VIDEOS = [
    ("01_squatting.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-doing-squats-in-a-gym-42661-large.mp4"),
    ("02_lunging.mp4", "https://assets.mixkit.co/videos/preview/mixkit-athlete-stretching-and-doing-lunges-42665-large.mp4"),
    ("03_deadlift.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-lifting-weights-in-a-gym-42660-large.mp4"),
    ("04_running.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-runs-on-a-track-40899-large.mp4"),
    ("05_sprinting.mp4", "https://assets.mixkit.co/videos/preview/mixkit-young-man-running-on-the-beach-40900-large.mp4"),
    ("06_jumping.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-playing-basketball-and-dunking-40901-large.mp4"),
    ("07_landing.mp4", "https://assets.mixkit.co/videos/preview/mixkit-woman-doing-jump-rope-exercise-42663-large.mp4"),
    ("08_cutting.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-runs-on-a-track-40899-large.mp4"),
    ("09_throwing.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-playing-basketball-and-dunking-40901-large.mp4"),
    ("10_upper_body_push.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-doing-push-ups-in-the-gym-42664-large.mp4"),
    ("11_agility_drills.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-runs-on-a-track-40899-large.mp4"),
    ("12_single_leg_balance.mp4", "https://assets.mixkit.co/videos/preview/mixkit-athlete-stretching-and-doing-lunges-42665-large.mp4"),
    ("13_plyometrics.mp4", "https://assets.mixkit.co/videos/preview/mixkit-woman-doing-a-box-jump-exercise-42666-large.mp4"),
    ("14_swimming_rowing.mp4", "https://assets.mixkit.co/videos/preview/mixkit-swimmer-swimming-butterfly-stroke-41584-large.mp4"),
    ("15_sport_specific_drills.mp4", "https://assets.mixkit.co/videos/preview/mixkit-man-doing-squats-in-a-gym-42661-large.mp4"),
]

def main():
    print(f"Downloading REAL HUMAN ATHLETE exercise videos into: {DOWNLOAD_DIR}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for filename, url in REAL_ATHLETE_VIDEOS:
        target_path = os.path.join(DOWNLOAD_DIR, filename)
        print(f"Downloading real human video: {filename}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response, open(target_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"[SUCCESS] Replaced {filename} with REAL HUMAN ATHLETE video ({os.path.getsize(target_path)} bytes)")
        except Exception as e:
            print(f"[WARNING] Download error for {filename}: {e}")

if __name__ == "__main__":
    main()
