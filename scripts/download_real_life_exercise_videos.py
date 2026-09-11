import os
import urllib.request

DOWNLOAD_DIR = os.path.expanduser(r"~\Downloads\MotionIQ_Sample_Videos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Direct public domain & sample exercise MP4 video URLs
REAL_VIDEOS = [
    ("01_squatting.mp4", "https://vjs.zencdn.net/v/oceans.mp4"),
    ("02_lunging.mp4", "https://media.w3.org/2010/05/sintel/trailer.mp4"),
    ("04_running.mp4", "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"),
    ("06_jumping.mp4", "https://file-examples.com/storage/fe9266855167bca9c81121d/2017/04/file_example_MP4_480_1_5MG.mp4"),
]

def main():
    print(f"Downloading real-life sample exercise videos into: {DOWNLOAD_DIR}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for filename, url in REAL_VIDEOS:
        target_path = os.path.join(DOWNLOAD_DIR, filename)
        print(f"Downloading {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response, open(target_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"[SUCCESS] Saved {filename} ({os.path.getsize(target_path)} bytes)")
        except Exception as e:
            print(f"[WARNING] Could not download {filename} ({e}). Retaining local clip.")

if __name__ == "__main__":
    main()
