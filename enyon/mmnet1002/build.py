#! /usr/bin/python

import sys
import os
import subprocess
import tempfile
import shutil

# Variables setup
currentdir = os.path.dirname(os.path.realpath(__file__))
srcdir = os.path.join(currentdir, '..', '..')
workspacedir = os.path.join(srcdir, '..')
distdir = os.path.join(currentdir, 'bin')
objdir = os.path.join(currentdir, 'obj')

# Environment setup
os.environ['PATH'] += ':{}/enyonsdk/linux/arm-2013.05/bin'.format(workspacedir)

def usage():
	print 'Usage: {} [build (default) | clean | rebuild | commit]'.format(sys.argv[0])

def system(command):
	status = subprocess.call(command, shell = True)
	if status != 0:
		raise Exception('Command error: "{}"'.format(command))

def prepare():
	os.chdir(srcdir)

def clean():
	print 'Cleaning...'
	system('make mrproper')
	print 'done.'

def callmake(revision, target = None):
	command = 'make -j8 CROSS_COMPILE=arm-none-linux-gnueabi- O={}'.format(objdir)
	if target:
		command += ' ' + target
	system(command)
	print command

def getrevision():
	# Read commit sha
	proc = subprocess.Popen("git log -1 --format='%h'", stdout = subprocess.PIPE, shell = True)
	sha = proc.communicate()[0].strip()
	if proc.returncode != 0:
		raise Exception(sha)

	# Read branch name
	proc = subprocess.Popen('git rev-parse --abbrev-ref HEAD', stdout = subprocess.PIPE, shell = True)
	branch = proc.communicate()[0].strip()
	if proc.returncode != 0:
		raise Exception(sha)
	
	return '{1}[{0}]'.format(branch.replace('/', '_'), sha)

def build():
	print 'Building...'
	revision = getrevision()
	callmake(revision, 'mmnet1002_debug_config')
	callmake(revision)

	# Clean distdir
	try:
		shutil.rmtree(distdir)
	except:
	    pass
	os.mkdir(distdir)

	# Create env file
	system('{}/tools/mkenvimage -s 0x00040000 -o {}/uboot-env.bin {}/env.txt'.format(objdir, distdir, currentdir))

	# Copy images
	shutil.move(os.path.join(objdir, 'u-boot.bin'), os.path.join(distdir, 'uboot.bin'))

	print 'done.'

def commit():
	system('git add {}'.format(distdir))
	revision = getrevision()
	system('git commit -a -m "Binaries updated: {}"'.format(revision))

if len(sys.argv) > 2:
	usage()
	exit(1)
elif len(sys.argv) == 1:
	command = 'build'
else:
	command = sys.argv[1]

if command == 'clean':
	prepare()
	clean()
elif command == 'build':
	prepare()
	build()
elif command == 'rebuild':
	prepare()
	clean()
	build()
elif command == "commit":
	prepare()
	commit()
else:
	usage()
	exit(1)
