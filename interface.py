import numpy as np
import cv2
from api import ADEX_API
import time
class Interface:
    def __init__(self, key=None):
        self.api = ADEX_API()
        self.playername = 'jsheo'
        self.enemyname = 'Bot'
        if key == None:
            self.api.create()
            self.api.join(self.playername)
            self.api.start(self.playername)
        else:
            self.api.key = key
        self.black = np.zeros((256,256,3), dtype=np.uint8)
        self.states = None # {'jsheo': state, 'enemy': state}
        self.update_states()

    def run(self):
        start = time.time()
        while True:
            if time.time()-start>=1:
                self.update_states()
                # self.update_board()
                """
                viewmaps = self.get_viewmaps(self.playername)
                for i, viewmap in enumerate(viewmaps):
                    viewmap = cv2.resize(viewmap, fx=20, fy=20, dsize=None, interpolation=cv2.INTER_NEAREST)
                    cv2.imshow(f'viewmap {i}', viewmap)
                viewmaps = self.get_viewmaps(self.enemyname)
                for i, viewmap in enumerate(viewmaps):
                    viewmap = cv2.resize(viewmap, fx=20, fy=20, dsize=None, interpolation=cv2.INTER_NEAREST)
                    cv2.imshow(f'enemy viewmap {i}', viewmap)
                start = time.time()
                """
            cv2.waitKey(1)

    def update_board(self):
        # TODO: visualize as a board with cv2.imshow
        state_jsheo = self.api.state(self.playername)
        state_bot = self.api.state(self.enemyname)
        print(state_jsheo)
        print(state_bot)
        print('board updated')

    def update_states(self):
        self.states = {
            self.playername: self.api.state(self.playername),
            self.enemyname: self.api.state(self.enemyname)
        }
        print('states updated')

    def get_viewmaps(self, name):
        viewmaps = []
        status, views = self.states[name]
        agents = status['responses']['data']['message']['agent_info']['agent']
        for i in range(len(views)):
            view = views[i]
            agent = agents[i]
            viewmap = np.zeros((10,24,3),dtype=np.uint8)
            # TODO: speed up by vectorization
            relative_locations = (np.array(list(map(lambda x: x['location'], view['responses']['data']['message']['info']))) - np.array(
                agent['location'])) // 1000
            min_y = relative_locations[:, 0].min()
            min_x = relative_locations[:, 1].min()
            max_y = relative_locations[:, 0].max() # to be removed
            max_x = relative_locations[:, 1].max()
            print(max_y-min_y,max_x-min_x)
            for object in view['responses']['data']['message']['info']:
                object_type = object['ObjectType']
                y, x = object['location']
                agent_y, agent_x = agent['location']
                idx_y = (y-agent_y)//1000
                idx_x = (x-agent_x)//1000

                base_adjusted_idx_y = idx_y + (-min_y)
                base_adjusted_idx_x = idx_x + (-min_x)
                print(base_adjusted_idx_y, base_adjusted_idx_x)
                if object_type==1:
                    viewmap[base_adjusted_idx_y, base_adjusted_idx_x] = [0,0,255]
                elif object_type==2:
                    viewmap[base_adjusted_idx_y, base_adjusted_idx_x] = [0, 255, 0]
                elif object_type==3:
                    viewmap[base_adjusted_idx_y, base_adjusted_idx_x] = [255, 0, 0]
            viewmaps.append(viewmap)
        return viewmaps



if __name__ == '__main__':
    interface = Interface()
    interface.run()