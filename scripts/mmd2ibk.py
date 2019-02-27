# -*- coding: utf-8 -*-

from PyQt5.QtGui import QQuaternion, QVector3D
import numpy as np
import pandas as pd
import re
import math
import argparse

def deorder(rotation):
    return np.array([rotation[0], rotation[2], rotation[1]])

def miku_to_ibuki(rotations):
    """
    input data format: 10x3 matrix
    output data format: 10x3 matrix
    """
    ibuki_rotations = []
    # deinitial
    # 上半身
    ibuki_rotations.append(deorder(rotations[0]))

    # 下半身
    # 省略

    # 首
    ibuki_rotations.append(deorder(rotations[2]))

    # 頭
    # 省略
#     ibuki_rotations.append(deorder(rotations[3]))

    # 左肩
    left_shoulder_rotation = QQuaternion.fromEulerAngles(*rotations[4])
    initial_orientation = QQuaternion.fromDirection(QVector3D(2, -0.8, 0), QVector3D(0.5, -0.5, -1))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(1, 0, 0), QVector3D(0, 0, -1))
    left_shoulder_rotation = left_shoulder_rotation * ibuki_initial.inverted()
    rotation_euler = left_shoulder_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    # 左腕
    left_arm_rotation = QQuaternion.fromEulerAngles(*rotations[5])
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(1, 0, 0))
    left_arm_rotation = left_arm_rotation * initial_orientation * ibuki_initial.inverted()
    rotation_euler = left_arm_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    # 左ひじ
    left_elbow_rotation = QQuaternion.fromEulerAngles(*rotations[6])
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(1, 0, 0))
    left_elbow_rotation = left_elbow_rotation * initial_orientation * ibuki_initial.inverted()
    rotation_euler = left_elbow_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    # 右肩
    right_shoulder_rotation = QQuaternion.fromEulerAngles(*rotations[7])
    initial_orientation = QQuaternion.fromDirection(QVector3D(-2, -0.8, 0), QVector3D(0.5, 0.5, 1))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(-1, 0, 0), QVector3D(0, 0, 1))
    right_shoulder_rotation = right_shoulder_rotation * ibuki_initial.inverted()
    rotation_euler = right_shoulder_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    # 右腕
    right_arm_rotation = QQuaternion.fromEulerAngles(*rotations[8])
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(1, 0, 0))
    right_arm_rotation = right_arm_rotation * initial_orientation * ibuki_initial.inverted()
    rotation_euler = right_arm_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    # 右ひじ
    right_elbow_rotation = QQuaternion.fromEulerAngles(*rotations[9])
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    ibuki_initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(1, 0, 0))
    right_elbow_rotation = right_elbow_rotation * initial_orientation * ibuki_initial.inverted()
    rotation_euler = right_elbow_rotation.getEulerAngles()
    ibuki_rotations.append(deorder(rotation_euler))

    with open('/home/fan/test.txt', 'a+') as f:
        f.write(str(ibuki_rotations))

    return ibuki_rotations

def save_csv(rotations):

    c = [u'time', u'_SHOULDER_RIGHT_PITCH', u'_SHOULDER_LEFT_PITCH',
       u'_NECK_UNIQUE_ROLL', u'_NECK_UNIQUE_YAW', u'_NECK_UNIQUE_PITCH',
       u'_ARML_UPPER_ROLL', u'_ARML_UPPER_YAW', u'_ARML_MIDDLE_PITCH',
       u'_ARML_MIDDLE_YAW', u'_ARML_EDGE_ROLL', u'_ARMR_UPPER_ROLL',
       u'_ARMR_UPPER_YAW', u'_ARMR_MIDDLE_PITCH', u'_ARMR_MIDDLE_YAW',
       u'_ARMR_EDGE_ROLL', u'_HANDL_THUMB_PITCH', u'_HANDL_INDEX_PITCH',
       u'_HANDL_MIDDLE_PITCH', u'_HANDL_RING_PITCH', u'_HANDL_LITTLE_PITCH',
       u'_HANDR_THUMB_PITCH', u'_HANDR_INDEX_PITCH', u'_HANDR_MIDDLE_PITCH',
       u'_HANDR_RING_PITCH', u'_HANDR_LITTLE_PITCH', u'_HEADL_OPHRYON_VERT',
       u'_HEADL_EYELIDU_VERT', u'_HEADL_EYELIDD_VERT', u'_HEADL_FACER_TENSE',
       u'_HEADL_FACEL_TENSE', u'_HEADC_EYEBROWR_VERT', u'_HEADC_EYEBROWL_VERT',
       u'_HEADC_EYER_YAW', u'_HEADC_EYEL_YAW', u'_HEADC_EYES_PITCH',
       u'_HEADR_LIPUP_REACH', u'_HEADR_LIPDOWN_REACH', u'_HEADR_MOUTHR_OPEN',
       u'_HEADR_MOUTHL_OPEN', u'_HEADR_CHIN_ROLL', u'_HIP_UNIQUE_PITCH',
       u'_HIP_UNIQUE_ROLL', u'_HIP_UNIQUE_YAW', u'_WHEEL_UNIQUE_VERT',
       u'_WHEEL_UNIQUE_STEEL', u'_WHEEL_UNIQUE_SPEED', u'_WHEEL_UNIQUE_BREAK',
       u'_ADD', u'_ADD', u'_ADD']

    mapping = [[41, 42, 43],
               [3, 4, 5],
               [2, 0, 0],
               [0, 6, 7],
               [8, 0, 9],
               [1, 0, 0],
               [0, 11, 12],
               [13, 0, 14]]

    df = pd.DataFrame(np.zeros((len(rotations), len(c))), columns=c)
    for i in range(len(rotations)):
        df.loc[i,'time'] = i/10.
        for j in range(len(rotations[i])):
            for k in range(len(rotations[i][j])):
                if mapping[j][k]:
                    df.loc[i,c[mapping[j][k]]] = rotations[i][j][k]/180.*math.pi
    df.to_csv(output)

def line2list(string):
    line = re.split(r'[,\s]+',string)
    if '' in line:
        line.remove('')
    line = [float(l) for l in line]

    return line

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-i', '--input', dest='input', type=str,
                        help='mmd file path')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='ibuki file path')
    args = parser.parse_args()
    input = args.input
    output = args.output

    with open(input, 'r') as txtfile:
        miku_rotations = [np.array(line2list(line)).reshape(10,3) for line in txtfile]

    ibuki_rotations = [miku_to_ibuki(frame) for frame in miku_rotations]
    save_csv(ibuki_rotations)
