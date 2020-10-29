#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
import os
from os.path import join
import logging

from input import pdftotext
from input import pdfminer_wrapper
from input import tesseract
from input import tesseract4
from input import gvision

from extract.loader import read_templates

from output import to_csv
from output import to_json
from output import to_xml
from output import to_mysql

from PyPDF2 import PdfFileReader, PdfFileWriter

logger = logging.getLogger(__name__)

input_mapping = {
    'pdftotext': pdftotext,
    'tesseract': tesseract,
    'tesseract4': tesseract4,
    'pdfminer': pdfminer_wrapper,
    'gvision': gvision,
}

output_mapping = {'csv': to_csv, 'json': to_json, 'xml': to_xml, 'mysql':to_mysql, 'none': None}


def extract_data(invoicefile, templates=None, input_module=pdftotext):
    """Extracts structured data from PDF/image invoices.

    This function uses the text extracted from a PDF file or image and
    pre-defined regex templates to find structured data.

    Reads template if no template assigned
    Required fields are matches from templates

    Parameters
    ----------
    invoicefile : str
        path of electronic invoice file in PDF,JPEG,PNG (example: "/home/duskybomb/pdf/invoice.pdf")
    templates : list of instances of class `InvoiceTemplate`, optional
        Templates are loaded using `read_template` function in `loader.py`
    input_module : {'pdftotext', 'pdfminer', 'tesseract'}, optional
        library to be used to extract text from given `invoicefile`,

    Returns
    -------
    dict or False
        extracted and matched fields or False if no template matches

    Notes
    -----
    Import required `input_module` when using invoice2data as a library

    See Also
    --------
    read_template : Function where templates are loaded
    InvoiceTemplate : Class representing single template files that live as .yml files on the disk

    Examples
    --------
    When using `invoice2data` as an library

    >>> from invoice2data.input import pdftotext
    >>> extract_data("invoice2data/test/pdfs/oyo.pdf", None, pdftotext)
    {'issuer': 'OYO', 'amount': 1939.0, 'date': datetime.datetime(2017, 12, 31, 0, 0), 'invoice_number': 'IBZY2087',
     'currency': 'INR', 'desc': 'Invoice IBZY2087 from OYO'}

    """
    if templates is None:
        templates = read_templates()

    # print(templates[0])
    extracted_str = input_module.to_text(invoicefile).decode('utf-8')
    tried_tesseract = False
    if len(extracted_str) < 20 and input_module == pdftotext:
        extracted_str = tesseract.to_text(invoicefile).decode('utf-8')
        tried_tesseract = True

    logger.debug('START pdftotext result ===========================')
    logger.debug(extracted_str)
    logger.debug('END pdftotext result =============================')

    logger.debug('Testing {} template files'.format(len(templates)))

    #get page count of invoicefile
    pdf = None
    pageCount = None
    try:
        pdf = PdfFileReader(open(invoicefile,'rb'))
        pageCount = pdf.getNumPages()
    except Exception as e:
        #print(e.message)
        logger.error(str(e))
        pass
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)

        if t.matches_input(optimized_str):
            if pageCount is not None and pageCount > 1:
                #dealing with pages
                confirmInTemplate = False
                for k, v in t['fields'].items():
                    if k == 'multiple_page' and v == 'True':
                        confirmInTemplate = True
                        break
                if confirmInTemplate:
                    try:
                        pdfdirectory = os.path.dirname(invoicefile)
                        pdfname = os.path.basename(invoicefile)
                        for i in range(pdf.numPages):
                            #split multi-page pdf file into multiple pdf files
                            output = PdfFileWriter()
                            output.addPage(pdf.getPage(i))
                            objectfile = join(pdfdirectory, pdfname.replace('.pdf','').replace('.PDF','') + '_' + str(i) + '.pdf' )
                            with open(objectfile, "wb") as outputStream:
                                output.write(outputStream)
                        os.remove(invoicefile)
                        logger.warning('Seperate pdf into multiple files, process in next scanning loop')
                        return 'pdf seperated'
                    except Exception as e:
                        #print(e.message)
                        logger.error(str(e))
                        pass

            ret = t.extract(optimized_str, invoicefile)
            if ret is not None and ret is not False:
                return ret

    if not tried_tesseract:
        logger.debug('No template matched, now try tesseract ===========================')
        tried_tesseract = True
        extracted_str2 = tesseract.to_text(invoicefile).decode('utf-8')
        logger.debug('START tesseract result ===========================')
        logger.debug(extracted_str2)
        logger.debug('END tesseract result =============================')
        logger.debug('Testing {} template files'.format(len(templates)))
        for t in templates:
            optimized_str2 = t.prepare_input(extracted_str2)

            if t.matches_input(optimized_str2):
                tesseract_result = t.extract(optimized_str2, invoicefile)
                if tesseract_result is None:
                    #tesseract find the right template, but do not match all required fields
                    #so use this template and use pdf2text string
                    optimized_str = t.prepare_input(extracted_str)
                    return t.extract(optimized_str, invoicefile)
                else:
                    return tesseract_result
    #print('No template for ' + invoicefile)
    logger.error('No template for %s', invoicefile)
    return False


