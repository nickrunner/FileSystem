#!/usr/bin/python
from mpl_toolkits.mplot3d import Axes3D
import os, sys, time
import matplotlib.pyplot as plt 
from collections import Counter
import numpy as np
from stat import *

tb=0
x=0
directories = []
files = []
new_list = []
units = ['B', 'K', 'M', 'G', 'T', 'P']
timebase = {'seconds': 1, 'minutes': 60, 'hours': 3600, 'days': 86400, 'months': 2592000, 'years': 31557600}
block_size = 0

if os.name == 'posix':
	block_size = 4096
elif os.name == 'nt':
	block_size = 0
	

def readable(bytes):
	if bytes == 0: 
		return '0B'
	i = 0
	while bytes >= 1024:
		i = i+1
		bytes /= 1024
	if bytes < 10:
		f = ('%.1f' % bytes)
	else:
		f = ('%.0f' % bytes)
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
			dir_size = block_size

			#Find directory age
			modified = os.stat(pathname).st_mtime

			#Recurse
			dir_size += traverse(pathname, grab_data)

			#Add directory to list
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

	return dir_size

def grab_data(f, count, size, age):
	directories.append(
		{'size': size, 
		'count': count, 
		'file': f, 
		'age': age})	

def sort_output(key):
	return 

def plot_data():
	
	#Plot 1: Histogram of file types
	extensions = []
	for f in files:
		if not f['extension']: 
			continue 	
		extensions.append(f['extension'])
	counter = Counter(extensions)
	ext_names = counter.keys()
	ext_counts = counter.values()
	indexes = np.arange(len(ext_counts))
	width = 0.5
	plt.bar(indexes, ext_counts, width)
	plt.xticks(indexes + width * 0.5, ext_names, rotation=75)
	plt.xlabel('File Types')
	plt.ylabel('Occurences')
	plt.title('Occurences of File Types')
	plt.show()

	#Plot 2: Sub-directory pie chart
	sizes = []
	labels = []
	for d in directories:
		if d['size'] > 1000000:
			sizes.append(d['size'])
			labels.append(d['file'])
	plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=75)
	plt.title('Proportion of Useage for Directories > 1MB')
	plt.show()
		
	#Plot 3: Directory Useage over time
	mod_ages = []
	change_ages = []
	acc_ages = []
	sys.stdout.flush()
	print 'Enter Time Base '
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
		if(value * timebase[tb] < 100000000):
			mod_ages.append(value) 
		value = t-f['accessed']/timebase[tb]
		if(value * timebase[tb] < 100000000):
			acc_ages.append(value) 
		value = t-f['change']/timebase[tb]
		if(value * timebase[tb] < 100000000):
			change_ages.append(value) 

	x, binEdges=np.histogram(acc_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	plt.plot(bincenters,x,'-')

	y, binEdges=np.histogram(mod_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	plt.plot(bincenters,y,'-')

	z, binEdges=np.histogram(change_ages, bins=mx, range=(0,mx))
	bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
	plt.plot(bincenters,z,'-')
	
	plt.gca().invert_xaxis()
	plt.show()

	'''
	#Plot 4 File Ages in 3D
	mod_ages[:] = []
	change_ages[:] = []
	acc_ages[:] = []
	for f in files:
		value = t-f['modified']/timebase[tb]
		mod_ages.append(value) 
		value = t-f['accessed']/timebase[tb]
		acc_ages.append(value) 
		value = t-f['change']/timebase[tb]
		change_ages.append(value) 
	fig = plt.figure()
	ax = fig.gca(projection='3d')
	X = mod_ages
	Y = change_ages
	Z = acc_ages
	X, Y = np.meshgrid(X,Y)
	surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
        linewidth=0, antialiased=False)
	ax.zaxis.set_major_locator(LinearLocator(10))
	ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

	fig.colorbar(surf, shrink=0.5, aspect=5)

	plt.show()
	'''



def print_usage(h_readable):	
	for directory in new_list:
		if h_readable == 'true':
			#print readable
			print  '{0:6} {1:4d} {2:50}'.format(readable(directory['size']), directory['count'], directory['file'])
		else: 
			#print standard
			print  '{0:6} {1:4d} {2:50}'.format(directory['size'], directory['count'], directory['file'])

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

	print_usage(h_readable)	
	sys.stdout.flush()
	print 'test'
	sys.stdout.flush()
	plot_data()
	

