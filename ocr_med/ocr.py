import pytesseract
from pathlib import Path
import os
import json
import cv2
import re
from ocr_med.filters.image_filters import ImageFilter

# Use the following line if you are using Docker
# TESSERACT_PATH = os.environ.get("TESSERACT_PATH")
# pytesseract.pytesseract.tesseract_cmd = r'TESSERACT_PATH'

pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'
ROOT_PATH :str = Path(__file__).parents[1]

def run_ocr(image, template_name, file_name):

    filter_functions = ImageFilter()

    json_file = os.path.join(ROOT_PATH, 'templates')
    template = os.path.join(json_file, f'{template_name}')

    with open(template, 'r') as file:
        template_dict = json.load(file)

    list_template = list(template_dict.keys())[2:]
    for region in list_template:
        list_roi = list(template_dict[region]['key_values'].values())
        list_keys = list(template_dict[region]['key_values'].keys())
        for roi_index, roi in enumerate(list_roi):
            image_roi = image[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
            image_roi = filter_functions.blurry_filter(image_roi)
            image_roi = filter_functions.salt_and_pepper_filter(image_roi)
            image_roi = filter_functions.convert_to_grayscale(image_roi)
            result = pytesseract.image_to_string(image_roi, lang='eng', config='--psm 6')
            result = re.sub(r'\n', '', result)
            template_dict[region]['key_values'][list_keys[roi_index]] = result 
    template_dict['image_file_name'] = file_name
    return template_dict

if __name__ == "__main__":
    image = cv2.imread(os.path.join(ROOT_PATH, 'data\jpg\GCA RE.jpg'))
    template_name = 'template1'
    print(run_ocr(image, template_name))