import random
class BaseModel():
    def __init__(self):
        pass

    def predict(self, x):
        """
        :param x: status of game.
        :return: Series of commands to be executed e.g., [(move, 1)]
        """
        return None

class Random():
    def __init__(self):
        pass
    def predict(self, state):
        # predict command ('move', 0, uid) from status
        # Caution predict function should not return the action which requires ap more then current remaining ap of uid!
        status = state[0]
        agents = status["data"]["message"]["agent_info"]["agent"]
        uids = [agentInfo['uid'] for agentInfo in agents]
        agents_info = {}
        for i in range(len(agents)):
            agents_info[agents[i]['uid']] = agents[i]
        index = random.randint(0,3)
        uid = uids[index]
        if agents_info[uid]['ap'] == 0:
            return ('endturn',)
        return ('move', 0, uid)