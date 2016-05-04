#!/usr/bin/python2.7

import sys

def convert(filename, outFilename):
	sentID = 0
	result = [[]]
	for line in open(filename):
		line = line.split()
		if float(line[-3]) <= float(line[-1]): continue
		line = line[0].split('--')
		line = (int(line[0][2:]), line[1])

		if line[0] != sentID:
			result.append([])
			sentID += 1
		if line[0] == sentID:
			result[-1].append(line[1])

	'''
	lines = [line.split() for line in open(filename).readlines()]
	lines = [line[0].split('--') for line in lines if float(line[-3]) > float(line[-1])] 
	lines = [[int(line[0][2:]), line[1]] for line in lines]

	sentID = 0
	result = [[]]
	for line in lines:
		if line[0] != sentID:
			result.append([])
			sentID += 1
		if line[0] == sentID:
			result[-1].append(line[1])
	'''

	result = [' '.join(line) for line in result]
	outf = open(outFilename, 'w')
	for line in result:
		outf.write(line + '\n')
	outf.close()

if __name__ == "__main__":
	convert(sys.argv[1], sys.argv[2])
