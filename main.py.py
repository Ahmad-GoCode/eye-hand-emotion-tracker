import time
import cv2
import mediapipe as mpa
import subprocess
import os
import webbrowser
from fer import FER

# ----------------- الإعدادات | CONFIGURATION -----------------
HOLD_TIME = 3.0           # ثواني لإغلاق العين لتنفيذ الأمر
COOLDOWN = 4.0            # فترة تهدئة بعد تنفيذ أمر
CLOSED_EYE_RATIO = 0.25   # نسبة إغلاق العين
CONFIRM_RESTART = False   # تفعيل إعادة التشغيل
ERA_INDEX = 0             # رقم الكاميرا

# ----------------- التهيئة | INITIALIZATION -----------------
mp_face_mesh = mpa.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

mp_hands = mpa.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mpa.solutions.drawing_utils

# FER emotion detector
emotion_detector = FER(mtcnn=True)

# ----------------- نقاط العين | Eye Landmarks -----------------
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]

# ----------------- Functions -----------------
def ahmad_eye_ratio(landmarks, eye_points):
    pts = [landmarks[i] for i in eye_points]
    a = ((pts[2].x - pts[4].x)**2 + (pts[2].y - pts[4].y)**2)**0.5
    b = ((pts[1].x - pts[5].x)**2 + (pts[1].y - pts[5].y)**2)**0.5
    c = ((pts[0].x - pts[3].x)**2 + (pts[0].y - pts[3].y)**2)**0.5
    if c == 0:
        return 0.0
    return (a + b) / (2.0 * c)

def ahmad_draw_eye(image, landmarks, eye_points, color=(0,255,0)):
    h, w = image.shape[:2]
    for i in eye_points:
        lm = landmarks[i]
        x = int(lm.x * w)
        y = int(lm.y * h)
        cv2.circle(image, (x, y), 2, color, -1)

def ahmad_open_chrome():
    try:
        os.system('start chrome')
    except:
        webbrowser.open('https://www.google.com')

def ahmad_open_explorer():
    try:
        os.system('explorer')
    except:
        print("تعذر فتح مستكشف الملفات.")

def ahmad_restart():
    print("طلب إعادة تشغيل.")
    if not CONFIRM_RESTART:
        print("إعادة التشغيل غير مفعلة.")
        return
    os.system('shutdown /r /t 0')

def ahmad_eye_logic(left, right, now, timers, last_time):
    l_closed = left is not None and left < CLOSED_EYE_RATIO
    r_closed = right is not None and right < CLOSED_EYE_RATIO

    if l_closed and r_closed:
        if timers['both'] is None:
            timers['both'] = now
        elif (now - timers['both']) >= HOLD_TIME and (now - last_time) > COOLDOWN:
            print("العينين مغلقتين -> إعادة تشغيل")
            ahmad_restart()
            return now, {'left': None, 'right': None, 'both': None}
    else:
        timers['both'] = None

    if l_closed and not r_closed:
        if timers['left'] is None:
            timers['left'] = now
        elif (now - timers['left']) >= HOLD_TIME and (now - last_time) > COOLDOWN:
            print("العين اليسرى مغلقة -> مستكشف الملفات")
            ahmad_open_explorer()
            return now, {'left': None, 'right': None, 'both': None}
    else:
        timers['left'] = None

    if r_closed and not l_closed:
        if timers['right'] is None:
            timers['right'] = now
        elif (now - timers['right']) >= HOLD_TIME and (now - last_time) > COOLDOWN:
            print("العين اليمنى مغلقة -> كروم")
            ahmad_open_chrome()
            return now, {'left': None, 'right': None, 'both': None}
    else:
        timers['right'] = None

    return last_time, timers

