# import the necessary packages
import pytesseract as pt
import argparse
import cv2
import os



if __name__ == '__main__':
    img_path = ('./data/test.png')
    language = 'pt-br'

    string = pt.image_to_string(img_path, lang=language)
    print(string)
    print("=========================================")
    box = pt.image_to_boxes(img_path, lang=language)
    print(box)
    print("=========================================")
    data = pt.image_to_data(img_path, lang=language)
    print(data)
    print("=========================================")
    osd = pt.image_to_osd(img_path, lang=language)
