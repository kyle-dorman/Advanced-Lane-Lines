#!/bin/python

import os
import sys

project_path, x = os.path.split(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_path)

from moviepy.editor import VideoFileClip
from lane_lines.road import Road
from lane_lines.file import full_path

def process_video(video_name):
	print("Processing your video!")
	clip = VideoFileClip(full_path("input_videos/" + video_name))

	road = Road()
	
	new_clip = clip.fl_image(road.process)
	new_clip.write_videofile(full_path("output_videos/" + video_name), audio=False)

	print("Finished processing your video!")
	print("Processed", road.frame_counter, "images and found", len(road.invalid_lanes), "invalid frames.")

process_video("challenge_video.mp4")
