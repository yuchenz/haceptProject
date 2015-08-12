#!/usr/bin/python2.7

import sys
import re

def sntAlign(sbtrAlignFilename, sntFilename):
	sbtrAlignFileBlocks = open(sbtrAlignFilename, 'r').read().split('\n\n')
	sntList = [line.lower().strip() for line in open(sntFilename, 'r').readlines()]
	sbtrAlign = []
	k = 0
	for i in xrange(len(sntList)):
		block = sbtrAlignFileBlocks[k]
		tmp1 = re.sub('@#\^%', '', sntList[i])
		tmp1 = re.sub('@', '', tmp1)
		tmp2 = re.sub('JJ', '', ' '.join(block.split('\n')[0].split()[1:]))
		tmp2 = re.sub('SYM', '', tmp2)
		tmp2 = re.sub('@', '', tmp2)
		print tmp1
		print tmp2
		if tmp1 == tmp2: 
			sbtrAlign.append(re.sub('snt[0-9]+', 'snt'+str(i), block))
			k += 1
		else:
			sbtrAlign.append('None')

	outF = open(sbtrAlignFilename+'.sntAligned', 'w')
	for block in sbtrAlign:
		outF.write(block+'\n\n')
	outF.close()

if __name__ == '__main__':
	sntAlign(sys.argv[1], sys.argv[2])
