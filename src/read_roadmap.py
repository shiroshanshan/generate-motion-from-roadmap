import numpy as np
from VmdCreator import *
import csv
import datetime
import re
import math
import argparse
import matplotlib.pyplot as plt
from utils import *

roadmap_array = {}

class Roadmap(object):

    def __init__(self):
        self.states = []
        self.length = 0
        self.one_way_states = []

    def read_roadmap(self, roadmap_dic):
        for key, value in roadmap_dic.items():
            for i in range(len(value[:-1])):
                value[i] = string2nparray(value[i])
            state = State(string2nparray(key),value[:-1])
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

    def motion_generation(self, init_state, vmd_file, bone_csv_file, plot, write):
        init_state = rdp.init_state()
        rotations = []
        print('vmd file generating')
        rotations.append(init_state)
        frames = 120
        route = []
        for i in range(frames):
            print('%d/%d'%(i, frames))
            if roadmap_array[np.array2string(init_state)]:
                next = roadmap_array[np.array2string(init_state)][:-1]
                route.append(roadmap_array[np.array2string(init_state)][-1])
                selected_state = select_policy(rotations, self.one_way_states, init_state, next, 100)
                rotations.append(selected_state)
                init_state = selected_state
            else:
                print('no connected state')
                break

        if write == True:
            with open('readed_data/raw_data.txt','w') as f:
                write_rotation_file(f, rotations)
        if plot == True:
            plt.figure(1)
            raw_data_image = showAnimCurves(rotations, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'images/raw_data.png'
            plt.savefig(fig_name)
        rotations = filter(rotations)
        if write == True:
            with open('readed_data/smoothed.txt','w') as f:
                write_rotation_file(f, rotations)
        if plot == True:
            plt.figure(2)
            smoothed_image = showAnimCurves(rotations, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'images/smoothed.png'
            plt.savefig(fig_name)
        if plot == True:
            plt.figure(3)
            raw_data_image = plot_route_transfer(route, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Route(#)')
            fig_name = 'images/route_transfer.png'
            plt.savefig(fig_name)
        generate_vmd_file(rotations, vmd_file, bone_csv_file)
        return rotations

    ##################################### old version ##############################################
    def isolated_proportion(self):
        for state, connect in roadmap_array.items():
            if (len(connect[:-1]) == 2 or len(connect[:-1]) == 1) and self.one_way_state(state):
                self.one_way_states.append(string2nparray(state))
        print(len(self.one_way_states))
        cnt = 0
        loop = 0
        while True:
            loop += 1
            print('loop:%d'%(loop))
            decrease = False
            for state, connect in roadmap_array.items():
                if whether_in(string2nparray(state), self.one_way_states):
                    continue
                ows = True
                for item in connect:
                    if np.all(item == string2nparray(state)):
                        continue
                    if not whether_in(item, self.one_way_states):
                        ows = False
                if ows:
                    cnt += 1
                    print(cnt)
                    self.one_way_states.append(string2nparray(state))
                    decrease = True
            if not decrease:
                break
        print('proportion: %d/%d'%(len(self.one_way_states), len(roadmap_array)))

    def one_way_state(self, state):
        next_state = roadmap_array[state]
        if len(next_state[:-1]) == 1:
            return True
        while len(next_state[:-1]) == 2:
            if np.all(next_state[:-1][0] == state):
                state = next_state[:-1][1]
            else:
                state = next_state[:-1][0]
            tmp = roadmap_array[np.array2string(state)]
            if (np.all(tmp[0] == next_state[0]) and np.all(tmp[1] == next_state[1])) or (np.all(tmp[0] == next_state[1]) and np.all(tmp[1] == next_state[0])):
                return True
            next_state = tmp
            if len(next_state[:-1]) == 1:
                return True
        return False

        ##################################################################

class State(object):

    def __init__(self, state, connect):
        self.state = state
        self.connect = connect

    def calculate_distance(self, state):
        position_distance = np.linalg.norm(self.state-state)
        return position_distance

with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
    roadmap = f.read()
    roadmap = eval(roadmap)
rdp = Roadmap()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-p', '--plot', dest='plot', type=bool,
                        help='plot images')
    parser.add_argument('-t', '--test', dest='test', type=bool,
                        help='for tests')
    parser.add_argument('-w', '--write', dest='write', type=bool,
                        help='write files')
    args = parser.parse_args()
    plot = args.plot
    test = args.test
    write = args.write

    with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
        roadmap = f.read()
        roadmap = eval(roadmap)
    rdp = Roadmap()
    rdp.read_roadmap(roadmap)
    init_state = rdp.init_state()
    # rdp.isolated_proportion()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bone_csv_file = '/home/fan/generate-motion-from-roadmap/model.csv'
    vmd_file = '/home/fan/generate-motion-from-roadmap/vmdfile/{0}.vmd'.format(timenow)
    states = rdp.motion_generation(init_state, vmd_file, bone_csv_file, plot, write)
