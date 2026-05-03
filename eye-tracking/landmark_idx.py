import cv2
import mediapipe as mp

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture
cap = cv2.VideoCapture(0)

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 900  # Adjust if needed

# Function to draw the landmark indices
def draw_landmark_indices(frame, face_landmarks, frame_width, frame_height):
    """Draw the landmark indices on the frame."""
    for idx, landmark in enumerate(face_landmarks.landmark):
        # Convert landmark coordinates from normalized (0 to 1) to pixel values
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)

        # Draw the index number on the frame
        cv2.putText(frame, str(idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

# Initialize Mediapipe FaceMesh
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Enables iris landmarks
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    print("Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)

        # Resize the frame
        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Convert the frame to RGB as MediaPipe works with RGB images
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
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                )

                # Draw landmark indices
                draw_landmark_indices(frame, face_landmarks, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Display the frame
        cv2.imshow('Face Landmarks with Indices', frame)

        # Check for quit ('q') key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()