from io import BytesIO
import streamlit as st
from PIL import Image
import requests
from bs4 import BeautifulSoup
import cv2
import pandas as pd
import numpy as np
import io
import sys
from tempfile import TemporaryFile
sys.path.append("/Users/joshuadiao/ASLEducation/API_AWS/handtrackingSSD")

import Image_Segmentation.foreground_segmentation
from handtrackingSSD import detect_single_threaded

labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R',18: 'S',19: 'T',20: 'U',21: 'V',22: 'W',23: 'X',24: 'Y',25: 'Z'}





def run():
    st.title("ASL Hand Classification")
    img_file = st.file_uploader("Choose an Image", type=["jpg", "png"])
    if img_file is not None:
        img = Image.open(img_file).resize((250, 250))
        st.image(img, use_column_width=False)
        # save_image_path = './upload_images/' + img_file.name
        # with open(save_image_path, "wb") as f:
        #     f.write(img_file.getbuffer())

        if img_file is not None:
            url = "http://54.234.222.205:5000/predict"
            img_detected =  detect_single_threaded.main(np.array(img.convert("RGB")).astype(np.uint8))
            img_detected1 = Image.fromarray(img_detected)
            img_segmented = Image_Segmentation.foreground_segmentation.main(img_detected1)
            st.image(img_detected, use_column_width=False)
            st.image(img_segmented, use_column_width=False)
            
            fp = TemporaryFile()
            Image.fromarray(img_segmented).save(fp, "PNG")
            form_data = {'file': fp}
            # cv2.imshow("Image", form_data['file'])
            resp = requests.post(url, files=form_data)
            resp_dict = resp.json()
            result = resp_dict['prediction']
            st.info("Prediction for hand sign is: " + result)
            # print(result)

run()

sys.path.pop()