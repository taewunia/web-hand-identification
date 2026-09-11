import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(1)
MAX_EPOCH = 100
CURRENT_EPOCH = 0
MAX_FRAME = 30
data = []
final_data = []
zero_data = np.zeros(63)
action = 'hello'

while cap.isOpened() and CURRENT_EPOCH < MAX_EPOCH:
    ret, frame = cap.read()
    if not ret:
        print("카메라 오류")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        joint = []
        for lm in hand_landmarks.landmark:
            joint.extend([lm.x, lm.y, lm.z])
        data.append(np.array(joint))

    else:
        data.append(zero_data)

    cv2.putText(frame, f"Action:{action} EPOCH:{CURRENT_EPOCH+1}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    if len(data) == MAX_FRAME:
        final_data.append(data)
        CURRENT_EPOCH += 1
        data = []

    cv2.imshow('test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
final_data = np.array(final_data)
print(final_data)
np.save("data_mountain", final_data)