
import sys
import MySQLdb
import logging as logger
import datetime
import uuid
from azure.storage.file import FileService
from azure.storage.file import ContentSettings


def write_to_db(data, path, date_format="%Y-%m-%d", dbpass="", azure_account="", azure_key=""):
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
        conn = MySQLdb.connect(host= "192.168.1.12",
                user="root",
                passwd=dbpass,
                db="edms_general")
        x = conn.cursor()
    except Exception as e:
        logger.error("Connecting mysql error '%s'", e.message)
        return 'link db failed'

    if data is None:
        return

    try:
        description = ''
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

        onlinefilename = str(uuid.uuid4()) + '.pdf'
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
            data['invoice_number'].replace("\'","\\\'") if data['invoice_number'] is not None else '',
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
            data['gst_number'].replace("\'","\\\'") if 'gst_number' in data and data['gst_number'] is not None else '',
            description.replace("\'",""),
            onlinefilename.replace("\'","\\\'")
        )
        x.execute(sqlstr)
        conn.commit()
        return 'succeed'
    except Exception as e:
        if e.message is not '':
            logger.error("db operation error: %s", e.message)
        elif len(e.args) > 1 and e.args[1] is not None and e.args[1] is not '':
            logger.error("db operation error: %s", e.args[1])
        else:
            logger.error("db operation error")
        conn.rollback()
    conn.close()
