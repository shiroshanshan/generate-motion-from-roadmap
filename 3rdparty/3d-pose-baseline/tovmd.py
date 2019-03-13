#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pos2vmd.py - convert joint position data to VMD

from __future__ import print_function

def usage(prog):
    print('usage: ' + prog + ' POSITION_FILE VMD_FILE')
    sys.exit()

import os
import re
from PyQt5.QtGui import QQuaternion, QVector4D, QVector3D, QMatrix4x4
from VmdWriter import VmdBoneFrame, VmdInfoIk, VmdShowIkFrame, VmdWriter
import argparse
import datetime
import numpy as np
import csv
from decimal import Decimal
from matplotlib import pyplot as plt

bone_frame_dic = {
    "上半身":[],
    "下半身":[],
    "首":[],
    "頭":[],
    "左肩":[],
    "左腕":[],
    "左ひじ":[],
    "右肩":[],
    "右腕":[],
    "右ひじ":[],
    "左足":[],
    "左ひざ":[],
    "右足":[],
    "右ひざ":[],
    "センター":[],
    "グルーブ":[],
    "左足ＩＫ":[],
    "右足ＩＫ":[]
}
euler_rotation = []

def positions_to_frames(pos, frame=0, xangle=0):
    decrease_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * 0.5, 0, 0))
    increase_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * 1.5, 0, 0))
    normal_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle, 0, 0))
    neck_correctqq = QQuaternion.fromEulerAngles(QVector3D(xangle * (-0.1), 0, 0))

    frame_rotation = []

    """convert positions to bone frames"""
    # 上半身
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8f\xe3\x94\xbc\x90\x67' # '上半身'
    direction = pos[8] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[14] - pos[11])).normalized()
    upper_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(0, 0, 1))
    upper_body_rotation = upper_body_orientation * initial.inverted()

    # 補正をかけて回転する
    if upper_body_rotation.toEulerAngles().y() < 30 and upper_body_rotation.toEulerAngles().y() > -30:
        # 前向きは増量補正
        upper_correctqq = increase_correctqq
    elif upper_body_rotation.toEulerAngles().y() < -120 or upper_body_rotation.toEulerAngles().y() > 120:
        # 後ろ向きは通常補正
        upper_correctqq = normal_correctqq
    else:
        # 横向きは減少補正
        upper_correctqq = decrease_correctqq

    upper_body_rotation = upper_body_rotation * upper_correctqq
    bf.rotation = upper_body_rotation
    upper_body_euler = list(upper_body_rotation.getEulerAngles())
    frame_rotation.append(upper_body_euler)
    # print(upper_body_rotation)
    # print(upper_body_euler)
    # tmpx,tmpy,tmpz = upper_body_euler
    # print(QQuaternion.fromEulerAngles(QVector3D(tmpx,tmpy,tmpz)))

    bone_frame_dic["上半身"].append(bf)

    # 下半身
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\xba\x94\xbc\x90\x67' # '下半身'
    direction = pos[0] - pos[7]
    up = QVector3D.crossProduct(direction, (pos[4] - pos[1]))
    lower_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(0, 0, 1))
    lower_body_rotation = lower_body_orientation * initial.inverted()
    lower_body_rotation = 0.3 * lower_body_rotation

    # 補正をかけて回転する
    if lower_body_rotation.toEulerAngles().y() < 30 and lower_body_rotation.toEulerAngles().y() > -30:
        # 前向きは通常補正
        lower_correctqq = QQuaternion.fromEulerAngles(QVector3D(0, 0, 0))
    elif lower_body_rotation.toEulerAngles().y() < -120 or lower_body_rotation.toEulerAngles().y() > 120:
        # 後ろ向きは通常補正
        lower_correctqq = normal_correctqq
    else:
        # 横向きは減少補正
        lower_correctqq = decrease_correctqq

    lower_body_rotation = lower_body_rotation * lower_correctqq
    bf.rotation = lower_body_rotation
    bone_frame_dic["下半身"].append(bf)

    # 首
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8e\xf1' # '首'
    direction = pos[9] - pos[8]
    up = QVector3D.crossProduct((pos[14] - pos[11]), direction).normalized()
    neck_orientation = QQuaternion.fromDirection(up, direction)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, 0, -1), QVector3D(0, -1, 0))
    rotation = neck_correctqq * neck_orientation * initial_orientation.inverted()
    bf.rotation = upper_body_orientation.inverted() * rotation
    neck_rotation = bf.rotation
    bone_frame_dic["首"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 頭
    bf = VmdBoneFrame(frame)
    bf.name = b'\x93\xaa' # '頭'
    direction = pos[10] - pos[9]
    up = QVector3D.crossProduct((pos[9] - pos[8]), (pos[10] - pos[9]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(1, 0, 0))
    rotation = normal_correctqq * orientation * initial_orientation.inverted()
    bf.rotation = neck_rotation.inverted() * upper_body_rotation.inverted() * rotation
    bone_frame_dic["頭"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左肩
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x8C\xA8' # '左肩'
    direction = pos[11] - pos[8]
    up = QVector3D.crossProduct((pos[11] - pos[8]), (pos[14] - pos[11]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(2, -0.8, 0), QVector3D(0.5, -0.5, -1))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    # 左肩ポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * bf.rotation = rotation なので、
    left_shoulder_rotation = upper_body_rotation.inverted() * rotation # 後で使うので保存しておく
    bf.rotation = left_shoulder_rotation
    bone_frame_dic["左肩"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左腕
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x98\x72' # '左腕'
    direction = pos[12] - pos[11]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    # 左腕ポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * left_shoulder_rotation * bf.rotation = rotation なので、
    bf.rotation = left_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    left_arm_rotation = bf.rotation # 後で使うので保存しておく
    bone_frame_dic["左腕"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左ひじ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x82\xd0\x82\xb6' # '左ひじ'
    direction = pos[13] - pos[12]
    up = QVector3D.crossProduct((pos[12] - pos[11]), (pos[13] - pos[12]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    # 左ひじポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * left_shoulder_rotation * left_arm_rotation * bf.rotation = rotation なので、
    bf.rotation = left_arm_rotation.inverted() * left_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    # bf.rotation = (upper_body_rotation * left_arm_rotation).inverted() * rotation # 別の表現
    bone_frame_dic["左ひじ"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右肩
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x8C\xA8' # '右肩'
    direction = pos[14] - pos[8]
    up = QVector3D.crossProduct((pos[14] - pos[8]), (pos[11] - pos[14]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-2, -0.8, 0), QVector3D(0.5, 0.5, 1))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    # 右肩ポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * bf.rotation = rotation なので、
    right_shoulder_rotation = upper_body_rotation.inverted() * rotation # 後で使うので保存しておく
    bf.rotation = right_shoulder_rotation
    bone_frame_dic["右肩"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右腕
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x98\x72' # '右腕'
    direction = pos[15] - pos[14]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    bf.rotation = right_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    right_arm_rotation = bf.rotation
    bone_frame_dic["右腕"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 右ひじ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x82\xd0\x82\xb6' # '右ひじ'
    direction = pos[16] - pos[15]
    up = QVector3D.crossProduct((pos[15] - pos[14]), (pos[16] - pos[15]))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1.73, -1, 0), QVector3D(1, -1.73, 0))
    rotation = upper_correctqq * orientation * initial_orientation.inverted()
    bf.rotation = right_arm_rotation.inverted() * right_shoulder_rotation.inverted() * upper_body_rotation.inverted() * rotation
    bone_frame_dic["右ひじ"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())
    frame_rotation.append(rotation_euler)

    # 左足
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x91\xab' # '左足'
    bone_frame_dic["左足"].append(bf)

    # 左ひざ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x82\xd0\x82\xb4' # '左ひざ'
    bone_frame_dic["左ひざ"].append(bf)

    # 右足
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x91\xab' # '右足'
    bone_frame_dic["右足"].append(bf)

    # 右ひざ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x82\xd0\x82\xb4' # '右ひざ'
    bone_frame_dic["右ひざ"].append(bf)

    # センター(箱だけ作る)
    bf = VmdBoneFrame(frame)
    bf.name = b'\x83\x5A\x83\x93\x83\x5E\x81\x5B' # 'センター'
    bone_frame_dic["センター"].append(bf)

    # グルーブ(箱だけ作る)
    bf = VmdBoneFrame(frame)
    bf.name = b'\x83\x4F\x83\x8B\x81\x5B\x83\x75' # 'グルーブ'
    bone_frame_dic["グルーブ"].append(bf)

    # 左足ＩＫ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x91\xab\x82\x68\x82\x6a' # '左足ＩＫ'
    bone_frame_dic["左足ＩＫ"].append(bf)

    # 右足ＩＫ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x91\xab\x82\x68\x82\x6a' # '右足ＩＫ'
    bone_frame_dic["右足ＩＫ"].append(bf)

    euler_rotation.append(frame_rotation)

#複数フレームの読み込み
def read_positions_multi(position_file):
    """Read joint position data"""
    f = open(position_file, "r")

    positions = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.rstrip('\n')

        # 一旦カンマで複数行に分解
        inposition = []
        for inline in re.split(",\s*", line):
            if inline:
                # 1フレーム分に分解したら、空白で分解
                a = re.split(' ', inline)
                # print(a)
                # 元データはz軸が垂直上向き。MMDに合わせるためにyとzを入れ替える。
                q = QVector3D(float(a[1]), float(a[3]), float(a[2])) # a[0]: index
                inposition.append(q) # a[0]: index

        positions.append(inposition)
    f.close()
    return positions

def convert_position(pose_3d):
    positions = []
    for pose in pose_3d:
        for j in range(pose.shape[1]):
            q = QVector3D(pose[0, j], pose[2, j], pose[1, j])
            positions.append(q)
    return positions

def write_rotation_file(rotationfile,rotationlist):
    for frame in rotationlist:
        for joint in frame:
            rotationfile.write(str(joint[0]) + " " + str(joint[1]) + " " + str(joint[2]))
            if joint != frame[len(frame)-1]:
                rotationfile.write(',')
            else:
                pass
        rotationfile.write('\n')


# 関節位置情報のリストからVMDを生成します
def position_list_to_vmd_multi(positions_multi, vmd_file, bone_csv_file, xangle, mdecimation, idecimation, ddecimation, alignment):
    writer = VmdWriter()

    rotationf = open('/home/fan/Documents/3dpose/output/rotation.txt', 'w')

    for frame, positions in enumerate(positions_multi):
        positions_to_frames(positions, frame, xangle)

    write_rotation_file(rotationf,euler_rotation)
    rotationf.close()
    calc_center()

    bone_frame_dic["左足ＩＫ"] = []
    bone_frame_dic["右足ＩＫ"] = []

    is_groove = set_groove(bone_csv_file)

    if mdecimation > 0 or idecimation > 0 or ddecimation > 0:

        base_dir = os.path.dirname(vmd_file)

        if alignment == True:

            decimate_bone_rotation_frames_array(["上半身"], ddecimation)
            decimate_bone_rotation_frames_array(["首", "頭"], ddecimation)
            decimate_bone_rotation_frames_array(["左ひじ", "左腕", "左肩"], ddecimation)
            decimate_bone_rotation_frames_array(["右ひじ", "右腕", "右肩"], ddecimation)
        else:

            decimate_bone_rotation_frames_array(["上半身"], ddecimation)
            decimate_bone_rotation_frames_array(["首"], ddecimation)
            decimate_bone_rotation_frames_array(["頭"], ddecimation)
            decimate_bone_rotation_frames_array(["左ひじ"], ddecimation)
            decimate_bone_rotation_frames_array(["左腕"], ddecimation)
            decimate_bone_rotation_frames_array(["左肩"], ddecimation)
            decimate_bone_rotation_frames_array(["右ひじ"], ddecimation)
            decimate_bone_rotation_frames_array(["右腕"], ddecimation)
            decimate_bone_rotation_frames_array(["右肩"], ddecimation)

    # ディクショナリ型の疑似二次元配列から、一次元配列に変換
    bone_frames = []
    for k,v in bone_frame_dic.items():
        for bf in v:
            bone_frames.append(bf)

    writer.write_vmd_file(vmd_file, bone_frames, None)

# 回転ボーンを揃えて登録する
def decimate_bone_rotation_frames_array(bone_name_array, ddecimation):

    # フィットさせたフレーム情報
    fit_frames = []

    # 同じフレーム内で回す
    for n in range(len(bone_frame_dic[bone_name_array[0]])):

        if n == 0:
            # 最初は必ず登録
            fit_frames.append(n)
            continue

        for bone_name in bone_name_array:
            if is_regist_rotation_frame(n, bone_name, fit_frames, ddecimation):
                # 登録可能な場合、登録
                fit_frames.append(n)
                break

    # 登録する場合、全ボーンの同じフレームで登録する
    for bone_name in bone_name_array:
        newbfs = []
        for n in fit_frames:
            newbfs.append(bone_frame_dic[bone_name][n])

        # 新しいフレームリストを登録する
        bone_frame_dic[bone_name] = newbfs



# 回転系のフレームを登録するか否か判定する
def is_regist_rotation_frame(n, bone_name, fit_frames, ddecimation):
    # # 二つ前の回転情報

    # 一つ前の回転情報
    prev1_rotation = bone_frame_dic[bone_name][fit_frames[-1]].rotation

    # 今回判定対象の回転情報
    now_rotation = bone_frame_dic[bone_name][n].rotation

    # # 2つ前から前回までの回転の差

    # 前回から今回までの回転の差
    diff_now_rotation = QQuaternion.rotationTo(prev1_rotation.normalized().vector(), now_rotation.normalized().vector())

    # 一定以上回転していれば登録対象
    if abs(diff_now_rotation.toEulerAngles().x()) >= ddecimation or abs(diff_now_rotation.toEulerAngles().y()) >= ddecimation or abs(diff_now_rotation.toEulerAngles().z()) >= ddecimation :
        if bone_name == "上半身" or bone_name == "下半身":
            # 細かい動きをするボーンは、1F隣でもOKとする
            return True
        elif fit_frames[-1] + 1 < n:
            return True
    elif diff_now_rotation.toEulerAngles().y() < 0 and ( now_rotation.toEulerAngles().y() <= -90 or now_rotation.toEulerAngles().y() >= 90 ):
        # 角度が小さくても後ろ向きなら登録対象
        if bone_name == "上半身" or bone_name == "下半身":
            return True

    return False


# 三辺から足の角度を求める
def calc_leg_angle(a, b, c):

    cos = ( pow(a.length(), 2) + pow(b.length(), 2) - pow(c.length(), 2) ) / ( 2 * a.length() * b.length() )

    radian = np.arccos(cos)

    angle = np.rad2deg(radian)

    return angle



# センターの計算
def calc_center():

    for n in range(len(bone_frame_dic["首"])):
            bone_frame_dic["センター"][n].position.setX(float(0.0))
            bone_frame_dic["センター"][n].position.setY(float(0.0))
            bone_frame_dic["センター"][n].position.setZ(float(0.0))


# センターY軸をグルーブY軸に移管
def set_groove(bone_csv_file):

    # グルーブボーンがあるか
    is_groove = False
    # ボーンファイルを開く
    with open(bone_csv_file, "r") as bf:
        reader = csv.reader(bf)

        for row in reader:
            if row[1] == "グルーブ":
                is_groove = True
                break

    if is_groove:

        for n in range(len(bone_frame_dic["センター"])):

            # グルーブがある場合、Y軸をグルーブに設定
            bone_frame_dic["グルーブ"][n].position = QVector3D(0, 0, 0)

    return is_groove


def position_multi_file_to_vmd(position_file, vmd_file, bone_csv_file, xangle, mdecimation, idecimation, ddecimation, alignment):
    positions_multi = read_positions_multi(position_file)
    position_list_to_vmd_multi(positions_multi, vmd_file, bone_csv_file, xangle, mdecimation, idecimation, ddecimation, alignment)

if __name__ == '__main__':
    import sys
    if (len(sys.argv) < 2):
        usage(sys.argv[0])

    parser = argparse.ArgumentParser(description='3d-pose-baseline to vmd')
    parser.add_argument('-t', '--target', dest='target', type=str,
                        help='target directory')
    parser.add_argument('-b', '--bone', dest='bone', type=str,
                        help='target model bone csv')
    parser.add_argument('-x', '--x-angle', dest='xangle', type=int,
                        default=0,
                        help='global x angle correction')
    parser.add_argument('-d', '--born-decimation-angle', dest='ddecimation', type=int,
                        default=0,
                        help='born frame decimation angle')
    parser.add_argument('-m', '--center-move-born-decimation', dest='mdecimation', type=float,
                        default=0,
                        help='born frame center decimation move')
    parser.add_argument('-i', '--ik-move-born-decimation', dest='idecimation', type=float,
                        default=0,
                        help='born frame ik decimation move')
    parser.add_argument('-a', '--decimation-alignment', dest='alignment', type=int,
                        default=1,
                        help='born frame decimation alignment')
    parser.add_argument('-n', '--dir_name', dest='name', type=str,
                        help='destinate directory')
    args = parser.parse_args()

    base_dir = args.target

    is_alignment = True if args.alignment == 1 else False

    position_file = base_dir + "/pos.txt"
    suffix = ""
    if args.mdecimation == 0 and args.idecimation == 0 and args.ddecimation == 0:
        suffix = "_間引きなし"
    elif is_alignment == False:
        suffix = "_揃えなし"

    vmd_file = "{0}/{1}.vmd".format("/home/fan/Documents/static/vmd", args.name)
    print("{0}".format(vmd_file))
    position_multi_file_to_vmd(position_file, vmd_file, args.bone, args.xangle, args.mdecimation, args.idecimation, args.ddecimation, is_alignment)
