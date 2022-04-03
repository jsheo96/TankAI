import time
from api import ADEX_API
import numpy as np
import gym
from gym import spaces

class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, key=None, playername='jsheo'):
        super(CustomEnv, self).__init__()
        self.action_space = spaces.Discrete(29)
        self.observation_space = spaces.Box(low=0, high=255, shape=(4, 9, 9, 3), dtype=np.uint8)
        self.api = ADEX_API()
        if key == None:
            self.api.create()
        else:
            self.api.key = key
        self.playername = playername
        self.previous_status = None
        #self.reset()

    def get_observation(self, status):
        """
        :param status: response message of query "game/status?key=..?playename=.."
        :return: np.array (4, 5, 5, 3), dtype=np.uint8, stacked sight array of all tanks.
                 If a tank is destroyed, it returns black array with the same shape.
        """
        viewmaps = []
        info_list = status['responses']['data']['message']["agent_info"]["agent"]
        print(status['responses']['data']['message']['game_info']['IsTurnOwner'])
        for info in info_list:
            viewmap = np.zeros((9,9,3),dtype=np.uint8)
            uid = info['uid']
            location = info['location']
            tank_y, tank_x = location
            tank_y = tank_y // 1000 # TODO: consider the cases when the unit length is not equal to 1000.
            tank_x = tank_x // 1000
            view = self.api.view(uid)
            if 'error' in view['responses'].keys():
                viewmaps.append(viewmap)
                continue
            for object in view['responses']['data']['message']['info']:
                object_location = object['location']
                obj_y, obj_x = object_location
                obj_y = obj_y // 1000
                obj_x = obj_x // 1000
                dy = obj_y - tank_y
                dx = obj_x - tank_x
                di = dy + 4
                dj = dx + 4
                object_type = object['ObjectType']
                if di >= 0 and di < 9 and dj >= 0 and dj < 9:
                    viewmap[di,dj] = object_type
            viewmaps.append(viewmap)
        observation = np.stack(viewmaps, 0)
        return observation

    def get_hp_reward(self, status):
        if self.previous_status == None:
            self.previous_status = status
        hp_sum = sum(list(map(lambda x:x['hp'], status['responses']['data']['message']["agent_info"]["agent"])))
        previous_hp_sum = sum(list(map(lambda x:x['hp'], self.previous_status['responses']['data']['message']["agent_info"]["agent"])))
        diff_hp = hp_sum - previous_hp_sum
        reward = -diff_hp
        self.previous_status = status
        return reward

    def take_action(self, action, mask):
        """
        Apply action to game. e.g. move, rotate and attack
        :param action: np.array (29)
        :param mask: np.array (29) disables the unavailable action
        :return:
        """
        if mask[action] == 0 or action == 28: # Tried to take an impossible action. gives turn
            self.api.endturn(self.playername)
            return
        uid_index = action // 7
        uid = self.agents[uid_index]
        act = action % 7
        if act < 4:
            self.api.move(uid, act)
        elif act == 4:
            self.api.rotate(uid, 45)
        elif act == 5:
            self.api.rotate(uid, -45)
        elif act == 6:
            self.api.attack(uid)

    def get_mask(self, status):
        mask = np.ones((29,), dtype=np.float32)
        ap_list = list(map(lambda x:x['ap'], status['responses']['data']['message']["agent_info"]["agent"]))
        ap = ap_list[0]
        ap == 0 #-> 0
        required_ap_for_action = np.array([2, 2, 2, 2, 1, 1, 4], dtype=np.uint8)
        for i,ap in enumerate(ap_list):
            mask[np.where(required_ap_for_action > ap)[0]+i*7] = 0
        return mask

    def get_mask_reward(self, action, mask):
        reward = 0
        reward -= (1-mask[action]) * 10
        return reward

    def step(self, action):
        status = self.api.status(self.playername)
        if 'data' not in status['responses'].keys():
            observation = np.zeros((4,9,9,3),dtype=np.uint8)
            reward = 10
            done = True
            info = {}
            return observation, reward, done, info
        mask = self.get_mask(status)
        reward = 0
        reward += self.get_mask_reward(action, mask)
        print(action, mask)
        self.take_action(action, mask)
        status = self.api.status(self.playername)
        if 'data' not in status['responses'].keys():
            observation = np.zeros((4,9,9,3),dtype=np.uint8)
            reward = 10
            done = True
            info = {}
            return observation, reward, done, info
        observation = self.get_observation(status)
        reward = self.get_hp_reward(status)
        done = False
        info = {}
        print('reward',reward)
        return observation, reward, done, info

    def reset(self):
        self.api.reset()
        self.api.join(self.playername)
        self.api.start(self.playername)
        time.sleep(1)
        self.agents = self.api.get_agents(self.playername)
        status = self.api.status(self.playername)
        observation = self.get_observation(status)
        return observation
        #if np.random.random()< 0.5:
        #    self.api.start('Bot')

    def render(self, mode='human', close=False):
        return False
