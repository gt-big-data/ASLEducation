import cv2
from cv2 import dnn_superres
import os

size = (224, 224)
SIZE = 224**2
THRESHOLD = 0.75
PATH = os.path.join(os.path.abspath(os.getcwd()), "API_AWS/Upscaling/ESPCN_x4.pb")
print(PATH)
sr = dnn_superres.DnnSuperResImpl_create()
# Read the desired model
sr.readModel(PATH)
# Set the desired model and scale to get correct pre- and post-processing
sr.setModel("espcn", 4)

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def upscale(image):

  result = None
  if len(image)*len(image[1])/SIZE <= THRESHOLD: 
    # Upscale the image
    result = sr.upsample(image)
    
  if result is None:
    print("here")
    result = image

  # return cv2.cvtColor(cv2.resize(result,dsize=size), cv2.COLOR_BGR2RGB) # bicupid interpolation, averages 16 pixels nearby and interpolates rgb values, adds more pixels
  return image_resize(result,width=224) 
