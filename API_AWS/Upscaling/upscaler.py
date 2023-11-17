import cv2
from cv2 import dnn_superres

size = (224, 224)
SIZE = 224**2
THRESHOLD = 0.75
PATH = "ESPCN_x4.pb"
sr = dnn_superres.DnnSuperResImpl_create()
# Read the desired model
sr.readModel(PATH)
# Set the desired model and scale to get correct pre- and post-processing
sr.setModel("espcn", 4)

def upscale(image):

  result = None
  if len(image)*len(image[1])/SIZE <= THRESHOLD:
    # Upscale the image
    result = sr.upsample(image)
    
  if result is None:
    print("here")
    result = image

  return cv2.cvtColor(cv2.resize(result,dsize=size), cv2.COLOR_BGR2RGB) # bicupid interpolation, averages 16 pixels nearby and interpolates rgb values, adds more pixels
