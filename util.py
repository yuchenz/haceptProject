#!/usr/bin/python2.7

import re
import pdb

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
			if waMatrix[i][j] == 1 and sum(waMatrix[i]) == 1 and sum([waMatrix[k][j] for k in xrange(len(waMatrix))]) == 1:
				srcWordPosition = srcTr.treeposition_spanning_leaves(i, i+1)
				tgtWordPosition = tgtTr.treeposition_spanning_leaves(j, j+1)
				if len(srcWordPosition) > 1 and len(tgtWordPosition) > 1 and \
						len(srcTr[srcWordPosition[:-2]].leaves()) == 1 and \
						len(tgtTr[tgtWordPosition[:-2]].leaves()) == 1:
							subtreeAlign.append((i, j, i+1, j+1))
	return subtreeAlign

def waMatrix2oneline(waMatrix):
	oneline = ''
	for i in xrange(len(waMatrix)):
		for j in xrange(len(waMatrix[i])):
			if waMatrix[i][j]:
				oneline += str(i)+'-'+str(j)+' '
	return oneline

def allCombinations(groupList):
	"""
	given a list of groups, output all combinations of picking one element from each group
	e.g. groups = [[1,2,3], [4,5], [6]], output [[1,4,6], [2,4,6], [3,4,6], [1,5,6], [2,5,6], [3,5,6]]

	:type groupList: a list of lists 
	:param groupList: a list of groups of elements
	"""
	queue = [groupList]
	result = []
	while len(queue) > 0:
		current = queue.pop(0)
		if sum([len(group) for group in current]) == len(current):
			result.append([group[0] for group in current])
			continue

		tmpList = []
		for i, group in enumerate(current):
			if len(group) == 1:
				tmpList.append(group)
			else:
				for j in xrange(len(group)):
					queue.append(tmpList + [[group[j]]] + current[i + 1:])
				break

	return result

	
