import cv2
import mediapipe as mp
import pyautogui
import time
import math

cap = None  # Will be set when gesture control starts
should_stop_callback = None  # Callback function for stopping gesture recognition

# MediaPipe initialization
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Screen size
screen_width, screen_height = pyautogui.size()

# Variables for tracking
prev_x, prev_y = 0, 0
click_threshold = 40
gesture_delay = 1
last_gesture_time = 0

# Set callback for external shutdown control
def set_should_stop_callback(callback):
    global should_stop_callback
    should_stop_callback = callback

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def fingers_up(landmarks):
    fingers = []
    # Thumb
    fingers.append(landmarks[4][0] > landmarks[3][0])
    # Other fingers
    for tip in [8, 12, 16, 20]:
        fingers.append(landmarks[tip][1] < landmarks[tip - 2][1])
    return fingers

def perform_click():
    pyautogui.click()

def perform_right_click():
    pyautogui.click(button='right')

def perform_scroll(up=True):
    pyautogui.scroll(300 if up else -300)

def move_cursor(x, y):
    pyautogui.moveTo(x, y)

def start_gesture_control():
    global cap, prev_x, prev_y, last_gesture_time
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        if should_stop_callback and should_stop_callback():
            break

        success, img = cap.read()
        if not success:
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        img_height, img_width, _ = img.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    lm_x, lm_y = int(lm.x * img_width), int(lm.y * img_height)
                    lm_list.append((lm_x, lm_y))

                if lm_list:
                    index_x, index_y = lm_list[8]
                    move_x = screen_width / img_width * index_x
                    move_y = screen_height / img_height * index_y
                    move_cursor(move_x, move_y)

                    fingers = fingers_up(lm_list)
                    current_time = time.time()

                    # Left click: Only index finger up
                    if fingers[1] and not any(fingers[2:]) and not fingers[0]:
                        if current_time - last_gesture_time > gesture_delay:
                            perform_click()
                            last_gesture_time = current_time

                    # Right click: Index + middle finger up
                    elif fingers[1] and fingers[2] and not any(fingers[3:]) and not fingers[0]:
                        if current_time - last_gesture_time > gesture_delay:
                            perform_right_click()
                            last_gesture_time = current_time

                    # Scroll up: All fingers up
                    elif all(fingers):
                        if current_time - last_gesture_time > gesture_delay:
                            perform_scroll(up=True)
                            last_gesture_time = current_time

                    # Scroll down: Only pinky folded
                    elif fingers[0] and fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
                        if current_time - last_gesture_time > gesture_delay:
                            perform_scroll(up=False)
                            last_gesture_time = current_time

                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) == 27:  # Esc key to exit
            break

    if cap:
        cap.release()
    cv2.destroyAllWindows()
