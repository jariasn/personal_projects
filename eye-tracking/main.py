import cv2
import pyautogui
import numpy as np
import mediapipe as mp
import time

# Initialize MediaPipe Face Mesh and Drawing Utilities
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Calibration data dictionary
calibration_data = {}

# Initialize video capture
cap = cv2.VideoCapture(0)

def compute_gaze_ratio_with_normalization(eye_indices, iris_indices, face_landmarks):
    """Compute gaze ratios based on the position of the iris and eye corners, normalized to the eye region."""
    eye_left_corner = face_landmarks.landmark[eye_indices['left_corner']]
    eye_right_corner = face_landmarks.landmark[eye_indices['right_corner']]
    eye_top = face_landmarks.landmark[eye_indices['top']]
    eye_bottom = face_landmarks.landmark[eye_indices['bottom']]

    eye_width = eye_right_corner.x - eye_left_corner.x
    eye_height = eye_bottom.y - eye_top.y

    if eye_width == 0 or eye_height == 0:
        return None, None

    iris = [face_landmarks.landmark[i] for i in iris_indices]
    iris_x = np.mean([p.x for p in iris])
    iris_y = np.mean([p.y for p in iris])

    x_ratio = (iris_x - eye_left_corner.x) / eye_width
    y_ratio = (iris_y - eye_top.y) / eye_height

    return x_ratio, y_ratio

def calibrate_gaze():
    """Calibrate the gaze positions by asking the user to look at specific screen locations with visual markers."""
    positions = {
        'top-left': (int(SCREEN_WIDTH * 0.1), int(SCREEN_HEIGHT * 0.1)),
        'top-right': (int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.1)),
        'bottom-left': (int(SCREEN_WIDTH * 0.1), int(SCREEN_HEIGHT * 0.9)),
        'bottom-right': (int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.9)),
        'center': (int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.5))
    }
    iris_positions = {}

    print("Calibration will start in 2 seconds. Please be ready...")
    time.sleep(2)

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # This enables iris landmarks
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

        for pos_name, screen_pos in positions.items():
            # Prepare the instruction text
            instruction_text = f"Please look at the {pos_name} of the screen."
            print(instruction_text)

            # Display a visual marker at the calibration point
            marker_window = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
            cv2.circle(marker_window, screen_pos, 20, (0, 255, 0), -1)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.0  # Font size
            thickness = 3
            text_size, _ = cv2.getTextSize(instruction_text, font, font_scale, thickness)
            text_x = (SCREEN_WIDTH - text_size[0]) // 2
            text_y = 100  # Adjust vertical position

            cv2.putText(marker_window, instruction_text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

            cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Calibration', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            x_ratios = []
            y_ratios = []

            start_time = time.time()
            while time.time() - start_time < 3:
                ret, frame = cap.read()
                if not ret:
                    continue

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]

                    # Left and right iris landmarks indices
                    left_iris_indices = [474, 475, 476, 477]
                    right_iris_indices = [469, 470, 471, 472]

                    # Left eye landmarks
                    left_eye_indices = {
                        'left_corner': 33,
                        'right_corner': 133,
                        'top': 159,
                        'bottom': 145
                    }

                    # Right eye landmarks
                    right_eye_indices = {
                        'left_corner': 362,
                        'right_corner': 263,
                        'top': 386,
                        'bottom': 374
                    }

                    left_x_ratio, left_y_ratio = compute_gaze_ratio_with_normalization(left_eye_indices, left_iris_indices, face_landmarks)
                    right_x_ratio, right_y_ratio = compute_gaze_ratio_with_normalization(right_eye_indices, right_iris_indices, face_landmarks)

                    if None in [left_x_ratio, left_y_ratio, right_x_ratio, right_y_ratio]:
                        continue

                    x_ratio = (left_x_ratio + right_x_ratio) / 2
                    y_ratio = (left_y_ratio + right_y_ratio) / 2

                    x_ratios.append(x_ratio)
                    y_ratios.append(y_ratio)

                cv2.imshow('Calibration', marker_window)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            average_x_ratio = np.mean(x_ratios)
            average_y_ratio = np.mean(y_ratios)
            iris_positions[pos_name] = (average_x_ratio, average_y_ratio)
            print(f"Calibrated {pos_name} with gaze ratios: ({average_x_ratio:.4f}, {average_y_ratio:.4f})")
            cv2.destroyWindow('Calibration')
            time.sleep(0.5)

        calibration_data['iris_positions'] = iris_positions

        gaze_ratios = []
        screen_positions_x = []
        screen_positions_y = []

        for pos_name, (screen_x, screen_y) in positions.items():
            average_x_ratio, average_y_ratio = iris_positions[pos_name]
            gaze_ratios.append([average_x_ratio, average_y_ratio])
            screen_positions_x.append(screen_x)
            screen_positions_y.append(screen_y)

        gaze_ratios = np.array(gaze_ratios)
        A = np.column_stack((gaze_ratios, np.ones(len(gaze_ratios))))

        coeffs_x, _, _, _ = np.linalg.lstsq(A, screen_positions_x, rcond=None)
        coeffs_y, _, _, _ = np.linalg.lstsq(A, screen_positions_y, rcond=None)

        calibration_data['coeffs_x'] = coeffs_x
        calibration_data['coeffs_y'] = coeffs_y

        print("Calibration completed.\n")

