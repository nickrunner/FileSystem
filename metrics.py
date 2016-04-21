#!/usr/bin/python

import os, sys, time
import datetime
from stat import *

tb=0
x=0
directories = []
files = []
new_list = []
units = ['B', 'K', 'M', 'G', 'T', 'P']
timebase = {'Seconds': 1, 'Minutes': 60, 'Hours': 3600, 'Days': 86400, 'Months': 2592000, 'Years': 31557600}
block_size = 0

if os.name == 'posix':
	block_size = 4096
elif os.name == 'nt':
	block_size = 0
	

def readable(bytes):
	b = float(bytes)
	if b == 0: 
		return '0B'
	i = 0
	while b >= 1024:
		i = i+1
		b /= 1024
	if b < 10:
		f = ('%.1f' % b)
	else:
		f = ('%.0f' % b)
	return '%s%s' % (f, units[i])


def traverse(path, callback):

	dirs = os.listdir(path)

	file_count = 0
	dir_size = 0
	age = 0
	
	for f in dirs:

		pathname = os.path.join(path, f)
		mode = os.stat(pathname).st_mode

		#check if it's a directory
		if S_ISDIR(mode):

			#initialize directory size to block size
			dir_size += block_size

			#Find directory age
			modified = os.stat(pathname).st_mtime

			#Recurse
			tmp = traverse(pathname, grab_data)
			dir_size = tmp[0]
			file_count = tmp[1]

			callback(pathname, file_count, dir_size, age)

		elif S_ISREG(mode):

			#Count files
			file_count += 1;

			#Add file size to directory size
			file_size = os.stat(pathname).st_size
			dir_size += file_size

			#Get age metrics
			modified = os.stat(pathname).st_mtime
			accessed = os.stat(pathname).st_atime
			changed = os.stat(pathname).st_ctime

			#Extract file name and type
			file_name, file_type = os.path.splitext(pathname)

			files.append(
				{
				'name': file_name, 
				'extension': file_type, 
				'size': file_size, 
				'modified': modified,
				'accessed': accessed,
				'change': changed,
				})
			
		else:
			print 'Unknown File Type'

	return [dir_size, file_count]

def grab_data(f, count, size, age):
	directories.append(
		{'size': size, 
		'count': count, 
		'file': f, 
		'age': age})	

def sort_output(key):
	return sorted(directories, key=lambda k: k[key])

