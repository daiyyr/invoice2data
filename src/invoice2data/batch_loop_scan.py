import os
import subprocess
import time
import datetime
import main
import sys
import shutil

dir_path = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(dir_path, 'run.config')
directory2 = None
directory3 = None
directory4 = None
directory5 = None
pdf_failed = ''
pdf_succeed = ''
pdf_moved_failed = ''

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
            elif 'pdf_failed:' in line:
                pdf_failed = line.replace('pdf_failed:','').replace('\n','').strip()
            elif 'pdf_succeed:' in line:
                pdf_succeed = line.replace('pdf_succeed:','').replace('\n','').strip()
            elif 'pdf_moved_failed:' in line:
                pdf_moved_failed = line.replace('pdf_moved_failed:','').replace('\n','').strip()
            elif 'pdf_2_path:' in line:
                directory2 = line.replace('pdf_2_path:','').replace('\n','').strip()
            elif 'pdf_3_path:' in line:
                directory3 = line.replace('pdf_3_path:','').replace('\n','').strip()
            elif 'pdf_4_path:' in line:
                directory4 = line.replace('pdf_4_path:','').replace('\n','').strip()
            elif 'pdf_5_path:' in line:
                directory5 = line.replace('pdf_5_path:','').replace('\n','').strip()

            line = fp.readline()
except:
    pass

# directory = ('/home/administrator/edms/failedTemp').replace("//", "/")
# directory = ('/home/teemo/source/invoice2data/src/invoice2data/pdf/testing2').replace("//", "/")

