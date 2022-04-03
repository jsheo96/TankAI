import cv2
import numpy as np
import json
j = json.load(open('viewlist_backup.json', 'r'))
global_map = np.zeros((200,200), dtype=np.uint8)
i_ = []
j_ = []
for object in j:
    y, x = object['location']
    i, j = (y-200) // 1000, (x-450) // 1000
    i_.append(i)
    j_.append(j)
    global_map[i][j] = object['ObjectType']
print(min(i_),max(i_))
print(min(j_),max(j_))
print(global_map)

def show_global_map(global_map):
    global_map = np.stack((global_map,)*3, -1)
    global_map *= 70
    cv2.imshow('', cv2.resize(global_map[24:58,147:182][::-1,:], fx=30, fy=30, dsize=None, interpolation=cv2.INTER_NEAREST))
    cv2.waitKey()

show_global_map(global_map)