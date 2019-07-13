import os
import subprocess
import time
import datetime

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

# directory = ('/home/administrator/edms/failedTemp').replace("//", "/")
# directory = ('/home/teemo/source/invoice2data/src/invoice2data/pdf/testing2').replace("//", "/")

while True:
    for filename in os.listdir(directory):
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            parame = ['invoice2data',
                "--dbhost", dbhost,
                "--dbuser", dbuser,
                "--dbpass", dbpass, 
                "--azure_account", azure_account, 
                "--azure_key", azure_key,
                "--output-format", "mysql" ]
            runlog = open('run.log', 'a')
            runlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' start process ' + filename + '\n')
            runlog.close()    
            #subprocess.check_output(['ls','-l']) #all that is technically needed...
            parame.append(directory+ "/" +filename)
            #print(subprocess.check_output(parame))
            errorlog = open('run.error.log', 'a')
            process = subprocess.Popen(parame, stdout=errorlog, stderr=errorlog)
            errorlog.close()
            process.communicate()
            if os.path.exists(directory+ "/" +filename):
                try:
                    failed_path = os.path.join(directory, 'failed')
                    if not os.path.exists(failed_path):
                        os.makedirs(failed_path)
                    os.rename(directory+ "/" +filename, failed_path+ "/" +filename)
                except Exception:
                    pass
    time.sleep(2) #Delays for 2 seconds