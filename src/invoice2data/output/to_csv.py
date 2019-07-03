import csv
import sys


def write_to_file(data, path, date_format="%Y-%m-%d"):
    """Export extracted fields to csv

    Appends .csv to path if missing and generates csv file in specified directory, if not then in root

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
    if path.endswith('.csv'):
        filename = path
    else:
        filename = path + '.csv'

    if sys.version_info[0] < 3:
        openfile = open(filename, "wb")
    else:
        openfile = open(filename, "w", newline='')


    if data is None or len(data) == 0:
        return
    with openfile as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

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

        writer.writerow(first_row)
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
                        csv_items.append(v)
                        break
                if not exist:
                    csv_items.append('')
            writer.writerow(csv_items)
