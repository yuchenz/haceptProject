#!/usr/bin/python2.7

import sys, pdb
import re

debug_log = sys.stderr

def sntAlign(sntFrameList, sntList):
	alignedSntFrameList = []
	k = 0
	for i in xrange(len(sntList)):
		frame = sntFrameList[k]
		tmp1 = re.sub('@#\^%', '', ' '.join(sntList[i]))
		tmp1 = re.sub('@', '', tmp1)
		tmp1 = tmp1.lower()
		tmp2 = re.sub('JJ', '', ' '.join(frame.tgtWordList))
		tmp2 = re.sub('SYM', '', tmp2)
		tmp2 = re.sub('@', '', tmp2)
		#print >> debug_log, tmp1
		#print >> debug_log, tmp2
		if tmp1 == tmp2: 
			alignedSntFrameList.append(frame)
			k += 1
		else:
			alignedSntFrameList.append(None)
	
	return alignedSntFrameList

if __name__ == '__main__':
	pass
