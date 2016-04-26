import nltk
import time
import re
import sys
import pdb

class Suba:
	def __init__(self, sTreePos, tTreePos, sOffset, tOffset, smallestBlock):
		self.srcTreePosition = sTreePos 
		self.tgtTreePosition = tTreePos
		self.srcOffset = sOffset
		self.tgtOffset = tOffset
		self.smallestBlock = smallestBlock

	def __str__(self):
		return str(self.srcOffset[0]) + '-' + str(self.srcOffset[1]) + '-' + str(self.tgtOffset[0]) + '-' + str(self.tgtOffset[1])

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
	
def extractAllSuba(srcTree, tgtTree, wa):
	'''
	type srcTree: nltk.ParentedTree
	param srcTree: source parse tree

	type tgtTree: nltk.ParentedTree
	param tgtTree: target parse tree

	type wa: list of lists (a matrix)
	param wa: word alignment between the two sentences

	rtype: list of suba objects
	rvalue: all possible subtree alignments on this sentence pair
	'''
	#pdb.set_trace()
	sDic, tDic = {}, {}

	simplifyTree(srcTree)
	simplifyTree(tgtTree)

	#s = time.clock()
	# for each source subtree, find its minimum block,
	# then for each target subtree, find its minimum block,
	# and compare if this target subtree covers the same minimum block as current source subtree
	# if it does, align these two subtree spans(offsets)
	allSubaList = []
	for sSubtr in srcTree.subtrees():
		if sSubtr.height() <= 2:
			continue

		sTreePos = sSubtr.treeposition()
		sOffset = treePosition2offset(sTreePos, srcTree)
		sDic[sTreePos] = scanBlock(sOffset, 'src', wa)

		#print >> sys.stderr, '='*30
		#print >> sys.stderr, sSubtr.pprint().encode('utf-8')

		for tSubtr in tgtTree.subtrees():
			if tSubtr.height() <= 2:
				continue

			tTreePos = tSubtr.treeposition()
			if tTreePos not in tDic:
				tOffset = treePosition2offset(tTreePos, tgtTree)
				tDic[tTreePos] = (scanBlock(tOffset, 'tgt', wa), tOffset)
			else:
				tOffset = tDic[tTreePos][1]

			#print >> sys.stderr, tSubtr.pprint().encode('utf-8')

			# if -1 in sDic[sTreePos] or -1 in tDic[tTreePos][0], it means that either sSubtr or tSubtr doesn't have any word alignments
			# we don't alignment two subtrees that have zero word alignment points
			if sDic[sTreePos] == tDic[tTreePos][0] and -1 not in sDic[sTreePos] and -1 not in tDic[tTreePos][0]:
				#print >> sys.stderr, 'pair\n'
				allSubaList.append(Suba(sTreePos, tTreePos, sOffset, tOffset, sDic[sTreePos]))
			#else:
				#print >> sys.stderr, sDic[sTreePos], tDic[tTreePos][0]
				#print >> sys.stderr, 'not pair\n'
	#print >> sys.stderr, "match suba: ", time.clock() - s
	
	return allSubaList

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

def oneline2waMatrix(line, srcLen, tgtLen):
	# the numbers in line has start from 0
	#print line, srcLen, tgtLen
	line = [[item.split('-')[0].split(','), item.split('-')[1].split(',')] for item in line.split()]

	wa = [[0 for j in xrange(tgtLen)] for i in xrange(srcLen)]

	for item in line:
		for i in item[0]:
			for j in item[1]:
				wa[int(i)][int(j)] = 1
	
	return wa

def oneline2subaList(line):
	result = []
	line = [item.split('-') for item in line.split()]
	for item in line:
		result.append((int(item[0]), int(item[2]), int(item[1]), int(item[3])))
	return result

