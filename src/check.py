
# coding: utf-8

import os
import json
import re
import math


def calculate_dis(xy1,xy2):
    return math.sqrt((xy2[0] - xy1[0]) ** 2 + (xy2[1] - xy1[1]) ** 2)

"""
discriminate human
"""
def is_human(_data):
    zero = 0
    low = 0
    for o in range(2,len(_data),3):
        if _data[o] < 0.4:
            low += 1
        elif _data[o] == 0:
            zero += 1

    return False if low > 10 or zero > 8 else True

"""
estimate size of model
"""
def all_dis(_data):
    xy = []
    xy2 = []
    for o in range(0,len(_data),3):
        xy.append(_data[o:o+2])
    distance = calculate_dis(xy[0],xy[1]) + calculate_dis(xy[1],xy[2]) + calculate_dis(xy[1],xy[5]) +\
     calculate_dis(xy[1],xy[11]) + calculate_dis(xy[1],xy[8])

    return distance

"""
replace json files
"""
def json_replace(string,opfile):
    f = open(opfile,"w")
    f.write(string)
    f.close()

"""
select function will choose the largest model
"""
def openpose_select(openpose_dir):
    json_files = os.listdir(openpose_dir)
    json_files = sorted([filename for filename in json_files if filename.endswith(".json")])

    for file_name in json_files:
        _file = os.path.join(openpose_dir, file_name)
        if not os.path.isfile(_file):
            raise Exception("No file found!!, {0}".format(_file))
        with open(_file, 'r+') as opfile:
            data = json.load(opfile)

        if len(data["people"]) == 0:
            return "error 0"
        elif len(data["people"]) != 1:
            opmax = 0
            human_in = False
            for i in range(len(data["people"])):
                _data = data["people"][i]["pose_keypoints_2d"]
                distance = all_dis(_data)
                human = is_human(_data)
                if distance > opmax and human:
                    opmax = distance
                    opidx = i
                    human_in = True
            if human_in == True:
                data["people"][0]["pose_keypoints_2d"] = data["people"][opidx]["pose_keypoints_2d"]
                data["people"] = data["people"][0:1]
                json_replace(json.dumps(data),_file)
                return "success"
            else:
                return "error 1"
