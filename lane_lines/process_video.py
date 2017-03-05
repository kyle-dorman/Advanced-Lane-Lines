#!/bin/python
from moviepy.editor import VideoFileClip
from lane_lines.road import Road
from lane_lines.file import full_path

def process_video(video_name):
	print("Processing your video!")
	road = Road()
	clip = VideoFileClip(full_path("videos/" + video_name))
	new_clip = clip.fl_image(road.process)
	new_clip.write_videofile(full_path("output_videos/" + video_name), audio=False)
	print("Finished processing your video!")
