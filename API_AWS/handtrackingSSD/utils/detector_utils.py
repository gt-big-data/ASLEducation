# Utilities for object detector.
from utils import label_map_util
import numpy as np
import sys
import tensorflow as tf
import os
from threading import Thread
from datetime import datetime
import cv2
from collections import defaultdict


detection_graph = tf.Graph()
sys.path.append("..")

# score threshold for showing bounding boxes.
_score_thresh = 0.27

parent_dir = 'API_AWS/handtrackingSSD/'
MODEL_NAME = 'hand_inference_graph'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = parent_dir + MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = parent_dir + MODEL_NAME + '/hand_label_map.pbtxt'
# if (os.path.exists(PATH_TO_LABELS)):
#     print("error1")
# else :
#     print("error2")
NUM_CLASSES = 1
# load label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# Load a frozen infrerence graph into memory
def load_inference_graph():

    # load frozen tensorflow model into memory
    print("> ====== loading HAND frozen graph into memory")
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.compat.v1.Session(graph=detection_graph)
    print(">  ====== Hand Inference graph loaded.")
    return detection_graph, sess


# draw the detected bounding boxes on the images
# You can modify this to also draw a label.
def get_cropped_image(score_thresh, scores, boxes, im_width, im_height, image_np, padding_percent):
    if (scores[0] > score_thresh):
        (left, right, top, bottom) = (boxes[0][1] * im_width, boxes[0][3] * im_width,
                                        boxes[0][0] * im_height, boxes[0][2] * im_height)
        p1 = (max(0, int(left) - int(left*padding_percent//2)), max(0, int(top) - int(top*padding_percent//2)))
        p2 = (min(im_width, int(right) + int(right*padding_percent//2)), min(im_height, int(bottom) + int(bottom*padding_percent//2)))
        
        return image_np[p1[0]:p2[0],p1[1]:p2[1]]
    else:
        return None



# draw the detected bounding boxes on the images
# You can modify this to also draw a label.
def draw_box_on_image(num_hands_detect, score_thresh, scores, boxes, im_width, im_height, image_np, padding_percent):
    for i in range(num_hands_detect):
        if (scores[i] > score_thresh):
            (left, right, top, bottom) = (boxes[i][1] * im_width, boxes[i][3] * im_width,
                                          boxes[i][0] * im_height, boxes[i][2] * im_height)
            p1 = (max(0, int(left) - int(left*padding_percent//2)), max(0, int(top) - int(top*padding_percent//2)))
            p2 = (min(im_width, int(right) + int(right*padding_percent//2)), min(im_height, int(bottom) + int(bottom*padding_percent//2)))
            
            cv2.rectangle(image_np, p1, p2, (77, 255, 9), 3, 1)

def get_image_cropped(num_hands_detect, score_thresh, scores, boxes, im_width, im_height, image_np, padding_percent):
    for i in range(num_hands_detect):
        p1x = p2x = p1y = p2y = None
        height = width = None
        p1xbox = p2xbox = p1ybox = p2ybox = None
        if (scores[i] > score_thresh):
            (left, right, top, bottom) = (boxes[i][1] * im_width, boxes[i][3] * im_width,
                                          boxes[i][0] * im_height, boxes[i][2] * im_height)

            p1x = max(0, int(left) - int(left*padding_percent//2))
            p1y = max(0, int(top) - int(top*padding_percent//2))
            p2x = min(im_width, int(right) + int(right*padding_percent//2))
            p2y = min(im_height, int(bottom) + int(bottom*padding_percent//2))
            
            height = p2y - p1y
            width = p2x - p1x
            
            p1xbox = int(left*padding_percent//2)
            p2xbox = width - int(right*padding_percent//2)
            p1ybox = int(top*padding_percent//2)
            p2ybox = height - int(bottom*padding_percent//2)
            
        return (p1xbox, p1ybox, p2xbox, p2ybox), image_np[p1y:p2y, p1x:p2x]

# Show fps value on image.
def draw_fps_on_image(fps, image_np):
    cv2.putText(image_np, fps, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (77, 255, 9), 2)

# Actual detection .. generate scores and bounding boxes given an image
def detect_objects(image_np, detection_graph, sess):
    # Definite input and output Tensors for detection_graph
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # Each box represents a part of the image where a particular object was detected.
    detection_boxes = detection_graph.get_tensor_by_name(
        'detection_boxes:0')
    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name(
        'detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name(
        'detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name(
        'num_detections:0')
    print("detobj - 111")

    image_np_expanded = np.expand_dims(image_np, axis=0)
    print("detobj - 222")

    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores,
            detection_classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})
    print("detobj - 333")
    return np.squeeze(boxes), np.squeeze(scores)


# Code to thread reading camera input.
# Source : Adrian Rosebrock
# https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
class WebcamVideoStream:
    def __init__(self, src, width, height):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def size(self):
        # return size of the capture device
        return self.stream.get(3), self.stream.get(4)

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
