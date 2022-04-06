import gym
from gym import spaces
import numpy as np
import cv2
class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(CustomEnv, self).__init__()
        self.action_space = spaces.Discrete(8) # 0~3: move 4~5: rotate 6: attack, 7: endturn
        # self.observation_space = spaces.Box(low=-1, high=50, shape=(7,7,4), dtype=np.float32)
        image_space = spaces.Box(low=-1, high=50, shape=(7,7,4), dtype=np.float32)
        ap_space = spaces.Box(low=0,high=10, shape=(1,), dtype=np.uint8)
        hp_space = spaces.Box(low=0,high=10, shape=(1,), dtype=np.uint8)
        aim_space = spaces.Box(low=-1,high=1, shape=(1,), dtype=np.uint8) # -1: zero 0: yes but obstacle :1 nice
        dict_space = {
            'image': image_space,
            'ap': ap_space,
            'hp': hp_space,
            'aim': aim_space
        }
        self.observation_space = gym.spaces.Dict(dict_space)

    def step(self, action):
        reward = 0
        self.take_action(action)
        # observation = self.preprocess(self.get_observation())
        image = self.get_observation()
        aim = self.get_aim()
        done = False
        if self.ap < 0:
            reward = -1
            done = True
        elif self.enemy_hp == 0:
            done = True
            reward = 1 - 0.9 * (self.step_count / self.max_steps)
        elif self.step_count >= self.max_steps:
            done = True
        self.step_count += 1
        info = {}
        # if done:
        #     print(reward)
        # print(action, self.enemy_hp, self.enemy_hp, self.my_coord, self.angle)
        observation = {'image': image, 'ap': self.ap, 'hp': self.hp, 'aim': aim}

        return observation, reward, done, info

    def get_aim(self):
        x,y = self.my_coord
        y_i = self.global_map.shape[0] - 1 - y
        x_j = x
        if self.angle % 90 == 0:
            front_item_list = [self.global_map[y_i+di,x_j+dj] for di,dj in [(r * np.sin(self.angle), -r*np.cos(self.angle)) for r in range(1,15)]]
        else:
            front_item_list = [self.global_map[y_i+di,x_j+dj] for di,dj in [(r * np.sin(self.angle), -r*np.cos(self.angle)) for r in range(1,11)]]

        if 2 not in front_item_list:
            return -1
        elif 3 in front_item_list:
            return 0 if front_item_list.index(3) < front_item_list.index(2) else 1
        else:
            return 1

    def reset(self):
        self.global_map = np.zeros((50,50),dtype=np.uint8)
        self.enemy_coord = [31,167]
        self.enemy_hp = 10
        self.my_coord = [30,157]
        self.angle = 0
        self.max_steps = 100
        self.step_count = 0
        image = self.get_observation()
        self.ap = 10
        self.hp = 10
        self.aim = -1

        observation = {'image': image, 'ap': self.ap, 'hp': self.hp, 'aim': self.aim}
        return observation

    def get_observation(self):
        x, y = self.my_coord
        observation = np.zeros((7,7,4),dtype=np.float32)
        for i in range(observation.shape[0]):
            for j in range(observation.shape[1]):
                x_i = x-3+j
                y_j = y+3-i
                enemy_x, enemy_y = self.enemy_coord
                dx = enemy_x - x_i
                dy = enemy_y - y_j
                danger_dist_from_perpendicular = min(abs(dx),abs(dy))
                danger_dist_from_diagonal = abs(abs(dx)-abs(dy))
                gamma = 2
                danger_dist = gamma ** (-danger_dist_from_perpendicular) + gamma**(-danger_dist_from_diagonal)
                observation[i,j,0] = danger_dist

                # TODO: caculate vector for agent with the greatest danger_dist value
                uv = np.array([dx,dy])/np.linalg.norm(np.array([dx,dy]))
                observation[i,j,2] = dx/50#uv[0]
                observation[i,j,3] = dy/50#uv[1]
        # observation[:,:,2] = self.normalize(observation[:,:,2])
        # observation[:,:,3] = self.normalize(observation[:,:,3])

        if self.angle % 90 == 0:
            for r in range(4):
                i = 3-int(r * np.cos(self.angle * np.pi / 180))
                j = 3+int(r * np.sin(self.angle * np.pi / 180))
                observation[i,j,1] = 1
        else:
            d = np.array([0,1,2,3])
            if self.angle == 45:
                i_ = 3-d
                j_ = 3+d
            elif self.angle == 135:
                i_ = 3+d
                j_ = 3+d
            elif self.angle == 225:
                i_ = 3+d
                j_ = 3-d
            else:
                i_ = 3-d
                j_ = 3-d
            for i,j in zip(i_,j_):
                observation[i,j,1] = 1
        return observation
    def take_action(self, action):
        if action == 0:
            self.my_coord = [self.my_coord[0], self.my_coord[1]-1]
            self.ap -= 2
        elif action == 1:
            self.my_coord = [self.my_coord[0]+1, self.my_coord[1]]
            self.ap -= 2
        elif action == 2:
            self.my_coord = [self.my_coord[0], self.my_coord[1]+1]
            self.ap -= 2
        elif action == 3:
            self.my_coord = [self.my_coord[0]-1, self.my_coord[1]]
            self.ap -= 2
        elif action == 4:
            self.angle += 45
            self.angle = (self.angle // 45) % 8 * 45
            self.ap -= 1
        elif action == 5:
            self.angle -= 45
            self.angle = (self.angle // 45) % 8 * 45
            self.ap -= 1
        elif action == 6:
            self.ap -= 4
            if self.is_targeted(self.my_coord, self.enemy_coord, self.angle):
                self.enemy_hp = 0
        elif action == 7:
            self.ap = 10

    def is_targeted(self, my_coord, enemy_coord, angle):
        x,y = my_coord
        enemy_x, enemy_y = enemy_coord
        dx = enemy_x - x
        dy = enemy_y - y
        v = np.array([dx,dy])
        v_ = v / np.linalg.norm(v)
        w_ = np.array([np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)])
        eps = 1e-10
        return abs(np.dot(v_,w_) - 1) < eps

    def render(self, mode='human', close=False):
        observation = self.get_observation()
        result = observation
        result = result * 1
        result = cv2.resize(result,dsize=None, fx=50,fy=50,interpolation=cv2.INTER_NEAREST)
        result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
        cv2.imshow('', result)
        cv2.waitKey()
