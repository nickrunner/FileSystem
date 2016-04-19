#!/usr/bin/python

import os, sys
from stat import *

def traverse(path, callback):

	dirs = os.listdir(path)
	file_count = 0;
	dir_size = os.stat(path).st_size;

	for f in dirs:
		#print f
		pathname = os.path.join(path, f)
		mode = os.stat(pathname).st_mode

		#check if it's a directory
		if S_ISDIR(mode):
			#Print Stats
			callback(pathname, file_count, dir_size)
			#Recurse
			traverse(pathname, callback)

		elif S_ISREG(mode):
			#Count files
			file_count += 1;
			dir_size += os.stat(pathname).st_size
			
		else:
			print 'Unknown File Type'

def print_usage(f, count, size):
	print  size, "    ", count, "    ", f 


if __name__ == '__main__':
	traverse(sys.argv[1], print_usage)		
