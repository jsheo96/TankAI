import gym
from gym import spaces
import numpy as np
class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(CustomEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(9) # 0~3: move 4~7: rotate 8: attack
        # Example for using image as input:
        self.observation_space = spaces.Box(low=0, high=255, shape=(5,2), dtype=np.uint8)

    def step(self, action):
        self.take_action(action)
        reward = 0
        observation = self.get_observation()
        done = False
        if observation[4,0] == 0 or observation[4,1] == 0:
            done = True
            reward = 1 - 0.9 * (self.step_count / self.max_steps)
        elif self.step_count >= self.max_steps:
            done = True
        self.step_count += 1
        info = {}
        if done:
            print(reward)
        return observation, reward, done, info

    def reset(self):
        self.enemy_coord = [np.random.randint(50), np.random.randint(50)]
        self.my_coord = [np.random.randint(50), np.random.randint(50)]
        self.my_angle = 0
        self.max_steps = 100
        self.step_count = 0
        observation = self.get_observation()
        return observation

    def get_observation(self):
        x, y = self.my_coord
        roi_points = np.array([[x,y-1],[x+1,y],[x,y+1],[x-1,y],[x,y]])
        dxy_roi_points = roi_points - np.array(self.enemy_coord)
        abs_dxy = np.abs(dxy_roi_points)
        min_abs_dxy = np.min(abs_dxy,axis=1)
        abs_diff_abs_dxy = np.squeeze(np.abs(np.diff(abs_dxy)), axis=-1)
        diff_min_abs_dxy = np.concatenate((min_abs_dxy[:4] - min_abs_dxy[4:5], min_abs_dxy[4:5]), axis=0)
        diff_abs_diff_abs_dxy = np.concatenate((abs_diff_abs_dxy[:4] - abs_diff_abs_dxy[4:5], abs_diff_abs_dxy[4:5]), axis=0)
        # observation = np.stack((min_abs_dxy, abs_diff_abs_dxy), axis=-1)
        observation = np.stack((diff_min_abs_dxy, diff_abs_diff_abs_dxy), axis=-1)
        return observation

    def take_action(self, action):
        if action == 4:
            return
        elif action == 0:
            self.my_coord = [self.my_coord[0], self.my_coord[1]-1]
        elif action == 1:
            self.my_coord = [self.my_coord[0]+1, self.my_coord[1]]
        elif action == 2:
            self.my_coord = [self.my_coord[0], self.my_coord[1]+1]
        elif action == 3:
            self.my_coord = [self.my_coord[0]-1, self.my_coord[1]]

    def render(self, mode='human', close=False):
        print(self.enemy_coord, self.my_coord)
