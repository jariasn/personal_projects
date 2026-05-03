import torch
import cv2
import numpy as np
import mediapipe as mp
import math
import torch.nn as nn
import pyautogui

class GazeToMouseModel(nn.Module):
    def __init__(self):
        super(GazeToMouseModel, self).__init__()
        self.fc1 = nn.Linear(9, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 32)
        self.fc4 = nn.Linear(32, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# Load the trained model
model = GazeToMouseModel()
model.load_state_dict(torch.load('gaze_to_mouse_model_.pth'))
model.eval()  # Set the model to evaluation mode

# Initialize MediaPipe Face Mesh and Drawing Utilities
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Get screen dimensions dynamically
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

cap = cv2.VideoCapture(0)

relevant_pupil_landmarks = {
    'left_pupil': [468],
    'right_pupil': [473]
}

def preprocess_for_model(pupil_landmarks, head_position, head_pose):
    left_pupil = [coord for point in pupil_landmarks['left_pupil'] for coord in point]
    right_pupil = [coord for point in pupil_landmarks['right_pupil'] for coord in point]
    
    normalized_head_position = [
        head_position[0] / SCREEN_WIDTH,
        head_position[1] / SCREEN_HEIGHT
    ]
    
    normalized_head_pose = [
        (head_pose[0] + 180) / 360,
        (head_pose[1] + 180) / 360,
        (head_pose[2] + 180) / 360
    ]
    
    features = left_pupil + right_pupil + normalized_head_position + normalized_head_pose
    input_tensor = torch.tensor(features, dtype=torch.float32)
    
    return input_tensor.unsqueeze(0)

def get_relevant_pupil_landmarks(face_landmarks):
    left_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['left_pupil']]
    right_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['right_pupil']]
    return {'left_pupil': left_pupil_landmarks, 'right_pupil': right_pupil_landmarks}

def calculate_head_position(face_landmarks, frame_width, frame_height):
    key_landmarks = [1, 33, 263, 61, 291]
    head_x = np.mean([face_landmarks.landmark[i].x for i in key_landmarks])
    head_y = np.mean([face_landmarks.landmark[i].y for i in key_landmarks])
    head_x_screen = head_x * frame_width
    head_y_screen = head_y * frame_height
    return head_x_screen, head_y_screen

def calculate_head_pose(face_landmarks):
    left_eye_outer = face_landmarks.landmark[33]
    right_eye_outer = face_landmarks.landmark[263]
    nose_tip = face_landmarks.landmark[1]
    eye_distance_x = right_eye_outer.x - left_eye_outer.x
    eye_distance_y = right_eye_outer.y - left_eye_outer.y
    yaw = math.degrees(math.atan2(eye_distance_y, eye_distance_x))
    eye_mid_y = (left_eye_outer.y + right_eye_outer.y) / 2
    pitch = math.degrees(math.atan2(nose_tip.y - eye_mid_y, abs(nose_tip.z)))
    roll = yaw
    return yaw, pitch, roll

with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    print("Running real-time prediction. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            pupil_landmarks = get_relevant_pupil_landmarks(face_landmarks)
            head_x, head_y = calculate_head_position(face_landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)
            yaw, pitch, roll = calculate_head_pose(face_landmarks)
            input_tensor = preprocess_for_model(pupil_landmarks, (head_x, head_y), (yaw, pitch, roll))

            with torch.no_grad():
                predicted_mouse_pos = model(input_tensor).squeeze(0)

            predicted_mouse_pos = predicted_mouse_pos * torch.tensor([SCREEN_WIDTH, SCREEN_HEIGHT])
            predicted_mouse_x, predicted_mouse_y = int(predicted_mouse_pos[0].item()), int(predicted_mouse_pos[1].item())
            pyautogui.moveTo(predicted_mouse_x, predicted_mouse_y)

            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
            )

        cv2.imshow('Real-Time Prediction', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()