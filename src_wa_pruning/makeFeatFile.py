#!/usr/bin/python2.7

import sys, codecs
import pdb
import multiprocessing as mp
import time
from feat import extractFeat
from util import Example

def extract(chSentL, enSentL, waL, baseID):
	expL = []
	for k, chSent in enumerate(chSentL):
		#print >> sys.stderr, k, 
		enSent = enSentL[k]
		waSent = waL[k]
		for i, ch in enumerate(chSent):
			for j, en in enumerate(enSent):
				ID = "ID" + str(baseID + k) + '--' + str(i) + '-' + str(j)
				label = "False"
				if str(i) + '-' + str(j) in waSent:
					label = "True"
				exp = Example(ID, label)
				exp.featList = extractFeat(i, j, chSent, enSent)
				expL.append(exp)

	return expL

def makeFeatFile(chF, enF, waF, outF, numProc):
	chSentL = [line.split() for line in codecs.open(chF, 'r', 'utf-8').readlines()]
	enSentL = [line.split() for line in codecs.open(enF, 'r', 'utf-8').readlines()]
	waL = [line.split() for line in codecs.open(waF, 'r', 'utf-8').readlines()]

	assert len(chSentL) == len(enSentL) == len(waL), \
			"len chSentL == %d, len enSentL == %d, len waL == %d" % (len(chSentL), len(enSentL), len(waL))
	
	s = time.clock()
	if numProc > 1:
		pool = mp.Pool(processes = numProc)
		tmp = []
		base = len(chSentL) / (numProc - 1)
		for i in xrange(1, numProc + 1):
			start = base * (i - 1)
			end = base * i if i < numProc else len(chSentL)
			tmp.append(pool.apply_async(extract, args=(chSentL[start:end], enSentL[start:end], waL[start:end], start)))
		
		expList = []
		for t in tmp:
			expL = t.get()
			expList.extend(expL)
	else:
		expList = extract(chSentL, enSentL, waL)

	print >> sys.stderr, "\nextraction time: %f" % (time.clock() - s)
		
	s = time.clock()
	outf = codecs.open("/dev/shm/tmp", 'w', 'utf-8')
	for exp in expList:
		outf.write(exp.__str__())
	outf.close()
	print >> sys.stderr, "outputing time: %f" % (time.clock() - s)

if __name__ == "__main__":
	chF = sys.argv[1]
	enF = sys.argv[2]
	waF = sys.argv[3]
	outF = sys.argv[4]
	numProc = int(sys.argv[5])

	makeFeatFile(chF, enF, waF, outF, numProc)
