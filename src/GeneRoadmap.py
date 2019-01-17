import json
import os
import re
import numpy as np
import threading
import math
import argparse
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from scipy import io
from scipy.stats import gaussian_kde
from scipy.sparse import lil_matrix, csr_matrix, csc_matrix
from sklearn.metrics.pairwise import cosine_similarity
from connect import connect_state

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


"""
search tiny loops in the graph by brute search
"""
class Searchloops:
    def __init__(self, matrix):
        self.matrix = matrix
        self.twos = 0
        self.threes = 0
        self.links = 0

    def search(self):
        for i in range(len(self.matrix.rows)):
            for j in self.matrix.rows[i]:
                self.links += 1
                ''' avoid twice count and self connect'''
                if j > i and self.matrix[j,i] != 0:
                    self.twos += 1

        for i in range(len(self.matrix.rows)):
            for j in self.matrix.rows[i]:
                for k in self.matrix.rows[j]:
                    if self.matrix[k,i] != 0:
                        self.threes += 1

        self.threes /= 3
        print('number of links: {0}'.format(self.links))
        print('number of loops (length of two) : {0}'.format(self.twos))
        print('number of loops (length of three) : {0}'.format(int(self.threes)))
        with open(LOG_PATH, 'a') as f:
            f.write('number of links: {0}\n'.format(self.links))
            f.write('number of loops (length of two) : {0}\n'.format(self.twos))
            f.write('number of loops (length of three) : {0}\n'.format(int(self.threes)))

"""
union find tree search
"""
class Unionfind:

    def __init__(self, groups):
        self.groups=groups
        self.items=[]
        for g in groups:
            self.items+=list(g)
        self.items=set(self.items)
        self.parent={}
        self.rootdict={}
        for item in self.items:
            self.rootdict[item]=1
            self.parent[item]=item

    def union(self, r1, r2):
        rr1=self.findroot(r1)
        rr2=self.findroot(r2)
        cr1=self.rootdict[rr1]
        cr2=self.rootdict[rr2]
        if cr1>=cr2:
            self.parent[rr2]=rr1
            self.rootdict.pop(rr2)
            self.rootdict[rr1]=cr1+cr2
        else:
            self.parent[rr1]=rr2
            self.rootdict.pop(rr1)
            self.rootdict[rr2]=cr1+cr2

    def findroot(self, r):
        if r in self.rootdict.keys():
            return r
        else:
            return self.findroot(self.parent[r])

    def createtree(self):
        for g in self.groups:
            if len(g)< 2:
                continue
            else:
                for i in range(0, len(g)-1):
                    if self.findroot(g[i]) != self.findroot(g[i+1]):
                        self.union(g[i], g[i+1])

    def tree(self, save=False):
        self.rs={}
        for item in self.items:
            root=self.findroot(item)
            self.rs.setdefault(root,[])
            self.rs[root]+=[item]
        if save:
            with open(LOG_PATH, 'a') as f:
                cnt = 0
                for item in self.rs.keys():
                    print('number of states in union {0}: {1}'.format(cnt, len(self.rs[item])))
                    f.write('number of states in union {0}: {1}\n'.format(cnt, len(self.rs[item])))
                    cnt += 1
                print('number of union: {0}'.format(len(self.rs.keys())))
                f.write('number of union: {0}\n'.format(len(self.rs.keys())))


