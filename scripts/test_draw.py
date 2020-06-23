from drawBoxes.drawBoxes import draw
from os import listdir
from os.path import isfile, join
import subprocess
import fitz
import unicodedata
import json
from prextract.box_extractor import get_doc_text_boxes

pdfs = listdir('../data/dodfs/2020/05_Maio/')

for pdf in pdfs:
    actual_pdf = join('../data/dodfs/2020/05_Maio/', pdf)
    pymu_file = fitz.open(actual_pdf)
    text_blocks = []
    for textboxes in get_doc_text_boxes(pymu_file):
        for text in textboxes:
            object = {
                "bounding_box": [text[0], text[2], 810-text[1], 810-text[3]],
                "text": unicodedata.normalize('NFKD', text[4]).encode('ascii', 'ignore').decode('utf8')
                     }
            text_blocks.append(object)

            json.dump(text_blocks, open(actual_pdf.replace('.pdf', '.json'), "w",
                                         encoding="utf-8"), ensure_ascii=False)



    # new_pdf = join('../data/dodfs/2020/05_Maio/converted/', pdf)
    # command = 'gs -q -sDEVICE=pdfwrite -dCompatibilityLevel=2.0 -o ' + new_pdf.replace(' ', '\ ') + ' ' \
    #                                                                  + actual_pdf.replace(' ', '\ ')
    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # output = process.communicate()[0]
    # exitCode = process.returncode

    # print(exitCode)
    # print(output)

    # process.wait()
    # print(process.returncode)

# pdfs_converted = listdir('../data/dodfs/2020/05_Maio/converted/')
# for pdf in pdfs_converted:
#     pdf_path = join('../data/dodfs/2020/05_Maio/converted/', pdf)
#     d = fitz.open(pdf_path)
#     draw(d)
#     d.save(d.name.replace('.pdf', '_drawBoxes.pdf'))
