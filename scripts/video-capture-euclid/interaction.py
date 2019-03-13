import rospy
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
from cv_bridge import CvBridge
import cv2
import time
import os

bridge = CvBridge()
seq = 0
cv_image = None
timenow = str(time.time()).split('.')[0]
os.mkdir('/home/euclid/scripts/images/%s'%(timenow))
index = 0

def camera_callback(data):
    try:
        global cv_image
        cv_image = bridge.imgmsg_to_cv2(data,"bgr8")
	#cv_image = cv2.resize(cv_image,(640,480),
	size = cv_image.shape
	print(size)
	rospy.loginfo('image transferring')
	global index
	filename = str(index).zfill(6)
	index += 1
	cv2.imwrite('/home/euclid/scripts/images/%s/%s.jpeg'%(timenow,filename),cv_image)
    except:
        print('error')

def info_callback(data):
    global stamp
    stamp = data.header.stamp.secs
    global seq 
    seq = data.header.seq

def listener():
    rospy.init_node('camera_listner', anonymous=True)
    rospy.Subscriber('/camera/fisheye/image_raw',Image,camera_callback)
    rospy.Subscriber('/camera/ir/camera_info',CameraInfo,info_callback)    
    
    rospy.spin()
#    while not rospy.is_shutdown():
#	global index
#	filename = str(index).zfill(6)
#	index += 1
#       cv2.imwrite('/home/euclid/scripts/images/%s/%s.jpeg'%(timenow,filename),cv_image)

if __name__ == '__main__':
    listener()
