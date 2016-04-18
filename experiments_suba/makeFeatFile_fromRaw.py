#!/usr/bin/python2.7

import sys, os
import codecs
from Bead2 import Bead2
from feat import features

def makeTrainData(rawDataDir):
	beadList = []
	for filename in os.listdir(rawDataDir):
		print >> sys.stderr, filename
		beadList.extend(Bead2.loadData(os.path.join(rawDataDir, filename)))
	
	trainExamples = []
	for bead in beadList:
		for suba in bead.otherSuba:
			trainExamples.append((features(bead, suba), False))   # add negative training examples
		for suba in bead.goldSuba:
			trainExamples.append((features(bead, suba), True))    # add positive training examples
	
	return trainExamples

	
if __name__ == "__main__":
	rawDataDir = sys.argv[1]
	trainExamples = makeTrainData(rawDataDir)

	outF = sys.argv[2]
	f = codecs.open(outF, 'w', 'utf-8')
	for i, example in enumerate(trainExamples):
		f.write('ID' + str(i) + '\t' +str(example[1]) + '\t' + '\t'.join(example[0]) + '\n')
	f.close()
