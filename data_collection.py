import cv2
import mediapipe as mp
from utills.web import GetVideosFromFile
import av
import io
import numpy as np


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def collection(vid):
    for name, mp4 in vid.items():

        buffer = io.BytesIO(mp4)
        container = av.open(buffer)
        video_sequence = []

        for frame in container.decode(video=0):
            cv_image = frame.to_ndarray(format="bgr24")

            left_hand = np.zeros(63)
            right_hand = np.zeros(63)
            result = hands.process(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(cv_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow('d', cv_image)
            if cv2.waitKey(1) & 0XFF == ord('q'):
                break

            if result.multi_hand_landmarks and result.multi_handedness:
                for hand_landmarks, handness in zip(result.multi_hand_landmarks, result.multi_handedness):
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.extend(([lm.x, lm.y, lm.z]))

                    label = handness.classification[0].label

                    if label == 'Left':
                        left_hand = np.array(landmarks)
                    elif label == 'Right':
                        right_hand = np.array(landmarks)

            frame_data = np.concatenate([left_hand, right_hand])
            video_sequence.append(frame_data)

        while len(video_sequence) < 300:
            video_sequence.append(np.zeros(126))
        if len(video_sequence) > 300:
            video_sequence = video_sequence[:300]

        np.save(f"data_{name}", video_sequence)
    cv2.destroyAllWindows()

vid = GetVideosFromFile()
collection(vid)

