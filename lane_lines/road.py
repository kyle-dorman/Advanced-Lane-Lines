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

		# for debugging purposes, log the verification data
		self.slope_diffs = []
		self.fit_diffs = []
		self.lane_distance = []
		self.frame_counter = 0
		self.invalid_lanes = []

	def process(self, image):
		self.frame_counter += 1
		undistorted = self.distorter.undistort(image)
		warped = self.transformer.warped(undistorted)
		warped_binary = filter(warped)
		lines = find_lane_lines(warped_binary, image, self.left_fit(), self.right_fit())
		self.validate_lane_lines(lines[0], lines[1])
		self.add_lanes(lines)
		# self.display_info()
		return self.draw_lanes(image, warped_binary)

	def display_info(self):
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
		
		pts_left = np.int32(pts_left)[0]
		pts_right = np.int32(pts_right)[0]

		for i in range(1, len(pts_left)):
			cv2.line(color_warp, (pts_left[i-1][0], pts_left[i-1][1]), (pts_left[i][0], pts_left[i][1]), (255,0,0), 5)

		for i in range(1, len(pts_right)):
			cv2.line(color_warp, (pts_right[i-1][0], pts_right[i-1][1]), (pts_right[i][0], pts_right[i][1]), (0,0,255), 5)

		# Warp the blank back to original image space using inverse perspective matrix (Minv)
		newwarp = self.transformer.unwarped(color_warp)
		# Combine the result with the original image
		result = cv2.addWeighted(image, 1, newwarp, 0.3, 0)
		return result

	# returns an optional fit for use when finding the next line
	def left_fit(self):
		return self.fit(self.left_lanes)

	# returns an optional fit for use when finding the next line
	def right_fit(self):
		return self.fit(self.right_lanes)

	# returns an fit(always) for use when drawing the lines
	def fit_for_draw(self, direction):
		if direction == 'left':
			fit = self.left_fit()
			if fit is None:
				print("No valid lines are available. Using the last invalid line only.")
				fit = self.left_lanes[-1].fit
		else:
			fit = self.right_fit()
			if fit is None:
				print("No valid lines are available. Using the last invalid line only.")
				fit = self.right_lanes[-1].fit
		return fit

	# returns an optional fit
	def fit(self, lines):
		if len(lines) == 0:
			return None
		fits = [line.fit for line in lines if line.valid]
		if len(fits) == 0:
			return None
		return np.average(fits, axis=0)

	def ploty(self):
		size = len(self.left_lanes[-1].ally)
		return np.linspace(0, size - 1, size)

	def left_fitx(self):
		return self.x_points(self.fit_for_draw('left'))

	def right_fitx(self):
		return self.x_points(self.fit_for_draw('right'))

	def x_points(self, fit):
		y_points = self.ploty()
		return fit[0]*y_points**2 + fit[1]*y_points + fit[2]

	def add_lanes(self, lanes):
		self.left_lanes.append(lanes[0])
		self.right_lanes.append(lanes[1])

		if len(self.left_lanes) > self.max_lanes:
			self.left_lanes.pop(0)
		if len(self.right_lanes) > self.max_lanes:
			self.right_lanes.pop(0)

	def validate_fit(self, left, right):
		# average fit of past 10 lines
		left_fit_diff = np.abs(self.fit_for_draw('left') - left.fit)
		right_fit_diff = np.abs(self.fit_for_draw('right') - right.fit)

		if self.validate_fit_diff(left, right, left_fit_diff) == False:
			return False

		if self.validate_fit_diff(left, right, right_fit_diff) == False:
			return False

		self.fit_diffs.append(left_fit_diff)
		self.fit_diffs.append(right_fit_diff)

		return True

	def validate_fit_diff(self, left, right, fit_diff):
		fit_diff_a_tolerance = 0.001
		fit_diff_b_tolerance = 0.2
		fit_diff_c_tolerance = 50

		if fit_diff[0] > fit_diff_a_tolerance:
			print("Marking line as invalid because first polynomial term difference is greater than", fit_diff_a_tolerance, ". Term difference is", fit_diff[0])
			return False

		if fit_diff[1] > fit_diff_b_tolerance:
			print("Marking line as invalid because second polynomial term difference is greater than", fit_diff_b_tolerance, ". Term difference is", fit_diff[1])
			return False

		if fit_diff[2] > fit_diff_c_tolerance:
			print("Marking line as invalid because third polynomial term difference is greater than", fit_diff_c_tolerance, ". Term difference is", fit_diff[2])
			return False

		return True

	def validate_lane_distance(self, left, right):
		lane_distance_min = 275.0
		lane_distance_max = 310.0
		lane_distance = right.allx[-1] - left.allx[-1]
		if lane_distance < lane_distance_min or lane_distance > lane_distance_max:
			print("Marking line as invalid because inter-lane distance falls outside range", lane_distance_min, "-", lane_distance_max, ". Distance is", lane_distance)
			return False
		self.lane_distance.append(lane_distance)
		return True

	def validate_slopes(self, left, right):
		slope_diff_tolerance = 0.2
		
		for i in range(-301, 0, 50):
			left_slope = slope(left.fit, left.ally[i])
			right_slope = slope(right.fit, right.ally[i])
			slope_diff = abs(left_slope - right_slope)
			
			if slope_diff > slope_diff_tolerance:
				print("Marking line invalid because slopes differ by more than", slope_diff_tolerance, ". Slope difference is", slope_diff)
				return False
			self.slope_diffs.append(slope_diff)

		return True

	def validate_lane_lines(self, left, right):
		if len(self.left_lanes) is 0 or len(self.right_lanes) is 0:
			return 

		if self.validate_fit(left, right) == False:
			left.valid = False
			right.valid = False
			self.invalid_lanes.append((self.frame_counter, "invalid_fit", left, right))
			return 

		if self.validate_lane_distance(left, right) == False:
			left.valid = False
			right.valid = False
			self.invalid_lanes.append((self.frame_counter, "invalid_lane_distance", left, right))
			return

		if self.validate_slopes(left, right) == False:
			left.valid = False
			right.valid = False
			self.invalid_lanes.append((self.frame_counter, "invalid_slope_difference", left, right))


def slope(fit, y):
	a = fit[0]
	b = fit[1]
	c = fit[2]

	return 2 * a * y + b

