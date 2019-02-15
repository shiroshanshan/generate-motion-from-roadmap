import numpy as np
from VmdCreator import *
from scipy.sparse import lil_matrix, csr_matrix, csc_matrix
from scipy import io
import csv
import datetime
import re
import math
import argparse
import matplotlib.pyplot as plt
from utils import *
import threading
import json
import os

# roadmap_array = {}

class Roadmap(object):

    def __init__(self):
        self.states = []
        self.routes_dic = {}
        self.init_states_stack = []
        self.routes_stack = []

    def read_roadmap(self, matrix, states_list, routes_num, str_routes_dic):
        self.length = len(states_list)
        self.matrix = matrix
        self.routes = routes_num
        print('number of states: ',self.length)
        idx = 0

        for key, value in str_routes_dic.items():
            self.routes_dic[int(key)] = value

        for i in range(len(states_list)):
            self.states.append(np.array(states_list[i]))

        ################## test ########################
        for i in range(self.length):
            next = np.array(self.matrix[i, :].todense()).flatten()
            if not np.any(next):
                print('==============================================')
                print(i,"th state don't have any connected state!")
        ################## test ########################
        print('read roadmap successful')

    def init_state(self):
        choice = np.random.randint(0, self.length)

        return choice

    def motion_generation(self, init_state, vmd_file, bone_csv_file, plot, write):
        # init_state = self.init_state()
        rotations = []
        routes = []
        # print('vmd file generating')
        rotations.append(init_state)
        frames = 50
        self.init_states_stack.append(init_state)

        if sample_new_route(self.routes_dic[init_state]):
            for i in range(frames-1):
                # print('frames:%d/%d'%(i, frames-1))
                next = np.array(self.matrix[init_state, :].todense()).flatten()
                if np.any(next):
                    routes.append(self.routes[init_state])
                    init_state = select_policy(init_state, next, 'no self')
                    rotations.append(init_state)
                else:
                    print('no connected state')
                    break
        else:
            rotations = sample_from_recorded_routes(self.routes_dic[init_state])

        last = rotations[-10]
        print(rotations)
        timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if write or plot:
            os.mkdir('readed/{0}'.format(timenow))

        if write:
            with open('readed/{0}/rotations.txt'.format(timenow),'w') as f:
                f.write(str(rotations))

        self.routes_stack.append(rotations)
        ## [0] => position, [1] => velocity
        rotations = np.array(list(map(lambda x: self.states[x][0], rotations)))

        if write:
            with open('readed/{0}/raw_data.txt'.format(timenow),'w') as f:
                write_rotation_file(f, rotations)

        # os.mkdir('readed/{0}'.format(timenow))
        if plot:
            plt.figure()
            raw_data_image = showAnimCurves(rotations[:40], plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'readed/{0}/raw_data.png'.format(timenow)
            plt.savefig(fig_name)

        rotations = interpolation(rotations)

        if write:
            with open('readed/{0}/interpolated.txt'.format(timenow),'w') as f:
                write_rotation_file(f, rotations)

        if plot:
            plt.figure()
            raw_data_image = showAnimCurves(rotations[:120], plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'readed/{0}/interpolated.png'.format(timenow)
            plt.savefig(fig_name)

        rotations, proportion = filter(rotations, plot, timenow, 2)

        if write:
            with open('readed/{0}/smoothed.txt'.format(timenow),'w') as f:
                write_rotation_file(f, list(rotations))

        if plot:
            plt.figure()
            smoothed_image = showAnimCurves(rotations[:120], plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'readed/{0}/smoothed.png'.format(timenow)
            plt.savefig(fig_name)

            plt.figure()
            raw_data_image = plot_route_transfer(routes, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Route(#)')
            fig_name = 'readed/{0}/route_transfer.png'.format(timenow)
            plt.savefig(fig_name)

        generate_vmd_file(rotations, vmd_file, bone_csv_file)
        print('vmd file successfully saved')

        return last, proportion

    def save_every_ten(self):
        def save_every_ten_min():
            with open('roadmap/saved/routes.json', 'w') as f:
                routes_dic = json.dumps(self.routes_dic)
                f.write(routes_dic)
            timer = threading.Timer(600, save_every_ten_min)
            timer.start()
            print('routes dictionary successfully saved')

        timer = threading.Timer(600, save_every_ten_min)
        timer.start()

    def test_filter_param(self, vmd_file, bone_csv_file, fc):
        rotations = [15063, 15064, 15065, 15066, 15067, 4852, 14793, 4834, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 8849, 8850, 8851, 8852, 329, 328, 342, 415, 3806, 4641, 7807, 7808]
        rotations = np.array(list(map(lambda x: self.states[x][0], rotations)))
        rotations = interpolation(rotations)
        rotations = filter(rotations, False, 0, fc)
        generate_vmd_file(rotations, vmd_file, bone_csv_file)
        print('test file created')

PATH = os.getcwd()

roadmap = io.loadmat("roadmap/roadmap")["roadmap"]

with open('roadmap/states.txt', 'r') as f:
    states = f.read()
    states = eval(states)
with open('roadmap/routes.txt', 'r') as f:
    routes = f.read()
    routes = eval(routes)
with open('roadmap/saved/routes.json', 'r') as f:
    routes_dic = f.read()
    routes_dic = eval(routes_dic)

rdp = Roadmap()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-p', '--plot', dest='plot', type=bool,
                        default=False, help='plot images')
    parser.add_argument('-w', '--write', dest='write', type=bool,
                        default=False, help='write files')
    parser.add_argument('-i', '--information', dest='information', type=bool,
                        default=False, help='debug information')
    args = parser.parse_args()
    plot = args.plot
    write = args.write
    information = args.information

    roadmap = io.loadmat("/home/fan/generate-motion-from-roadmap/roadmap/roadmap")["roadmap"]

    with open('/home/fan/generate-motion-from-roadmap/roadmap/states.txt', 'r') as f:
        states = f.read()
        states = eval(states)
    with open('/home/fan/generate-motion-from-roadmap/roadmap/routes.txt', 'r') as f:
        routes = f.read()
        routes = eval(routes)
    with open('/home/fan/generate-motion-from-roadmap/roadmap/saved/routes.json', 'r') as f:
        routes_dic = f.read()
        routes_dic = eval(routes_dic)

    rdp = Roadmap()
    rdp.read_roadmap(roadmap, states, routes, routes_dic)
    init_state = rdp.init_state()
    # rdp.isolated_proportion()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bone_csv_file = '/home/fan/generate-motion-from-roadmap/model.csv'
    vmd_file = '/home/fan/generate-motion-from-roadmap/test/vmdfile/{0}.vmd'.format(timenow)
    states = rdp.motion_generation(init_state, vmd_file, bone_csv_file, plot, write)
