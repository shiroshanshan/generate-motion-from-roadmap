import numpy as np
import re
import matplotlib.pyplot as plt
import os

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

PATH = '/home/fan/generate-motion-from-roadmap/rotation/'
dirs = os.listdir(PATH)
positions = []
velocities = []
ends = []

for files in dirs:
    with open(PATH + files, 'r') as f:
        fr = f.readlines()
        if not ends:
            ends.append(len(fr))
        else:
            ends.append(len(fr) + ends[-1])
        for line in fr:
            frame = []
            line = re.split('[,\s]+', line)
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
            positions.append(np.array(frame))

for i in range(len(positions)):
    if i == 0 or i in ends:
        velocity = positions[i+1] - positions[i]
    elif i + 1 in ends:
        velocity = positions[i] - positions[i-1]
    else:
        velocity = (positions[i+1] - positions[i-1]) / 2
    velocities.append(velocity)

dps = []
dvs = []
for i in range(len(velocities)):
    if i + 1 in ends:
        pass
    else:
        dp = positions[i+1] - (positions[i] + velocities[i])
        dv = velocities[i+1] - velocities[i]
        dps.append(dp)
        dvs.append(dv)

dvs = np.array(dvs)
dps = np.array(dps)

def normalize(x):
    return (x - np.mean(x)) / np.std(x)

def normalize_and_plot(idx):
    row = idx
    dvx = dvs[:, row, 0]
    dpx = dps[:, row, 0]
    dvx = normalize(dvx)
    dpx = normalize(dpx)

    dvy = dvs[:, row, 1]
    dpy = dps[:, row, 1]
    dvy = normalize(dvy)
    dpy = normalize(dpy)

    dvz = dvs[:, row, 2]
    dpz = dps[:, row, 2]
    dvz = normalize(dvz)
    dpz = normalize(dpz)

    plt.figure(figsize=(20,20))
    plt.subplot(221)
    plt.scatter(dvx, dpx, s=3)
    plt.title(JOINT_NAME[idx] + ' Pitch')
    plt.xlabel('dv')
    plt.ylabel('dp')

    plt.subplot(222)
    plt.scatter(dvy, dpy, s=3)
    plt.title(JOINT_NAME[idx] + ' Yaw')
    plt.xlabel('dv')
    plt.ylabel('dp')

    plt.subplot(223)
    plt.scatter(dvz, dpz, s=3)
    plt.title(JOINT_NAME[idx] + ' Roll')
    plt.xlabel('dv')
    plt.ylabel('dp')

    # plt.rcParams['figure.figsize'] = (40.0, 40.0)
    plt.savefig('/home/fan/generate-motion-from-roadmap/images/dp_dv/' + JOINT_NAME[idx] + '.jpg')

for i in range(10):
    normalize_and_plot(i)