def create_parser():
    """Returns argument parser """

    parser = argparse.ArgumentParser(
        description='Extract structured data from PDF files and save to CSV or JSON.'
    )

    parser.add_argument(
        '--input-reader',
        choices=input_mapping.keys(),
        default='pdftotext',
        help='Choose text extraction function. Default: pdftotext',
    )

    parser.add_argument(
        '--output-format',
        choices=output_mapping.keys(),
        default='none',
        help='Choose output format. Default: none',
    )

    parser.add_argument(
        '--output-date-format',
        dest='output_date_format',
        default="%Y-%m-%d",
        help='Choose output date format. Default: %Y-%m-%d (ISO 8601 Date)',
    )

    parser.add_argument(
        '--output-name',
        '-o',
        dest='output_name',
        default='invoices-output',
        help='Custom name for output file. Extension is added based on chosen format.',
    )

    parser.add_argument(
        '--debug', dest='debug', action='store_true', help='Enable debug information.'
    )

    parser.add_argument(
        '--copy', '-c', dest='copy', help='Copy and rename processed PDFs to specified folder.'
    )

    parser.add_argument(
        '--move', '-m', dest='move', help='Move and rename processed PDFs to specified folder.'
    )

    parser.add_argument(
        '--filename-format',
        dest='filename',
        default="{date} {invoice_number} {desc}.pdf",
        help='Filename format to use when moving or copying processed PDFs.'
             'Default: "{date} {invoice_number} {desc}.pdf"',
    )

    parser.add_argument(
        '--template-folder',
        '-t',
        dest='template_folder',
        help='Folder containing invoice templates in yml file. Always adds built-in templates.',
    )

    parser.add_argument(
        '--exclude-built-in-templates',
        dest='exclude_built_in_templates',
        default=False,
        help='Ignore built-in templates.',
        action="store_true",
    )

    parser.add_argument(
        'input_files', type=argparse.FileType('r'), nargs='+', help='File or directory to analyze.'
    )

    parser.add_argument(
        '--dbhost',
        dest='dbhost',
        default=None,
        help='Specify mysql db host name.',
    )
    parser.add_argument(
        '--dbuser',
        dest='dbuser',
        default=None,
        help='Specify mysql db dbuser name.',
    )
    parser.add_argument(
        '--dbpass',
        dest='dbpass',
        default=None,
        help='Specify mysql db password.',
    )
    parser.add_argument(
        '--dbname',
        dest='dbname',
        default=None,
        help='Specify mysql db name.',
    )
    parser.add_argument(
        '--azure_account',
        dest='azure_account',
        default=None,
        help='Specify Azure account name for pdf uploading',
    )
    parser.add_argument(
        '--azure_key',
        dest='azure_key',
        default=None,
        help='Specify Azure account key for pdf uploading',
    )

    parser.add_argument(
        '--pdf_path',
        dest='pdf_path',
        default=None,
        help='Specify directory to save succeed/failed pdf',
    )
    

    return parser


def main(args=None):
    """Take folder or single file and analyze each."""

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    input_module = input_mapping[args.input_reader]
    output_module = output_mapping[args.output_format]

    templates = []
    # Load templates from external folder if set.
    if args.template_folder:
        templates += read_templates(os.path.abspath(args.template_folder))

    # Load internal templates, if not disabled.
    if not args.exclude_built_in_templates:
        templates += read_templates()
    output = []
    for f in args.input_files:
        res = extract_data(f.name, templates=templates, input_module=input_module)
        if res == 'pdf seperated':
            continue
        re = None
        if res:
            logger.info(res)
            output.append(res)
            if args.dbpass is not None:
                re = output_module.write_to_db(res, f.name, args.output_date_format, 
                args.dbhost, args.dbuser, args.dbpass, args.dbname,
                args.azure_account, args.azure_key, args.pdf_path)

            if args.copy:
                filename = args.filename.format(
                    date=res['date'].strftime('%Y-%m-%d'),
                    invoice_number=res['invoice_number'],
                    desc=res['desc'],
                )
                shutil.copyfile(f.name, join(args.copy, filename))
            if args.move:
                filename = args.filename.format(
                    date=res['date'].strftime('%Y-%m-%d'),
                    invoice_number=res['invoice_number'],
                    desc=res['desc'],
                )
                shutil.move(f.name, join(args.move, filename))
        f.close()
        if args.dbpass is not None:
            #move source pdf
            pdfdirectory = os.path.dirname(f.name) #failedTemp
            pdfpath = f.name
            pdfname = os.path.basename(f.name)
            if re == 'succeed':

                #move to successful
                #succeed_path = join(pdfdirectory, 'successful')
                #move to public successful folder where clients can access
                succeed_path = os.path.abspath(os.path.join(pdfdirectory, os.pardir))
                succeed_path = join(succeed_path, 'successful')

                from datetime import date
                succeed_path = join(succeed_path, date.today().strftime('%d-%m-%Y'))

                if not os.path.exists(succeed_path):
                    os.makedirs(succeed_path)
                destinateFile = join(succeed_path, pdfname)
                shutil.move(pdfpath, destinateFile)
                pass
            elif re == 'link db failed':
                pass
            elif re == 'exists':
                #delete
                os.remove(pdfpath)
                pass

            else:
                #move to failed
                failed_path = join(pdfdirectory, 'failed')
                if not os.path.exists(failed_path):
                    os.makedirs(failed_path)
                destinateFile = join(failed_path, pdfname)
                shutil.move(pdfpath, destinateFile)
                pass


    
    if output_module is not None:
        if args.dbpass is not None:
            pass #for data base output, do it in loop of extracting
        else:
            output_module.write_to_file(output, args.output_name, args.output_date_format)


        


