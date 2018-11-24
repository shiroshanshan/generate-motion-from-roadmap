
# coding: utf-8

# In[133]:


import os
import json
import re
import math


# In[156]:


def calculate_dis(xy1,xy2):
    return math.sqrt((xy2[0] - xy1[0]) ** 2 + (xy2[1] - xy1[1]) ** 2)


# In[164]:
def is_human(_data):
    tmp = 0
    for o in range(2,len(_data),3):
        if _data[o] < 0.4:
            tmp += 1
        else:
            pass
    if tmp > 10:
        return False
    else:
        return True

def nose_neck_dis(_data):
    xy = []
    for o in range(0,len(_data),3):
        xy.append(_data[o:o+2])
    distance = calculate_dis(xy[0],xy[1])
    return distance

def all_dis(_data):
    xy = []
    xy2 = []
    for o in range(0,len(_data),3):
        xy.append(_data[o:o+2])
    distance = calculate_dis(xy[0],xy[1])
    distance += calculate_dis(xy[1],xy[2]) + calculate_dis(xy[1],xy[5]) + calculate_dis(xy[1],xy[11]) + calculate_dis(xy[1],xy[8])
    return distance

def json_replace(string,opfile):
    f = open(opfile,"w")
    f.write(string)
    f.close()

# In[189]:


def openpose_select(openpose_dir):
    json_files = os.listdir(openpose_dir)
    json_files = sorted([filename for filename in json_files if filename.endswith(".json")])
    for file_name in json_files:
        opmax = 0
        _file = os.path.join(openpose_dir, file_name)
        if not os.path.isfile(_file): raise Exception("No file found!!, {0}".format(_file))
        with open(_file,'r+') as opfile:
            data = json.load(opfile)
            oplen = len(data["people"])
            if oplen == 0:
                return "error 0"
            if oplen == 1:
                continue
            else:
                human_in = False
                for i in range(oplen):
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
                else:
                    return "error 2"
                # json.dump(data,opfile)
                json_replace(json.dumps(data),_file)

    return "success"

# In[193]:


def openpose_check(openpose_dir):
    json_files = os.listdir(openpose_dir)
    json_files = sorted([filename for filename in json_files if filename.endswith(".json")])
    detect = 0
    cache = {}
    for file_name in json_files:
        _file = os.path.join(openpose_dir, file_name)
        if not os.path.isfile(_file): raise Exception("No file found!!, {0}".format(_file))
        data = json.load(open(_file))
        #take first person
        try:
            _data = data["people"][0]["pose_keypoints_2d"]
        except:
            return "error 0"
        xy = []
        for o in range(0,len(_data),3):
            detect += 1
            #print(len(_data))
            xy.append(_data[o])
            xy.append(_data[o+1])
            xy.append(_data[o+2])

        # get frame index from openpose 12 padding
        frame_indx = re.split(r'[\_]+',file_name)[1]
        #add xy to frame
        cache[int(frame_indx)] = xy

    zero = 0
    for key,value in cache.items():
        tmp = 0
        for item in value[2::3]:
            if item == 0:
                tmp += 1
            else:
                pass
        if tmp > zero:
            zero = tmp


    less = 0
    for key,value in cache.items():
        tmp = 0
        for item in value[2::3]:
            if item < 0.3:
                tmp += 1
            else:
                pass
        if tmp > less:
            less = tmp


    if zero > 8:
        return "error 1"
    elif less > 11:
        return "error 2"
    else:
        return "pass"
