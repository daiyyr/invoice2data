import os
import subprocess
import sys
import main
import shutil

dir_path = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(dir_path, 'run.config')
directory = (dir_path + '/pdf/testing').replace("//", "/")

with open(configfile) as fp:
    line = fp.readline()
    while line:
        if 'pdf_failed:' in line:
            directory = line.replace('pdf_failed:','').replace('\n','').strip()
            break
        line = fp.readline()

succeed_path = os.path.join(directory, 'succeed')
if not os.path.exists(succeed_path):
    os.makedirs(succeed_path)
all_files = []
parame = ['invoice2data','--output-format', 'csv']
firstpdf = ''

for filename in sorted(os.listdir(directory)):
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        #subprocess.check_output(['ls','-l']) #all that is technically needed...
        all_files.append(directory+ "/" +filename)
        parame.append(directory+ "/" +filename)
        firstpdf = filename
        break

parame.append("--debug")

#run main directly
dir_path = os.path.dirname(os.path.realpath(__file__))

parame = {}
parame['dbpass'] = None
parame['output_format'] = 'csv'
parame['input_files'] = all_files
parame['output_name'] = os.path.join(dir_path, 'output.csv')
parame['template_folder'] = 'extract/templates/nz'

try:
    re = main.main2(parame)
    if re:
        shutil.move(os.path.join(directory, firstpdf), os.path.join(succeed_path, firstpdf))
    else:
        pass
except Exception as e:
    print(e)

#Use: python batch_print_raw_text.py &> output.txt

# subprocess.check_output(parame)




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


