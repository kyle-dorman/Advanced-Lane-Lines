#!/bin/python

import os

# Get full path to a resource underneath this project (CarND-Behavioral-Cloning)
def full_path(name):
	base_dir_name = "Advanced-Lane-Lines"
	base_dir_list = os.getcwd().split("/")
	i = base_dir_list.index(base_dir_name)
	return "/".join(base_dir_list[0:i+1]) + "/" + name
