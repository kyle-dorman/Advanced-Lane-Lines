# !/bin/python
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from lane_lines.file import full_path

class ImageDistorter:
	def __init__(self):
		size = (9,6)
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
		shape = mpimg.imread(cal_image_files()[0]).shape[0:2]

		objpoints, imgpoints = calibration_points(cal_image_files(), criteria, size)

		ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, shape, None, None)
		h, w = shape

		self.ret = ret
		self.mtx = mtx 
		self.dist = dist 
		self.rvecs = rvecs
		self.tvecs = tvecs

	def undistort(self, image):
		return cv2.undistort(image, self.mtx, self.dist, None, self.mtx)

class PerspectiveTransformer:
	def __init__(self, shape, src, dst):
		self.src = src
		self.dst = dst
		self.shape = shape
		self.M = cv2.getPerspectiveTransform(src, dst)
		self.Minv = cv2.getPerspectiveTransform(dst, src)

	# warp an already undistorted image
	def warped(self, image):
		return cv2.warpPerspective(image, self.M, (self.dst[-1][0], self.dst[-1][1]), flags=cv2.INTER_LINEAR)

	# unwarp a warped image
	def unwarped(self, image):
		return cv2.warpPerspective(image, self.Minv, self.shape, flags=cv2.INTER_LINEAR)

def cal_image_files():
  return glob.glob(full_path('camera_cal') + '/*.jpg')

class RoadTransformer(PerspectiveTransformer):
	def __init__(self):
		src = np.float32([(546, 460), (737, 460), (20, 680), (1280, 680)])
		dst = np.float32([(0, 0), (400, 0), (0, 500), (400, 500)])
		PerspectiveTransformer.__init__(self, (1280, 720), src, dst)

def find_corners(image, image_file, criteria, size):
  gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
  ret, corners = cv2.findChessboardCorners(gray, size, None)
  if ret == False:
    print('Unable to find corners in image {}.'.format(image_file))
    return (False, None)
  else:
  	# upgrade corners
    corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1),criteria)
    return (True, corners2)

def show_corners(image, corners, ret, size):
  image = cv2.drawChessboardCorners(image, size, corners, ret)
  plt.imshow(image)
  plt.show()

def calibration_points(image_files, criteria, size):
	cols = size[0]
	rows = size[1]
	objp = np.zeros((cols*rows,3), np.float32)
	objp[:,:2] = np.mgrid[0:cols,0:rows].T.reshape(-1,2)

	# Arrays to store object points and image points from all the images.
	objpoints = [] # 3d point in real world space
	imgpoints = [] # 2d points in image plane.

	for image_file in image_files:
		image = mpimg.imread(image_file)
		ret, corners = find_corners(image, image_file, criteria, size)

		if ret == True:
			objpoints.append(objp)
			imgpoints.append(corners)
          
	return (objpoints, imgpoints)

