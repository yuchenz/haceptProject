#!/usr/bin/python2.7

import re
import pdb
import nltk

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

def scanBlock(offset, lan, wa):
	'''
	given the offsets 'offset' of a phrase in language 'lan',
	find the minimum block it covers in the word alignment matrix 'wa'
	'''
	if lan == 'tgt':
		tmpWa = [[wa[i][j] for i in xrange(len(wa))] for j in xrange(len(wa[0]))] 
	elif lan == 'src':
		tmpWa = wa
	else:
		print >> sys.stderr, "illegal language in scanSpan(): ", lan
	
	x1, x2, y1, y2 = -1, -1, -1, -1 
	for j in xrange(len(tmpWa[0])):
		for i in xrange(offset[0], offset[1]):
			#print len(tmpWa), len(tmpWa[0]), offset, i, j, lan
			if tmpWa[i][j]:
				y1 = j
				break
		else: continue
		break

	for j in xrange(len(tmpWa[0]) - 1, -1, -1):
		for i in xrange(offset[0], offset[1]):
			if tmpWa[i][j]:
				y2 = j
				break
		else: continue
		break

	for i in xrange(offset[0], offset[1]):
		for j in xrange(len(tmpWa[0])):
			if tmpWa[i][j]:
				x1 = i
				break
		else: continue
		break

	for i in xrange(offset[1] - 1, offset[0] - 1, -1):
		for j in xrange(len(tmpWa[0])):
			if tmpWa[i][j]:
				x2 = i
				break
		else: continue
		break

	if lan == 'tgt':
		return (y1, y2, x1, x2)
	else:
		return (x1, x2, y1, y2)

def simplifyTree(tr):
	'''
	if a subtree in this tree has only one child, combine the subtree's node label and the child's node label,
	and reduce a level of the subtree (keep POS tags for words)

	e.g.

	input: "(TOP (S (NP (NN (XX I))) (VP (XX (VV love) (NP (XX (NN python)))))))"
	output: "(TOP+S (NP+NN (XX I)) (VP+XX (VV love) (NP+XX (NN python))))" 
	
	'''
	stack = [tr]
	while stack:
		pointer = stack.pop() 
		if pointer.height() <= 2:
			continue
		while len(list(pointer)) == 1:
			if pointer.height() <= 3:
				break
			child = pointer[0]
			pointer.node += '+' + child.node 
			pointer.pop()
			for ch in child:
				ch._parent = None
				pointer.append(ch)
		else:
			for child in pointer:
				stack.append(child)

	return 

def treePosition2offset(treePos, treeRoot):
	cnt = 0
	parent = treeRoot[treePos]
	while parent != treeRoot:
		for i in xrange(parent.parent_index()):
			if isinstance(parent.parent()[i], nltk.ParentedTree):
				cnt += len(parent.parent()[i].leaves())
			else:
				print >> sys.stderr, treeRoot
		parent = parent.parent()
	return (cnt, cnt + len(treeRoot[treePos].leaves()))

