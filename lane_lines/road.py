#!/bin/python

import numpy as np
import cv2
from lane_lines.filter import filter
from lane_lines.PerspectiveTransformer import ImageDistorter
from lane_lines.PerspectiveTransformer import RoadTransformer
from lane_lines.find_lane_lines import find_lane_lines

class Road:
	max_lanes = 10

	def __init__(self):
		self.left_lanes = []
		self.right_lanes = []
		self.distorter = ImageDistorter()
		self.transformer = RoadTransformer()

	def process(self, image):
		undistorted = distorter.undistort(image)
		warped = transformer.warped(undistorted)
		warped_binary = filter(warped)

		self.add_lanes(find_lane_line(warped_binary, self.left_fit(), self.right_fit()))
		self.display_info()
		return self.draw_lanes(image, warped_binary)

	def display_info():
		print("Radius of curvature(L):", self.left_lanes[-1].radius_of_curvature)
		print("Radius of curvature(R):", self.right_lanes[-1].radius_of_curvature)
		print("Center offset(m):", self.left_lanes[-1].line_base_pos)

	def draw_lanes(self, image, warped_binary):
		# Create an image to draw the lines on
		warp_zero = np.zeros_like(warped_binary).astype(np.uint8)
		color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

		# Recast the x and y points into usable format for cv2.fillPoly()
		pts_left = np.array([np.transpose(np.vstack([self.left_fitx(), self.ploty()]))])
		pts_right = np.array([np.flipud(np.transpose(np.vstack([self.right_fitx(), self.ploty()])))])
		pts = np.hstack((pts_left, pts_right))

		# Draw the lane onto the warped blank image
		cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

		# Warp the blank back to original image space using inverse perspective matrix (Minv)
		newwarp = self.transformer.unwarped(color_warp)
		# Combine the result with the original image
		result = cv2.addWeighted(image, 1, newwarp, 0.3, 0)
		return result

	def left_fit(self):
		return None

	def right_fit(self):
		return None

	def ploty(self):
		return self.left_lanes[-1].ally

	def left_fitx(self):
		self.left_lanes[-1].allx

	def right_fitx(self):
		self.right_lanes[-1].allx


	def add_lanes(self, lanes):
		self.left_lanes.append(lanes[0])
		self.right_lanes.append(lanes[1])

		if len(left_lanes) > self.max_lanes:
			self.left_lanes.pop(0)
		if len(right_lanes) > self.max_lanes:
			self.right_lanes.pop(0)

		self.validate_lane_lines()

	def validate_lane_lines(self):
		if len(self.left_lanes) is 0 or len(self.right_lanes) is 0:
			return 

		


		# # x values of the last n fits of the line
		# self.recent_xfitted = [] 
		# #average x values of the fitted line over the last n iterations
		# self.bestx = None     
		# #polynomial coefficients averaged over the last n iterations
		# self.best_fit = None 
		# #difference in fit coefficients between last and new fits
		# self.diffs = np.array([0,0,0], dtype='float') 

