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

# Store the last mouse position
last_mouse_position = None

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()  # Set to your screen size (3024 x 1964)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Define the relevant pupil landmarks
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

def save_data(eye_landmarks, mouse_position, head_position, head_pose, ear):
    """Save pupil landmarks, mouse position, head position, and head pose to data array."""
    data_entry = {
        'eye_landmarks': eye_landmarks,
        'mouse_position': mouse_position,
        'head_position': head_position,
        'head_pose': {
            'yaw': head_pose[0],
            'pitch': head_pose[1],
            'roll': head_pose[2]
        },
        'ear': {
            'left': ear[0],
            'right': ear[1]
        }
    }
    data.append(data_entry)

def calculate_ear(eye_landmarks):
    """Calculate the Eye Aspect Ratio (EAR) based on eye landmarks with one upper and one lower eyelid point."""
    # Single vertical distance between upper and lower eyelid points
    A = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[3]))  # Upper (159/386) to lower (145/374)
    
    # Horizontal distance between the eye corners
    C = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[2]))  # Outer (33/263) to inner (133/362)

    # Eye Aspect Ratio formula using only one vertical distance
    ear = A / C
    return ear

def get_eye_landmarks(face_landmarks):
    """Extract relevant landmarks around both eyes for better gaze estimation."""
    left_eye_landmarks = [33, 133, 159, 145]  # Add key landmarks around the left eye
    right_eye_landmarks = [263, 362, 386, 374]  # Add key landmarks around the right eye

    left_eye = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in left_eye_landmarks]
    right_eye = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in right_eye_landmarks]

    return left_eye, right_eye

def get_relevant_pupil_landmarks(face_landmarks):
    """Extract the relevant pupil landmarks."""
    left_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['left_pupil']]
    right_pupil_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in relevant_pupil_landmarks['right_pupil']]
    return left_pupil_landmarks, right_pupil_landmarks

# Initialize Mediapipe FaceMesh
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Enables iris landmarks
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    # Create OpenCV window for full screen
    cv2.namedWindow('Data Collection', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Data Collection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("Press and hold the space bar to collect data. Release it to stop. Press 'q' to quit and save.")

    # Variable to track whether the space bar is pressed
    recording = False

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

        # Get current mouse position
        current_mouse_position = pyautogui.position()

        # Capture key input
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # Space bar pressed
            recording = True
        elif key == ord('q'):  # 'q' pressed to quit
            break
        else:
            recording = False  # Space bar released

        # If space bar is pressed, record data
        if recording:
            # If landmarks are detected
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # Extract the pupil landmarks
                    left_eye, right_eye = get_eye_landmarks(face_landmarks)

                    # Calculate the Eye Aspect Ratio (EAR) for both eyes
                    ear_left = calculate_ear(left_eye)
                    ear_right = calculate_ear(right_eye)

                    # Extract the relevant pupil landmarks
                    left_pupil, right_pupil = get_relevant_pupil_landmarks(face_landmarks)

                    # Calculate head position in the field of view (relative to the screen size)
                    head_x, head_y = calculate_head_position(face_landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)

                    # Calculate head pose (yaw, pitch, roll)
                    yaw, pitch, roll = calculate_head_pose(face_landmarks)

                    # Save the pupil landmarks, mouse position, head position, and head pose
                    save_data({
                        'left_eye': (left_eye, left_pupil),
                        'right_eye': (right_eye, right_pupil)
                    }, current_mouse_position, (head_x, head_y), (yaw, pitch, roll), (ear_left, ear_right))
                    

                    print(f"Data point saved at mouse position: {current_mouse_position}, Head position: ({head_x:.2f}, {head_y:.2f}), Pose (Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f})")
        
        # Draw the face mesh landmarks on the frame (optional for visualization)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )
                # Extract the left and right eye landmarks (6 points each)
                left_eye_landmarks = [33, 133, 159, 145]
                right_eye_landmarks = [263, 362, 386, 374]

                # Draw the left eye landmarks in blue
                for idx in left_eye_landmarks:
                    x = int(face_landmarks.landmark[idx].x * frame.shape[1])
                    y = int(face_landmarks.landmark[idx].y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)  # Blue color (BGR format)

                # Draw the right eye landmarks in red
                for idx in right_eye_landmarks:
                    x = int(face_landmarks.landmark[idx].x * frame.shape[1])
                    y = int(face_landmarks.landmark[idx].y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)  # Red color (BGR format)

                # Optionally, display the modified frame
                cv2.imshow('Data Collection', frame)
                

        # Display the mouse position on the screen
        mouse_position_text = f"Mouse Position: {current_mouse_position[0]}, {current_mouse_position[1]}"
        cv2.putText(frame, mouse_position_text, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # If landmarks are detected, display the required values
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract the pupil landmarks
                left_eye, right_eye = get_eye_landmarks(face_landmarks)

                # Calculate the Eye Aspect Ratio (EAR) for both eyes
                ear_left = calculate_ear(left_eye)
                ear_right = calculate_ear(right_eye)

                # Extract the relevant pupil landmarks
                left_pupil, right_pupil = get_relevant_pupil_landmarks(face_landmarks)

                # Calculate head position in the field of view (relative to the screen size)
                head_x, head_y = calculate_head_position(face_landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)

                # Calculate head pose (yaw, pitch, roll)
                yaw, pitch, roll = calculate_head_pose(face_landmarks)

                # Display eye landmarks
                left_eye_text = f"Left Eye: {[(round(x, 2), round(y, 2)) for (x, y) in left_eye]}"
                right_eye_text = f"Right Eye: {[(x, y) for (x, y) in right_eye]}"
                left_pupil_text = f"Left Pupil: {[(x, y) for (x, y) in left_pupil]}"
                right_pupil_text = f"Right Pupil: {[(x, y) for (x, y) in right_pupil]}"

                # Display head position, pose (yaw, pitch, roll), and EAR for both eyes
                head_position_text = f"Head Position: ({round(head_x, 2)}, {round(head_y, 2)})"
                head_pose_text = f"Pose - Yaw: {round(yaw, 2)}, Pitch: {round(pitch, 2)}, Roll: {round(roll, 2)}"
                ear_text = f"EAR - Left: {round(ear_left, 2)}, Right: {round(ear_right, 2)}"

                # Display on the frame
                # cv2.putText(frame, left_eye_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                # cv2.putText(frame, right_eye_text, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, left_pupil_text, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, right_pupil_text, (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                # cv2.putText(frame, head_position_text, (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                # cv2.putText(frame, head_pose_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                # cv2.putText(frame, ear_text, (50, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


        # Display the frame
        cv2.imshow('Data Collection', frame)

    # Save the collected data to a file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"gaze_data_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Data saved to {filename}")

# Release resources
cap.release()
cv2.destroyAllWindows()