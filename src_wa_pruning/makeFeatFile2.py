#!/usr/bin/python2.7

import codecs
import sys
from util import Example, loadWordPairDict, loadFuncWordDict
from feat import extractFeat

def make(chF, enF, gwaF, waF, outF):
	chSentL = [line.split() for line in codecs.open(chF, 'r', 'utf-8').readlines()]
	enSentL = [line.split() for line in codecs.open(enF, 'r', 'utf-8').readlines()]
	gwaL = [line.split() for line in open(gwaF).readlines()]
	waL = [line.split() for line in open(waF).readlines()]

	print "len of chSentL, enSentL, gwaL, waL: ", len(chSentL), len(enSentL), len(gwaL), len(waL)

	fwD = loadFuncWordDict("ch_funcWordL.txt")
	wpD = loadWordPairDict("hacept_train.dict")

	expList = []
	for k, chSent in enumerate(chSentL):
		if k % 100 == 0: print k,
		enSent = enSentL[k]
		waSent = waL[k]
		gwaSent = gwaL[k]

		for wa in waSent:
			ID = 'ID' + str(k) + '--' + wa
			label = 'False'
			if wa in gwaSent:
				label = 'True'
			exp = Example(ID, label)
			i, j = int(wa.split('-')[0]), int(wa.split('-')[1])
			exp.featList = extractFeat(i, j, chSent, enSent, wpD, fwD)
			expList.append(exp)
	
	outf = codecs.open(outF, 'w', 'utf-8')
	for exp in expList:
		outf.write(exp.__str__())
	outf.close()

if __name__ == "__main__":
	chF = sys.argv[1]
	enF = sys.argv[2]
	gwaF = sys.argv[3]
	waF = sys.argv[4]
	outF = sys.argv[5]

	make(chF, enF, gwaF, waF, outF)
