#!/usr/bin/python2.7

import sys
import os
import codecs
import random
from Bead import Bead
import util

def compileData(dirname, output):
	"""
	Compile hacept raw data in separated files in hacept_raw_data/ into 
		- hacept.ch(en), containing word separated sentences
		- hacept.ch(en).gps, containing gold parse trees
		- hacept.wa, containing gold word alignment
		- hacept.suba, comtaining gold subtree alignment

	:type dirname: str
	:param dirname: the directory that contains the hacept raw data

	:type output: str
	:param output: the output file stem, i.e. the source language output file is "output".ch and target language is "output".en

	"""

	chSntList = []
	enSntList = []
	waList = []
	chGtrList = []
	enGtrList = []
	subaList = []
	for filename in os.listdir(dirname):
		filename = os.path.join(dirname, filename)
		print filename
		beadList = Bead.loadData(filename)
		for bead in beadList:
			chSntList.append(' '.join(bead.srcTree.leaves()))
			enSntList.append(' '.join(bead.tgtTree.leaves()))
			chGtrList.append(' '.join(bead.srcTree.pprint().split()))
			enGtrList.append(' '.join(bead.tgtTree.pprint().split()))
			waList.append(util.waMatrix2oneline(bead.wordAlignment))
			subaList.append(' '.join([str(suba) for suba in bead.subtreeAlignment]))

	chF = codecs.open(output+'.ch', 'w', 'utf-8')
	enF = codecs.open(output+'.en', 'w', 'utf-8')
	chGpsF = codecs.open(output+'.ch.gps', 'w', 'utf-8')
	enGpsF = codecs.open(output+'.en.gps', 'w', 'utf-8')
	waF = codecs.open(output+'.wa', 'w', 'utf-8')
	subaF = codecs.open(output+'.suba', 'w', 'utf-8')

	for i, enSnt in enumerate(enSntList):
		chF.write(chSntList[i]+'\n')
		enF.write(enSnt+'\n')
		chGpsF.write(chGtrList[i]+'\n')
		enGpsF.write(enGtrList[i]+'\n')
		waF.write(waList[i]+'\n')
		subaF.write(subaList[i]+'\n')

	chF.close(); enF.close(); chGpsF.close(); enGpsF.close(); waF.close(); subaF.close()

if __name__ == "__main__":
	compileData(sys.argv[1], sys.argv[2])
