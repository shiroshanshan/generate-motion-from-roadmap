import os
import cv2
import numpy as np

path = '/home/euclid/scripts/images/'
folderlist = os.listdir(path)
fps = 30

for item in folderlist:
    if '.' in item:
	continue
    else:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        videoWriter = cv2.VideoWriter("/home/euclid/scripts/video/%s.avi"%(item),fourcc,fps,(640,480))
        filelist = os.listdir(path+item)
	filelist.sort()
        for onefile in filelist:
            img = cv2.imread(path+item+'/'+onefile)
            try:
                videoWriter.write(img)
	    except:
	        print('error') 
        videoWriter.release()

