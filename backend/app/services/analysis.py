from pathlib import Path
import math
import cv2

try:
    import mediapipe as mp
except Exception:
    mp = None


def angle(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    ba = (ax-bx, ay-by); bc = (cx-bx, cy-by)
    den = math.hypot(*ba) * math.hypot(*bc)
    if den == 0: return None
    value = max(-1, min(1, (ba[0]*bc[0] + ba[1]*bc[1]) / den))
    return math.degrees(math.acos(value))


def analyze_video(video_path: Path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError('Could not open the uploaded video.')
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    sample_every = max(1, frames // 60) if frames else 1
    processed = detected = 0
    knees, hips, ankles = [], [], []

    pose = None
    if mp is not None:
        try:
            pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        except Exception:
            pose = None

    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        if idx % sample_every != 0:
            idx += 1; continue
        processed += 1
        if pose is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if result.pose_landmarks:
                lm = result.pose_landmarks.landmark
                detected += 1
                # MediaPipe indices: hip 23/24, knee 25/26, ankle 27/28
                for hip_i, knee_i, ankle_i in [(23,25,27),(24,26,28)]:
                    h=(lm[hip_i].x,lm[hip_i].y); k=(lm[knee_i].x,lm[knee_i].y); a=(lm[ankle_i].x,lm[ankle_i].y)
                    val=angle(h,k,a)
                    if val is not None and 40 < val < 180: knees.append(val)
                for sh_i, hip_i, knee_i in [(11,23,25),(12,24,26)]:
                    s=(lm[sh_i].x,lm[sh_i].y); h=(lm[hip_i].x,lm[hip_i].y); k=(lm[knee_i].x,lm[knee_i].y)
                    val=angle(s,h,k)
                    if val is not None and 30 < val < 180: hips.append(val)
                for knee_i, ankle_i, foot_i in [(25,27,31),(26,28,32)]:
                    k=(lm[knee_i].x,lm[knee_i].y); a=(lm[ankle_i].x,lm[ankle_i].y); f=(lm[foot_i].x,lm[foot_i].y)
                    val=angle(k,a,f)
                    if val is not None and 20 < val < 180: ankles.append(val)
        idx += 1
    cap.release()
    if pose is not None:
        pose.close()

    detection_rate = (detected / processed * 100) if processed else 0
    # A transparent milestone-2 heuristic: lower detection and extreme average knee angle reduce movement score.
    avg_knee = sum(knees)/len(knees) if knees else 120.0
    knee_penalty = min(35, abs(avg_knee - 120) * 0.45)
    movement_score = max(0, min(100, detection_rate - knee_penalty + 20 if detection_rate else 58))
    risk_score = max(0, min(100, 100 - movement_score + (12 if avg_knee < 75 or avg_knee > 165 else 0)))
    risk_level = 'High' if risk_score >= 65 else 'Medium' if risk_score >= 35 else 'Low'
    rec = {
        'High': 'Review technique with a qualified coach, prioritize controlled movement, warm-up and recovery, and consider professional assessment if symptoms are present.',
        'Medium': 'Improve movement control, warm-up and mobility work, and monitor technique during training.',
        'Low': 'Maintain current technique, warm-up and recovery practices while continuing to monitor movement quality.'
    }[risk_level]
    return {
        'movement_score': round(movement_score, 1), 'risk_score': round(risk_score, 1), 'risk_level': risk_level,
        'knee_angle': round(sum(knees)/len(knees),1) if knees else None,
        'hip_angle': round(sum(hips)/len(hips),1) if hips else None,
        'ankle_angle': round(sum(ankles)/len(ankles),1) if ankles else None,
        'movement_quality': round(movement_score,1), 'frames_processed': processed,
        'pose_detection_rate': round(detection_rate,1), 'recommendation': rec,
        'pose_engine': 'MediaPipe Pose' if pose is not None else 'OpenCV fallback'
    }
