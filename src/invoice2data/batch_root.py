import os
import subprocess

dir_path = os.path.dirname(os.path.realpath(__file__))
directory = (dir_path + '/pdf').replace("//", "/")
all_files = ''
parame = ['invoice2data','--output-format', 'csv', '--exclude-built-in-templates', '--template-folder', 'template']

for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        #subprocess.check_output(['ls','-l']) #all that is technically needed...
        all_files += "\"" + directory+ "/" +filename + '\" '
        parame.append(directory+ "/" +filename)
        
print (subprocess.check_output(parame))