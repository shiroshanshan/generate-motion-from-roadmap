import numpy as np
from motion_generator import *
import csv
import datetime
import re

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
        frames = 9000
        for i in range(frames):
            print('%d/%d'%(i, frames))
            if roadmap_array[np.array2string(init_state)]:
                next = roadmap_array[np.array2string(init_state)]
                selected_state = divergence_select(next)
                rotations.append(selected_state)
                init_state = selected_state
            else:
                print('no connected state')
                break
        generate_vmd_file(rotations, vmd_file, bone_csv_file)

        return rotations

class State(object):

    def __init__(self, state, connect):
        self.state = state
        self.connect = connect

    def calculate_distance(self, state):
        position_distance = np.linalg.norm(self.state-state)
        return position_distance


def string2nparray(string):
    string = re.split('\n\s+',string)
    for i in range(len(string)):
        string[i] = string[i].lstrip('[ ')
        string[i] = string[i].rstrip(' ]')
        string[i] = re.split('\s+', string[i])
        for j in range(len(string[i])):
            string[i][j] = float(string[i][j])

    return np.array(string)

def divergence_select(states):
    connect_num = len(states)
    choice = np.random.randint(0, connect_num)
    return states[choice]

if __name__ == '__main__':
    with open('/home/fan/build_roadmap/roadmap/roadmap.json', 'r') as f:
        roadmap = f.read()
        roadmap = eval(roadmap)
    roadmap_array = {}
    rdp = Roadmap()
    rdp.read_roadmap(roadmap)
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bone_csv_file = '/home/fan/Documents/model.csv'
    vmd_file = '/home/fan/build_roadmap/vmdfile/{0}.vmd'.format(timenow)
    states = rdp.motion_generation(init_state, vmd_file, bone_csv_file)
