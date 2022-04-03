import requests
import json
import random
import time
from api import ADEX_API
import random
import time
from model import Random

if __name__  == '__main__':
    api = ADEX_API()
    api.create()
    api.join('jsheo')
    api.join('enemy')
    api.start('jsheo')

    model = Random()

    while True:
        while True:
            state = api.state('enemy')
            command = model.predict(state)
            api.execute(command, playername='enemy')
            if command[0] == 'endturn':
                break
        while True:
            state = api.state('jsheo')
            command = model.predict(state)
            api.execute(command, playername='jsheo')
            if command[0] == 'endturn':
                break
