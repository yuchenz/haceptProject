#!/usr/bin/python2.7

import sys, os
import time
import codecs
import nltk
import multiprocessing as mp
import subprocess
from Bead2 import Bead2
from feat import features
from util import oneline2waMatrix
from util import oneline2subaList

def make(srcSnt, tgtSnt, srcTree, tgtTree, wa, gsuba, base):
	f = codecs.open('/dev/shm/subaFeatEx.' + str(base), 'w', 'utf-8')
	#f = codecs.open('/dev/shm/koala.suba', 'w', 'utf-8')
	sentID = base
	for i in xrange(len(srcSnt)):
		#print wa[i], srcSnt[i], tgtSnt[i]
		if i % 1000 == 0: print >> sys.stderr, i, 
		bead = Bead2(nltk.ParentedTree(srcTree[i]), nltk.ParentedTree(tgtTree[i]), \
				oneline2waMatrix(wa[i], len(srcSnt[i].split()), len(tgtSnt[i].split())), oneline2subaList(gsuba[i]))

		for suba in bead.otherSuba:
			example = (features(bead, suba), False, str(sentID) + '--' + suba.__str__())   # add negative training examples
			f.write('ID' + example[2] + '\t' +str(example[1]) + '\t' + '\t'.join(example[0]) + '\n')
			#f.write(suba.__str__()+' ')
		for suba in bead.goldSuba:
			example = (features(bead, suba), True, str(sentID) + '--' + suba.__str__())    # add positive training examples
			f.write('ID' + example[2] + '\t' +str(example[1]) + '\t' + '\t'.join(example[0]) + '\n')
			#f.write(suba.__str__()+' ')
		#f.write('\n')
		sentID += 1
	f.close()

def makeData(srcF, tgtF, srcTF, tgtTF, waF, gsubaF, numProc):
	srcSnt = codecs.open(srcF, 'r', 'utf-8').readlines()
	print len(srcSnt)
	tgtSnt = codecs.open(tgtF, 'r', 'utf-8').readlines()
	print len(srcSnt), len(tgtSnt)
	srcTree = codecs.open(srcTF, 'r', 'utf-8').readlines()
	print len(srcSnt), len(tgtSnt), len(srcTree)
	tgtTree = codecs.open(tgtTF, 'r', 'utf-8').readlines()
	print len(srcSnt), len(tgtSnt), len(srcTree), len(tgtTree)
	wa = codecs.open(waF, 'r', 'utf-8').readlines()
	print len(srcSnt), len(tgtSnt), len(srcTree), len(tgtTree), len(wa)
	if gsubaF != "None": gsuba = codecs.open(gsubaF, 'r', 'utf-8').readlines()
	else: gsuba = ["" for line in srcSnt]
	print len(srcSnt), len(tgtSnt), len(srcTree), len(tgtTree), len(wa), len(gsuba)

	pool = mp.Pool(processes = numProc)
	base = len(srcSnt) / (numProc - 1)
	tmp = []
	for i in xrange(1, numProc + 1):
		start = base * (i - 1)
		end = base * i if i < numProc else len(srcSnt)
		tmp.append(pool.apply_async(make, args = (srcSnt[start:end], tgtSnt[start:end], srcTree[start:end], tgtTree[start:end], wa[start:end], gsuba[start:end], start)))
	
	for t in tmp:
		ans = t.get()
	
	subprocess.call("touch /dev/shm/subaFeatEx.all", shell = True)
	for i in xrange(1, numProc + 1):
		start = base * (i - 1)
		subprocess.call("cat /dev/shm/subaFeatEx." + str(start) + " >> /dev/shm/subaFeatEx.all", shell = True)
	
if __name__ == "__main__":
	print sys.argv
	srcF, tgtF, srcTF, tgtTF, waF, gsubaF = sys.argv[1:7]
	outF = sys.argv[7]
	if len(sys.argv) == 9: numProc = int(sys.argv[8])
	else: numProc = 24
	print >> sys.stderr, len(sys.argv), numProc, "processes"
	makeData(srcF, tgtF, srcTF, tgtTF, waF, gsubaF, numProc)

	subprocess.call("mv /dev/shm/subaFeatEx.all " + outF, shell = True)

