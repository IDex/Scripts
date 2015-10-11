import os
import sys
import re
import json
import subprocess as sp


def save():
    with open(os.path.dirname(os.path.realpath(__file__)) +
              '/watched.json', 'w') as f:
        json.dump(watched, f)

wdir = os.path.expanduser('~/new/')
arg = '.*'.join(sys.argv[1:])
watched = []
try:
    with open(os.path.dirname(os.path.realpath(__file__)) +
              '/watched.json', 'r') as f:
        watched = json.load(f)
except:
    watched = []
matches = [x for x in os.listdir(wdir)
           if re.search(arg, x, re.IGNORECASE) and x not in watched]
try:
    for f in sorted(matches):
        print(f)
        if not sp.call(['mpv', '--fs', wdir+f], stdout=sp.DEVNULL):
            watched.append(f)
            print(f)
            save()
except KeyboardInterrupt:
    SystemExit