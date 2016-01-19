#!/usr/bin/python2.7

from Frame import Frame, SntFrame, loadDataParallelWrapper
import sys, pdb, os

def topAlign(frame, srcTr, tgtTr):
	"""
	Return a subtree alignment for a given frame.

	:type frame: Frame
	:param frame: a frame in a tree pair.

	:type srcTr: nltk.ParentedTree
	:param srcTr: source tree.

	:type tgtTr: nltk.ParentedTree
	:param tgtTr: target tree.

	:rtype: 2-tuple
	:rvalue: (src subtree treeposition, tgt subtree treeposition) 

	"""
	return [(sorted(frame.srcList)[0], sorted(frame.tgtList)[0])]

def bottomAlign(frame, srcTr, tgtTr):
	"""
	Return a subtree alignment for a given frame.

	:type frame: Frame
	:param frame: a frame in a tree pair.

	:type srcTr: nltk.ParentedTree
	:param srcTr: source tree.

	:type tgtTr: nltk.ParentedTree
	:param tgtTr: target tree.

	:rtype: 2-tuple
	:rvalue: (src subtree treeposition, tgt subtree treeposition) 

	"""
	return [(sorted(frame.srcList)[-1], sorted(frame.tgtList)[-1])]

def allAlign(frame, srcTr, tgtTr):
	result = []
	for sf in frame.srcList:
		for tf in frame.tgtList:
			result.append((sf, tf))
	return result

alignFuncMap = {'top' : topAlign, 'bottom' : bottomAlign, 'all' : allAlign}

def align(srcTreeFilename, tgtTreeFilename, waFilename, alignFunc, numProc, ruleExFlag, wordRulesFlag, minMemFlag, verbose, extensiveRulesFlag, fractionalCountFlag):
	sntFrameList = loadDataParallelWrapper(srcTreeFilename, tgtTreeFilename, waFilename, numProc, alignFuncMap[alignFunc], ruleExFlag, wordRulesFlag, minMemFlag, verbose, extensiveRulesFlag, fractionalCountFlag)
	return sntFrameList

if __name__ == '__main__':
	sntFrameList = align(sys.argv[1], sys.argv[2], sys.argv[3])

	for i, sntFrame in enumerate(sntFrameList):
		print "sentence pair #", i, "="*30
		print sntFrame
		print

