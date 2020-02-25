#!/usr/bin/env python

import string, sys, os
import math
import time
import subprocess
import threading
from Tkinter import *
from patches import *
import glob

master = Tk()
G_OPTIONS = {}
G_OPTIONS_sortedKeys = []
semaphore = threading.Semaphore(4)


def ToForwardSlash(path):
	while("\\" in path):
		path = string.replace(path, "\\", "/")
	return path

def InitOptions():
	global G_OPTIONS

	G_OPTIONS["smode"] = (IntVar(), ["black", "clamp", "periodic"])
	G_OPTIONS["tmode"] = (IntVar(), ["black", "clamp", "periodic"])
	G_OPTIONS["colorspace"] = (IntVar(), ["linear", "srgb"])
	G_OPTIONS["nomipmap"] = (IntVar(), ["Off", "On"])
	G_OPTIONS["multi_files"] = (IntVar(), ["Selected", "UV_Patches", "EntireDir", "Sequence"])
	G_OPTIONS["envlatl"] = (IntVar(), ["Off", "On"])

	G_OPTIONS["smode"][0].set(2)
	G_OPTIONS["tmode"][0].set(2)

	G_OPTIONS["keep_orig_extension"] = (IntVar(), ["Off", "On"])
	G_OPTIONS["keep_orig_extension"][0].set(1)

	global G_OPTIONS_sortedKeys
	G_OPTIONS_sortedKeys.append( "multi_files" )
	G_OPTIONS_sortedKeys.append( "keep_orig_extension" )
	G_OPTIONS_sortedKeys.append( "colorspace" )
	G_OPTIONS_sortedKeys.append( "envlatl" )
	G_OPTIONS_sortedKeys.append( "nomipmap" )
	G_OPTIONS_sortedKeys.append( "smode" )
	G_OPTIONS_sortedKeys.append( "tmode" )


def AssembleOptionsStr(i_fileList):
	global G_OPTIONS
	optStr = ""
	for O in G_OPTIONS.keys():
		if(O == "multi_files"):continue
		elif(O == "keep_orig_extension"):continue
		elif(O == "nomipmap"):
			if(G_OPTIONS[O][0].get()==1):
				optStr += " -" + O + " "
		elif(O == "envlatl"):
			if(G_OPTIONS[O][0].get()==1):
				optStr += " -" + O + " "
		else:
			optStr += " -" + O + " " + G_OPTIONS[O][1][G_OPTIONS[O][0].get()] + " "

	if len(i_fileList) == 1:
		optStr += " -progress "
	return optStr



def DoItButtonCB():
	global G_OPTIONS
	sequence_mode = G_OPTIONS["multi_files"][0].get()


	fileList = []
	if sequence_mode==0:
		#fileList.append( sys.argv[1] )
		fileList.extend( sys.argv[1:] )
	elif sequence_mode==2:#entire dir
		fileList = GetEntireDir(sys.argv[1])
	else:
		(fileList, mode) = GetFileListToProcess( sys.argv[1] )
	fileList = ValidateFileList(fileList)

	optionsStr = " -preview 512 " + AssembleOptionsStr(fileList)
	print "\n", optionsStr, "\n"

	RunCommandParallel2("tdlmake", optionsStr, fileList)
	#print "DONE" # !! it will print BEFORE actually being done ...
	sys.exit()


def TestWin():
	global G_OPTIONS

	print sys.argv[1], "\n"
	if string.lower(os.path.splitext(sys.argv[1])[1]) not in [".exr", ".hdr"]:
		G_OPTIONS["colorspace"][0].set(1)

	if string.lower(os.path.splitext(sys.argv[1])[1])  == ".hdr":
		G_OPTIONS["envlatl"][0].set(1)

	grid_row = 0
	for O in G_OPTIONS_sortedKeys:
		grid_col = 0
		Label(master, text=O).grid(row = grid_row, column = grid_col)
		grid_col += 1
		val = 0
		for LABEL in G_OPTIONS[O][1]:
			Radiobutton(master, text=LABEL, variable=G_OPTIONS[O][0], value=val).grid(row = grid_row, column = grid_col)
			val += 1
			grid_col += 1
		grid_row += 1

	(seq, mode) = GetFileListToProcess( sys.argv[1] )
	if( len(seq) > 1 ):
		G_OPTIONS["multi_files"][0].set(mode)
		print "Found multiple files:"
		print string.join(map(os.path.basename, seq), "\n")

	Button(master, text="OK", command=DoItButtonCB).grid(row = grid_row, column = grid_col)
	master.mainloop()

def ValidateFileList(i_files):
	res = i_files[:]
	res = filter(lambda x: os.path.isfile(x), res)
	res = filter(lambda x: string.lower(x)[-4:] != ".tdl", res)
	res = filter(lambda x: string.lower(x)[-3:] != ".tx", res)
	return res

def GetEntireDir(i_file):
	(path, file) = os.path.split(i_file)
	files = os.listdir(path)
	files = map(lambda x: os.path.join(path, x), files)
	files = sorted(files)
	return files

def GetSequenceFromFile(i_file):
	template =  r'(.+\.{1})([0-9]{4})(\.{1}.+)'
	if((re.match(template, i_file) != None)):
		searchObj = re.search( template, i_file)
		elements = searchObj.groups()
		(base, frame, ext) = ( string.join(elements[:-2]), elements[-2], elements[-1] )
		files = glob.glob(base + "*" + ext)
		files = map(lambda x: os.path.join(path, x), files)
		return sorted(files)
	else:
		return []


def GetFileListToProcess(i_file):
	files = []
	(path, fil)= os.path.split(i_file)

	if(IsMariPatch(fil)):
		files = os.listdir(path)
		files = FilterMariPatches(fil, files)
		files = map(lambda x: os.path.join(path, x), files)
		if(len(files)):return (files, 1)

	if(IsMudboxPatch(fil)):
		files = os.listdir(path)
		files = FilterMudboxPatches(fil, files)
		files = map(lambda x: os.path.join(path, x), files)
		if(len(files)):return (files, 1)

	files = GetSequenceFromFile(i_file)
	if(len(files)):
		return (files, 3)

	files = [i_file]
	return (files, 0)


def RunCommandParallel2(cmdString, optionsStr, parameters):
	#print (cmdString, optionsStr, parameters)
	global G_OPTIONS

	processes = set()
	max_processes = 8;
	for par in parameters:
		# add colorspace to fname
		outFile = par
		if 'srgb' in optionsStr:
			outFile += '.sRGB'
		else:
			outFile += '.ln'
		outFile += '.tdl'
		#
		print cmdString, optionsStr, par, outFile
		#continue
		#outFile = par + ".tdl"
		if( G_OPTIONS["keep_orig_extension"][0].get() == 0 ):
			fileName, fileExtension = os.path.splitext(par)
			outFile = fileName + ".tdl"

		#processes.add(subprocess.Popen( cmdString + " " + optionsStr + " " + par + " " + outFile ))
		processes.add(subprocess.Popen( cmdString + " " + optionsStr + " \"" + par + "\" \"" + outFile + "\"" ))
		while len(processes) >= max_processes:
			time.sleep(3)
			diffP = [p for p in processes if p.poll() is not None]
			processes.difference_update(diffP)


def RunCommandSequential(cmdString, parameters):
	for p in parameters:
		cmd = cmdString + " " + p + " " + p + ".tdl"
		print cmd
		os.system(cmd)


if __name__ == "__main__":
	print sys.argv
	InitOptions()
	TestWin()
	#print string.join( GetSequenceFromFile(sys.argv[1]), "\n")