while True:
    for filename in os.listdir(directory):
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            parame0 = [
                'python',
                'main.py',
                "--dbhost", dbhost,
                "--dbuser", dbuser,
                "--dbpass", dbpass, 
                "--dbname", dbname,
                "--azure_account", azure_account, 
                "--azure_key", azure_key,
                "--pdf_path", directory,
                "--output-format", "mysql" ]
            parame0.append(directory+ "/" +filename)

            parame = {}
            parame['dbhost'] = dbhost
            parame['dbuser'] = dbuser
            parame['dbpass'] = dbpass
            parame['dbname'] = dbname
            parame['azure_account'] = azure_account
            parame['azure_key'] = azure_key
            parame['pdf_path'] = directory
            parame['pdf_failed'] = pdf_failed
            parame['pdf_succeed'] = pdf_succeed
            parame['pdf_moved_failed'] = pdf_moved_failed
            parame['output_format'] = 'mysql'
            parame['template_folder'] = 'extract/templates/nz'
            runlog = open('run.log', 'a')
            runlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' start process ' + filename + '\n')
            runlog.close()
            
            input_files = []
            input_files.append(directory+ "/" +filename)
            parame['input_files'] = input_files
            #print(subprocess.check_output(parame))
            errorlog = open('run.error.log', 'a')
            oristd = sys.stdout
            orierr = sys.stderr
            sys.stdout = errorlog
            sys.stderr = errorlog
            # process = subprocess.Popen(parame0, stdout=errorlog, stderr=errorlog)
            # process.communicate()
            try:
                main.main2(parame)
            except Exception as e:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' process ' + filename + ' error ' + str(e))
                #errorlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' process ' + filename + ' error ' + str(e) + '\n')
            sys.stdout = oristd
            sys.stderr = orierr
            errorlog.close()
            if os.path.exists(directory+ "/" +filename):
                try:
                    #failed_path = os.path.join(directory, 'failed2')
                    failed_path = pdf_moved_failed
                    if not os.path.exists(failed_path):
                        os.makedirs(failed_path)
                    shutil.move(directory+ "/" +filename, failed_path+ "/" +filename)
                except Exception:
                    pass
    if directory2 is not None:
        for filename in os.listdir(directory2):
            if filename.endswith(".pdf") or filename.endswith(".PDF"):
                parame0 = [
                    'python',
                    'main.py',
                    "--dbhost", dbhost,
                    "--dbuser", dbuser,
                    "--dbpass", dbpass, 
                    "--dbname", dbname,
                    "--azure_account", azure_account, 
                    "--azure_key", azure_key,
                    "--pdf_path", directory2,
                    "--output-format", "mysql" ]
                parame0.append(directory2+ "/" +filename)

                parame = {}
                parame['dbhost'] = dbhost
                parame['dbuser'] = dbuser
                parame['dbpass'] = dbpass
                parame['dbname'] = dbname
                parame['azure_account'] = azure_account
                parame['azure_key'] = azure_key
                parame['pdf_path'] = directory2
                parame['output_format'] = 'mysql'
                parame['template_folder'] = 'extract/templates/nz'
                runlog = open('run.log', 'a')
                runlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' start process ' + filename + '\n')
                runlog.close()
                
                input_files = []
                input_files.append(directory2+ "/" +filename)
                parame['input_files'] = input_files
                #print(subprocess.check_output(parame))
                errorlog = open('run.error.log', 'a')
                oristd = sys.stdout
                orierr = sys.stderr
                sys.stdout = errorlog
                sys.stderr = errorlog
                # process = subprocess.Popen(parame0, stdout=errorlog, stderr=errorlog)
                # process.communicate()
                try:
                    main.main2(parame)
                except Exception as e:
                    errorlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    + ' process ' + filename + ' error ' + e.message + '\n')
                sys.stdout = oristd
                sys.stderr = orierr
                errorlog.close()
                if os.path.exists(directory2+ "/" +filename):
                    try:
                        failed_path = os.path.join(directory2, 'failed2')
                        if not os.path.exists(failed_path):
                            os.makedirs(failed_path)
                        shutil.move(directory2+ "/" +filename, failed_path+ "/" +filename)
                    except Exception:
                        pass
    if directory3 is not None:
        for filename in os.listdir(directory3):
            if filename.endswith(".pdf") or filename.endswith(".PDF"):
                parame0 = [
                    'python',
                    'main.py',
                    "--dbhost", dbhost,
                    "--dbuser", dbuser,
                    "--dbpass", dbpass, 
                    "--dbname", dbname,
                    "--azure_account", azure_account, 
                    "--azure_key", azure_key,
                    "--pdf_path", directory3,
                    "--output-format", "mysql" ]
                parame0.append(directory3+ "/" +filename)

                parame = {}
                parame['dbhost'] = dbhost
                parame['dbuser'] = dbuser
                parame['dbpass'] = dbpass
                parame['dbname'] = dbname
                parame['azure_account'] = azure_account
                parame['azure_key'] = azure_key
                parame['pdf_path'] = directory3
                parame['output_format'] = 'mysql'
                parame['template_folder'] = 'extract/templates/nz'
                runlog = open('run.log', 'a')
                runlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' start process ' + filename + '\n')
                runlog.close()
                
                input_files = []
                input_files.append(directory3+ "/" +filename)
                parame['input_files'] = input_files
                #print(subprocess.check_output(parame))
                errorlog = open('run.error.log', 'a')
                oristd = sys.stdout
                orierr = sys.stderr
                sys.stdout = errorlog
                sys.stderr = errorlog
                # process = subprocess.Popen(parame0, stdout=errorlog, stderr=errorlog)
                # process.communicate()
                try:
                    main.main2(parame)
                except Exception as e:
                    errorlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    + ' process ' + filename + ' error ' + e.message + '\n')
                sys.stdout = oristd
                sys.stderr = orierr
                errorlog.close()
                if os.path.exists(directory3+ "/" +filename):
                    try:
                        failed_path = os.path.join(directory3, 'failed2')
                        if not os.path.exists(failed_path):
                            os.makedirs(failed_path)
                        shutil.move(directory3+ "/" +filename, failed_path+ "/" +filename)
                    except Exception:
                        pass
    time.sleep(2) #Delays for 2 seconds
