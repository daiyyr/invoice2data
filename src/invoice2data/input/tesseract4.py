# -*- coding: utf-8 -*-
def to_text(path, language='fra'):
    """Wraps Tesseract 4 OCR with custom language model.

    Parameters
    ----------
    path : str
        path of electronic invoice in JPG or PNG format

    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format

    """
    import subprocess
    from distutils import spawn
    import tempfile
    import time
    from pdf2image import convert_from_path
    from PIL import Image
    import logging as logger

    # Check for dependencies. Needs Tesseract and Imagemagick installed.
    if not spawn.find_executable('tesseract'):
        raise EnvironmentError('tesseract not installed.')
    if not spawn.find_executable('convert'):
        raise EnvironmentError('imagemagick not installed.')
    if not spawn.find_executable('gs'):
        raise EnvironmentError('ghostscript not installed.')



    try:
        pages = convert_from_path(path, 500)
    except Exception as e:
        logger.error('pdf2image failed processing ' + path)
        logger.error(e.message)
        return ''

    if(len(pages)==1):
        pages[0].save('out.jpg', 'JPEG')
    else:
        imagefiles = []
        i = 0
        for page in pages:
            page.save('out'+str(i)+'.jpg', 'JPEG')
            imagefiles.append('out'+str(i)+'.jpg')
            i += 1
        images = map(Image.open, imagefiles)
        widths, heights = zip(*(j.size for j in images))
        new_width = max(widths)
        new_height = sum(heights)
        new_im = Image.new('RGB', (new_width, new_height))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0,y_offset))
            y_offset += im.size[1]
        new_im.save('out.jpg')

    extracted_str = ''

    try:

        with tempfile.NamedTemporaryFile(suffix='.tiff') as tf:
            # Step 1: Convert to TIFF
            gs_cmd = [
                'gs',
                '-q',
                '-dNOPAUSE',
                '-r600x600',
                '-sDEVICE=tiff24nc',
                '-sOutputFile=' + tf.name,
                'out.jpg', #path
                '-c',
                'quit',
            ]
            subprocess.Popen(gs_cmd)
            time.sleep(3)

            # Step 2: Enhance TIFF
            magick_cmd = [
                'convert',
                tf.name,
                '-colorspace',
                'gray',
                '-type',
                'grayscale',
                '-contrast-stretch',
                '0',
                '-sharpen',
                '0x1',
                'tiff:-',
            ]

            p1 = subprocess.Popen(magick_cmd, stdout=subprocess.PIPE, shell=True)

            tess_cmd = ['tesseract', '-l', language, '--oem', '1', '--psm', '3', 'stdin', 'stdout']
            p2 = subprocess.Popen(tess_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)

            out, err = p2.communicate()

            extracted_str = out

    except Exception as e:
        logger.error('tesseract4 failed processing ' + path + ', please check your RAM using')
        logger.error(e.message)


    return extracted_str