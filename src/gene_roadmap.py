import json
import os
import re
import numpy as np
from scipy.stats import gaussian_kde
from scipy.sparse import lil_matrix, csr_matrix, csc_matrix
from sklearn.metrics.pairwise import cosine_similarity
import threading
import math
import argparse
import datetime

###
#a object called state
###
class State(object):
    def __init__(self, roataion):
        if type(rotation) == list:
            self.position = np.array(rotation)
            self.prev = None
            self.next = None
            self.velocity = None
            self.state = None
        else:
            print('the argument need to be a list(frame)')
            with open(LOG_PATH, 'a') as f:
                f.write('the argument need to be a list(frame)\n')

    def calculate_velocity(self):
        if self.next == None:
            self.velocity = self.position - self.prev
        elif self.prev == None:
            self.velocity = self.next - self.position
        else:
            self.velocity = (self.next - self.prev) / 2
        self.state = np.vstack((self.position[np.newaxis,:], self.velocity[np.newaxis,:]))

    def calculate_difference(self, position, velocity):
        position_difference = position - (self.position + self.velocity)
        velocity_difference = velocity - self.velocity

        return position_difference, velocity_difference

    def connect(self, state, threshold):
        confidence = discriminator(self.state, state)
        if confidence > threshold:
            return True
        else:
            return False

    def rounded(self):
        idx, row, column = self.state.shape
        state = np.zeros((idx, row, column))
        for i in range(self.state.size):
            state[i//30][i%30//column][i%column] = round(self.position.item(i),1)
        return state


class Roadmap(object):
    def __init__(self, length):
        self.ends = []
        for i in range(len(length)):
            if i == 0:
                self.ends.append(length[0])
            else:
                self.ends.append(self.ends[i-1] + length[i])
        self.number = len(self.ends)
        self.states = []

    ###
    #initiate states
    ###
    def create_states(self, data):
        for i in range(self.number):
            if i == 0:
                partition = data[:self.ends[i]]
            else:
                partition = data[self.ends[i-1]:self.ends[i]]
            route = []
            for j in range(len(partition)):
                state = State(partition[j])
                if j == 0:
                    state.next = partition[j+1]
                elif j == len(routes)-1:
                    state.prev = partition[j-1]
                else:
                    state.next = partition[j+1]
                    state.prev = partition[j-1]
                state.calculate_velocity()
                route.append(state)
            self.states.append(route)

    ###
    #delete state if norm(s_i, s_j) < epsilon
    ###
    def eliminate_same_state(self):
        repeat_nums = 0
        for i in range(len(self.states)):
            accessed = []
            delect = []
            for j in range(len(self.states[i])):
                if np.array2string(self.states[i][j].rounded()) not in accessed:
                    accessed.append(np.array2string(self.states[i][j].rounded()))
                else:
                    repeat_nums += 1
                    delect.append(j)
            if delect:
                self.states[i] = [self.states[i][k] for k in range(len(self.states[i])) if k not in delect]
            else:
                print('no same state in route %d'%i)
        print('repeat:%d'%repeat_nums)
        with open(LOG_PATH, 'a') as f:
            f.write('repeat:%d\n'%repeat_nums)

        return repeat_nums

    ###
    #reject sampling
    ###
    def resampling(self, connected, threshold=10):
        if np.random.uniform(0, len(connected)) > threshold:
            return True
        else:
            return False

    ###
    #use matrix connect roadmap and resampling
    ###
    def create_roadmap_matrix_and_resampling(self, data):
        self.create_states(data)
        decrease = self.eliminate_same_state()
        self.resampling()
        roadmap_list = []
        route_list = []
        next = []
        delect = []
        cnt = 0
        print('creating roadmap')
        nums = self.length_list[self.number-1] - decrease)

        for i in range(len(self.states)):
            for j in range(len(self.states[i])):

                np.array2string(self.states[i][j].rounded())
                print('creating roadmap:%d/%d (approximate)'%(cnt, nums)
                roadmap_list.append((i,j))
                route_list.append(i)
                connected = []

                for k in range(len(self.states)):
                    for l in range(len(self.states[k])):
                        if self.states[i][j].connect(self.states[k][l].state, threshold):
                            connected.append((k,l))

                if self.resampling(connected, threshold):
                    delect.append(cnt)
                elif j == len(self.states[i])-1:
                    pass
                elif (i,j+1) not in connected:
                    connected.append((i,j+1))
                else:
                    pass
                print('%d states connected', len(connected))
                next.append(connected)
                cnt += 1

        with open(CONNECT_PATH, 'w') as f:
            f.wirte(str(list(map(lambda x: len(x), next))))

        print('%d states delected due to resampling!')
        with open(LOG_PATH, 'a') as f:
            f.write('%d states delected due to resampling!\n')

        ###
        #check if delected state in the connection list of other state
        ###
        delected_states = [roadmap_list[i] for i in delect]
        for i in range(len(next)):
            next[i] = [next[i][j] for j in range(len(next[i])) if next[i][j] not in delected_states]

        ###
        #delect states that should be resampled
        ###
        roadmap_list = [roadmap_list[i] for i in range(len(roadmap_list)) if i not in delect]
        route_list = [route_list[i] for i in range(len(route_list)) if i not in delect]
        next = [next[i] for i in range(len(next)) if i not in delect]

        ###
        #connect states in matrix
        ###
        roadmap = lil_matrix((len(roadmap_list), len(roadmap_list)))
        print('calculating roadmap matrix')
        cnt = 0
        successed = False

        def printf():
            if successed == True:
                return 0
            timer = threading.Timer(10, printf)
            timer.start()
            print('calculating roadmap matrix:%d/%d'%(cnt,len(roadmap_list)))

        timer = threading.Timer(10, printf)
        timer.start()

        for i in range(len(next)):
            cnt += 1
            for j in range(len(next[i])):
                idx = roadmap_list.index(next[i][j])
                roadmap[i,idx] = 1
        successed = True
        roadmap_list = list(map(lambda i,j: self.states[i][j].rounded(), *zip(*roadmap_list)))
        return roadmap, roadmap_list, route_list

    def eliminate_isolated_state_matrix(self, roadmap, roadmap_list, route_list):
        roadmap = roadmap.tocsr()
        change = True
        loop = 0
        dot = 0
        while change:
            print('loop:%s'%(loop))
            loop += 1
            change = False
            delete = []
            s = roadmap.sum(axis=1)
            for i in range(len(s)):
                if s[i] == 1:
                    change = True
                    delete.append(i)
            dot += len(delete)
            row = np.arange(roadmap.shape[0])
            row = np.where(np.logical_not(np.in1d(row, delete)))[0]
            roadmap = roadmap[row,:]
            roadmap = roadmap[:,row]
            roadmap_list = [roadmap_list[i] for i in range(len(roadmap_list)) if i not in delect]
            route_list = [route_list[i] for i in range(len(route_list)) if i not in delect]
        print('after %d loops, %d dots deleted because of isolated dot'%(loop, dot))
        with open(LOG_PATH, 'a') as f:
            f.write('after %d loops, %d dots deleted because of isolated dot\n'%(loop, dot))

        return roadmap, roadmap_list, route_list

    def convert_matrix2dict(self, roadmap, roadmap_list, route_list):
        roadmap_dic = {}
        for i in range(len(roadmap_list)):
            state = np.array2string(self.states[roadmap_list[i]].state)
            roadmap_dic[state] = []
            for j in range(len(roadmap_list)):
                if roadmap[i,j] == 1:
                    connect = self.states[roadmap_list[j]].state.tolist()
                    roadmap_dic[state].append(connect)
            roadmap_dic[state].append(route_list[i])

        return roadmap_dic

    def save_roadmap(self, path, data):
        roadmap, roadmap_list, route_list = self.create_roadmap_matrix(data)
        roadmap, roadmap_list, route_list = self.eliminate_isolated_state_matrix(roadmap, roadmap_list, route_list)
        roadmap = self.convert_matrix2dict(roadmap, roadmap_list, route_list)

        roadmap = json.dumps(roadmap)
        with open(path, 'w') as f:
            f.write(roadmap)
        global successed
        successed = True
        print('successed save')
        with open(LOG_PATH, 'a') as f:
            f.write('successed save')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='create roadmap by dict (or matrix)')
    parser.add_argument('-m', '--matrix', dest='matrix', type=bool,
                        help='create roadmap by matrix')
    args = parser.parse_args()
    matrix = args.matrix

    JOINT_NAME = [''] * 10
    JOINT_NAME[0] = 'Upper Body'
    JOINT_NAME[1] = 'Lower Body Scaled'
    JOINT_NAME[2] = 'Neck'
    JOINT_NAME[3] = 'Head'
    JOINT_NAME[4] = 'Left Shoulder'
    JOINT_NAME[5] = 'Left Wrist'
    JOINT_NAME[6] = 'Left Elbow'
    JOINT_NAME[7] = 'Right Shoulder'
    JOINT_NAME[8] = 'Right Wrist'
    JOINT_NAME[9] = 'Right Elbow'

    ROADMAP = {}
    successed = False
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    PATH = '/home/fan/generate-motion-from-roadmap/rotation/'
    LOG_PATH = '/home/fan/generate-motion-from-roadmap/logs/log'
    CONNECT_PATH = '/home/fan/generate-motion-from-roadmap/logs/connect/{0}'.format(timenow)
    dirs = os.listdir(PATH)
    data = []
    length = []

    with open(LOG_PATH, 'a') as f:
        f.write('\n-----------------------------------\n{0}\n-----------------------------------\n\n'.format(timenow))

    for files in dirs:
        with open(PATH + files, 'r') as f:
            fr = f.readlines()
            length.append(int(math.ceil(len(fr)/3.)))
            for i in range(0, len(fr), 3):
                frame = []
                line = re.split('[,\s]+',fr[i])
                if '' in line:
                    line.remove('')
                else:
                    pass
                for j in range(0, len(line), 3):
                    joint = []
                    joint.append(float(line[j]))
                    joint.append(float(line[j+1]))
                    joint.append(float(line[j+2]))
                    frame.append(joint)
                data.append(frame)

    roadmap = Roadmap(length)
    roadmap.save_roadmap('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', data)
