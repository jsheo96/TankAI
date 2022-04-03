import json
import cv2
import numpy as np
from scipy.ndimage import convolve
from collections import defaultdict
class SimulatorAPI:
    def __init__(self):
        self.viewmap, self.realmap = self.parse_map('viewlist_backup.json', 'location_list_backup.json')

    def parse_map(self, viewlist_path, location_list_path):
        viewmap = np.zeros((40,40),dtype=np.uint8)
        realmap = np.zeros((80,80),dtype=np.float32)
        viewlist = json.load(open(viewlist_path, 'r'))
        locations = np.array(list(map(lambda x:x['location'], viewlist))) #
        y_min, x_min = 24200, 147450

        locations_by_name = defaultdict(lambda :[])
        for view in viewlist:
            location = view['location']
            object_type = view['ObjectType']
            object_name = view['ObjectName']
            locations_by_name[object_name].append(location)
            y, x = location
            dy = (y-y_min) // 1000
            dx = (x-x_min) // 1000
            if object_type == 3:
                viewmap[dy,dx] = 255

            real_dy = dy * 2
            real_dx = dx * 2
            if object_type == 3:
                #realmap[real_dy-1:real_dy+2, real_dx-1:real_dx+2] = 255
                realmap[real_dy, real_dx] = 1
                #realmap[real_dy-1:real_dy+2, real_dx-1:real_dx+2] += 50
        tankmap = np.zeros((80,80),dtype=np.uint8)
        tank_locations = json.load(open(location_list_path, 'r'))
        prev_real_dy = None
        prev_real_dx = None
        for location in tank_locations:
            y, x = location
            dy = (y-y_min) // 1000
            dx = (x-x_min) // 1000
            real_dy = dy * 2
            real_dx = dx * 2
            if prev_real_dx == None or prev_real_dy == None:
                prev_real_dx = real_dx
                prev_real_dy = real_dy
            inter_dy = (prev_real_dy + real_dy) // 2
            inter_dx = (prev_real_dx + real_dx) // 2
            prev_real_dy = real_dy
            prev_real_dx = real_dx
            tankmap[real_dy, real_dx] = 1
            tankmap[inter_dy, inter_dx] = 1
        realmap = realmap#*(1-tankmap)
        realmap = np.zeros((80,80),dtype=np.float32)
        kernel = np.array([[1,2,1],[2,4,2],[1,2,1]],dtype=np.float32) / 16
        for name in locations_by_name.keys():
            if name == '' or 'K1A1' in name:# or 'Sandbox' in name or 'CarZaAzBK' in name:
                continue
            print('name: {}'.format(name))
            locations = locations_by_name[name]
            objectmap = np.zeros((80,80),np.float32)
            for location in locations:
                y, x = location
                dy = (y - y_min) // 1000
                dx = (x - x_min) // 1000
                real_dy = dy * 2
                real_dx = dx * 2
                objectmap[real_dy, real_dx] = 1
            objectmap = convolve(objectmap, kernel)
            objectmap = objectmap * (1 - tankmap)
            #cv2.imshow('objectmap',cv2.resize(objectmap, fx=10, fy=10, dsize=None, interpolation=cv2.INTER_NEAREST))
            #cv2.waitKey()
            #print(np.unique(objectmap))
            #objectmap[objectmap<0.1875] = 0
            #objectmap[objectmap>0] = 1
            #objectmap = objectmap * (1 - tankmap)
            realmap = realmap + objectmap
            #print(object_name, object_type)
            #cv2.imshow('realmap',cv2.resize(realmap[::-1,:],  fx=10, fy=10, dsize=None, interpolation=cv2.INTER_NEAREST))
            #cv2.waitKey()
        #realmap = convolve(realmap, kernel)
        realmap[realmap<0.25] = 0
        realmap[realmap>0] = 1
        realmap = realmap * (1 - tankmap)
        return viewmap, realmap


    def render(self):
        result = self.realmap
        result = np.stack((result,)*3, -1)
        result = cv2.resize(result[::-1,:,:], fx=10, fy=10, dsize=None, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('', result)
        cv2.waitKey()

if __name__ == '__main__':
    api = SimulatorAPI()
    api.render()