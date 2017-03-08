#!/bin/python

import numpy as np
import cv2
from scipy.signal import convolve2d

# filter an RGB image for yellow and while lane lines
def filter(image):
  shadow = shadow_lane_finder(image)
  non_shadow = non_shadow_lane_finder(image)
  result = np.zeros_like(shadow)
  result[(shadow==1)|(non_shadow==1)] = 1
  return result

# filter an rgb image for yellow and white lane lines in areas of higher brightness
def non_shadow_lane_finder(image):
  yellow = yellow_finder(image)
  white = white_finder(image)
  shadow = shadow_mask(image, thresh=(0,50))
  
  result = np.zeros_like(white)
  result[((yellow==1)|(white==1)) & (shadow==0)] = 1
  return result

# filter an rgb image high contrast areas in areas of low brightness
def shadow_lane_finder(image):
  shadow = shadow_mask(image)
  r_sobel = abs_sobel_mask(image[:,:,0], shadow)
  g_sobel = abs_sobel_mask(image[:,:,0], shadow)
  b_sobel = abs_sobel_mask(image[:,:,0], shadow)
  
  result = np.zeros_like(r_sobel)
  result[(r_sobel==1)|(g_sobel==1)|(b_sobel==1)] = 1
  return result

# find white lane lines
def white_finder(image, thresh=(200, 255)):
  r = image[:,:,0]
  g = image[:,:,1]
  b = image[:,:,2]
  white = np.zeros_like(r)
  white[((r >=thresh[0]) & (r <= thresh[1])) & ((g >=thresh[0]) & (g <= thresh[1])) & ((b >=thresh[0]) & (b <= thresh[1]))] = 1
  black = hsv_threshold(image, channel=2, thresh=(0, 180))
  gradx = abs_sobel_thresh(image, orient='x', sobel_kernel=15, thresh=(25, 100))
  
  combined = np.zeros_like(gradx)
  combined[((gradx==1)|(white==1))&(black==0)] = 1
  return combined

#find yellow lane lines
def yellow_finder(image):
  h1 = hsv_threshold(image, channel=0, thresh=(17, 30))
  h2 = hls_threshold(image, channel=0, thresh=(20, 30))
  # s = hls_threshold(image, channel=2, thresh=(100, 255))
  result = np.zeros_like(h1)
  # result[((h1==1)|(h2==1))&(s==1)] = 1
  result[(h1==1)|(h2==1)] = 1
  return result

# find areas of shadow based on brightness from an rgb image
# thresh (0-50) will hide shadow
# thresh (50-255) is show shadow)
def shadow_mask(image, thresh=(50, 255)):
  l = cv2.cvtColor(image, cv2.COLOR_RGB2HLS).astype(np.float)[:,:,1]
  mask = convolve2d(l, np.ones((3, 3)), mode='same')
  scaled_mask = np.uint8(255*mask/np.max(mask))
  shadow_mask = np.zeros_like(scaled_mask)
  shadow_mask[(scaled_mask>=thresh[0])&(scaled_mask<=thresh[1])] = 1
  return shadow_mask

# filter an rgb image for a certain channel in hsv
def hsv_threshold(image, channel=0, thresh=(0, 255)):
  hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
  c_img = hsv[:,:,channel]
  binary = np.zeros_like(c_img)
  binary[(c_img >= thresh[0]) & (c_img <= thresh[1])] = 1
  return binary

# filter an rgb image for a certain channel in hls
def hls_threshold(image, channel=0, thresh=(0, 255)):
  hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS).astype(np.float)
  c_img = hls[:,:,channel]
  binary = np.zeros_like(c_img)
  binary[(c_img >= thresh[0]) & (c_img <= thresh[1])] = 1
  return binary

# filter a single channel image for the absolute value of the Sobel operator in the X direction with a filter mask
def abs_sobel_mask(c_img, mask):
  sobel = cv2.Sobel(c_img, cv2.CV_64F, 1, 0, ksize=11)
  abs_sobel = np.absolute(sobel)
  abs_sobel[(mask == 1)] = 0
  scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
  scaled_sobel[(mask == 1)] = 0
  result = np.zeros_like(scaled_sobel)
  result[(scaled_sobel>25)] = 1
  return result

# filter an rgb image for the absolute value of the Sobel operator in the X direction
def abs_sobel_thresh(img, orient='x', sobel_kernel=3, thresh=(0, 255)):
  gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  if orient is 'x':
      sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
  else:
      sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
  abs_sobel = np.absolute(sobel)
  scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
  grad_binary = np.zeros_like(scaled_sobel)
  grad_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
  return grad_binary
