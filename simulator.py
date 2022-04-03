import cv2
import numpy as np
import json

class Tank:
    def __init__(self):
        self.location = [16, 20]
        self.hp = 100
        self.ap = 10
        self.angle = 0

    def move(self, direction):
        if direction == 0:
            self.ap -= 2

    def rotate(self, angle):
        self.angle -= 45
        self.ap -= 1

    def attack(self):
        self.ap -= 4

    def status(self):
        raise NotImplementedError
        return 1

    def view(self):
        raise NotImplementedError
        return 1

class Environment: # The oracle which knows everything about the current state of the simulaotor.
    def __init__(self):
        self.global_map = self.parse_viewlist('viewlist_backup.json')

    def get_random_color_by_index(self, index):
        if index == 0:
            return np.zeros((3))
        h = hash(str(index))
        r = h % 256
        g = h >> 8 % 256
        b = h >> 16 % 256
        return np.array([r,g,b])

    def parse_viewlist(self, path):
        j = json.load(open(path, 'r'))
        locations = list(map(lambda x:x['location'], j))
        locations = np.array(locations)
        locations[:,0] -= 200
        locations[:,1] -= 450
        locations = locations / 1000
        locations *= 2
        locations = locations.astype(np.uint8)
        locations[:,0] -= locations[:,0].min()
        locations[:,1] -= locations[:,1].min()
        object_names = list(map(lambda x:x['ObjectName'], j))
        object_names_set = list(set(object_names))
        object_name_num = len(object_names_set)
        global_map = np.zeros((locations[:,0].max()+1, locations[:,1].max()+1,object_name_num+1), dtype=np.uint8) # The last index of last channel is preserved for objects with unknown names.
        for i in range(len(object_names)):
            object_name = object_names[i]
            object_name_index = object_names_set.index(object_name)
            location = locations[i,:]
            global_map[location[0],location[1],object_name_index] = 1 # one hot vector
        return global_map

    def visualize_map(self):
        index_map = np.argmax(self.global_map, axis=2)
        result = np.zeros((index_map.shape[0],index_map.shape[1],3),dtype=np.uint8)
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                result[i,j,:] = self.get_random_color_by_index(index_map[i,j])
        result = cv2.resize(result, fx=10, fy=10, dsize=None,interpolation=cv2.INTER_NEAREST)
        return result

if __name__ == '__main__':
    env = Environment()
    cv2.imshow('global map', env.visualize_map())
    cv2.waitKey()


