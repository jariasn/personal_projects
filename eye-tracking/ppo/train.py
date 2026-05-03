from stable_baselines3 import PPO
from stable_baselines3.common.envs import DummyVecEnv

# Create the environment
env = GazeTrackingEnv(screen_width=1920, screen_height=1080)

# Wrap the environment
env = DummyVecEnv([lambda: env])

# Create the PPO model
model = PPO('MlpPolicy', env, verbose=1)

# Train the model
model.learn(total_timesteps=10000)

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        env.click_event([x, y])

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_event)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process frame to get eye landmarks
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        # Extract relevant landmarks for eyes (e.g., 6 points)
        landmarks = extract_eye_landmarks(results.multi_face_landmarks[0])
        
        # Step the environment (get observation, reward, done)
        obs, reward, done, _ = env.step(landmarks)
        
        # Show frame
        cv2.imshow("Frame", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()