def iris_to_screen_coordinates(x_ratio, y_ratio):
    coeffs_x = calibration_data.get('coeffs_x', None)
    coeffs_y = calibration_data.get('coeffs_y', None)

    if coeffs_x is None or coeffs_y is None:
        return None, None

    x = coeffs_x[0] * x_ratio + coeffs_x[1] * y_ratio + coeffs_x[2]
    y = coeffs_y[0] * x_ratio + coeffs_y[1] * y_ratio + coeffs_y[2]

    x = max(0, min(SCREEN_WIDTH - 1, x))
    y = max(0, min(SCREEN_HEIGHT - 1, y))

    return x, y

def smooth_cursor_movement(new_x, new_y, prev_x, prev_y, smoothing=0.2):
    x = prev_x + (new_x - prev_x) * smoothing
    y = prev_y + (new_y - prev_y) * smoothing
    return x, y

def get_head_orientation(face_landmarks):
    nose_tip = face_landmarks.landmark[1]
    left_eye_outer = face_landmarks.landmark[33]
    right_eye_outer = face_landmarks.landmark[263]

    head_tilt_x = right_eye_outer.x - left_eye_outer.x
    head_tilt_y = right_eye_outer.y - left_eye_outer.y

    return head_tilt_x, head_tilt_y

def adjust_gaze_for_head_pose(x_ratio, y_ratio, head_tilt_x, head_tilt_y):
    x_ratio_corrected = x_ratio - head_tilt_x * 0.1
    y_ratio_corrected = y_ratio - head_tilt_y * 0.1

    return x_ratio_corrected, y_ratio_corrected

def main():
    calibrate_gaze()

    prev_x, prev_y = pyautogui.position()

    print("Starting iris-tracking. Press 'q' to exit.")

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                left_iris_indices = [474, 475, 476, 477]
                right_iris_indices = [469, 470, 471, 472]

                left_eye_indices = {
                    'left_corner': 33,
                    'right_corner': 133,
                    'top': 159,
                    'bottom': 145
                }

                right_eye_indices = {
                    'left_corner': 362,
                    'right_corner': 263,
                    'top': 386,
                    'bottom': 374
                }

                left_x_ratio, left_y_ratio = compute_gaze_ratio_with_normalization(left_eye_indices, left_iris_indices, face_landmarks)
                right_x_ratio, right_y_ratio = compute_gaze_ratio_with_normalization(right_eye_indices, right_iris_indices, face_landmarks)

                if None in [left_x_ratio, left_y_ratio, right_x_ratio, right_y_ratio]:
                    continue

                x_ratio = (left_x_ratio + right_x_ratio) / 2
                y_ratio = (left_y_ratio + right_y_ratio) / 2

                head_tilt_x, head_tilt_y = get_head_orientation(face_landmarks)

                x_ratio, y_ratio = adjust_gaze_for_head_pose(x_ratio, y_ratio, head_tilt_x, head_tilt_y)

                x, y = iris_to_screen_coordinates(x_ratio, y_ratio)
                if x is not None and y is not None:
                    x, y = smooth_cursor_movement(x, y, prev_x, prev_y)
                    prev_x, prev_y = x, y
                    pyautogui.moveTo(x, y)

                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )

            cv2.imshow('Iris Tracker', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()