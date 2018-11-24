import sys
sys.path.append('/home/fan/generate-motion-from-roadmap/src')
from read_roadmap import *
from flask import Flask, render_template, g, current_app, Blueprint
from werkzeug.local import LocalProxy

app = Flask(__name__)

# b = Blueprint("b", __name__)

rdp.read_roadmap(roadmap)
bone_csv_file = '/home/fan/generate-motion-from-roadmap/model.csv'
# app.register_blueprint(b)

@app.route("/")
def index():
    return render_template('betterone.html')

@app.route("/initate", methods=['GET'])
def initate():
    global last_state
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '/home/fan/generate-motion-from-roadmap/server/static/vmd/{0}.vmd'.format(timenow)
    last_state = rdp.motion_generation(init_state, vmd_file, bone_csv_file, False, False)[-1]
    return timenow

@app.route("/gene_motion", methods=['GET'])
def gene_motion():
    global last_state
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '/home/fan/generate-motion-from-roadmap/server/static/vmd/{0}.vmd'.format(timenow)
    last_state = rdp.motion_generation(last_state, vmd_file, bone_csv_file, False, False)
    return timenow

if __name__ == "__main__":
    # app = make_app()
    # app.jinja_env.auto_reload = True
    # app.run(host='0.0.0.0', debug=True, port=5000, ssl_context='adhoc')
    app.run(port=8008, debug=True)
