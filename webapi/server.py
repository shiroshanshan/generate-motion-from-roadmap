
# coding: utf-8

# In[12]:


import pandas as pd
import datetime
from flask import Flask, render_template, request
import os
import json


# In[14]:


# In[15]:


app = Flask(__name__)


# In[16]:


@app.route("/")
def index():
    return render_template('webapi.html')


# In[17]:


@app.route('/openface', methods=['POST'])
def openface():
    result = {}
    Imgfile = request.files['file']
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    Imgfile.save('/home/fan/generate-motion-from-roadmap/webapi/static/input/{0}.png'.format(timenow))
    print(Imgfile)
    os.popen('~/OpenFace/build/bin/FaceLandmarkImg -f /home/fan/generate-motion-from-roadmap/webapi/static/input/{0}.png\
              -out_dir /home/fan/generate-motion-from-roadmap/webapi/static/output/{1}'.format(timenow, timenow)).readlines()
    try:
        df = pd.read_csv('/home/fan/generate-motion-from-roadmap/webapi/static/output/{0}/{1}.csv'.format(timenow, timenow), sep=',')
    except:
        return 'error'
    value = df[[' gaze_0_x', ' gaze_0_y', ' gaze_0_z', ' gaze_1_x', ' gaze_1_y', ' gaze_1_z']].values
    result['left_eye'] = str(value[0][:3])
    result['right_eye'] = str(value[0][3:])
    result['timenow'] = timenow
    return json.dumps(result)


# In[19]:


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
#     app.run(host='0.0.0.0', debug=True, port=5000, ssl_context='adhoc')
    app.run(debug=True, port=5001)
