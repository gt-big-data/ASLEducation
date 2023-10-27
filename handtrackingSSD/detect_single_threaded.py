from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse

import dataset_gen

detection_graph, sess = detector_utils.load_inference_graph()

path_to_train_images = 'Image-Annotation-5/train/images'
# path_to_train_labels = '/content/Image-Annotation-5/train/labels'
path_to_test_images = 'Image-Annotation-5/test/images'
# path_to_test_labels = '/content/Image-Annotation-5/test/labels'
path_to_val_images = 'Image-Annotation-5/valid/images'
# path_to_val_labels = '/content/Image-Annotation-5/valid/labels'

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-sth',
        '--scorethreshold',
        dest='score_thresh',
        type=float,
        default=0.2,
        help='Score threshold for displaying bounding boxes')
    # parser.add_argument(
    #     '-fps',
    #     '--fps',
    #     dest='fps',
    #     type=int,
    #     default=1,
    #     help='Show FPS on detection/display visualization')
    # parser.add_argument(
    #     '-src',
    #     '--source',
    #     dest='video_source',
    #     default=0,
    #     help='Device index of the camera.')
    # parser.add_argument(
    #     '-wd',
    #     '--width',
    #     dest='width',
    #     type=int,
    #     default=320,
    #     help='Width of the frames in the video stream.')
    # parser.add_argument(
    #     '-ht',
    #     '--height',
    #     dest='height',
    #     type=int,
    #     default=180,
    #     help='Height of the frames in the video stream.')
    # parser.add_argument(
    #     '-ds',
    #     '--display',
    #     dest='display',
    #     type=int,
    #     default=1,
    #     help='Display the detected images using OpenCV. This reduces FPS')
    # parser.add_argument(
    #     '-num-w',
    #     '--num-workers',
    #     dest='num_workers',
    #     type=int,
    #     default=4,
    #     help='Number of workers.')
    # parser.add_argument(
    #     '-q-size',
    #     '--queue-size',
    #     dest='queue_size',
    #     type=int,
    #     default=5,
    #     help='Size of the queue.')
    args = parser.parse_args()
    
    start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (512, 513)
    # max number of hands we want to detect/track
    num_hands_detect = 1

    cv2.namedWindow('Single-Threaded Detection', cv2.WINDOW_NORMAL)

    for image_path in dataset_gen.generate_stream(path_to_val_images):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np = cv2.imread(image_path)
        # image_np = cv2.flip(image_np, 1)
        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
        # while scores contains the confidence for each of these boxes.
        # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

        boxes, scores = detector_utils.detect_objects(image_np,
                                                      detection_graph, sess)
        
        # # draw bounding boxes on frame
        detector_utils.draw_box_on_image(num_hands_detect, args.score_thresh,
                                         scores, boxes, im_width, im_height,
                                         image_np, 0.75)
        (p1x, p1y, p2x, p2y), image_display = detector_utils.get_image_cropped(num_hands_detect, args.score_thresh,
                                         scores, boxes, im_width, im_height,
                                         image_np, 0.75)
        image_display = cv2.cvtColor(image_display, cv2.COLOR_RGB2BGR)
        cv2.rectangle(image_display, (p1x, p1y), (p2x, p2y), (77, 255, 9), 3, 1)

        # Calculate Frames per second (FPS)
        num_frames += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time

        if (len(boxes) >= 1):
            # cv2.drawContours(image_np, contours=(77, 255, 9))
            cv2.imshow('Single-Threaded Detection',
                       image_np)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            
            dataset_gen.saveImage(image_display, 'Image-Cropped/valid/images', image_path.split('/')[-1])
        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                  elapsed_time, "fps: ", str(int(fps)))
