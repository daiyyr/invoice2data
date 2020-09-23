
import sys
import MySQLdb
import logging as logger
import datetime
import uuid
from azure.storage.file import FileService
from azure.storage.file import ContentSettings
from shutil import copyfile
import os
import re


def write_to_db(data, path, date_format="%Y-%m-%d", dbhost="", dbuser="", dbpass="", dbname="", azure_account="", azure_key="", pdf_path=""):
    """Insert extracted fields to mysql

    Parameters
    ----------
    data : dict
        Dictionary of extracted fields
    path : str
        path of the original pdf file
    date_format : str
        Date format used in generated file

    Notes
    ----
    Do give file name to the function parameter path.

    Examples
    --------
        re = output_module.write_to_db(res, f.name, args.output_date_format, 
                args.dbpass, args.azure_account, args.azure_key)

    """
    try:
        conn = MySQLdb.connect(host= dbhost,
                user=dbuser,
                passwd=dbpass,
                db=dbname)

        x = conn.cursor()

        if data['issuer'].replace("\'","\\\'") == 'Watercare Services Limited':
            connWatercare = MySQLdb.connect(host= dbhost,
                user=dbuser,
                passwd=dbpass,
                db='watercare')
	    watercareCur = connWatercare.cursor()

    except Exception as e:
        logger.error("Connecting mysql error " + str(e))
        return 'link db failed'

    if data is None:
        return

    try:
        sqlstr = ''
        description = ''
        if 'description' in data:
            description += data['description'] + '; '
        if 'this_month_reading' in data:
            description += data['this_month_reading'] + '; '
        if 'last_month_reading' in data:
            description += data['last_month_reading'] + '; '
        if 'last_month_reading' in data:
            description += data['last_month_reading'] + '; '
        if 'water_usage_0_water_1_wastewater' in data:
            description += 'water usage: ' + data['water_usage_0_water_1_wastewater'] + '; '
        if 'fixed_charges' in data:
            description += 'fixed charges: ' + data['fixed_charges'] + '; '

        #Norma requested @23.09.2020, Watercare description: Water charges 18/04/2019-22/05/2019
        if data['issuer'].replace("\'","\\\'") == 'Watercare Services Limited':
            if 'this_month_reading' in data and data['this_month_reading'] and 'last_month_reading' in data and data['last_month_reading']:
                last_month = re.findall("(\d{1,2}\-[a-zA-Z]{3}\-\d\d)", data['last_month_reading'])
                this_month = re.findall("(\d{1,2}\-[a-zA-Z]{3}\-\d\d)", data['this_month_reading'])
		if last_month and this_month:
                    description = 'Water charges ' + last_month[0] + ' - ' + this_month[0]
        gst = 0
        try:
            gst = float(data['gst'])
        except:
            pass
        gross = 0
        try:
            gross = float(data['amount'])
        except:
            pass
        net = gross - gst

	if data['issuer'].replace("\'","\\\'") == 'Watercare Services Limited':
            getbccodesql= 'select accountnumber, bccode from useraccount where accountnumber=\'' + data['invoice_number'].replace(u'\u2212', '-').decode('utf-8','ignore').encode("utf-8").replace("\'","\\\'") + '\''
            try:
                watercareCur.execute(getbccodesql)
            except Exception as e:
                logger.error("db operation error: " + str(e))
                print(getbccodesql)
            accountNumberRows = watercareCur.fetchall()
            if accountNumberRows:
                for row in accountNumberRows:
                    data['bc_number'] = row[1]
                    break

            checksql='select `BC number`, `Invoice Date`, `Invoice Total` from edms where `BC number` = ' + "'"+data['bc_number'].replace("\'","\\\'")+"'" + ' and `Invoice Date`= ' + ("'"+data['date'].strftime('%Y-%m-%d')+"'") + ' and `Invoice Total`= ' + str(gross)
            try:
                x.execute(checksql)
            except Exception as e:
                logger.error("db operation error: " + str(e))
                print(checksql)
            checkRows = x.fetchall()
            if checkRows:
                for row in checkRows:
                    return 'exists'



        onlinefilename = str(uuid.uuid4()) + '.pdf'
        if azure_account == 'nextcloud' and azure_key == 'nextcloud':
            uploadfolder = os.path.join(os.path.abspath(os.path.join(pdf_path, os.pardir)),'upload')
            if not os.path.exists(uploadfolder):
                os.makedirs(uploadfolder)
            copyfile(path, os.path.join(uploadfolder,onlinefilename))
        else:
            file_service = FileService(protocol = 'https', endpoint_suffix = 'core.windows.net', 
            account_name = azure_account, 
            account_key = azure_key)
            file_service.create_file_from_path(
                'cinvoice',
                None, # We want to create this blob in the root directory, so we specify None for the directory_name
                onlinefilename,
                path,
                content_settings=ContentSettings(content_type='application/pdf'))
            # file_service.get_file_to_path('cinvoice', None, onlinefilename, 'out-from-file-service.pdf')

        sqlstr = """
INSERT INTO edms set
`Document type` = 'invoice2data',
`Supplier` = '%s',
`Invoice Number` = '%s',
`BC number` = '%s',
`Invoice Date` = %s,
`Due Date` = %s,
`Net Total` = %s,
`Tax Total` = %s,
`Invoice Total` = %s,
`GST Number` = '%s',
`defaultcoa` = 0,
`defaultcoastring` = null,
`description` = '%s',
GUID = '%s',
flag = 0,
addTime = NOW(),
creditor_id = null,
creditor_name = null
""" % (
            data['issuer'].replace("\'","\\\'") if data['issuer'] is not None else '',
            (data['invoice_number'].replace(u'\u2212', '-').decode('utf-8','ignore').encode("utf-8").replace("\'","\\\'") + "/" + data['date'].strftime('%d%m%Y')) if data['invoice_number'] is not None else '',
            data['bc_number'].replace("\'","\\\'") if data['bc_number'] is not None else '',
            ("'"+data['date'].strftime('%Y-%m-%d')+"'") \
            if data['date'] is not None 
            and (type(data['date']) is datetime.date or type(data['date']) is datetime.datetime) \
            else 'null',
            ("'"+data['due_date'].strftime('%Y-%m-%d')+"'") \
            if 'due_date' in data and data['due_date'] is not None 
            and (type(data['due_date']) is datetime.date or type(data['due_date']) is datetime.datetime) \
            else 'null',
            net,
            gst,
            gross,
            data['gst_number'].replace(u'\u2212', '-').decode('utf-8','ignore').encode("utf-8").replace("\'","\\\'").replace(' ', '') if 'gst_number' in data and data['gst_number'] is not None else '',
            description.replace("\'",""),
            onlinefilename.replace("\'","\\\'")
        )
        x.execute(sqlstr)
        conn.commit()
        return 'succeed'
    except Exception as e:
        logger.error("db operation error: " + str(e))
        if sqlstr:
            print(str(sqlstr))
        conn.rollback()
    try:
        conn.close()
    except:
        pass
