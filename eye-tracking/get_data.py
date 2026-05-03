import cv2
import pyautogui
import numpy as np
import mediapipe as mp
import json
import time
import math

# Initialize MediaPipe Face Mesh and Drawing Utilities
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Create a dictionary to store data
data = []

# Store the click positions
click_positions = []

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 3024, 1964  # Set to your screen size (3024 x 1964)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Define the relevant iris landmarks
relevant_pupil_landmarks = {
    'left_pupil': [468],  # Left pupil landmark
    'right_pupil': [473]  # Right pupil landmark
}

def calculate_head_position(face_landmarks, frame_width, frame_height):
    """Calculates the head position in the field of view and transforms it to screen coordinates."""
    key_landmarks = [1, 33, 263, 61, 291]  # Nose tip, outer corners of eyes, mouth corners
    head_x = np.mean([face_landmarks.landmark[i].x for i in key_landmarks])
    head_y = np.mean([face_landmarks.landmark[i].y for i in key_landmarks])
    head_x_screen = head_x * frame_width
    head_y_screen = head_y * frame_height
    return head_x_screen, head_y_screen

def calculate_head_pose(face_landmarks):
    """Calculates yaw, pitch, and roll based on the positions of the nose and eyes."""
    left_eye_outer = face_landmarks.landmark[33]  # Left outer eye corner
    right_eye_outer = face_landmarks.landmark[263]  # Right outer eye corner
    nose_tip = face_landmarks.landmark[1]  # Nose tip
    eye_distance_x = right_eye_outer.x - left_eye_outer.x
    eye_distance_y = right_eye_outer.y - left_eye_outer.y
    yaw = math.degrees(math.atan2(eye_distance_y, eye_distance_x))
    eye_mid_y = (left_eye_outer.y + right_eye_outer.y) / 2
    pitch = math.degrees(math.atan2(nose_tip.y - eye_mid_y, abs(nose_tip.z)))
    roll = yaw  # Approximate roll based on yaw (left-right)
    return yaw, pitch, roll

def save_data(iris_landmarks, mouse_position, head_position, head_pose):
    """Save iris landmarks, mouse position, head position, and head pose to data array."""
    data_entry = {
        'iris_landmarks': iris_landmarks,
        'mouse_position': mouse_position,
        'head_position': head_position,
        'head_pose': {
            'yaw': head_pose[0],
            'pitch': head_pose[1],
            'roll': head_pose[2]
        }
    }
    data.append(data_entry)

def get_relevant_pupil_landmarks(face_landmarks):
    """Extract the relevant pupil landmarks."""
    left_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['left_pupil']]
    right_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['right_pupil']]
    return left_pupil_landmarks, right_pupil_landmarks

def draw_click_marker(frame, x, y):
    """Draw a marker (circle) where the mouse was clicked."""
    # Draw a circle at the click position (color = red, radius = 10 pixels)
    cv2.circle(frame, (x, y), 10, (0, 0, 255), 3)

def on_click(event, x, y, flags, param):
    """Callback for mouse click events."""
    if event == cv2.EVENT_LBUTTONDOWN:
        # When a click happens, save the current face and pupil landmarks
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Extract the pupil landmarks
            left_pupil, right_pupil = get_relevant_pupil_landmarks(face_landmarks)

            # Calculate head position in the field of view (relative to the screen size)
            head_x, head_y = calculate_head_position(face_landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)

            # Calculate head pose (yaw, pitch, roll)
            yaw, pitch, roll = calculate_head_pose(face_landmarks)

            # Save the pupil landmarks, mouse position, head position, and head pose
            save_data({
                'left_pupil': left_pupil,
                'right_pupil': right_pupil
            }, (x, y), (head_x, head_y), (yaw, pitch, roll))

            # Store the click position to draw it later
            click_positions.append((x, y))

            print(f"Data point saved at mouse position: {x}, {y}, Head position: ({head_x:.2f}, {head_y:.2f}), Pose (Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f})")

# Initialize Mediapipe FaceMesh
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Enables iris landmarks
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    # Create OpenCV window for full screen
    cv2.namedWindow('Data Collection', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Data Collection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('Data Collection', on_click)

    print("Click on the screen to collect data. Press 'q' to quit and save.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Flip the frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)

        # Resize frame to match the screen size exactly (3024 x 1964)
        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Convert the frame to RGB as Mediapipe works with RGB images
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe to get face landmarks
        results = face_mesh.process(rgb_frame)

        # If landmarks are detected
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw the face mesh landmarks on the frame (optional for visualization)
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )

        # Draw markers at all previously clicked positions
        for click_position in click_positions:
            draw_click_marker(frame, click_position[0], click_position[1])

        # Display the frame
        cv2.imshow('Data Collection', frame)

        # Check for quit ('q') key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save the collected data to a file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"gaze_data_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Data saved to {filename}")

# Release resources
cap.release()
cv2.destroyAllWindows()