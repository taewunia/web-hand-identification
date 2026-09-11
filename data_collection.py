import cv2
import mediapipe as mp
import numpy as np
from utills.web import GetVideosFromFile, GetVideoUrl


# 국립국어원에서 추출한 MP4 영상 URL
video_url = GetVideoUrl('01a13035-b352-4375-ae83-d7e5c8c4618b', '0')

# URL을 바로 VideoCapture에 전달
cap = cv2.VideoCapture('https://sldict.korean.go.kr/multimedia/multimedia_files/convert/20191022/630116/MOV000235141_700X466.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Sign Video Stream", frame)

    if cv2.waitKey(30) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
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