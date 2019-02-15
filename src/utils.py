import re
import numpy as np
import math
import random
from scipy import signal, fftpack
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def interpolation(data):
    frames = len(data)
    new_data = np.zeros((data.shape[0]*3, data.shape[1], data.shape[2]))
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            y = data[:,i,j]
            x = np.linspace(0, frames * 3, num=frames, endpoint=True)
            f = interp1d(x,y,kind='cubic')
            x_new = np.linspace(0, frames * 3, num=frames * 3, endpoint=True)
            new_data[:,i,j] = f(x_new)
    return new_data

def string2nparray(strings):
    strings = re.split('\n\s+',strings)
    strings = [strings[:10], strings[10:]]
    for string in strings:
        for i in range(len(string)):
            string[i] = string[i].lstrip('[ ')
            string[i] = string[i].rstrip(' ]')
            string[i] = re.split('\s+', string[i])
            for j in range(len(string[i])):
                string[i][j] = float(string[i][j])

    return np.array(strings)

def select_policy(init, next_states, policy):
    if policy == 'no self':
        possibilities = [next_states[i] for i in range(len(next_states)) if next_states[i] != 0 and i != init]
        idxes = [i for i in range(len(next_states)) if next_states[i] != 0 and i != init]
        s = sum(possibilities)
        possibilities = [x/s for x in possibilities]
    elif policy == 'random':
        possibilities = [next_states[i] for i in range(len(next_states)) if next_states[i] != 0]
        idxes = [i for i in range(len(next_states)) if next_states[i] != 0]
        s = sum(possibilities)
        possibilities = [x/s for x in possibilities]

    return idxes[np.random.choice(np.arange(len(idxes)),p=possibilities)]

def filter(data, plot, timenow, cutoff=4):

    amplitude = 0
    fps = 30
    N = len(data)
    dt = 1./fps
    t = np.arange(0, N*dt, dt)
    t = t[:N]
    freq = np.linspace(0, 1.0/dt, N)
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            f = data[:,i,j]
            F = np.fft.fft(f)
            # F_abs = np.abs(F)
            # F_abs_amp = F_abs / N * 2
            # F_abs_amp[0] = F_abs_amp[0] / 2
            F2 = F.copy()
            F2 = F2 / N * 2.
            F2[0] = F2[0] / 2.
            F2[(freq > cutoff)] = 0
            F2_abs = np.abs(F2)
            amplitude += F2_abs
            f2 = np.fft.ifft(F2)
            f2 = np.real(f2*N)
            data[:,i,j] = f2

    if plot:
        plt.figure()
        plt.plot(amplitude)
        plt.xlabel('Frequence')
        plt.ylabel('Amplitude')
        fig_name = 'readed/{0}/freqs.png'.format(timenow)
        plt.savefig(fig_name)
    proportion = sum(amplitude[:5])/sum(amplitude)
    print('proportion below 1Hz: ', proportion)

    return data, proportion

def showAnimCurves(animData, _plt):
    animData = np.array(animData)
    for o in range(animData.shape[1]):
        xl = animData[:,o,0]
        yl = animData[:,o,1]
        zl = animData[:,o,2]
        il = np.arange(0,(animData.shape[0]-0.001)/30.,1/30.)
        _plt.plot(il, xl, 'r--', linewidth=0.2)
        _plt.plot(il, yl, 'g', linewidth=0.2)
        _plt.plot(il, zl, 'b', linewidth=0.2)
    return _plt

def plot_route_transfer(route,_plt):
    il = np.arange(0,(len(route)-0.001)/30.,1/30.)
    route = np.array(route)
    _plt.scatter(il, route, marker='_')
    return _plt

def write_rotation_file(rotationfile,rotationlist):
    for frame in rotationlist:
        for joint in frame:
            rotationfile.write(str(joint[0]) + " " + str(joint[1]) + " " + str(joint[2]))
            if np.all(joint != frame[len(frame)-1]):
                rotationfile.write(',')
            else:
                rotationfile.write('\n')

def sample_new_route(connects, m=10):
    if random.random() < math.exp(-len(connects)/m):
        return True
    else:
        return False

def sample_from_recorded_routes(connects):
    possibilities = [connects[i][40]/connects[i][41]*connects[i][42]/connects[i][43] for i in range(len(connects))]
    possibilities = list(map(lambda x: math.exp(-x), possibilities))
    s = sum(possibilities)
    possibilities = [x/s for x in possibilities]

    return connects[np.random.choice(np.arange(len(connects)),p=possibilities)]
