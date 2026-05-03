import gym
import numpy as np
from gym import spaces

class GazeTrackingEnv(gym.Env):
    def __init__(self, screen_width, screen_height):
        super(GazeTrackingEnv, self).__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Observation space: the eye landmarks (e.g., 6 key points from the eyes)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(6,), dtype=np.float32)
        
        # Action space: the predicted (x, y) coordinates on the screen
        self.action_space = spaces.Box(low=0, high=max(screen_width, screen_height), shape=(2,), dtype=np.float32)
        
        # Store the true gaze point (where the user clicks)
        self.true_gaze = None
        
    def step(self, action):
        # Action is the predicted screen coordinates (x, y)
        predicted_gaze = np.array(action)
        
        # Calculate the distance between predicted gaze and true gaze
        if self.true_gaze is not None:
            distance = np.linalg.norm(predicted_gaze - self.true_gaze)
        else:
            distance = 0
        
        # Reward: negative distance (smaller distance gives a higher reward)
        reward = -distance
        
        # Done condition
        done = False  # You can define when an episode should end
        
        # Placeholder observation (replace with actual eye landmarks)
        obs = np.random.uniform(-1, 1, size=(6,))
        
        return obs, reward, done, {}
    
    def reset(self):
        # Reset environment, typically you could capture new eye landmarks here
        self.true_gaze = None
        return np.random.uniform(-1, 1, size=(6,))
    
    def click_event(self, true_gaze):
        """This method will be called when the user clicks on the screen to set the true gaze."""
        self.true_gaze = true_gaze