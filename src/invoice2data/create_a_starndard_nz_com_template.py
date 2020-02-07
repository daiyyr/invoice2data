from shutil import copyfile
import sys
import re
import os

companyname = sys.argv[1]
validletter = re.sub(r'[\W_]+', '', companyname)
filename = 'nz.com.' + re.sub(r'[\s]+', '', validletter).lower() + '.yml'
validnamewithspace = re.sub(r'[^\w\s]+', '', companyname)
issuer = re.sub(r'[\s]+', ' ', validnamewithspace).strip().lower().title()
keywords = re.sub(r'[^\w\s]+', '.', companyname.strip())
keywords = re.sub(r'\s+', "This_is_a_space_to_avoid_KeyError_Teemo", keywords)
keywords = keywords.replace("This_is_a_space_to_avoid_KeyError_Teemo", '\\s*')
if not os.path.exists('./extract/templates/nz'):
    os.makedirs('./extract/templates/nz')
if os.path.isfile('./extract/templates/nz/' + filename): 
    print('Template already exist: ' + './extract/templates/nz/' + filename)
    quit
else:
    copyfile('standard_template_nz_com.yml', './extract/templates/nz/'+filename)
    newline = os.linesep # Defines the newline based on your OS.
    source_fp = open('standard_template_nz_com.yml', 'r')
    target_fp = open('./extract/templates/nz/'+filename, 'w')
    lineN = 0
    for row in source_fp:
        if lineN == 0:
            row = 'issuer: ' + issuer + "\n"
        if lineN == 2:
            row = "- '" + keywords + "'" + "\n"
        lineN += 1
        target_fp.write(row)
    source_fp.close()
    target_fp.close()
    print('Template created: ' + './extract/templates/nz/' + filename)
quit