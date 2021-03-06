import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
directory = (dir_path + '/pdf/testing').replace("//", "/")

configfile = os.path.join(dir_path, 'run.config')

with open(configfile) as fp:
    line = fp.readline()
    while line:
        if 'pdf_failed:' in line:
            directory = line.replace('pdf_failed:','').replace('\n','').strip()
            break
        line = fp.readline()


all_files = ''
parame = ['invoice2data','--output-format', 'csv']

for filename in sorted(os.listdir(directory)):
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        #subprocess.check_output(['ls','-l']) #all that is technically needed...
        all_files += "\"" + directory+ "/" +filename + '\" '
        parame.append(directory+ "/" +filename)
        break

parame.append("--debug")

subprocess.check_output(parame)

#Use: python batch_print_raw_text.py &> output.txt



#Neither of following methods work. 
# outputfile = 'output.txt'
# open(outputfile, 'w').close() #clean file first

# try method 1
# orig_stdout = sys.stdout
# orig_stderr = sys.stderr
# f = open(outputfile, 'w')
# sys.stdout = f
# sys.stderr = f
# print(subprocess.check_output(parame))
# sys.stdout = orig_stdout
# sys.stderr = orig_stderr
# f.close()

# try method 2
# f = open(outputfile,'w')
# print 2>>f, subprocess.check_output(parame)     # Python 2.x
# print('whatever', file=f) # Python 3.x

# print('find result in: ' + outputfile)


