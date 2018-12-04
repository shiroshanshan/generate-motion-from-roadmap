import json

with open('/home/fan/generate-motion-from-roadmap/roadmap/roadmap.json', 'r') as f:
    roadmap = f.read()
    roadmap = eval(roadmap)
routes_dic = {}
for i in range(len(roadmap)):
    routes_dic[i] = []
print('create routes_dic: done, {0} states in roadmap'.format(len(routes_dic)))
routes_dic = json.dumps(routes_dic)
with open('/home/fan/generate-motion-from-roadmap/roadmap/saved/routes.json', 'w') as f:
    f.write(routes_dic)
