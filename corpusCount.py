#!/usr/bin/python2.7

import pdb
import time 
import sys

def genDict(tupleList):
	'''
	:type tupleList: a list of 2-tuples
	:param tupleList: each tuple is (item, count), item may not be distinct

	generate a dictionary of {item: total count of item}
	'''

	dic = {}
	for tup in tupleList:
		dic[tup[0]] = dic.get(tup[0], 0) + tup[1]
	return dic

def xgram(corpus, x):
	'''
	:type corpus: a list of lists
	:param corpus: a list of sentences, each sentence is a list of words

	:type x: int
	:param x: count the number of x-grams in this corpus
	'''

	dic = {}
	for sent in corpus:
		for i in xrange(len(sent) - x + 1):
			dic[tuple(sent[i:i + x])] = dic.get(tuple(sent[i:i + x]), 0) + 1
	return dic

def corpusCount(ruleList, ruleInvList, corpusCh, corpusEn, verbose):
	print 

	s = time.clock()

	ruleList2 = [line.split('|||') for line in ruleList]
	print 'splitted ruleList2: ', time.clock() - s
	ruleList2 = [[line[0].strip().split()[:-1], line[1].strip().split()[:-1], line[2].strip(), float(line[3].strip())] \
			for line in ruleList2]
	print 'stripped ruleList2: ', time.clock() - s
	
	chCount = genDict([(tuple(line[0]), line[3]) for line in ruleList2 if '[X][X]' not in line[0]])
	print 'created chCount dictionary: ', time.clock() - s
	enCount = genDict([(tuple(line[1]), line[3]) for line in ruleList2 if '[X][X]' not in line[1]])
	print 'created enCount dictionary: ', time.clock() - s
	print

	#print "\t# total distinct ch phrases: ", len(chCount.keys())
	#print "\t# total distinct en phrases: ", len(enCount.keys())

	#chCount = {key:chCount[key] for key in chCount if '[X][X]' not in key}
	#enCount = {key:enCount[key] for key in enCount if '[X][X]' not in key}

	print "\t# distinct ch phrases w/o [X][X]: ", len(chCount.keys())
	print "\t# distinct en phrases w/o [X][X]: ", len(enCount.keys())

	chStat = genDict([(len(key), 1) for key in chCount])
	enStat = genDict([(len(key), 1) for key in enCount])

	for keyLen in chStat:
		print "\t#", keyLen, "gram in ch phrases: ", chStat[keyLen]
		xgramDict = xgram(corpusCh, keyLen)
		for key in chCount:
			if len(key) == keyLen: 
				if key not in xgramDict:
					print >> sys.stderr, "key %s not found in corpus, key frequency in the rule table: %f" % (' '.join(key), chCount[key])
					continue
				tmp = xgramDict[key] - chCount[key]
				if tmp > 0:
					ruleList.append(' '.join(key) + ' [X] ||| placeholder [X] ||| 0-0 ||| ' + \
							str(tmp) + '\n')
					ruleInvList.append('placeholder [X] ||| ' + ' '.join(key) + ' [X] ||| 0-0 ||| ' + \
							str(tmp) + '\n')

	for keyLen in enStat:
		print "\t#", keyLen, "gram in en phrases: ", enStat[keyLen]
		xgramDict = xgram(corpusEn, keyLen)
		for key in enCount:
			if len(key) == keyLen: 
				if key not in xgramDict:
					print >> sys.stderr, "key %s not found in corpus, key frequency in the rule table: %f" % (' '.join(key), enCount[key])
					continue
				tmp = xgramDict[key] - enCount[key]
				if tmp > 0:
					ruleList.append('placeholder [X] ||| ' + ' '.join(key) + ' [X] ||| 0-0 ||| ' + \
							str(tmp) + '\n')
					ruleInvList.append(' '.join(key) + ' [X] ||| placeholder [X] ||| 0-0 ||| ' + \
							str(tmp) + '\n')
	
	

