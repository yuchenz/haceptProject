#!/usr/bin/python2.7

import sys, os
import codecs
import nltk
from Bead2 import Bead2
from feat import features
from util import oneline2waMatrix
from util import oneline2subaList

def makeData(srcF, tgtF, srcTF, tgtTF, waF, gsubaF):
	beadList = []
	srcSnt = codecs.open(srcF, 'r', 'utf-8').readlines()
	tgtSnt = codecs.open(tgtF, 'r', 'utf-8').readlines()
	srcTree = codecs.open(srcTF, 'r', 'utf-8').readlines()
	tgtTree = codecs.open(tgtTF, 'r', 'utf-8').readlines()
	wa = codecs.open(waF, 'r', 'utf-8').readlines()
	gsuba = codecs.open(gsubaF, 'r', 'utf-8').readlines()

	for i in xrange(len(srcSnt)):
		beadList.append(Bead2(nltk.ParentedTree(srcTree[i]), nltk.ParentedTree(tgtTree[i]), \
				oneline2waMatrix(wa[i], len(srcSnt[i].split()), len(tgtSnt[i].split())), oneline2subaList(gsuba[i])))

	trainExamples = []
	f = codecs.open('koala.suba', 'w', 'utf-8')
	sentID = 0
	for bead in beadList:
		for suba in bead.otherSuba:
			trainExamples.append((features(bead, suba), False, str(sentID) + '--' + suba.__str__()))   # add negative training examples
			f.write(suba.__str__()+' ')
		for suba in bead.goldSuba:
			trainExamples.append((features(bead, suba), True, str(sentID) + '--' + suba.__str__()))    # add positive training examples
			f.write(suba.__str__()+' ')
		f.write('\n')
		sentID += 1
	
	return trainExamples

	
if __name__ == "__main__":
	srcF, tgtF, srcTF, tgtTF, waF, gsubaF = sys.argv[1:7]
	exampleList = makeData(srcF, tgtF, srcTF, tgtTF, waF, gsubaF)

	outF = sys.argv[7]
	f = codecs.open(outF, 'w', 'utf-8')
	for i, example in enumerate(exampleList):
		f.write('ID' + example[2] + '\t' +str(example[1]) + '\t' + '\t'.join(example[0]) + '\n')
	f.close()
