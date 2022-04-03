# execute python controller.py after activating reciever
import cv2
import numpy as np
from api import ADEX_API
import json
import time
class Controller:
    def __init__(self, key=None):
        self.playername = 'jsheo'
        self.api = ADEX_API()
        if key == None:
            self.api.create()
            #self.api.join(self.playername)
            #self.api.start(self.playername)
        else:
            self.api.key = key
        self.black = np.zeros((500,200,3),dtype=np.uint8)
        self.ap = 10
        self.arrowmap = {ord('i'):0,ord('l'):1,ord('k'):2,ord('j'):3}
        self.viewlist = []
        self.location_list = []
        self.uid = None

    def reload(self):
        self.api.endturn(self.playername)
        self.api.endturn(self.enemyname)
        self.ap = 10

    def get_status_board(self, status):
        agents = status['responses']['data']['message']['agent_info']['agent'] # agents: list of dict
        status_board = np.zeros((1000,500,3),dtype=np.uint8)
        org_x = 0
        org_y = 30
        for agent in agents:
            cv2.putText(status_board, 'UID:'+str(agent['uid']), (org_x,org_y),0,1,(255,255,255),2)
            org_y += 30
            cv2.putText(status_board, 'Name: ' + str(agent['name']), (org_x, org_y), 0, 1, (255, 255, 255), 2)
            org_y += 30
            cv2.putText(status_board, 'Location: '+str(agent['location']), (org_x,org_y),0,1,(255,255,255),2)
            org_y += 30
            cv2.putText(status_board, 'HP: '+str(agent['hp']), (org_x, org_y), 0, 1, (255, 255, 255), 2)
            org_y += 30
            cv2.putText(status_board, 'AP: '+str(agent['ap']), (org_x,org_y),0,1,(255,255,255),2)
            org_y += 30
        return status_board

    def start_game_with_bot(self):
        self.api.reset()
        self.api.join(self.playername)
        self.api.start(self.playername)

    def run(self):
        while True:
            while True:
                status = self.api.status(self.playername)
                if 'data' in status['responses'].keys():
                    # set default UID (the first one)
                    self.agents = list(
                        map(lambda x: x['uid'], status['responses']['data']['message']['agent_info']['agent']))
                    if self.uid == None:
                        self.uid = self.agents[0]
                    break
                reset_board = np.zeros((400,1300,3),dtype=np.uint8)
                org_y = 30
                cv2.putText(reset_board, 'The game is over or not started yet', (0,org_y), 0,1,(255,255,255),2)
                org_y += 30
                cv2.putText(reset_board, 'If you want to start the game with Bot, press Y', (0,org_y), 0,1,(255,255,255),2)
                org_y += 30
                cv2.putText(reset_board, 'Otherwise, press N after you join the players and start the game', (0,org_y), 0,1,(255,255,255),2)
                cv2.imshow('', reset_board)
                c = cv2.waitKey()
                if c == ord("y"):
                    self.start_game_with_bot()
            cv2.imshow('', self.get_status_board(status))
            c = cv2.waitKey()
            if c in self.arrowmap.keys(): #move
                self.api.move(self.uid, self.arrowmap[c])
                self.ap -= 2
            elif c == ord('g'):
                self.api.attack(self.uid)
                self.ap -= 4
            elif c == ord('u'):
                self.api.rotate(self.uid, -45)
                self.ap -= 1
            elif c == ord('o'):
                self.api.rotate(self.uid, 45)
                self.ap -= 1
            elif c == ord('h'):
                #json.dump(self.viewlist, open('viewlist.json','w'))
                json.dump(self.location_list, open('location_list2.json', 'w'))
            elif c == ord('q'):
                self.uid = self.agents[0]
            elif c == ord('w'):
                self.uid = self.agents[1]
            elif c == ord('e'):
                self.uid = self.agents[2]
            elif c == ord('r'):
                self.uid = self.agents[3]
            elif c == ord('z'):
                self.api.endturn(self.playername)

            #self.update_location_list()

    def update_location_list(self):
        location = self.api.get_agent_info(self.playername)[self.uid]['location']
        self.location_list.append(location)
        #if location not in self.location_list:

    def update_viewlist(self):
        locations =list(map(lambda x: x['location'], self.viewlist))
        view = self.api.view(self.uid)
        for object in view['responses']['data']['message']['info']:
            if object['location'] not in locations:
                self.viewlist.append(object)




if __name__ == '__main__':
    controller = Controller()
    controller.run()