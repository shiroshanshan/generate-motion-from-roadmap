import numpy as np
from motion_generator import *
import csv
import datetime
import re
import math
from util import *

class Roadmap(object):

    def __init__(self):
        self.states = []
        self.length = 0

    def read_roadmap(self, roadmap_dic):
        for key, value in roadmap_dic.items():
            for i in range(len(value)):
                value[i] = string2nparray(value[i])
            state = State(string2nparray(key),value)
            self.states.append(state)
            roadmap_array[key] = value
        self.length = len(self.states)
        print('read roadmap successful')

    def init_state(self, np_initial_state = None):
        if np_initial_state:
            dis = 999
            for state in self.states:
                tmpdis = state.calculate_distance(np_initial_state)
                if tmpdis < dis:
                    dis = tmpdis
                    init_state = state.state

            return initial_state
        else:
            choice = np.random.randint(0, self.length)

            return self.states[choice].state

    def motion_generation(self, init_state, vmd_file, bone_csv_file):
        rotations = []
        print('vmd file generating')
        rotations.append(init_state)
        frames = 900
        for i in range(frames):
            print('%d/%d'%(i, frames))
            if roadmap_array[np.array2string(init_state)]:
                next = roadmap_array[np.array2string(init_state)]
                selected_state = select_policy(rotations, init_state, next, 100)
                rotations.append(selected_state)
                init_state = selected_state
            else:
                print('no connected state')
                break
        rotations = filter(rotations)
        generate_vmd_file(rotations, vmd_file, bone_csv_file)
        return rotations

class State(object):

    def __init__(self, state, connect):
        self.state = state
        self.connect = connect

    def calculate_distance(self, state):
        position_distance = np.linalg.norm(self.state-state)
        return position_distance

if __name__ == '__main__':
    with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
        roadmap = f.read()
        roadmap = eval(roadmap)
    roadmap_array = {}
    rdp = Roadmap()
    rdp.read_roadmap(roadmap)
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bone_csv_file = '/home/fan/Documents/model.csv'
    vmd_file = '/home/fan/generate-motion-from-roadmap/vmdfile/{0}.vmd'.format(timenow)
    states = rdp.motion_generation(init_state, vmd_file, bone_csv_file)
