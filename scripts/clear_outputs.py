import os

os.popen('rm -rf /home/fan/generate-motion-from-roadmap/server/static/vmd/*').readlines()
os.popen('rm -rf /home/fan/generate-motion-from-roadmap/server/static/input/*').readlines()
os.popen('rm -rf /home/fan/generate-motion-from-roadmap/server/static/output/*').readlines()
os.popen('rm -rf /home/fan/generate-motion-from-roadmap/logs/*').readlines()
print('/server/vmd cleared!')
print('/server/static/input/* cleared!')
print('/server/static/output/* cleared!')
print('/logs/* cleared!')
