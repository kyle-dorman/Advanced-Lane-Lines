## Advanced Lane Finding

In this project I will demonstrate how to identify lane lines using traditional image processing libraries like OpenCV. Processing a video is really just processing a series of images one at a time. Processing an image is done through a pipeline of steps which I will layout below. 

[//]: # (Image References)

[image1]: ./output_images/calibrated_board.png "Calibration Board Image"
[image2]: ./output_images/filter_threshold.png "Filter Threshold Image"
[image3]: ./output_images/image_mask.png "Image Mask Image"
[image4]: ./output_images/lane_lines_from_fit_line.png "Lane Lines From Fit Line Image"
[image5]: ./output_images/lane_lines_identified.png "Lane Lines Identified Image"
[image6]: ./output_images/orig_distored_filtered.png "Original Distorted And Filtered Image"
[image7]: ./output_images/warped_road_curved.png "Warped Road Curved Image"
[image8]: ./output_images/warped_road_straight.png "Warped Road Straight"
[image9]: ./output_images/found_lanes_displayed.png "Found Lanes"

## Step 0: Calibrate Camera

This step actually only happens once and is completed before processing a video. Cameras map the 3D world into a 2D representation and each camera does this slightly differently. As a result, we need to calibrate our camera to ensure a consistent view of the world no matter what camera we use. 

Camera calibration is done using 20 images of a chess board found in `camera_cal`. The images are taken with the same camera from different angles. This board has 9x6 intersections of the black and white squares. Using OpenCV's `findChessboardCorners`, `cornerSubPix` and `calibrateCamera` functions. This specifically happens in `lane_lines/PerspectiveTransformer.py`. Whenever an `ImageDistorter` class is instantiated, the camera images are used to calibrate the camera. The camera matrix(`mtx`) and the distortion coefficients(`dist`) are stored on the class instance. The instance can then be used throughout the video to undistorted each image.

Below is an example of a chess board before and after it has been undistorted:

![alt text][image1]

## Step 1: Filter Image

The first step in processing an image is to convert the image to a binary array where 1s will most likely be lane lines and 0s are everything else. To do this, I broke out the searching into two distinct areas. One where there is high brightness and one where there is low brightness. I broke these two areas out because the types of filters that are successful in high brightness areas are not successful in low brightness areas. I specifically wanted different filters for areas with shadows. In high brightness areas I mostly looked for places that where white (high R, G, & B) or places that were yellow (range in Hue). In the shadow areas, I instead relied on areas of high contrast. In the shadow areas, it was difficult to rely on any specific colors to be available, so looking for high contrast in the X direction helped identify lines. The filter logic is in the file `lane_lines/filter.py`.

Below is an example image showing the shadow area identified in red and the non shadow areas in blue:

![alt text][image2]

## Step 2: Perspective Transform

The next step is to transform the image into a bird's eye view of the space around the lane. This is done in `lane_lines/PerspectiveTransform.py` using the class `RoadTransformer`. `RoadTransformer` uses hard-coded source and destination points to identify the lane area and the resulting image shape respectively. Below is an image showing the source mask shape on an image.

![alt text][image3]

And here is the result of the transform on a straight road and on a curved road::

![alt text][image8]

![alt text][image7]

and here is the distorted filtered image:

![alt text][image6]

This is specifically done using the OpenCV `getPerspectiveTransform` function. The resulting transformation matrix is saved to the `RoadTransformer` class along with the reverse matrix to re-transform the image back after processing. 

## Step 3: Identify lane lines

Once the binary image is transformed into a bird's eye view, a simple search algorithm is used to identify the lane lines in `lane_lines/find_lane_lines.py`. There are two ways of identifying lane lines. The first is when there are no previous lines found or there are no "valid" lines found. In this case I first try to fit a line using a sliding window approach. The starting point for the search is found by looking at the bottom half of the image and finding the two places (one on the left half one on the right half) with the largest number of pixels. A single window is searched using `find_window_centroid` in the same file. After searching a line of best fit is drawn for the window frames found. An example of this is show below:

![alt image][image5]

In the case where previous valid lanes existed, an initial line of best fit already exists. Using either line of best fit, pixels within a certain margin are then used to fit another line. This happens in `find_lane_lines_from_fit`. An example of the result is show below:

![alt image][image4]

Step 4: Find radius of curvature and vehicle position offset

Up until now, everything we have done is specific to the world of the image. But the important part of this image processing is to actually translate our results back to the real world. One way to can begin to do this is to translate the fit lines into a real world radius of curvature for the road and a position offset for the car from the center of the lane. These calculations are done in `lane_lines/find_lane_lines.py`'s `find_radius` and `find_line_base_pos` functions. These functions use hard coded translation params to convert the bird's eye view pixel space back to the real world. The code in these functions is not overly complex and is not robust to changing lane widths. 

Step 5: Display found lines on original image

The last step is to actually visualize what the algorithm has found. To do this, the space between the lanes in the bird's eye image is colored green and then projected back down onto the original image space and overlaid on the original image. This is done in `lane_lines/road.py`'s `draw_lanes` function. The lane that is actually displayed is an average of the last 10 lane lines found which pass some validation filters. An example result is below:

![alt image][image9]

## Result

The results of the project were very successful for the `input_videos/project_videp.mp4`. This video has minimal shadows and "weird" road colors and for the most part the car drives on a flat path. The results of my video processing for the project video is below:

![Project Video Link](https://www.youtube.com/watch?v=sajyBSXdqZ0)

## Reflections

I had less success with the challenge_video and the harder_challenge_video. In the challenge_video my model had a hard time picking out lane lines from the other high contrast areas in the image. I did a lot of work to make the filters more robust and from my original filters but at this point they continue to need more work. The harder_challenge_video is much much harder. One huge assumption that I made during the project was the projection area where I should look for the lanes never changes. In the challenge video, the car drives on uneven terrain which changes the area where I need to search for lane lines and should also change the projection matrix. A lot more work would have to be done to support changing projection areas. 

One of my biggest take aways from this project is that hard coded image processing is bound to fail in the real world. The part of the project I spent the most time on was tweaking my image filters to find what might be lane line pixels. My filters became more and more complicated as I tweaked them but they always used hard coded values based purely on my intuition and what I saw from processing a few images. I feel very strongly that a neural network would provide a much more robust solution to lane finding than any hard coded solution can given enough well tagged data. I am left wondering what methods companies are using to find lane lines or if they are doing it at all. 