def ahmad_hand_gestures(hand_results, frame):
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            thumb_mcp = hand_landmarks.landmark[2]
            index_mcp = hand_landmarks.landmark[5]
            wrist = hand_landmarks.landmark[0]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            tips = [hand_landmarks.landmark[i] for i in [4, 8, 12, 16, 20]]

            if (thumb_tip.y < thumb_mcp.y and thumb_tip.y < index_mcp.y and thumb_tip.y < wrist.y and
                abs(thumb_tip.y - thumb_ip.y) > 0.07):
                cv2.putText(frame, "Thumbs Up!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            elif (thumb_tip.y > thumb_mcp.y and thumb_tip.y > index_mcp.y and thumb_tip.y > wrist.y and
                  abs(thumb_tip.y - thumb_ip.y) > 0.07):
                cv2.putText(frame, "Thumbs Down!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            elif all(tip.y < wrist.y for tip in tips[1:]):
                cv2.putText(frame, "Hi (Open Palm)", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            elif (index_tip.y < wrist.y and middle_tip.y < wrist.y and
                  ring_tip.y > wrist.y and pinky_tip.y > wrist.y):
                cv2.putText(frame, "Peace (V)", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
            elif all(abs(tip.y - wrist.y) < 0.05 for tip in tips):
                cv2.putText(frame, "Fist", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
            elif ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5 < 0.05:
                cv2.putText(frame, "OK Sign", (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,200), 2)

def ahmad_main():
    cap = cv2.VideoCapture(ERA_INDEX)
    if not cap.isOpened():
        print(f"الكاميرا غير متصلة: {ERA_INDEX}")
        return

    # خفض الدقة
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    timers = {'left': None, 'right': None, 'both': None}
    last_action_time = 0.0

    # مشاعر (FER) - نخزن آخر نتيجة
    last_emotion = ("Neutral", 0.0)
    last_emotion_time = 0.0

    print("تشغيل تتبع العين واليد + الانفعالات. للخروج اضغط ESC أو q.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("لم يتم استقبال إطار الكاميرا. الخروج.")
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        now = time.time()

        # --- FaceMesh ---
        results = face_mesh.process(rgb_frame)
        left_ear = right_ear = None

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            try:
                left_ear = ahmad_eye_ratio(landmarks, LEFT_EYE)
                right_ear = ahmad_eye_ratio(landmarks, RIGHT_EYE)
            except:
                left_ear = right_ear = None

            ahmad_draw_eye(frame, landmarks, LEFT_EYE, color=(0,200,255))
            ahmad_draw_eye(frame, landmarks, RIGHT_EYE, color=(0,200,255))

            if left_ear is not None:
                cv2.putText(frame, f"L_EAR: {left_ear:.3f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            if right_ear is not None:
                cv2.putText(frame, f"R_EAR: {right_ear:.3f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            last_action_time, timers = ahmad_eye_logic(left_ear, right_ear, now, timers, last_action_time)
        else:
            cv2.putText(frame, "لا يوجد وجه", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            timers = {'left': None, 'right': None, 'both': None}

        # --- Hand Gestures ---
        hand_results = hands.process(rgb_frame)
        ahmad_hand_gestures(hand_results, frame)

        # --- Emotions (FER) ---
        # نظهر آخر نتيجة دائمًا
        cv2.putText(frame, f"Emotion: {last_emotion[0]} ({last_emotion[1]:.2f})",
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,255,100), 2)

        # نحدث المشاعر كل ثانية فقط
        if now - last_emotion_time >= 1.0:
            emotions = emotion_detector.detect_emotions(frame)
            if emotions:
                top_emotion, score = sorted(emotions[0]["emotions"].items(),
                                            key=lambda x: x[1], reverse=True)[0]
                last_emotion = (top_emotion, score)
            last_emotion_time = now

        # --- Info line ---
        cv2.putText(frame, f"THRESH: {CLOSED_EYE_RATIO:.2f} HOLD(s): {HOLD_TIME}",
                    (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

        cv2.imshow("Ahmad Eye-Hand-Emotion Tracker (ESC/q)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ahmad_main()
