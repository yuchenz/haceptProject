#!/usr/bin/python2.7

import sys, pdb
import re

debug_log = sys.stderr

def sntAlign(sntFrameList, sntList):
	alignedSntFrameList = []
	k = 0
	for i in xrange(len(sntList)):
		frame = sntFrameList[k]
		if frame == None:
			alignedSntFrameList.append(None)
			k += 1
			continue
		tmp1 = re.sub('@#\^%', '', ' '.join(sntList[i]).lower())
		#print >> debug_log, tmp1
		tmp1 = re.sub('sym', '', tmp1)
		tmp1 = re.sub('nnp', '', tmp1)
		tmp1 = re.sub('jj', '', tmp1)
		tmp1 = re.sub('@', '', tmp1)
		tmp2 = re.sub('@#\^%', '', ' '.join(frame.tgtWordList).lower())
		#print >> debug_log, tmp2
		tmp2 = re.sub('sym', '', tmp2)
		tmp2 = re.sub('nnp', '', tmp2)
		tmp2 = re.sub('jj', '', tmp2) 
		tmp2 = re.sub('@', '', tmp2)
		#print >> debug_log, tmp1
		#print >> debug_log, tmp2
		#print >> debug_log
		if tmp1 == tmp2: 
			alignedSntFrameList.append(frame)
			k += 1
		else:
			alignedSntFrameList.append(None)
	
	return alignedSntFrameList

if __name__ == '__main__':
	pass