def plot_data():
	import matplotlib.pyplot as plt 
	from collections import Counter
	import numpy as np
	import matplotlib.dates as mdates

	#Plot 1: Histogram of file types
	extensions = []
	count = 0
	for f in files:
		if not f['extension']: 
			continue 	
		extensions.append(f['extension'])
		count += 1
	counter = Counter(extensions)
	ext_names = counter.keys()
	ext_counts = counter.values() 
	for ext in ext_names:
		if count > 10 and counter[ext] < 2:
			del(counter[ext])
		if count > 20 and counter[ext] < 4:
			del(counter[ext])
		if count > 40 and counter[ext] < 8:
			del(counter[ext])
		if count > 80 and counter[ext] < 16:
			del(counter[ext])
		if count > 160 and counter[ext] < 32:
			del(counter[ext])
		if count > 320 and counter[ext] < 64:
			del(counter[ext])
	indexes = np.arange(len(counter.values()))
	width = 0.5
	plt.bar(indexes, counter.values(), width)
	plt.xticks(indexes + width * 0.5, counter.keys(), rotation=75)
	plt.xlabel('File Types')
	plt.ylabel('Occurences')
	plt.title('Most Common File Types')
	plt.show()

	#Plot 2: Sub-directory pie chart
	sizes = []
	labels = []
	colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'gray', 'white']
	total_size = 0
	#Scale Output
	for d in directories:
		total_size += d['size']
	avg_size = total_size/len(directories)
	min_size = 0
	if len(directories) > 10:
		min_size = avg_size/2
	if len(directories) > 20:
		min_size = avg_size
	if len(directories) > 40:
		min_size = avg_size * 2
	if len(directories) > 80:
		min_size = avg_size*3
	if len(directories) > 160:
		min_size = avg_size*4
	if len(directories) > 320:
		min_size = avg_size*8
	if len(directories) > 640:
		min_size = avg_size*16
	for d in directories:
		if d['size'] > min_size:
			sizes.append(d['size'])
			labels.append(d['file'])
	plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=75, colors=colors)
	plt.title('Proportion of Useage for Directories >' + readable(min_size))
	plt.show()
		
	#Plot 3: Directory Useage over time
	mod_ages = []
	change_ages = []
	acc_ages = []
	sys.stdout.flush()
	print 'Enter Time Base (Seconds, Minutes, Hours, Days, Months, Years)'
	sys.stdout.flush()
	tb = raw_input('Enter Duration ') 
	sys.stdout.flush()
	mx = input('Thank you')
	sys.stdout.flush()
	#bins = raw_input ("Enter number of data points: ")
	#x = input("Enter time period: ")
	t = time.time()/timebase[tb]
	for f in files:
		value = t-f['modified']/timebase[tb]
		if value * timebase[tb] < 100000000:
			mod_ages.append(value) 
		value = t-f['accessed']/timebase[tb]
		if value * timebase[tb] < 100000000:
			acc_ages.append(value) 
		value = t-f['change']/timebase[tb]
		if value * timebase[tb] < 100000000:
			change_ages.append(value) 

	x, binEdges=np.histogram(acc_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	line_1, = plt.plot(bincenters,x,'-',label = 'Accessed')

	y, binEdges=np.histogram(mod_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	line_2, = plt.plot(bincenters,y,'-', label = 'Modified')

	z, binEdges=np.histogram(change_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	line_3, = plt.plot(bincenters,z,'-', label = 'Changed')
	if tb == 'Months':
		plt.ylim(0, 1000)
	if tb == 'Days':
		plt.ylim(0, 80)
	plt.xlabel(tb + ' since ' + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time())))
	plt.ylabel('Useage')
	plt.title('Directory Useage Over Time')
	plt.legend(handles=[line_1, line_2, line_3])
	plt.gca().invert_xaxis()
	plt.show()


def print_usage(h_readable):
	total_size = 0
	avg_size = 0	
	for directory in new_list:
		if h_readable == 'true':
			#print readable
			print  '{0:6} {1:4d} {2:50}'.format(readable(directory['size']), directory['count'], directory['file'])
		else: 
			#print standard
			print  '{0:6} {1:4d} {2:50}'.format(directory['size'], directory['count'], directory['file'])
		total_size += directory['size']
	avg_size = total_size/len(directories)	
	print ' '
	print 'Average Directory Size: ', readable(avg_size)
	total_size = 0
	for f in files:
		total_size += f['size']
	avg_size = total_size/len(files)
	print 'Average File Size: ', readable(avg_size)	

if __name__ == '__main__':
	print ''
	
	#default path is working directory
	path = './'

	#use argument 1 if a path is specified
	if len(sys.argv) != 1:
		if sys.argv[1].find('-') == -1:		
			path = sys.argv[1]

	traverse(path, grab_data)

	h_readable = 'false'
	plots = 'false'

	new_list = directories

	for arg in sys.argv:

		#Possible arguments

		# -ss = sort by directory size
		if arg == '-ss':
			new_list = sort_output('size')

		#-sp = sort by pathname alphabetically
		elif arg == '-sp':
			new_list = sort_output('file')

		#-sf = sort by file count
		elif arg == '-sf':
			new_list = sort_output('count')

		#-h = make block size human readable
		elif arg == '-h':
			h_readable = 'true'

		#-plot = show all plots
		elif arg == '-plot':
			plots = 'true'

	print_usage(h_readable)	
	sys.stdout.flush()
	print ' '
	sys.stdout.flush()
	if plots == 'true':
		plot_data()
	

