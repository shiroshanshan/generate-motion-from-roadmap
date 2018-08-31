# -*- coding: utf-8 -*-

import os
from PyQt5.QtGui import QQuaternion, QVector4D, QVector3D, QMatrix4x4
from VmdWriter import VmdBoneFrame, VmdInfoIk, VmdShowIkFrame, VmdWriter
import numpy as np
import csv

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

def euler2qq(state, frame=0):

    # 上半身
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8f\xe3\x94\xbc\x90\x67' # '上半身'
    x, y, z = tuple(state[0])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["上半身"].append(bf)

    # 下半身
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\xba\x94\xbc\x90\x67' # '下半身'
    x, y, z = tuple(state[1])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["下半身"].append(bf)

    # 首
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8e\xf1' # '首'
    x, y, z = tuple(state[2])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["首"].append(bf)

    # 頭
    bf = VmdBoneFrame(frame)
    bf.name = b'\x93\xaa' # '頭'
    x, y, z = tuple(state[3])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["頭"].append(bf)

    # 左肩
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x8C\xA8' # '左肩'
    x, y, z = tuple(state[4])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["左肩"].append(bf)

    # 左腕
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x98\x72' # '左腕'
    x, y, z = tuple(state[5])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["左腕"].append(bf)
    rotation_euler = list(bf.rotation.getEulerAngles())

    # 左ひじ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x8d\xb6\x82\xd0\x82\xb6' # '左ひじ'
    x, y, z = tuple(state[6])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["左ひじ"].append(bf)

    # 右肩
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x8C\xA8' # '右肩'
    x, y, z = tuple(state[7])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["右肩"].append(bf)

    # 右腕
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x98\x72' # '右腕'
    x, y, z = tuple(state[8])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["右腕"].append(bf)

    # 右ひじ
    bf = VmdBoneFrame(frame)
    bf.name = b'\x89\x45\x82\xd0\x82\xb6' # '右ひじ'
    x, y, z = tuple(state[9])
    bf.rotation = QQuaternion.fromEulerAngles(QVector3D(x, y, z))
    bone_frame_dic["右ひじ"].append(bf)

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


def generate_vmd_file(rotations, vmd_file, bone_csv_file):
    writer = VmdWriter()

    for frame, rotation in enumerate(rotations):
        euler2qq(rotation, frame)

    calc_center()

    bone_frame_dic["左足ＩＫ"] = []
    bone_frame_dic["右足ＩＫ"] = []

    is_groove = set_groove(bone_csv_file)

    bone_frames = []
    for k,v in bone_frame_dic.items():
        for bf in v:
            bone_frames.append(bf)

    writer.write_vmd_file(vmd_file, bone_frames, None)

def calc_center():
    for n in range(len(bone_frame_dic["首"])):
            bone_frame_dic["センター"][n].position.setX(float(0.0))
            bone_frame_dic["センター"][n].position.setY(float(0.0))
            bone_frame_dic["センター"][n].position.setZ(float(0.0))


def set_groove(bone_csv_file):
    is_groove = False
    with open(bone_csv_file, "r") as bf:
        reader = csv.reader(bf)
        for row in reader:
            if row[1] == "グルーブ":
                is_groove = True
                break
    if is_groove:
        for n in range(len(bone_frame_dic["センター"])):
            bone_frame_dic["グルーブ"][n].position = QVector3D(0, 0, 0)

    return is_groove
