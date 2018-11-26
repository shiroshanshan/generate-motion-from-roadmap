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

# roadmap_array = {}

class Roadmap(object):

    def __init__(self):
        self.states = []
        self.route = []

    def read_roadmap(self, string_dic):
        roadmap_dic = {}
        self.length = len(string_dic)
        self.matrix = lil_matrix(self.length, self.length)
        idx = 0

        for key, value in string_dic.items():
            for i in range(len(value[:-1])):
                self.matrix[idx][string_dic.keys().index(value[i])] = 1
            idx += 1
            self.states.append(string2nparray(key))
            self.route.append(value[-1])

        print('read roadmap successful')

    def init_state(self):
        choice = np.random.randint(0, self.length)

        return self.states[choice]

    def motion_generation(self, init_state, vmd_file, bone_csv_file, plot, write):
        init_state = self.init_state()
        rotations = np.array([])
        routes = []
        print('vmd file generating')
        rotations = np.append(rotations, init_state[0])
        frames = 40

        for i in range(frames):
            print('frames:%d/%d'%(i, frames))
            idx = self.states.index(init_state)
            next = self.matrix[idx, :].todense()

            if 1 in next:
                routes.append(self.route[idx])
                selected_state = self.states[select_policy(next, 'random')]
                init_state = selected_state
                rotations = np.append(rotations, selected_state[0])
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

        return rotations

# with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
#     roadmap = f.read()
#     roadmap = eval(roadmap)
# rdp = Roadmap()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-p', '--plot', dest='plot', type=bool,
                        help='plot images')
    parser.add_argument('-w', '--write', dest='write', type=bool,
                        help='write files')
    args = parser.parse_args()
    plot = args.plot
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
