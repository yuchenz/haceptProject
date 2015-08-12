#!/usr/bin/python2.7

import sys
import codecs
import re
import pdb
from Bead import Bead

def eval(beadsDirname, autoSubtrAlignFilename):
	import os

	print "Reading in all beads ..."
	beadList = []
	for filename in os.listdir(beadsDirname):
		print filename,
		beadList.extend(Bead.loadData(os.path.join(beadsDirname, filename)))
	
	print "\nComputing p, r, and f ..."
	autoFBlocks = codecs.open(autoSubtrAlignFilename, 'r', 'utf-8').read().split('\n\n')[:-1]

	assert len(autoFBlocks) == len(beadList), \
			'number of auto tree pairs doesn\'t match number of gold beads!!!\n # auto == %d, # gold == %d\n' \
			% (len(autoFBlocks), len(beadList))
	
	truePositive = 0
	autoPositive = 0
	correctPositive = 0
	for i, block in enumerate(autoFBlocks):
		autoTuples = set([tuple([int(item) for item in line.strip()[1:-1].split(',')]) for line in block.split('\n')[1:]])
		correctTuples = set(beadList[i].subtreeAlignment)

		truePositive += len(correctTuples.intersection(autoTuples))
		autoPositive += len(autoTuples)
		correctPositive += len(correctTuples)
	
	print "\n\ntruePositive = %d" % truePositive
	print "autoPositive = %d" % autoPositive
	print "correctPositive = %d" % correctPositive
	p = truePositive * 1.0 / autoPositive
	r = truePositive * 1.0 / correctPositive
	print "\np = %.5f" % p 
	print "r = %.5f" % r
	print "f = %.5f" % (2.0 * p * r / (p + r))


if __name__ == "__main__":
	eval(sys.argv[1], sys.argv[2])
