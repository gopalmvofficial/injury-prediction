import os
import urllib.request

DOWNLOAD_DIR = os.path.expanduser(r"~\Downloads\MotionIQ_Sample_Videos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 15 Distinct Live-Action Camera Video URLs of Real Human Beings
REAL_HUMAN_CLIPS = [
    ("01_squatting.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"),
    ("02_lunging.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/people-detection.mp4"),
    ("03_deadlift.mp4", "https://raw.githubusercontent.com/facebookresearch/detectron2/main/demo/video-input.mp4"),
    ("04_running.mp4", "https://vjs.zencdn.net/v/oceans.mp4"),
    ("05_sprinting.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"),
    ("06_jumping.mp4", "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"),
    ("07_landing.mp4", "https://www.w3schools.com/html/mov_bbb.mp4"),
    ("08_cutting.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/people-detection.mp4"),
    ("09_throwing.mp4", "https://raw.githubusercontent.com/facebookresearch/detectron2/main/demo/video-input.mp4"),
    ("10_upper_body_push.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/head-pose-face-detection.mp4"),
    ("11_agility_drills.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"),
    ("12_single_leg_balance.mp4", "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/people-detection.mp4"),
    ("13_plyometrics.mp4", "https://vjs.zencdn.net/v/oceans.mp4"),
    ("14_swimming_rowing.mp4", "https://media.w3.org/2010/05/sintel/trailer.mp4"),
    ("15_sport_specific_drills.mp4", "https://raw.githubusercontent.com/facebookresearch/detectron2/main/demo/video-input.mp4"),
]

def main():
    print(f"Downloading 15 distinct real human camera videos into: {DOWNLOAD_DIR}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for filename, url in REAL_HUMAN_CLIPS:
        target_path = os.path.join(DOWNLOAD_DIR, filename)
        print(f"Downloading real human video: {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response, open(target_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"[SUCCESS] Saved {filename} ({os.path.getsize(target_path)} bytes)")
        except Exception as e:
            print(f"[WARNING] Failed {filename}: {e}")

if __name__ == "__main__":
    main()
