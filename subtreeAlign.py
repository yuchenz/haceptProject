#!/usr/bin/python2.7

from Frame import Frame, SntFrame
import sys, pdb

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
	return (frame.srcList[0], frame.tgtList[0])

def align(srcTreeFilename, tgtTreeFilename, waFilename):
	sntFrameList = SntFrame.loadData(srcTreeFilename, tgtTreeFilename, waFilename)

	for sntFrame in sntFrameList:
		sntFrame.subtreeAlign(topAlign)

	return sntFrameList


if __name__ == '__main__':
	sntFrameList = align(sys.argv[1], sys.argv[2], sys.argv[3])

	for i, sntFrame in enumerate(sntFrameList):
		print "sentence pair #", i, "="*30
		print sntFrame
		print

