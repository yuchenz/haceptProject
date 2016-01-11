#!/usr/bin/python2.7

import sys, os
import codecs
import re
import pdb
from Bead import Bead
import util

def evaluate(goldSubaFile, alignedSntFrameList, softEval=False, analysis=False):
	print "\n\nComputing p, r, and f ..."

	goldSuba = [[tuple([int(d) for d in item.split(', ')]) \
			if item else tuple() \
			for item in line.strip()[1:-1].split(') (')] \
			for line in codecs.open(goldSubaFile, 'r', 'utf-8')]
	
	assert len(alignedSntFrameList) == len(goldSuba), \
			'number of auto tree pairs doesn\'t match number of gold beads!!!\n # auto == %d, # gold == %d\n' \
			% (len(alignedSntFrameList), len(goldSuba))
	
	truePositive = 0.0
	falsePositive = 0.0
	falseNegative = 0.0

	# if output for analysis
	if analysis:
		print 'outputing for comparison analysis ...'
		outf = codecs.open(os.path.join(analysis, 'analysis.cmp'), 'w', 'utf-8')

	for i, sntFrame in enumerate(alignedSntFrameList):
		if sntFrame == None:
			autoTuples = set([])
		else:
			#assert ' '.join(sntFrame.srcWordList) == ' '.join(beadList[i].srcSnt), \
			#		"ERROR!! sntFrame and bead are not matching!!!"
			autoTuples = set([suba for frame in sntFrame.frameList for suba in frame.subtreeAlignment_waMatrixPos])
			softAutoTuples = set([suba for frame in sntFrame.frameList for suba in frame.allPossibleSubtreeAlignment()])
			softAutoFrames = set([tuple([suba for suba in frame.allPossibleSubtreeAlignment()]) for frame in sntFrame.frameList]) 
		goldTuples = set(goldSuba[i])
		#pdb.set_trace()
		
		truePosSet = goldTuples.intersection(softAutoTuples) if softEval else goldTuples.intersection(autoTuples)
		falseNegSet = goldTuples.difference(softAutoTuples) if softEval else goldTuples.difference(autoTuples)
		falsePosSet = softAutoFrames.difference(set([frame for frame in softAutoFrames for tup in goldTuples if tup in frame])) \
				if softEval else autoTuples.difference(goldTuples)

		if analysis:
			tmp = '='*30+'snt'+str(i)+'='*30
			tmp = tmp.encode('utf-8')
			print >> outf, tmp
			print >> outf, 'soft_eval' if softEval else 'hard_eval'
			print >> outf, 'correct:', truePosSet 
			print >> outf, 'false positive:', falsePosSet 
			print >> outf, 'false negative:', falseNegSet
			print >> outf, '\n\n'

		truePositive += len(truePosSet)
		falsePositive += len(falsePosSet)
		falseNegative += len(falseNegSet)
	
	print "truePositive = %d" % truePositive
	print "auto = %d" % (truePositive + falsePositive)
	print "gold = %d" % (truePositive + falseNegative) 
	p = truePositive / (truePositive + falsePositive) 
	r = truePositive / (truePositive + falseNegative) 
	print "\np = %.5f" % p 
	print "r = %.5f" % r
	print "f = %.5f\n" % (2 * p * r / (p + r))

if __name__ == "__main__":
	pass
