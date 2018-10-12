# coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import os
from sklearn.decomposition import PCA
import re
import math

Dir = '/home/fan/generate-motion-from-roadmap/readed_data/smoothed.txt'
data = []
with open(Dir, 'r') as txtFile:
    for line in txtFile:
        tmplist = []
        line = re.split(r'[,\s]+',line)
        if '' in line:
            line.remove('')
        else:
            pass
        for i in range(len(line)):
            tmplist.append(float(line[i]))
        data.append(tmplist)

data = np.array(data)
pca = PCA(n_components=2)
pca.fit(data)
processed = pca.transform(data)

x = processed[:,0]
y = processed[:,1]
xi, yi = [], []
fig = plt.figure(figsize=(8,8))
plt.scatter(x,y)
plt.title("PCA")
# ax = plt.axes()
line, = plt.plot([], [], 'r-', lw=1, animated=False)

def init():
    line.set_data([], [])
    return line,

def animate(i):
    xi.append(x[i])
    yi.append(y[i])# update the data
    line.set_data(xi, yi)
    return line,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=900, blit=True)
anim.save('basic_animation.gif', writer='imagemagick', fps=90)
plt.show()
