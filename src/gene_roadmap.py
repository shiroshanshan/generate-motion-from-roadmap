import json
import os
import re
import numpy as np
from scipy.stats import gaussian_kde

class State(object):
    def __init__(self, position, next):
        if type(position) == list and type(next) == list:
            self.position = np.array(position)
            self.next = np.array(next)
            self.velocity = self.next - self.position
            self.state = np.hstack((self.position, self.velocity))
        else:
            print('the argument need to be a list(frame)')

    def calculate_distance(self, state):
        position_distance = np.linalg.norm(self.position-state.position)
        velocity_distance = np.linalg.norm(self.velocity-state.velocity)

        return position_distance, velocity_distance

    def connect(self, state, mp, mv):
        position, velocity = self.calculate_distance(state)
        if position < 2*mp and velocity < 2*mv and position != 0:
            return True
        else:
            return False

    def rounded(self):
        row, column = self.position.shape
        state = np.zeros((row, column))
        for i in range(self.position.size):
            state[i/column][i%column] = round(self.position.item(i),1)
        return state

    def rounded_next(self):
        row, column = self.next.shape
        state = np.zeros((row,column))
        for i in range(self.next.size):
            state[i/column][i%column] = round(self.next.item(i),1)
        return state


class Roadmap(object):
    def __init__(self, data_list, length_list):
        self.data_list = data_list
        self.length_list = []
        for i in range(len(length_list)):
            if i == 0:
                self.length_list.append(length_list[0])
            else:
                self.length_list.append(self.length_list[i-1] + length_list[i])
        self.number = len(self.length_list)
        self.route = []
        for i in range(self.number):
            if i == 0:
                self.route.append(self.data_list[:self.length_list[i]])
            else:
                self.route.append(self.data_list[self.length_list[i-1]:self.length_list[i]])

    def create_states(self):
        self.states = []
        for rt in self.route:
            route = []
            for i in range(len(rt)):
                if i == len(rt) - 1:
                    state = State(rt[i],rt[i])
                    route.append(state)
                else:
                    state = State(rt[i],rt[i+1])
                    route.append(state)
            self.states.append(route)

    def eliminate_same_state(self):
        repeat = 0
        for i in range(len(self.states)):
            tmp_rt = []
            delect = []
            for j in range(len(self.states[i])):
                if np.array2string(self.states[i][j].rounded()) not in tmp_rt:
                    tmp_rt.append(np.array2string(self.states[i][j].rounded()))
                else:
                    repeat += 1
                    delect.append(j)
            print(delect)
            try:
                delect.sort()
                for k in reversed(delect):
                    del self.states[i][k]
            except:
                print('no same state in route %d'%i)
        print('repeat:%d'%repeat)

    def resampling(self, size=0, threshold=10):
        eliminate = 0
        for i in range(len(self.states)):
            delect = []
            for j in range(len(self.states[i])):
                near = []
                for rt in self.states:
                    for state in rt:
                        if self.states[i][j].calculate_distance(state)[0] < size:
                            near.append(state)
                if np.random.uniform(0, len(near)) > threshold:
                    delect.append(j)
                    eliminate += 1
            try:
                print('eliminate:%d'%eliminate)
                delect.sort()
                for k in reversed(delect):
                    del self.states[i][k]
            except:
                print('no state delected in resampling')

    def find_mean_distance(self):
        # states = self.create_states()
        position_distances = 0
        velocity_distances = 0
        for route in self.states:
            for i in range(len(route)-1):
                dp, dv = route[i].calculate_distance(route[i+1])
                position_distances += dp
                velocity_distances += dv
        mean_pos_dis = position_distances / self.length_list[self.number-1]
        mean_velo_dis = velocity_distances / self.length_list[self.number-1]

        return mean_pos_dis, mean_velo_dis

    def create_roadmap(self):
        self.create_states()
        self.eliminate_same_state()
        mp, mv = self.find_mean_distance()
        self.resampling(size=mp)
        roadmap = {}
        cnt = 1
        repeat = 0
        error = []
        for rt in self.states:
            for state in rt:
                print('%d/%d'%(cnt, self.length_list[self.number-1]))
                try:
                    tmp = roadmap[np.array2string(state.rounded())]
                    print(len(state.rounded()))
                    error.append(state.rounded())
                    repeat += 1
                except:
                    cnt += 1
                    roadmap[np.array2string(state.rounded())] = []
                    roadmap[np.array2string(state.rounded())].append(np.array2string(state.rounded_next()))
                    for rt2 in self.states:
                        for state2 in rt2:
                            if state.connect(state2, mp, mv) and np.array2string(state2.rounded()) not in roadmap[np.array2string(state.rounded())]:
                                roadmap[np.array2string(state.rounded())].append(np.array2string(state2.rounded()))

                    print('%d state connected'%(len(roadmap[np.array2string(state.rounded())])))
        print('mean velocity: %f'%mv)
        print('mean position: %f'%mp)
        print('repeat: %d'%repeat)
        return roadmap

    def save_roadmap(self, path):
        roadmap = self.create_roadmap()
        roadmap = json.dumps(roadmap)
        with open(path + 'roadmap.json', 'w') as f:
            f.write(roadmap)
        print('successed save')


if __name__ == '__main__':
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
    PATH = '/home/fan/build_roadmap/rotation/'
    dirs = os.listdir(PATH)
    data = []
    length = []

    for files in dirs:
        with open(PATH + files, 'r') as f:
            f_read = f.readlines()
            length.append(len(f_read))
            for line in f_read:
                tmplist = []
                line = re.split('[,\s]+',line)
                if '' in line:
                    line.remove('')
                else:
                    pass
                for i in range(0, len(line), 3):
                    joint = []
                    joint.append(float(line[i]))
                    joint.append(float(line[i+1]))
                    joint.append(float(line[i+2]))
                    tmplist.append(joint)
                data.append(tmplist)

    roadmap = Roadmap(data, length)
    roadmap.save_roadmap('/home/fan/build_roadmap/roadmap/')
