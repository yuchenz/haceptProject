#!/usr/bin/python2.7

import re

def cleanData(rawData):
	"""
	Clean raw hacept data.

	:type rawData: str
	:param rawData: raw hacept data

	"""
	rawData = re.sub(r'R-LRB- \(', r'R-LRB- -LRB-', rawData)
	rawData = re.sub(r'R-RRB- \)', r'R-RRB- -RRB-', rawData)
	rawData = re.sub(r'R-RRB- \(', r'R-RRB- -LRB-', rawData)
	rawData = re.sub(r'-LRB- \(', r'-LRB- -LRB-', rawData)
	rawData = re.sub(r'-RRB- \)', r'-RRB- -RRB-', rawData)
	rawData = re.sub(r'PU \(', r'PU -LRB-', rawData)
	rawData = re.sub(r'PU \)', r'PU -RRB-', rawData)
	rawData = re.sub(r':-\)', r'smileyface', rawData)

	return rawData

def waMatrix2unarySubtreeAlignments(waMatrix, srcTr, tgtTr):
	subtreeAlign = []
	for i in xrange(len(waMatrix)):
		for j in xrange(len(waMatrix[i])):
			if waMatrix[i][j] == 1:
				srcWordPosition = srcTr.treeposition_spanning_leaves(i, i+1)
				tgtWordPosition = tgtTr.treeposition_spanning_leaves(j, j+1)
				if len(srcWordPosition) > 1 and len(tgtWordPosition) > 1 and \
						len(srcTr[srcWordPosition[:-2]].leaves()) == 1 and \
						len(tgtTr[tgtWordPosition[:-2]].leaves()) == 1:
							subtreeAlign.append((i, j, i+1, j+1))
	return subtreeAlign
