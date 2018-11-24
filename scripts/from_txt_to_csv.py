
# coding: utf-8

# In[9]:


import os
import re
import csv
import numpy as np


# In[11]:

def line2list(data_string):
    line = re.split(r'[,\s]+',data_string)
    if '' in line:
        line.remove('')
    else:
        pass
    for i in range(len(line)):
        line[i] = float(line[i])
    
    return line

CSVDIR = '/home/fan/generate-motion-from-roadmap/csv/'
DIR = '/home/fan/generate-motion-from-roadmap/rotation/'
joint = ["index", "上半身", "下半身", "首", "頭", "左肩", "左腕", "左ひじ","右肩", "右腕", "右ひじ"]
joints = []
for item in joint:
    if item == 'index':
	joints.append(item)
    else:
	joints.append(item+'_x')
	joints.append(item+'_y')
	joints.append(item+'_z')
files = os.listdir(DIR)
print('%d files need to be process'%(len(files)))
for file in files:
    data = []
    txtdir = os.path.join('%s%s'%(DIR, file))
    with open(txtdir, 'r') as txtfile:
        cnt = 0
        for line in txtfile:
            line = line2list(line)
            line.insert(0, cnt)
            data.append(line)
            cnt += 1
    data = np.array(data)
    csvdir = os.path.join('%s%s%s'%(CSVDIR, file.split('.')[0], '.csv'))
    with open(csvdir, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(joints)
        writer.writerows(data)
print('saved')
