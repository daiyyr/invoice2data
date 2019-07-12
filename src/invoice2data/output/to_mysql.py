
import sys
import MySQLdb
import logging as logger
import datetime

def write_to_file(data, path, date_format="%Y-%m-%d", dbpass=""):
    """Insert extracted fields to mysql

    Parameters
    ----------
    data : dict
        Dictionary of extracted fields
    path : str
        directory to save generated csv file
    date_format : str
        Date format used in generated file

    Notes
    ----
    Do give file name to the function parameter path.

    Examples
    --------
        >>> from invoice2data.output import to_csv
        >>> to_csv.write_to_file(data, "/exported_csv/invoice.csv")
        >>> to_csv.write_to_file(data, "invoice.csv")

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

    if data is None or len(data) == 0:
        return

    """
    first_row = []
    for line in data:
        for k, v in line.items():
            exist = False
            for column in first_row:
                if column == k:
                    exist = True
                    break
            if not exist:
                first_row.append(k)

    for line in data:
        csv_items = []
        for column in first_row:
            exist = False
            for k, v in line.items():
                if column == k:
                # first_row.append(k)
                    if k.startswith('date') or k.endswith('date'):
                        try:
                            v = v.strftime('%d/%m/%Y')
                        except:
                            pass
                    exist = True
                    if isinstance(v, basestring):
                        v = v.encode('utf-8')
                    csv_items.append(v)
                    break
            if not exist:
                csv_items.append('')
        #writer.writerow(csv_items)
    """        

    try:
        description = ''
        if 'this_month_reading' in data[0]:
            description += data[0]['this_month_reading'] + '; '
        if 'last_month_reading' in data[0]:
            description += data[0]['last_month_reading'] + '; '
        if 'last_month_reading' in data[0]:
            description += data[0]['last_month_reading'] + '; '
        if 'water_usage_0_water_1_wastewater' in data[0]:
            description += 'water usage: ' + data[0]['water_usage_0_water_1_wastewater'] + '; '
        if 'fixed_charges' in data[0]:
            description += 'fixed charges: ' + data[0]['fixed_charges'] + '; '

        gst = 0
        try:
            gst = float(data[0]['gst'])
        except:
            pass
        gross = 0
        try:
            gross = float(data[0]['amount'])
        except:
            pass
        net = gross - gst

        azurepathguid = ''
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
`defaultcoa` = null,
`defaultcoastring` = null,
`description` = '%s',
GUID = '%s',
flag = 0,
addTime = NOW(),
creditor_id = null,
creditor_name = null
""" % (
            data[0]['issuer'].replace("\'","\\\'") if data[0]['issuer'] is not None else '',
            data[0]['invoice_number'].replace("\'","\\\'") if data[0]['invoice_number'] is not None else '',
            data[0]['bc_number'].replace("\'","\\\'") if data[0]['bc_number'] is not None else '',
            ("'"+data[0]['date'].strftime('%Y-%m-%d')+"'") \
            if data[0]['date'] is not None 
            and (type(data[0]['date']) is datetime.date or type(data[0]['date']) is datetime.datetime) \
            else 'null',
            ("'"+data[0]['due_date'].strftime('%Y-%m-%d')+"'") \
            if 'due_date' in data[0] and data[0]['due_date'] is not None 
            and (type(data[0]['due_date']) is datetime.date or type(data[0]['due_date']) is datetime.datetime) \
            else 'null',
            net,
            gst,
            gross,
            data[0]['gst_number'].replace("\'","\\\'") if 'gst_number' in data[0] and data[0]['gst_number'] is not None else '',
            description.replace("\'",""),
            azurepathguid.replace("\'","\\\'")
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
