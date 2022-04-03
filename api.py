import requests
import json

class ADEX_API(object):
    def __init__(self):
        self.ip = "121.152.194.120"
        self.url = 'http://20.196.214.79:5050'

    def createtest(self):
        params = {"ip": self.ip, 'port': 5050, 'key': self.key}
        create = requests.post(self.url + '/session/CreateTest', data=params)
        assert create.status_code == 200, 'CreateTest error'

    def change(self, map_name):
        params = {"key": self.key, "map_name": map_name}
        change = requests.post(self.url + '/session/change', data=params)
        print(change.content)
        assert change.status_code == 200, 'change error'

    def create(self):
        params = {"ip": self.ip}
        create = requests.post(self.url + '/session/create', data=params)
        self.key = json.loads(create.content)['key']
        print(self.key)
        # self.port = json.loads(create.content)['data']['message']['port']
        assert create.status_code == 200, 'create error'

    def end(self):
        params = {"key": self.key}
        end = requests.post(self.url + '/session/end', data=params)
        assert end.status_code == 200, 'end error'

    def join(self, playername):
        params = {"key": self.key, "playername": playername}
        join = requests.post(self.url + '/session/join', data=params)
        assert join.status_code == 200, 'Join error'

    def reset(self):
        param = {"key": self.key}
        reset = requests.post(self.url+'/session/reset', data=param)
        assert reset.status_code == 200, 'reset error'

    def resource(self):
        resource = requests.get(self.url+'/session/resource')
        assert resource.status_code == 200, 'resource error'
        json_object = json.loads(resource.content)
        return json_object

    def endturn(self, playername):
        param = {"key": self.key, "playername": playername}
        endturn = requests.post(self.url+'/game/endturn', data=param)
        assert endturn.status_code == 200, 'endturn error'

    def giveup(self, playername):
        param = {"key": self.key, "playername": playername}
        giveup = requests.post(self.url+'/game/giveup', data=param)
        assert giveup.status_code == 200, 'giveup error'

    def start(self, playername):
        startParams = {"key": self.key, "playername": playername, "istimeout": False, "timeout":60, "turn": 2, "dilation": 100}#5
        start = requests.post(self.url + '/game/start', data=startParams)
        assert start.status_code == 200, 'start error'

    def status(self, playername): # if playername is not player, it would consider it as a enemy's name
        statusParam = {"key": self.key, "playername": playername}
        # status = requests.get(self.url+'/game/status', data=statusParam)
        status = requests.get(self.url+f'/game/status?key={self.key}&playername={playername}')
        assert status.status_code == 200, 'status error'
        json_object = json.loads(status.content)
        return json_object

    def view(self, uid):
        #agents = json_object["data"]["message"]["agent_info"]["agent"]
        #agentInfo=agents[0]
        #viewParam={"key":key,"uid":agentInfo["uid"]}
        # viewParam={"key":self.key,"uid":uid}
        view = requests.get(self.url+f'/game/view?key={self.key}&uid={uid}')
        assert view.status_code == 200, 'view error'
        json_object = json.loads(view.content)
        return json_object

    def attack(self, uid, dummy=None):
        param = {"key": self.key, "uid": uid}
        attack = requests.post(self.url + '/agent/attack', data=param)
        assert attack.status_code == 200, 'attack error'

    def move(self, uid, direction):
        param = {"key": self.key, "uid": uid, "direction": direction}
        move = requests.post(self.url+'/agent/move', data=param)
        assert move.status_code == 200, 'move error'

    def rotate(self, uid, angle):
        param = {"key": self.key, "uid": uid, "angle": angle}
        rotate = requests.post(self.url+'/agent/rotate', data=param)
        assert rotate.status_code == 200, 'rotate error'


    def get_agents(self, playername):
        json_object = self.status(playername)
        agents = json_object['responses']["data"]["message"]["agent_info"]["agent"]
        uids = [agentInfo['uid'] for agentInfo in agents]
        return uids

    def get_agent_info(self, playername):
        agents_list = self.status(playername)['responses']['data']['message']['agent_info']['agent']
        agents = {}
        for i in range(len(agents_list)):
            agents[agents_list[i]['uid']] = agents_list[i]
        return agents

    def execute(self, command, playername): # must not be executed more than one within 1 sec
        # parse and execute command safely
        while True:
            isturnowner = self.status(playername)['responses']['data']['message']['game_info']['IsTurnOwner']
            if isturnowner:
                break
        assert command[0] in ['endturn','move','rotate','attack'], 'command should be one of move/rotate/attack. Got {}'.format(command[0])
        if command[0] == 'endturn':
            self.endturn(playername)
            return
        if command[0] == 'move':
            direction = command[1]
            uid = command[-1]
            func = self.move
            args = (uid, direction)
        elif command[0] == 'rotate':
            angle = command[1]
            uid = command[-1]
            func = self.rotate
            args = (uid, angle)
        elif command[0] == 'attack':
            uid = command[-1]
            func = self.attack
            args = (uid,)
        else:
            print(command)
            print('Unknown command error')
            raise NotImplementedError
        func(*args)
        print('executed', uid)

        # while True:
        #     prev_ap = self.get_agent_info(playername)[uid]['ap']
        #     func(*args)
        #     curr_ap = self.get_agent_info(playername)[uid]['ap']
        #     if prev_ap is not curr_ap:
        #         print('executed', uid)
        #         break

    def state(self, playername):
        status = self.status(playername)
        uids = self.get_agents(playername)
        views = [self.view(uid) for uid in uids]
        state = (status, views)
        return state


    def __del__(self):
        print('Destroyed')
        self.end()

if __name__ == '__main__':
    api = ADEX_API()
    api.create()
    api.join('jsheo')
    api.start('jsheo')
    status = api.status('Bot')
    print(status)
    api.end()
#
