## Advanced Lane Finding

In this project I will demonstrate how to identify lane lines using traditional image processing libraries like OpenCV. Processing a video is really just processing a series of images one at a time. Processing an image is done through a pipeline of steps which I will layout below. 

[//]: # (Image References)

[image1]: ./output_images/calibration_board.png "Calibration Board Image"
[image2]: ./output_images/filter_threshold.png "Filter Threshold Image"
[image3]: ./output_images/image_mask.png "Image Mask Image"
[image4]: ./output_images/lane_lines_from_fit_line.png "Lane Lines From Fit Line Image"
[image5]: ./output_images/lane_lines_identified.png "Lane Lines Identified Iamge"
[image6]: ./output_images/orig_distorted_filtered.png "Original Distored And Filtered Image"
[image7]: ./output_images/warped_road_curved.png "Warped Road Curved Image"
[image8]: ./output_images/warped_road_straight.png "Warped Road Straight"

## Step 0: Calibrate Camera

This step actually only happens once and is completed before processing a video. Cameras map the 3D world into a 2D representation and each camera does this slightly differently. As a result, we need to calibrate our camera to ensure a consistent view of the world no matter what camera we use. 

Camera calibration is done using 20 images of a chess board found in `camera_cal`. The images are taken with the same camera from different angles. This board has 9x6 interestions of the black and white squares. Using OpenCV's 
`findChessboardCorners`, `cornerSubPix` and `calibrateCamera` functions. This specifically happens in `lane_lines/PerspectiveTransformer.py`. Whenever an `ImageDistorter` class is instantiated, the camera images are used to calibrate the camera. The camera matrix(`mtx`) and the distortion coefficents(`dist`) are stored on the class instance. The instance can then be used throughout the video to undistort each image.

Below is an example of a chess board before and after it has been undistored:

![alt text][image1]

## Step 1: Filter Image

The first step in processing an image is to convert the image to a binary array where 1s will most likely be lane lines and 0s are everything else. To do this, the image is inspected in a few different color channels. I specifically looked at the image in the red channel (RGB), the lightness channel (HSL), the value channel (HSV), and the saturation channel (HSL). In these channels, I applied the Sobel operator in the X direction only and filter the result based on the threshold. What I am trying to do is look for high contrast areas 








