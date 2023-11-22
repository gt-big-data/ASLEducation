import io
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model
from flask import Flask, jsonify, request
import sys
import os
from PIL import Image
import cv2


sys.path.append(os.path.abspath(os.getcwd()) + "/API_AWS/handtrackingSSD")
print(os.path.abspath(os.getcwd()) + "API_AWS/handtrackingSSD")

import Image_Segmentation.foreground_segmentation
import Upscaling.upscaler 

model = load_model('API_AWS/resnet101_seg.h5')

labels = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R',18: 'S',19: 'T',20: 'U',21: 'V',22: 'W',23: 'X',24: 'Y',25: 'Z'}


def prepare_image(img_bytes):
    # pil_img = Image.open(io.BytesIO(img))
    
    # # Convert PIL Image to OpenCV format (if necessary)
    # cv2_img = np.array(pil_img)
    
    # # Perform necessary image processing here using cv2_img or pil_img
    
    # # Example: Display the image using OpenCV
    # cv2.imshow("Image", cv2_img)
    # cv2.waitKey(0)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize((224,224))
    img = np.array(img)
    img_upscale = Image.fromarray(Upscaling.upscaler.upscale(img))
    img_segmented = Image_Segmentation.foreground_segmentation.main(img_upscale)
    # img_path = "./test.jpg"
    # img = Image.fromarray(img_segmented)
    # img.save('bruh.jpg')
    
    
    img = img_segmented / 255
    img = np.expand_dims(img, [0])
    answer = model.predict(img)
    y_class = answer.argmax(axis=-1)
    print(y_class)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = labels[y]
    print(res)
    return res
    #return res.capitalize()


app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def infer_image():
    if 'file' not in request.files:
        return jsonify(error="Please try again. The Image doesn't exist")

    file = request.files.get('file')
    img_bytes = file.read()
    # img_path = "./upload_images/test.jpg"
    # with open(img_path, "wb") as img:
    #     img.write(img_bytes)
    result = prepare_image(img_bytes)
    return jsonify(prediction=result)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')