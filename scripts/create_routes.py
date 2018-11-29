import json

with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
    roadmap = f.read()
    roadmap = eval(roadmap)
routes_dic = {}
for i in raneg(len(roadmap)):
    routes_dic[i] = []
roadmap_dic = json.dumps(roadmap_dic)
with open('/home/fan/generate-motion-from-roadmap/saved/routes.json', 'w') as f:
    f.write(roadmap_dic)
