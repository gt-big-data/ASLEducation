import cv2
from roboflow import Roboflow
import os


# rf = Roboflow(api_key="8O0d3piVDubPgWzft4ha")

# project = rf.workspace("bdbi").project("image-annotation-lxsso")
# dataset = project.version(5).download("yolov8")

def generate_stream(folder):
    files = os.listdir(folder)
    files.sort()
    for file in files:
        yield folder+'/'+file

def saveImage(image, folder, name):
    image_dir = os.path.join(folder, name)
    print(image_dir)
    cv2.imwrite(image_dir, image)
    

