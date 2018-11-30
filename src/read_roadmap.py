import numpy as np
from VmdCreator import *
from scipy.sparse import lil_matrix, csr_matrix, csc_matrix
import csv
import datetime
import re
import math
import argparse
import matplotlib.pyplot as plt
from utils import *
import threading
import json

# roadmap_array = {}

class Roadmap(object):

    def __init__(self):
        self.states = []
        self.route = []
        self.routes_dic = {}

    def read_roadmap(self, string_dic, string_routes_dic):
        self.length = len(string_dic)
        self.matrix = lil_matrix((self.length, self.length))
        print('number of states: ',self.length)
        idx = 0

        for key, value in string_routes_dic.items():
            self.routes_dic[int(key)] = value

        for key, value in string_dic.items():
            self.states.append(string2nparray(key))
            self.route.append(value[-1])

            for i in range(len(value[:-1])):
                self.matrix[idx,list(string_dic.keys()).index(np.array2string(np.array(value[i])))] = 1
            idx += 1

        print('read roadmap successful')

    def init_state(self):
        choice = np.random.randint(0, self.length)

        return choice

    def motion_generation(self, init_state, vmd_file, bone_csv_file, plot, write):
        init_state = self.init_state()
        rotations = []
        routes = []
        print('vmd file generating')
        rotations.append(init_state)
        frames = 40
        init_states_stack.append(init_state)

        if sample_new_route(self.routes_dic[init_state]):
            for i in range(frames-1):
                print('frames:%d/%d'%(i, frames-1))
                next = np.array(self.matrix[init_state, :].todense()).flatten()

                if 1 in next:
                    routes.append(self.route[init_state])
                    init_state = select_policy(next, 'random')
                    rotations.append(init_state)
                else:
                    print('no connected state')
                    break
        else:
            rotations = sample_from_recorded_routes(self.routes_dic[init_state])

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

        routes_stack.append(rotations)
        rotations = np.array(list(map(lambda x: self.states[x][0], rotations)))
        rotations = interpolation(rotations)

        if write == True:
            with open('readed_data/interpolated.txt','w') as f:
                write_rotation_file(f, rotations)

        if plot == True:
            plt.figure(2)
            raw_data_image = showAnimCurves(rotations, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'images/interpolated.png'
            plt.savefig(fig_name)

        rotations = filter(rotations)
        rotations = list(rotations)

        if write == True:
            with open('readed_data/smoothed.txt','w') as f:
                write_rotation_file(f, rotations)

        if plot == True:
            plt.figure(3)
            smoothed_image = showAnimCurves(rotations, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Rotations(Degree)')
            fig_name = 'images/smoothed.png'
            plt.savefig(fig_name)

            plt.figure(4)
            raw_data_image = plot_route_transfer(route, plt)
            plt.xlabel('Time(Second)')
            plt.ylabel('Route(#)')
            fig_name = 'images/route_transfer.png'
            plt.savefig(fig_name)
        generate_vmd_file(rotations, vmd_file, bone_csv_file)
        print('vmd file successfully saved')

        return rotations

    def save_every_ten(self):
        def save_every_ten_min():
            with open('/home/fan/generate-motion-from-roadmap/routes.json', 'w') as f:
                routes_dic = json.dumps(self.routes_dic)
                f.write(routes_dic)
            timer = threading.Timer(600, save_every_ten_min)
            timer.start()
            print('routes dictionary successfully saved')

        timer = threading.Timer(600, save_every_ten_min())
        timer.start()

with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
    roadmap = f.read()
    roadmap = eval(roadmap)

rdp = Roadmap()

with open('/home/fan/generate-motion-from-roadmap/saved/routes.json', 'r') as f:
    routes_dic = f.read()
    routes_dic = eval(routes_dic)

init_states_stack = []
routes_stack = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-p', '--plot', dest='plot', type=bool,
                        help='plot images')
    parser.add_argument('-w', '--write', dest='write', type=bool,
                        help='write files')
    args = parser.parse_args()
    plot = args.plot
    write = args.write
    with open('/home/fan/generate-motion-from-roadmap/saved/routes.json', 'r') as f:
        routes_dic = f.read()
        routes_dic = eval(routes_dic)

    init_states_stack = []
    routes_stack = []

    with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
        roadmap = f.read()
        roadmap = eval(roadmap)
    rdp = Roadmap()
    rdp.read_roadmap(roadmap, routes_dic)
    init_state = rdp.init_state()
    # rdp.isolated_proportion()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bone_csv_file = '/home/fan/generate-motion-from-roadmap/model.csv'
    vmd_file = '/home/fan/generate-motion-from-roadmap/vmdfile/{0}.vmd'.format(timenow)
    states = rdp.motion_generation(init_state, vmd_file, bone_csv_file, plot, write)
