# if execute within one hour, move first pdf into failed folder

import time
import shutil
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
runtimefile = os.path.join(dir_path, 'run.time')
configfile = os.path.join(dir_path, 'run.config')

time_seconds = int(round(time.time()))
last_time = 0
if not os.path.exists(runtimefile):
    with open(runtimefile, 'w'): pass
with open(runtimefile, 'r+') as f:
	t = f.read().replace('\n', '')
	if len(t) > 0:
		last_time = int(t)
	if time_seconds - last_time < 60 * 65:
		with open(configfile) as fp:
        		line = fp.readline()
        		while line:
            			if 'pdf_path:' in line:
                			directory = line.replace('pdf_path:','').replace('\n','').strip()
				line = fp.readline()
    		for filename in os.listdir(directory):
        		if filename.endswith(".pdf") or filename.endswith(".PDF"):
				faileddirectory = os.path.join(directory, 'failed')
				shutil.move(os.path.join(directory, filename), os.path.join(faileddirectory, filename))
				break
	f.seek(0)
	f.write(str(time_seconds))
	f.truncate()
	f.close()
	