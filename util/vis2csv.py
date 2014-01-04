#!/usr/bin/python

"""
This will strip the DRAMSim2 vis files into a csv file that can be used by R scripting

This script takes a single argument which is the path of the .vis file to convert
the output file will be the same filename with extension .csv
"""

from optparse import OptionParser
import re
import os
import sys

class VisFileData:
	def __init__(self, filename):
		self.fp = open(filename, "r")

	def writeCSVFile(self, output_filename):
		fp = open(output_filename, "w");
		line = 'blah'
		startCopying = False
		while line:
			line = self.fp.readline()
			if line.startswith("!!EPOCH_DATA"):
				startCopying = True;
				continue
			elif line.endswith("!!HISTOGRAM_DATA\n"):
				break
			if startCopying:
				fp.write(line)
		fp.close()


if __name__ == "__main__":
	if (len(sys.argv) < 2):
		print "missing input filename"
	filename = sys.argv[1]
	print filename
	output_filename = filename.replace(".vis", ".csv")
	print output_filename
	v = VisFileData(filename)
	v.writeCSVFile(output_filename)
