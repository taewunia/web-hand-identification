import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset,DataLoader
import numpy as np
import cv2
import mediapipe as mp
from collections import deque
import os

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(device)


EPOCH = 30
BATCH_SIZE= 30


class GestureDataset(Dataset):
    def __init__(self):
        love_data = np.load('data/data_love.npy')
        poop_data = np.load('data/data_poop.npy')
        mountain_data = np.load('data/data_mountain.npy')

        hello_label = np.zeros(len(love_data))
        fist_label = np.ones(len(poop_data))
        mountain_label = np.full(len(mountain_data), 2)

        self.x_data = np.concatenate((love_data, poop_data, mountain_data), axis=0)
        self.y_data = np.concatenate((hello_label, fist_label, mountain_label), axis=0)

    def __len__(self):
        return len(self.x_data)

    def __getitem__(self, idx):
        x = torch.FloatTensor(self.x_data[idx])
        y = torch.LongTensor([self.y_data[idx]])
        return x, y

DS = GestureDataset()
DL = DataLoader(DS, batch_size=BATCH_SIZE, shuffle=True)

class D_cnn(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Sequential(nn.Conv1d(in_channels=63,
                                              out_channels=128,
                                              kernel_size=3,
                                              padding=1
                                              ),
                                    nn.BatchNorm1d(128),
                                    nn.MaxPool1d(kernel_size=2,
                                                 stride=2),
                                    nn.ReLU()) #30 -> 15

        self.conv2 = nn.Sequential(nn.Conv1d(in_channels=128,
                                              out_channels=256,
                                              kernel_size=3,
                                              padding=1
                                              ),
                                    nn.BatchNorm1d(256),
                                    nn.MaxPool1d(kernel_size=2,
                                                 stride=2),
                                    nn.ReLU()) #15 -> 7

        self.conv3 = nn.Sequential(nn.Conv1d(in_channels=256,
                                              out_channels=512,
                                              kernel_size=3,
                                              padding=1
                                              ),
                                    nn.BatchNorm1d(512),
                                    nn.MaxPool1d(kernel_size=2,
                                                 stride=2),
                                    nn.ReLU()) #7-> 3

        self.avg_pool = nn.AdaptiveAvgPool1d(1)

        self.fc_layer = nn.Linear(512, 3)

    def forward(self, x):
        x = x.permute(0,2,1)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.avg_pool(x)
        x = torch.flatten(x, 1)
        x = self.fc_layer(x)
        return x

model = D_cnn()
print(model)


model = model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=0.001)

for epoch in range(EPOCH):
    for x, y in DL:
        x, y = x.to(device), y.to(device)
        result = model(x)
        loss = criterion(result, y.squeeze())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f' Epoch {epoch+1}/{EPOCH} | Loss: {loss.item():.4f}')


model.eval()

idx_list = [2]

img_love = cv2.imread('/Users/choetaewon/PyCharmMiscProject/model/heart.jpg')
img_poop = cv2.imread('/Users/choetaewon/PyCharmMiscProject/model/poop.jpeg')
img_mountain = cv2.imread('/Users/choetaewon/PyCharmMiscProject/model/mountain.png')

if img_love is not None: img_love = cv2.resize(img_love, (400, 400))
if img_poop is not None: img_poop = cv2.resize(img_poop, (400, 400))
if img_mountain is not None: img_mountain = cv2.resize(img_mountain, (400, 400))

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(1)
seq_data = deque(maxlen=30)

with torch.no_grad():
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                joint = []
                for lm in hand_landmarks.landmark:
                    joint.extend([lm.x, lm.y, lm.z])
                seq_data.append(joint)

        if len(seq_data) == 30:
            input_data = torch.FloatTensor(seq_data).to(device).unsqueeze(0)
            output = model(input_data)
            _, predicted = torch.max(output, 1)
            action_idx = predicted.item()
            idx_list.append(action_idx)


            if action_idx == 0:
                cv2.putText(frame, "love", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                if img_love is not None:
                    cv2.imshow('Result Image', img_love)

                    if idx_list[-2] != 0:
                        os.system("say '좋아하다' &")

            elif action_idx == 1:
                cv2.putText(frame, "poop", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                if img_poop is not None:
                    cv2.imshow('Result Image', img_poop)

                    if idx_list[-2] != 1:
                        os.system("say '똥' &")



            elif action_idx == 2:
                cv2.putText(frame, "mountain", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                if img_mountain is not None:
                    cv2.imshow('Result Image', img_mountain)

                    if idx_list[-2] != 2:
                        os.system("say '산' &")

        cv2.imshow('taewon_project', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()


