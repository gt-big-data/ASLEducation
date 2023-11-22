from urllib.request import urlretrieve
from PIL import Image
from matplotlib import pyplot as plt
import os

import numpy as np
import torch
from torchvision import transforms
from google.colab.patches import cv2_imshow

def load_model():
  model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet50', pretrained=True)
  model.eval()
  return model

def make_transparent_foreground(pic, mask):
  # split the image into channels
  r, g, b = cv2.split(np.array(pic).astype('uint8'))
  # add an alpha channel with and fill all with transparent pixels (max 255)
  a = np.ones(mask.shape, dtype='uint8') * 255
  # merge the alpha channel back
  alpha_im = cv2.merge([b, g, r, a], 4)
  # create a transparent background
  bg = np.zeros(alpha_im.shape)
  # setup the new mask
  new_mask = np.stack([mask, mask, mask, mask], axis=2)
  # copy only the foreground color pixels from the original image where mask is set
  foreground = np.where(new_mask, alpha_im, 0).astype(np.uint8)

  return foreground

def remove_background(model, input_file):
  input_image =input_file
  print(input_image is None)
  preprocess = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])

  input_tensor = preprocess(input_image)
  input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

  # move the input and model to GPU for speed if available
  if torch.cuda.is_available():
      input_batch = input_batch.to('cuda')
      model.to('cuda')

  with torch.no_grad():
      output = model(input_batch)['out'][0]
  output_predictions = output.argmax(0)

  # create a binary (black and white) mask of the profile foreground
  mask = output_predictions.byte().cpu().numpy()
  background = np.zeros(mask.shape)
  bin_mask = np.where(mask, 255, background).astype(np.uint8)
  new_mask = np.stack([mask, mask, mask], axis=2)
  input_image = np.array(input_image)
  #input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
  input_image = np.where(new_mask, input_image, new_mask).astype(np.uint8)
  #cv2_imshow(input_image)
  #foreground = make_transparent_foreground(input_image ,bin_mask)

  return input_image, bin_mask

def main(image):
  from google.colab.patches import cv2_imshow
  deeplab_model = load_model()
  # directory = os.path.abspath(os.getcwd())+  '/API_AWS/upload_images'
  # dst =  os.path.abspath(os.getcwd()) +  '/API_AWS/segmented_images'
  # for filename in os.listdir(directory):
  #     print ("hello")
  #     input_file = os.path.join(directory, filename)
  #     img, bin_mask = remove_background(deeplab_model, input_file)
  #     cv2.imwrite(os.path.join(dst, filename), img)
  img, bin_mask = remove_background(deeplab_model, image)
  return img
      