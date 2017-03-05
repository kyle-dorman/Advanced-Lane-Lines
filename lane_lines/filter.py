#!/bin/python

import numpy as np
import cv2

def abs_channel_sobel_thresh(image, channel=0, orient='x', sobel_kernel=3, thresh=(0, 255)):
  channel_image = image[:,:,channel]
  if orient is 'x':
      sobel = cv2.Sobel(channel_image, cv2.CV_64F, 1, 0)
  else:
      sobel = cv2.Sobel(channel_image, cv2.CV_64F, 0, 1)
  abs_sobel = np.absolute(sobel)
  scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
  grad_binary = np.zeros_like(scaled_sobel)
  grad_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
  return grad_binary

def filter(image, s_thresh=(20, 45), x_thresh=(20, 35)):

	image = np.copy(image)
	# Convert to HSV color space and separate the V channel
	hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float)
	hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS).astype(np.float)

	vx = abs_channel_sobel_thresh(hsv, channel = 2, thresh=x_thresh)
	lx = abs_channel_sobel_thresh(hls, channel = 1, thresh=x_thresh)
	rx = abs_channel_sobel_thresh(image, channel = 0, thresh=x_thresh)
	sx = abs_channel_sobel_thresh(hls, channel = 2, thresh=s_thresh)

	comb_vlr = np.zeros_like(rx)
	comb_vlr[((rx == 1) & (lx == 1)) | ((rx == 1) & (vx == 1)) | ((lx == 1) & (vx == 1))] = 255

	result = np.zeros_like(rx)
	result[(comb_vlr == 1) | (sx == 1)] = 1
	return result 
