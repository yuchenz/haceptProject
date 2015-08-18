#!/usr/bin/python2.7

import sys, os
import codecs
import re
import pdb
from Bead import Bead

def evaluate(beadsDirname, alignedSntFrameList):

	print "Reading in all beads ..."
	beadList = []
	for filename in os.listdir(beadsDirname):
		print filename,
		beadList.extend(Bead.loadData(os.path.join(beadsDirname, filename)))
	
	print "\nComputing p, r, and f ..."

	assert len(alignedSntFrameList) == len(beadList), \
			'number of auto tree pairs doesn\'t match number of gold beads!!!\n # auto == %d, # gold == %d\n' \
			% (len(autoFBlocks), len(beadList))
	
	truePositive = 0
	autoPositive = 0
	correctPositive = 0
	for i, sntFrame in enumerate(alignedSntFrameList):
		if sntFrame == None:
			autoTuples = set([])
		else:
			autoTuples = set([frame.subtreeAlignment_waMatrixPos for frame in sntFrame.frameList])
		correctTuples = set(beadList[i].subtreeAlignment)

		truePositive += len(correctTuples.intersection(autoTuples))
		autoPositive += len(autoTuples)
		correctPositive += len(correctTuples)
	
	print "\ntruePositive = %d" % truePositive
	print "autoPositive = %d" % autoPositive
	print "correctPositive = %d" % correctPositive
	p = truePositive * 1.0 / autoPositive
	r = truePositive * 1.0 / correctPositive
	print "\np = %.5f" % p 
	print "r = %.5f" % r
	print "f = %.5f" % (2.0 * p * r / (p + r))


if __name__ == "__main__":
	pass