if __name__ == '__main__':
    main()
    # import sys
    # main(sys.argv[1:])

# if __name__ == 'main':
#     import sys
#     main(sys.argv[1:])




def main2(args=None):
    """Take folder or single file and analyze each."""

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    args['output_date_format'] = '%Y-%m-%d'
    input_module = input_mapping['pdftotext']
    output_module = output_mapping[args['output_format']]

    templates = []
    # Load templates from external folder if set.
    # if args['template_folder']:
    #     templates += read_templates(os.path.abspath(args['template_folder']))

    # Load internal templates, if not disabled.
    # if not args['exclude_built_in_templates']:
    if 'template_folder' in args:
        templates += read_templates(os.path.abspath(args['template_folder']))
    else:
        templates += read_templates()
    output = []
    for fs in args['input_files']:
        f = open(fs, 'r') 
        res = extract_data(f.name, templates=templates, input_module=input_module)
        if res == 'pdf seperated':
            continue
        re = None
        if res:
            logger.info(res)
            output.append(res)
            if args['dbpass'] is not None:
                re = output_module.write_to_db(res, f.name, args['output_date_format'], 
                args['dbhost'], args['dbuser'], args['dbpass'], args['dbname'],
                args['azure_account'], args['azure_key'], args['pdf_path'])

        f.close()
        if args['dbpass'] is not None:
            #move source pdf
            pdfdirectory = os.path.dirname(f.name)
            pdfpath = f.name
            pdfname = os.path.basename(f.name)
            if re == 'succeed':
                #move to successful
                if args['pdf_succeed']:
                    succeed_path = args['pdf_succeed']
                else:
                    #succeed_path = join(pdfdirectory, 'successful')
                    #move to public successful folder where clients can access
                    succeed_path = os.path.abspath(os.path.join(pdfdirectory, os.pardir))
                    succeed_path = join(succeed_path, 'successful')

                from datetime import date
                succeed_path = join(succeed_path, date.today().strftime('%d-%m-%Y'))
                try:
                    if not os.path.exists(succeed_path):
                        os.makedirs(succeed_path)
                    destinateFile = join(succeed_path, pdfname)
                    shutil.move(pdfpath, destinateFile)
                except:
                    if args['pdf_moved_failed']:
                        succeed_path = args['pdf_moved_failed']
                    else:
                        succeed_path = join(pdfdirectory, 'failedToMove')
                    succeed_path = join(succeed_path, date.today().strftime('%d-%m-%Y'))
                    if not os.path.exists(succeed_path):
                        os.makedirs(succeed_path)
                    destinateFile = join(succeed_path, pdfname)
                    shutil.move(pdfpath, destinateFile)
                pass
            elif re == 'link db failed':
                pass
            elif re == 'exists':
                #delete
                print('data already exists in edms: ' + pdfname)
                os.remove(pdfpath)
                pass
            else:
                #move to failed
                if args['pdf_failed']:
                    failed_path = args['pdf_failed']
                else:
                    father_path = os.path.abspath(os.path.join(pdfdirectory, os.pardir))
                    failed_path = join(father_path, 'failed')
                if not os.path.exists(failed_path):
                    os.makedirs(failed_path)
                destinateFile = join(failed_path, pdfname)
                shutil.move(pdfpath, destinateFile)
                pass


    
    if output_module is not None:
        if args['dbpass'] is not None:
            pass #for data base output, do it in loop of extracting
        else:
            logger.warning(output)
            output_module.write_to_file(output, args['output_name'], args['output_date_format'])
    return res
