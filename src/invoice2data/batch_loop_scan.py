import os
import subprocess
import time
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
directory = ('/home/administrator/edms/failedTemp').replace("//", "/")
# directory = ('/home/teemo/source/invoice2data/src/invoice2data/pdf/testing2').replace("//", "/")

while True:
    for filename in os.listdir(directory):
        parame = ['invoice2data',
                "--dbpass", "", 
                "--azure_account", "", 
                "--azure_key", "",
                "--output-format", "mysql" ]
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
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
    time.sleep(10) #Delays for 10 seconds