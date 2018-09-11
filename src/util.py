import re
import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt

def normalize(input_list):
    sum = 0.
    for item in input_list:
        sum += item
    print(sum)
    return np.array(input_list)/sum

def string2nparray(string):
    string = re.split('\n\s+',string)
    for i in range(len(string)):
        string[i] = string[i].lstrip('[ ')
        string[i] = string[i].rstrip(' ]')
        string[i] = re.split('\s+', string[i])
        for j in range(len(string[i])):
            string[i][j] = float(string[i][j])

    return np.array(string)

def select_policy(prev_states, state, next_states, number=100):
    connect_num = len(next_states)
    if len(prev_states) > number:
        memo = prev_states[-number:]
    elif len(prev_states) == 0:
        choice = np.random.randint(0, connect_num)
    else:
        memo = prev_states

    possibility = []
    for i in range(len(next_states)):
        possibility.append(1.)

    for i in range(len(memo)):
        for j in range(len(next_states)):
            if np.all(memo[i] == next_states[j]):
                possibility[j] = math.exp(-i)
            else:
                pass
    possibility = normalize(possibility)
    choice = np.random.choice(connect_num, 1, p=possibility)[0]

    return next_states[choice]

def filter(data,fc=6):
    # fps = 30
    # n = len(data)
    # dt = 1./fps
    # f = 1
    # fn = 1/(2*dt)
    #
    # fp = 2
    # fs = 3
    # gpass = 1
    # gstop = 40
    # Wp = fp/fn
    # Ws = fs/fn
    #
    # N, Wn = signal.cheb1ord(Wp, Ws, gpass, gstop)
    # b2, a2 = signal.cheby1(N, gpass, Wn, "low")
    #
    # data = np.array(data)
    # for i in range(data.shape[1]):
    #     for j in range(data.shape[2]):
    #         y = data[:,i,j]
    #         y2 = signal.filtfilt(b2, a2, y)
    #         data[:,i,j] = y2
    #
    # return data

    fps = 30
    N = len(data)
    dt = 1./fps
    t = np.arange(0, N*dt, dt)
    t = t[:N]
    freq = np.linspace(0, 1.0/dt, N)
    data = np.array(data)
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            f = data[:,i,j]
            F = np.fft.fft(f)
            F = F/(N/2.)
            F[0] = F[0]/2.
            F2 = F.copy()
            F2[(freq > fc)] = 0
            f2 = np.fft.ifft(F2)
            f2 = np.real(f2*N)
            data[:,i,j] = f2

    return data

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
    _plt.plot(il, route, 'r', linewidth=0.5)
    return _plt