class State(object):

    """
    initiate state
    """
    def __init__(self, rotation):
        if type(rotation) == np.ndarray:
            self.position = np.array(rotation)
            self.prev = None
            self.next = None
            self.velocity = None
            self.state = None
        else:
            print('the argument need to be a list(frame)')
            with open(LOG_PATH, 'a') as f:
                f.write('the argument need to be a list(frame)\n')

    """
    calculate velocity from rotations
    """
    def calculate_velocity(self):
        if np.all(self.next == None):
            self.velocity = self.position - self.prev
        elif np.all(self.prev == None):
            self.velocity = self.next - self.position
        else:
            self.velocity = (self.next - self.prev) / 2
        self.state = np.vstack((self.position[np.newaxis,:], self.velocity[np.newaxis,:]))

    """
    calculate dp and dv
    """
    def calculate_difference(self, position, velocity):
        position_difference = position - (self.state[0] + self.state[1])
        velocity_difference = velocity - self.state[1]

        return position_difference, velocity_difference

    """
    calculate norm
    """
    def calculate_distance(self, state):
        ''' return norm of difference of original data'''
        position_distance = np.linalg.norm(self.state[0]-state.state[0])
        velocity_distance = np.linalg.norm(self.state[1]-state.state[1])

        return position_distance + velocity_distance

    """
    determine connection
    """
    def connect(self, state, threshold):
        ''' return confidence of connection'''
        dp, dv = self.calculate_difference(state.state[0], state.state[1])
        confidence = connect_state(dp, dv, dif_mean, dif_std, threshold)
        if confidence > threshold:
            return confidence
        else:
            return 0

    """
    round function
    """
    def rounded(self):
        ''' return rounded value'''
        idx, row, column = self.state.shape
        state = np.zeros((idx, row, column))
        for i in range(self.state.size):
            state[i//30][i%30//column][i%30%column] = round(self.state.item(i), 1)
        return state


class Roadmap(object):

    """
    initiate states
    """
    def __init__(self, length):
        self.ends = []
        for i in range(len(length)):
            if i == 0:
                self.ends.append(length[0])
            else:
                self.ends.append(self.ends[i-1] + length[i])
        self.number = len(self.ends)
        self.states = []
        self.passes = []

    """
    create states
    """
    def create_states(self, data):
        ''' create state obj in roadmap obj'''
        global dif_mean, dif_std
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
                elif j == len(partition)-1:
                    state.prev = partition[j-1]
                else:
                    state.next = partition[j+1]
                    state.prev = partition[j-1]
                state.calculate_velocity()
                route.append(state)
            self.states.append(route)

        ''' calculate std error and mean value'''
        differences = []
        for i in range(len(self.states)):
            for j in range(len(self.states[i]))[:-1]:
                difference = np.array([*self.states[i][j].calculate_difference\
                                       (self.states[i][j+1].position, self.states[i][j+1].velocity)])
                differences.append(difference)
        differences = np.array(differences)
        dif_mean = np.mean(differences, axis=0)
        dif_std = np.std(differences, axis=0)

    """
    delete state if norm(s_i, s_j) < epsilon (not be used in current version)
    """
    def eliminate_same_state(self):
        repeat_nums = 0
        accessed = []
        delete = []
        for i in range(len(self.states)):
            for j in range(len(self.states[i])):
                if np.array2string(self.states[i][j].rounded()) not in accessed:
                    accessed.append(np.array2string(self.states[i][j].rounded()))
                else:
                    repeat_nums += 1
                    delete.append((i,j,accessed.index(np.array2string(self.states[i][j].rounded()))))
            self.ends[i] -= repeat_nums
        if delete:
            for item in delete:
                self.states[item[0]][item[1]] = item[2]
                self.passes.append((item[0], item[1]))
        else:
            print('no same state')
        print('repeat:%d'%repeat_nums)
        with open(LOG_PATH, 'a') as f:
            f.write('repeat:%d\n'%repeat_nums)

        return repeat_nums

    """
    hierarchy clustering
    """
    def resampling(self, matrix, rdmplist, rtlist, rthreshold):

        ''' locality sensitive hash'''
        def lsh(state):
            return np.sum(abs(state))
        buckets = [[] for i in range(1000)]
        for i in range(len(rdmplist)):
            idx = int(lsh(rdmplist[i].state) // rthreshold + 1)
            buckets[idx].append(i)

        l = 0
        cnt = 0
        while True:
            ''' find nearest ${batch_size} states'''
            print('resampling loops: {0}'.format(cnt))
            cnt += 1
            replaces = []
            for i in range(len(rdmplist)):
                idx = int(lsh(rdmplist[i].state) // rthreshold + 1)
                bucket = buckets[idx-1] + buckets[idx] + buckets[idx+1]
                for item in bucket:
                    if i > item:
                        dis = rdmplist[i].calculate_distance(rdmplist[item])
                        if dis < rthreshold:
                            replaces.append(((i, item) ,dis))
            if len(replaces) >= 256:
                replaces = sorted(replaces, key=lambda x: x[-1])[:256]
            else:
                replaces = sorted(replaces, key=lambda x: x[-1])
            l += len(replaces)

            ''' merge matrix  and roadmap list and route list'''
            if replaces:
                u = Unionfind([x[0] for x in replaces])
                u.createtree()
                u.tree()
                delete = []
                for key in u.rs.keys():
                    idxes = sorted(u.rs[key])
                    delete += idxes[1:]
                    s = np.zeros(self.states[0][0].state.shape)
                    for i in range(len(idxes)):
                        s += rdmplist[idxes[i]].state
                        if i == 0:
                            pass
                        else:
                            matrix[idxes[0],:] += matrix[idxes[i],:]
                            matrix[:,idxes[0]] += matrix[:,idxes[i]]
                    s /= len(idxes)
                    rtlist = [rtlist[i] for i in range(len(rtlist)) if i not in idxes[1:]]
                    rdmplist[idxes[0]].state = s

                row = [i for i in range(len(matrix.rows)) if i not in delete]
                matrix = matrix[row,:]
                matrix = matrix[:,row]
                rdmplist = [rdmplist[i] for i in range(len(rdmplist)) if i not in delete]
            else:
                break

        print('{0} states deleted during resampling'.format(l))
        with open(LOG_PATH, 'a') as f:
            f.write('{0} states deleted during resampling\n'.format(l))

        return matrix, rdmplist, rtlist

    """
    connect states between current state and next state
    """
    def connect_origin(self):
        cnt = 0
        print('creating roadmap')
        nums = self.ends[-1]
        roadmap_list = []
        route_list = []
        roadmap = lil_matrix((nums, nums))
        for i in range(len(self.states)):
            for j in range(len(self.states[i])):
                    roadmap_list.append(self.states[i][j])
                    route_list.append(i)
                    if cnt + 1in self.ends:
                        pass
                    else:
                        roadmap[cnt, cnt+1] = 1
                    cnt += 1

        return roadmap, roadmap_list, route_list

    """
    connect states by dp and dv
    """
    def connect_probabilistic(self, matrix, rdmplist, cthreshold):
        successed = False
        cnums = []
        cnt = 0
        nums = len(matrix.rows)
        def printf():
            if successed == True:
                return 0
            timer = threading.Timer(10, printf)
            timer.start()
            print('creating roadmap:%d/%d (approximate)'%(cnt, nums))
        timer = threading.Timer(10, printf)
        timer.start()

        for i in range(len(rdmplist)):
            cnum = 0
            for j in range(len(rdmplist)):
                if i == j:
                    pass
                else:
                    v = rdmplist[i].connect(rdmplist[j], cthreshold)
                    if v:
                        matrix[i,j] = v
                        cnum += 1
            cnums.append(cnum)
            print('%d states connected'%cnum)
        successed = True

        with open(CONNECT_PATH + 'connect.txt', 'w') as f:
            f.write(str(cnums) + '\n')

        connect_image = self.cplot(cnums, plt)
        plt.xlabel('Connection')
        plt.ylabel('Number')
        fig_name = CONNECT_PATH + 'connect.png'
        plt.savefig(fig_name)

        return matrix, rdmplist

    """
    plot connect image
    """
    def cplot(self, c, _plt):
        _plt.hist(c, 5000)

        return _plt

    """
    use matrix connect roadmap and resampling
    """
    def create_roadmap_matrix_and_resampling(self, data, threshold, resampling):
        with open(LOG_PATH, 'a') as f:
            f.write('start create states @ threshold:{0} and resampling:{1}\n'.format(threshold, resampling))

        self.create_states(data)
        roadmap, roadmap_list, route_list = self.connect_origin()
        roadmap, roadmap_list, route_list = self.resampling(roadmap, roadmap_list, route_list, resampling)
        roadmap, roadmap_list = self.connect_probabilistic(roadmap, roadmap_list, threshold)

        '''make sure all states will not connect to itself'''
        for i in range(len(roadmap.rows)):
            roadmap[i,i] = 0

        roadmap_list = [roadmap_list[i].state for i in range(len(roadmap_list))]

        return roadmap, roadmap_list, route_list

    """
    decrease loops
    """
    def connection_filter(self, roadmap):
        for i in range(len(roadmap.rows)):
            if len(roadmap.rows[i]) == 1 and roadmap.rows[roadmap.rows[i][0]][0] == i:
                roadmap 

    """
    remove isolating state recursively
    """
    def eliminate_isolated_state_matrix(self, roadmap, roadmap_list, route_list):
        roadmap = roadmap.tocsr()
        change = True
        loop = 0
        dot = 0
        while change:
            print('loop of remove isolating states: {0}'.format(loop))
            loop += 1
            change = False
            delete = []
            s = roadmap.sum(axis=1)
            for i in range(len(s)):
                if s[i] == 0:
                    change = True
                    delete.append(i)
            dot += len(delete)
            row = np.arange(roadmap.shape[0])
            row = np.where(np.logical_not(np.in1d(row, delete)))[0]
            roadmap = roadmap[row,:]
            roadmap = roadmap[:,row]
            roadmap_list = [roadmap_list[i] for i in range(len(roadmap_list)) if i not in delete]
            route_list = [route_list[i] for i in range(len(route_list)) if i not in delete]
        print('after %d loops, %d dots removed because of isolating dot'%(loop, dot))
        with open(LOG_PATH, 'a') as f:
            f.write('after %d loops, %d dots removed because of isolating dot\n'%(loop, dot))
        roadmap = roadmap.tolil()
        return roadmap, roadmap_list, route_list

    """
    convert matrix obj to dictionary obj (not be used in current version)
    """
    def convert_matrix2dict(self, roadmap, roadmap_list, route_list):
        roadmap_dic = {}
        for i in range(len(roadmap_list)):
            state = np.array2string(roadmap_list[i])
            roadmap_dic[state] = []
            for j in range(len(roadmap_list)):
                if roadmap[i,j] == 1:
                    connect = roadmap_list[j].tolist()
                    roadmap_dic[state].append(connect)
            roadmap_dic[state].append(route_list[i])

        return roadmap_dic

    """
    eliminate isolated island
    """
    def eliminate_isolated_island(self, roadmap, roadmap_list, route_list):
        sets = [(i,j) for i in range(len(roadmap.rows)) for j in roadmap.rows[i]]
        u = Unionfind(sets)
        u.createtree()
        u.tree(True)

        delete = []
        m = max([len(item) for item in u.rs.values()])
        for key, item in u.rs.items():
            if len(item) == m:
                pass
            else:
                delete += item

        row = np.arange(roadmap.shape[0])
        row = np.where(np.logical_not(np.in1d(row, delete)))[0]
        roadmap = roadmap[row,:]
        roadmap = roadmap[:,row]
        roadmap_list = [roadmap_list[i] for i in range(len(roadmap_list)) if i not in delete]
        route_list = [route_list[i] for i in range(len(route_list)) if i not in delete]

        print('%d states removed because of isolated groups\n'%(len(delete)))
        with open(LOG_PATH, 'a') as f:
            f.write('%d states removed because of isolated groups\n'%(len(delete)))

        return roadmap, roadmap_list, route_list


    """
    save at ./roadmap/${timenow}
    """
    def save_roadmap(self, path, data, threshold, resampling):
        roadmap, roadmap_list, route_list = self.create_roadmap_matrix_and_resampling(data, threshold, resampling)
        roadmap, roadmap_list, route_list = self.eliminate_isolated_state_matrix(roadmap, roadmap_list, route_list)
        roadmap, roadmap_list, route_list = self.eliminate_isolated_island(roadmap, roadmap_list, route_list)

        io.savemat(path + "roadmap", {"roadmap":roadmap})
        s = Searchloops(roadmap)
        s.search()

        with open(path + 'states.txt', 'w') as f:
            f.write(str(np.array(roadmap_list).tolist()) + '\n')
        with open(path + 'routes.txt', 'w') as f:
            f.write(str(route_list) + '\n')

        print('successed save')
        print('roadmap matrix @ size of: {0}x{0}'.format(len(roadmap.rows)))
        with open(LOG_PATH, 'a') as f:
            f.write('successed save\n')
            f.write('roadmap matrix @ size of: {0}x{0}\n'.format(len(roadmap.rows)))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='create roadmap by matrix and dict')
    parser.add_argument('-t', '--threshold', dest='threshold', type=float,
                        default=0.7,help='threshold for connection, default is 0.7')
    parser.add_argument('-s', '--sampling', dest='sampling', type=bool,
                        default=False, help='whether sample @30 fps, default is 10 fps')
    parser.add_argument('-r', '--resampling', dest='resampling', type=int,
                        default=20, help='threshold for resampling, default is 20')
    args = parser.parse_args()
    threshold = args.threshold
    sampling = args.sampling
    resampling = args.resampling

    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    PATH = os.getcwd()
    ROTATION = '{0}/rotation/'.format(PATH)
    LOG_PATH = '{0}/logs/{1}/log'.format(PATH, timenow)
    CONNECT_PATH = '{0}/logs/{1}/'.format(PATH, timenow)

    if not os.path.exists('{0}/roadmap/threshold{1}_re{2}'.format(PATH, threshold, resampling)):
        os.mkdir('{0}/roadmap/threshold{1}_re{2}'.format(PATH, threshold, resampling))
    if not os.path.exists('{0}/logs/{1}'.format(PATH, timenow)):
        os.mkdir('{0}/logs/{1}'.format(PATH, timenow))
    dirs = os.listdir(ROTATION)

    data = []
    length = []

    for files in dirs:
        with open(ROTATION + files, 'r') as f:
            fr = f.readlines()

        if not sampling:
            length.append(int(math.ceil(len(fr)/3.)))
            for i in range(0, len(fr), 3):
                frame = []
                line = re.split('[,\s]+',fr[i])
                if '' in line:
                    line.remove('')
                for j in range(0, len(line), 3):
                    frame.append([float(line[j]), float(line[j+1]), float(line[j+2])])
                data.append(frame)
        else:
            length.append(len(fr))
            for line in fr:
                frame = []
                line = re.split('[,\s]+',line)
                if '' in line:
                    line.remove('')
                for j in range(0, len(line), 3):
                    frame.append([float(line[j]), float(line[j+1]), float(line[j+2])])
                data.append(frame)

    data = np.array(data)

    roadmap = Roadmap(length)
    roadmap.save_roadmap('{0}/roadmap/threshold{1}_re{2}/'.format(PATH, threshold, resampling), data, threshold, resampling)
