import cv2
import mediapipe as mp
import numpy as np
import time
import socket
import json
from ultralytics import YOLO
from lego_fsm_controller import FSM, UIState

# === UDP CONFIG ===
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
SEND_RATE = 0.1  # seconds
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_message(msg):
    try:
        sock.sendto(msg.encode("utf-8"), (UDP_IP, UDP_PORT))
    except Exception as e:
        print(f"[UDP Error] {e}")

# === CÁMARA ===
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

# === MediaPipe ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6)

# === FSM ===
fsm = FSM()
hover_state = None
hover_start = 0
last_activation_time = 0
last_button_pressed = None

# === Escaneo ===
scan_start_time = None
SCAN_DURATION = 3.0
SCAN_TOP, SCAN_BOTTOM = 100, 650
scan_flash = False

# === Layout ===
UI_WIDTH = 1170
UI_HEIGHT = 884

#=== YOLO ===
model = YOLO('runs/detect/lego_model3/weights/best.pt')

CONTROL_BTNS = [
    {"name": "SCAN",  "x": 403, "y": 127, "radius": 40},
    {"name": "RETRY", "x": 780, "y": 134, "radius": 40},
    {"name": "BACK",  "x": 535, "y": 129, "radius": 45},
    {"name": "NEXT",  "x": 644, "y": 129, "radius": 45},
]

SET_BTNS = [
    {"name": "SET 1", "x": 138, "y": 136, "radius": 70},
    {"name": "SET 2", "x": 133, "y": 337, "radius": 70},
    {"name": "SET 3", "x": 133, "y": 558, "radius": 70},
    {"name": "SET 4", "x": 133, "y": 752, "radius": 70},
]

def draw_layout(state, selected_set=None, pointer=None, scan_y=None, flash=False):
    img = np.ones((UI_HEIGHT, UI_WIDTH, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (300, 240), (1096, 800), (200, 200, 200), 2)
    cv2.rectangle(img, (870, 20), (1000, 120), (0, 0, 0), 2)
    if state == UIState.ASSEMBLY:
        cv2.putText(img, f"Step {fsm.step_index+1}", (880, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if state == UIState.START:
        cv2.putText(img, "Put your legos here", (350, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

    for btn in CONTROL_BTNS:
        x, y, r = btn["x"], btn["y"], btn["radius"]
        color = (0, 255, 0) if btn["name"] == hover_state else (100, 100, 255)
        if state == UIState.START and btn["name"] == "SCAN":
            cv2.circle(img, (x, y), r, (0, 200, 0), -1)
        elif state == UIState.SCAN and btn["name"] == "SCAN":
            color = (0, 255, 0) if flash else (200, 255, 200)
            cv2.circle(img, (x, y), r, color, -1)
        elif state == UIState.FINISH and btn["name"] == "RETRY":
            cv2.circle(img, (x, y), r, (0, 200, 0), -1)
        else:
            cv2.circle(img, (x, y), r, color, 2)
        cv2.putText(img, btn["name"], (x - 30, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255) if color == (0, 255, 0) else (50, 50, 200), 2)

    for btn in SET_BTNS:
        x, y, r = btn["x"], btn["y"], btn["radius"]
        filled = selected_set == btn["name"]
        highlight = state == UIState.CHOOSE
        color = (0, 200, 0) if filled or highlight else (180, 180, 180)
        cv2.circle(img, (x, y), r, color, -1)
        cv2.putText(img, btn["name"], (x - 30, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255) if color[1] > 180 else (50, 50, 50), 2)

    if pointer:
        cv2.circle(img, pointer, 10, (0, 255, 0), -1)
    if state == UIState.SCAN and scan_y is not None:
        cv2.line(img, (300, scan_y), (1096, scan_y), (0, 255, 0), 2)

    return img

# === Main loop ===
frame_count = 0
last_sent = time.time()
prev_state = None
prev_step = -1
prev_pointer = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, -1)
    frame = frame[129:1013, 302:1472]
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    now = time.time()
    pointer = None
    scan_y = None
    scan_flash = (frame_count // 10) % 2 == 0
    frame_count += 1

    if fsm.state == UIState.SCAN:
        if scan_start_time is None:
            scan_start_time = time.time()

        seconds_elapsed = time.time() - scan_start_time
        countdown = max(0, 5 - int(seconds_elapsed))

        if countdown > 0:
            countdown_img = frame.copy()
            cv2.putText(countdown_img, f"Scanning in {countdown}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.imshow("Debug Centers", countdown_img)
            img = draw_layout(fsm.state, fsm.selected_set, pointer, scan_y, scan_flash)
            cv2.imshow("UI con dedo", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        results_scan = model(frame, conf=0.05, verbose=False)
        pos_x = []
        pos_y = []

        debug_frame = frame.copy()

        for rs in results_scan:
            for box in rs.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{model.names[cls_id]} {conf:.2f}"
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                pt1 = (300, 240)
                pt2 = (1096, 800)
                norm_x = (cx - pt1[0]) / (pt2[0] - pt1[0])
                norm_y = (cy - pt1[1]) / (pt2[1] - pt1[1])

                pos_x.append(norm_x)
                pos_y.append(norm_y)

                cv2.circle(debug_frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(debug_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        cv2.imshow("Debug Centers", debug_frame)
        scan_start_time = None
        fsm.handle_input("choose")

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        fx = int(hand.landmark[8].x * w)
        fy = int(hand.landmark[8].y * h)
        ui_x = int(fx * UI_WIDTH / w)
        ui_y = int(fy * UI_HEIGHT / h)
        pointer = (ui_x, ui_y)

        all_btns = CONTROL_BTNS + SET_BTNS
        hit = False
        for btn in all_btns:
            bx, by, br = btn["x"], btn["y"], btn["radius"]
            if (ui_x - bx) ** 2 + (ui_y - by) ** 2 < br ** 2:
                hit = True
                if hover_state != btn["name"]:
                    hover_state = btn["name"]
                    hover_start = now
                elif now - hover_start > 0.5 and now - last_activation_time > 1.0:
                    if btn["name"] != last_button_pressed:
                        print(f"🟢 Activado: {btn['name']}")
                        fsm.handle_input(btn["name"])
                        last_activation_time = now
                        last_button_pressed = btn["name"]
                        hover_state = None
                        hover_start = 0
                break
        if not hit:
            hover_state = None
            hover_start = 0
            last_button_pressed = None

    if time.time() - last_sent > SEND_RATE:
        try:
            data = {
                "state": fsm.state,
                "step": fsm.step_index + 1 if fsm.state == UIState.ASSEMBLY else None,
                "selected_set": fsm.selected_set,
                "pos_x": pos_x,
                "pos_y": pos_y,
            }
            json_data = json.dumps(data)
            send_udp_message(json_data)
        except Exception as e:
            print(f"[UDP Error] {e}")
        last_sent = time.time()

    img = draw_layout(fsm.state, fsm.selected_set, pointer, scan_y, scan_flash)
    cv2.imshow("UI con dedo", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
sock.close()
cv2.destroyAllWindows()