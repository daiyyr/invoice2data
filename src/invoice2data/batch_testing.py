import os
import subprocess
import sys
import main

dir_path = os.path.dirname(os.path.realpath(__file__))
directory = (dir_path + '/pdf/testing').replace("//", "/")
all_files = []
parame = ['invoice2data','--output-format', 'csv']

for filename in os.listdir(directory):
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        #subprocess.check_output(['ls','-l']) #all that is technically needed...
        all_files.append(directory+ "/" +filename)
        parame.append(directory+ "/" +filename)

parame.append("--debug")

#run main directly
dir_path = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(dir_path, 'run.config')
try:
    with open(configfile) as fp:
        line = fp.readline()
        while line:
            if 'dbhost:' in line:
                dbhost = line.replace('dbhost:','').replace('\n','').strip()
            elif 'dbuser:' in line:
                dbuser = line.replace('dbuser:','').replace('\n','').strip()
            elif 'dbpass:' in line:
                dbpass = line.replace('dbpass:','').replace('\n','').strip()
            elif 'dbname:' in line:
                dbname = line.replace('dbname:','').replace('\n','').strip()
            elif 'azure_account:' in line:
                azure_account = line.replace('azure_account:','').replace('\n','').strip()
            elif 'azure_key:' in line:
                azure_key = line.replace('azure_key:','').replace('\n','').strip()
            elif 'pdf_path:' in line:
                directory = line.replace('pdf_path:','').replace('\n','').strip()

            line = fp.readline()
except:
    pass
parame = {}
parame['dbpass'] = None
parame['output_format'] = 'csv'
parame['input_files'] = all_files
parame['output_name'] = os.path.join(dir_path, 'output.csv')
main.main2(parame)

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


