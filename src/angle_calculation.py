import os
import re
from PyQt5.QtGui import QQuaternion, QVector3D
import numpy as np

def read_files(PATH, files):
    with open(PATH + files, 'r') as f:
        positions = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.rstrip('\n')

            inposition = []
            for inline in re.split(",\s*", line):
                if inline:
                    a = re.split(' ', inline)

                    q = QVector3D(float(a[1]), float(a[3]), float(a[2]))
                    inposition.append(q)

            positions.append(inposition)
    return positions

def write_rotation_file(rotationfile,rotationlist):
    for frame in rotationlist:
        for joint in frame:
            rotationfile.write(str(joint[0]) + " " + str(joint[1]) + " " + str(joint[2]))
            if joint != frame[len(frame)-1]:
                rotationfile.write(',')
            else:
                rotationfile.write('\n')

def positions_to_rotation(pos, frame=0, xangle=0):
    decrease_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * 0.5, 0, 0))
    increase_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * 1.5, 0, 0))
    normal_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle, 0, 0))
    neck_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * (-0.1), 0, 0))

    frame_rotation = []

    # 上半身
    direction = pos[8] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[14] - pos[11])).normalized()
    upper_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(0, 0, 1))
    upper_body_rotation = upper_body_orientation * initial.inverted()

    if upper_body_rotation.toEulerAngles().y() < 30 and upper_body_rotation.toEulerAngles().y() > -30:
        upper_correctqq = increase_correctqq
    elif upper_body_rotation.toEulerAngles().y() < -120 or upper_body_rotation.toEulerAngles().y() > 120:
        upper_correctqq = normal_correctqq
    else:
        upper_correctqq = decrease_correctqq

    upper_body_rotation = upper_body_rotation * upper_correctqq
    upper_body_euler = list(upper_body_rotation.getEulerAngles())
    frame_rotation.append(upper_body_euler)

    # 下半身
    direction = pos[0] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[4] - pos[1]))
    lower_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(0, 0, 1))
    lower_body_rotation = lower_body_orientation * initial.inverted()
    lower_body_rotation = 0.3 * lower_body_rotation

    if lower_body_rotation.toEulerAngles().y() < 30 and lower_body_rotation.toEulerAngles().y() > -30:
        lower_correctqq = QQuaternion.fromEulerAngles(QVector3D(0, 0, 0))
    elif lower_body_rotation.toEulerAngles().y() < -120 or lower_body_rotation.toEulerAngles().y() > 120:
        lower_correctqq = normal_correctqq
    else:
        lower_correctqq = decrease_correctqq

    lower_body_rotation_scaled = lower_body_rotation * lower_correctqq
    lower_body_euler_scaled = list(lower_body_rotation.getEulerAngles())
    frame_rotation.append(lower_body_euler_scaled)

    # 首
    direction = pos[9] - pos[8]
    up = QVector3D.crossProduct((pos[14] - pos[11]), direction).normalized()
    neck_orientation = QQuaternion.fromDirection(up, direction)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, 0, -1), QVector3D(0, -1, 0))
    rotation = neck_correctqq * neck_orientation * initial_orientation.inverted()
    neck_rotation = upper_body_orientation.inverted() * rotation
    rotation_euler = list(neck_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 頭
    direction = pos[10] - pos[9]
    up = QVector3D.crossProduct((pos[9] - pos[8]), (pos[10] - pos[9]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(1, 0, 0))
    rotation = normal_correctqq * orientation * initial_orientation.inverted()
    head_rotation = neck_rotation.inverted() * upper_body_rotation.inverted() * rotation
    rotation_euler = list(head_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左肩
    direction = pos[11] - pos[8]
    up = QVector3D.crossProduct((pos[11] - pos[8]), (pos[14] - pos[11]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(2, -0.8, 0), QVector3D(0.5, -0.5, -1))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    left_shoulder_rotation = upper_body_rotation.inverted() * rotation # 後で使うので保存しておく
    rotation_euler = list(left_shoulder_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左腕
    direction = pos[12] - pos[11]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    left_arm_rotation = left_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    rotation_euler = list(left_arm_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左ひじ
    direction = pos[13] - pos[12]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    left_elbow_rotation = left_arm_rotation.inverted() * left_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    rotation_euler = list(left_elbow_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右肩
    direction = pos[14] - pos[8]
    up = QVector3D.crossProduct((pos[14] - pos[8]), (pos[11] - pos[14]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-2, -0.8, 0), QVector3D(0.5, 0.5, 1))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    right_shoulder_rotation = upper_body_rotation.inverted() * rotation # 後で使うので保存しておく
    rotation_euler = list(right_shoulder_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右腕
    direction = pos[15] - pos[14]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    right_arm_rotation = right_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    rotation_euler = list(right_arm_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右ひじ
    direction = pos[16] - pos[15]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    right_elbow_rotation = right_arm_rotation.inverted() * right_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    rotation_euler = list(right_elbow_rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    return frame_rotation
