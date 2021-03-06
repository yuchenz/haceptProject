#!/usr/bin/python2.7

import nltk
import pdb, sys
import re
import codecs
import multiprocessing as mp
import os
import time
from Bead import Bead
from glueRules import extractLabels
from util import simplifyTree, treePosition2offset, scanBlock

MAX=int(10e5)
MIN=int(-10e5)

debug_log = sys.stderr

class Frame:
	def __init__(self, srcPos, tgtPos, srcTr, tgtTr):
		"""
		Initialize a Frame instance.

		:type srcPos: a list of tuples
		:param srcPos: treeposition on src tree

		:type tgtPos: a list of tuples
		:param tgtPos: treeposition on tgt tree

		:type srcTr: nltk.ParentedTree
		:param srcTr: src tree

		:type tgtTr: nltk.ParentedTree
		:param tgtTr: tgt tree

		self.srcList and self.tgtList are lists of treepositions.

		"""
		self.srcList = srcPos
		self.tgtList = tgtPos
		self.srcTree = srcTr
		self.tgtTree = tgtTr
		self.srcListMatrixPos = self.treeposition2offsetPosition(self.srcList, self.srcTree) 
		self.tgtListMatrixPos = self.treeposition2offsetPosition(self.tgtList, self.tgtTree) 
		
		# two different representation of a subtree alignment
		self.subtreeAlignment_treepos = None
		self.subtreeAlignment_waMatrixPos = None  

	def __eq__(self, other):
		"""
		Overload the == operator.

		:type other: Frame
		:param other: another Frame instance.

		"""
		return (self.srcList == other.srcList) and (self.tgtList == other.tgtList) 

	def __hash__(self):
		"""
		Return an integer to specify the hash behavior.

		"""
		return 1 

	def __getitem__(self, index):
		"""
		Overload the [] operator.

		:type index: tuple, representing a treeposition 
		:param index: the treeposition on src or tgt tree.

		"""
		assert(index in self.srcList + self.tgtList)
		if index in self.srcList:
			return self.tgtList
		elif index in self.tgtList:
			return self.srcList

	def mergable(self, frame):
		"""
		Return True if frame is mergable with self instance.

		:type frame: Frame
		:param frame: another frame to be merged with self.

		"""
		for pos in self.srcList: 
			if pos in frame.srcList:
				return True

		for pos in self.tgtList: 
			if pos in frame.tgtList:
				return True

		return False 

	@classmethod
	def merge(cls, frame1, frame2):
		"""
		Merge two Frame instances frame1 and frame 2, 
		return merged Frame instance.

		frame1 and frame2 must be on the same tree pair.

		:type frame1: Frame
		:para frame1: a Frame to be merged.

		:type frame2: Frame
		:para frame2: a Frame to be merged.

		"""
		return cls(list(set(frame1.srcList+frame2.srcList)), list(set(frame1.tgtList+frame2.tgtList)), frame1.srcTree, frame1.tgtTree)

	def __str__(self):
		tmp = '\nsrcList: ' + str(self.srcListMatrixPos) + '\ttgtList: ' + str(self.tgtListMatrixPos)
		#tmp += 'srcList: ' + str(self.srcList) + '\ttgtList: ' + str(self.tgtList)
		#if self.subtreeAlignment_treepos != None:
		#	tmp += '\nsrcSubtree: ' + str(self.subtreeAlignment_treepos[0]) 
		#	tmp += '\ttgtSubtree: ' + str(self.subtreeAlignment_treepos[1])
		if self.subtreeAlignment_waMatrixPos != None:
			tmp += '\nwaMatrixPosition: ' + str(self.subtreeAlignment_waMatrixPos)
		return tmp

	@staticmethod
	def treeposition2offsetPosition(subTrPosList, tr):
		"""
		Return the offset of the first word and the last word for every subtree in the list.

		:type subTrPosList: a list of tree positions
		:param subTrPosList: subtrees' tree positions

		:type tr: nltk.ParentedTree
		:param tr: the tree

		"""
		offsetList = []
		cnt = 0
		for pos in subTrPosList:
			par = tr[pos]
			while par != tr:
				for i in xrange(par.parent_index()):
					if isinstance(par.parent()[i], nltk.ParentedTree):
						cnt += len(par.parent()[i].leaves())
					else:
						print >> debug_log, tr
				par = par.parent()

			label = ''
			start = False
			for char in tr[pos].node:
				if not start:
					if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 
						continue
					else:
						start = True
						label += char
				else:
					if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 
						break
					else:
						label += char
			offsetList.append((cnt, cnt+len(tr[pos].leaves()), label)) 
			cnt = 0
		return offsetList

	@staticmethod
	def treeposition2waMatrixPosition(srcTrPos, tgtTrPos, srcTr, tgtTr):
		"""
		Return a subtree alignment in the form of a square on the word alignment matrix.

		:type srcTrPos: tuple
		:param srcTrPos: treeposition of the source subtree

		:type tgtTrPos: tuple
		:param tgtTrPos: treeposition of the target subtree

		:type srcTr: nltk.ParentedTree
		:param srcTr: source tree

		:type tgtTr: nltk.ParentedTree
		:param tgtTr: target tree

		:rtype: 4-tuple
		:rvalue: (x1, y1, x2, y2) represents the subtree square on the word alignment matrix.

		"""
		x1, x2, xlabel = Frame.treeposition2offsetPosition([srcTrPos], srcTr)[0]
		y1, y2, ylabel = Frame.treeposition2offsetPosition([tgtTrPos], tgtTr)[0]

		return (x1, y1, x2, y2, xlabel, ylabel)

	def subtreeAlign(self, subtreeAlignFunc, srcTr, tgtTr):
		"""
		Use subtreeAlignFunc to pick one subtree alignment from this frame.

		:type subtreeAlignFunc: function
		:param subtreeAlignFunc: a function that takes in a frame and two trees to do a subtree alignment

		"""
		self.subtreeAlignment_treepos = subtreeAlignFunc(self, srcTr, tgtTr)
		self.subtreeAlignment_waMatrixPos = [self.treeposition2waMatrixPosition(suba[0], suba[1], srcTr, tgtTr) \
				for suba in self.subtreeAlignment_treepos] 

	def allPossibleSubtreeAlignment(self):
		ans = []
		for srcPos in self.srcListMatrixPos:
			for tgtPos in self.tgtListMatrixPos:
				ans.append((srcPos[0], tgtPos[0], srcPos[1], tgtPos[1]))
		return ans

class SntFrame:
	def __init__(self, srcTree, tgtTree, wordAlignment, alignFunc, ruleExFlag, wordRulesFlag, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t, verbose): 
		"""
		Initialize a FrameList instance.

		:type srcTree: nltk.ParentedTree
		:param srcTree: constituent phrase-based tree of the source language (e.g. ch);

		:type tgtTree: nltk.ParentedTree
		:param tgtTree: constituent phrase-based tree of the target language (e.g. en);

		:type wordAlignment: a list of tuples 
		:param wordAlignment: [([f1, f2], [e1]), ...] representing source words f1 and f2 are aligned with target word e1.

		"""
		self.srcTree = srcTree
		self.srcWordList = [word.lower() for word in srcTree.leaves()]
		self.tgtTree = tgtTree
		self.basicGlueRuleTopLabels, self.basicGlueRuleLabels = extractLabels(self.tgtTree)
		self.tgtWordList = [word.lower() for word in tgtTree.leaves()]
		self.waMatrix = self._makeWaMatrix_(wordAlignment, len(srcTree.leaves()), len(tgtTree.leaves()))

		self.frameList = self._extractFrames_(wordRulesFlag)
		self.subtreeAlign(alignFunc)

		if verbose:
			print >> debug_log
			#print >> debug_log, "SntFrame got the word alignment matrix:"
			#print >> debug_log, '\n'.join([' '.join([str(d) for d in row]) for row in self.waMatrix])
			#print >> debug_log
			print >> debug_log, "SntFrame's frameList:  (" + str(len(self.frameList)) + " lists)" 
			for frame in self.frameList:
				print frame.subtreeAlignment_waMatrixPos
			print >> debug_log
			#print >> debug_log, 'src tree:'
			#print >> debug_log, self.srcTree
			#print >> debug_log, 'tgt tree:'
			#print >> debug_log, self.tgtTree

		self.ruleList = []
		if s2t: self.glueRuleList = []
		if ruleExFlag:
			tmpSubaList = [frame.subtreeAlignment_waMatrixPos for frame in self.frameList]

			if verbose:
				print >> debug_log
				print >> debug_log, "SntFrame's all suba given align_func", alignFunc.__name__, ": (this one should be the same with the above frameList)"
				print >> debug_log, tmpSubaList
				print >> debug_log
				print >> debug_log, "rules in the Bead:"

			tmpBead = Bead(self.srcTree, self.tgtTree, self.waMatrix, tmpSubaList, wordRulesFlag, extensiveRulesFlag, phraseRulesFlag, s2t, verbose)

			if verbose:
				print >> debug_log
				print >> debug_log, "corresponding bead info: (this one should be a sorted version of the above frameList, sorted by the area of each square, biggest to smallest)"
				print >> debug_log, tmpBead
				print >> debug_log

			self.ruleList = [rule.mosesFormatRule() for rule in self.consolidateRules(tmpBead.ruleList, fractionalCountFlag) if rule.count > 0]
			if s2t: self.glueRuleList = [rule.mosesFormatRule() for rule in tmpBead.glueRuleList]

		if verbose:
			print >> debug_log, "SntFrame got the following rules: (" + str(len(self.ruleList)) + ")"
			for rule in self.ruleList:
				print >> debug_log, ''.join(rule[0]).encode('utf-8'),
			print >> debug_log
			
			if s2t:
				print >> debug_log, "SntFrame got the following glue rules: (" + str(len(self.glueRuleList)) + ")"
				for rule in self.glueRuleList:
					print >> debug_log, ''.join(rule[0]).encode('utf-8'),
				print >> debug_log
	
	"""
	# old version return a list
	@classmethod
	def loadData(cls, srctrFilename, tgttrFilename, waFilename):
		'''
		Return a list of SntFrame instances.
		Load source trees, target trees, and word alignments from three parallel files, and create Frame instances.

		:type srctrFilename: str
		:param srctrFilename: filename for source trees

		:type tgttrFilename: str
		:param tgttrFilename: filename for target trees

		:type waFilename: str
		:param waFilename: filename for word alignments 

		'''

		#srcTreeList = [nltk.ParentedTree(re.sub(' \(\)', ' -lbr-)', re.sub(' \)\)', ' -rbr-)', line))) for line in codecs.open(srctrFilename, 'r', 'utf-8')]
		srcTreeList = [nltk.ParentedTree(line) for line in codecs.open(srctrFilename, 'r', 'utf-8')]
		tgtTreeList = [nltk.ParentedTree(line) for line in codecs.open(tgttrFilename, 'r', 'utf-8')]

		waList = [[([int(i) for i in item.split('-')[0].split(',')], [int(j) for j in item.split('-')[1].split(',')]) \
				for item in line.split()] for line in open(waFilename, 'r').readlines()]

		assert(len(srcTreeList) == len(tgtTreeList))
		assert(len(srcTreeList) == len(waList))
		#print len(srcTreeList)
		#pdb.set_trace()

		sntList = []
		for i in xrange(len(srcTreeList)):
			if len(srcTreeList[i].leaves()) == 0 or len(tgtTreeList[i].leaves()) == 0:
				#print >> debug_log, 'sentence #', i, 'no parse, skipped',
				sntList.append(None)
			else:
				#print >> debug_log, 'sentence #', i,
				#print 'sentence #', i
				#print ' '.join(srcTreeList[i].pprint().split()).encode('utf-8')
				#print ' '.join(tgtTreeList[i].pprint().split()).encode('utf-8')
				#print waList[i]
				#print 
				sntList.append(cls(srcTreeList[i], tgtTreeList[i], waList[i]))
			if i % 1000 == 0:
				print >> debug_log, i, '...',
		print >> debug_log
		#pdb.set_trace()
		return sntList
	"""

	def _makeWaMatrix_(self, wa, nRow, nCol):
		"""
		Return a word alignment matrix A, where A[i][j] == 1 indicates source word i is aligned with target word j.

		:type wa: a list of tuples 
		:param wa: [([f1, f2], [e1]), ...] representing source words f1 and f2 are aligned with target word e1.

		:type nRow: int
		:param nRow: number of rows of the matrix.

		:type nCol: int
		:param nCol: number of columns of the matrix.

		"""
		#print nRow, nCol
		#print wa
		#print
		waMatrix = [[0 for j in xrange(nCol)] for i in xrange(nRow)]
		for a in wa: 
			for i in a[0]:
				for j in a[1]:
					waMatrix[i][j] = 1
		return waMatrix

	def _extractFrames_(self, wordRulesFlag):
		"""
		Return a list of Frame instances.

		"""
		#pdb.set_trace()
		simplifyTree(self.srcTree)
		simplifyTree(self.tgtTree)

		sDic, tDic = {}, {}
		frameSet = set() 
		for sSubtr in self.srcTree.subtrees():
			if sSubtr.height() <= 2:
				continue

			sTreePos = sSubtr.treeposition()
			sOffset = treePosition2offset(sTreePos, self.srcTree)
			sDic[sTreePos] = scanBlock(sOffset, 'src', self.waMatrix)

			for tSubtr in self.tgtTree.subtrees():
				if tSubtr.height() <= 2:
					continue

				tTreePos = tSubtr.treeposition()
				if tTreePos not in tDic:
					tOffset = treePosition2offset(tTreePos, self.tgtTree)
					tDic[tTreePos] = scanBlock(tOffset, 'tgt', self.waMatrix)
				else:
					tOffset = tDic[tTreePos]

				#print >> debug_log, self.srcTree[sTreePos]
				#print >> debug_log, self.tgtTree[tTreePos]
				if sDic[sTreePos] == tDic[tTreePos] and -1 not in sDic[sTreePos] and -1 not in tDic[tTreePos]:
					#print >> debug_log, 'paird up!!'
					frameSet.add(Frame([sTreePos], [tTreePos], self.srcTree, self.tgtTree))
				#print >> debug_log

		'''
		srcSubtreeSpanDict = self._extractSubtreeSpan_(self.srcTree, wordRulesFlag)
		tgtSubtreeSpanDict = self._extractSubtreeSpan_(self.tgtTree, wordRulesFlag)

		frameSet = set() 
		for span in srcSubtreeSpanDict:
			if not self._consistentWithWA_(span, 'src'):
				continue
			tgtSpanList = self._scanSpan_(span, 'src')
			for tgtSpan in tgtSpanList:
				if tgtSpan in tgtSubtreeSpanDict:
					#print >> debug_log, span, tgtSpan
					frameSet.add(Frame([srcSubtreeSpanDict[span]], [tgtSubtreeSpanDict[tgtSpan]], self.srcTree, self.tgtTree))

		#print >> debug_log, '\n'
		for span in tgtSubtreeSpanDict:
			if not self._consistentWithWA_(span, 'tgt'):
				continue
			srcSpanList = self._scanSpan_(span, 'tgt')
			for srcSpan in srcSpanList:
				if srcSpan in srcSubtreeSpanDict:
					#print >> debug_log, srcSpan, span
					frameSet.add(Frame([srcSubtreeSpanDict[srcSpan]], [tgtSubtreeSpanDict[span]], self.srcTree, self.tgtTree))
		'''
		#pdb.set_trace()
		frameList = self._mergeFrames_(frameSet)
		#print >> debug_log, len(frameList)
		return frameList

	def _extractSubtreeSpan_(self, tree, wordRulesFlag):
		"""
		Return a dictionary, keys are 2-tuples, each tuple (i, j) represents a subtree span covering from word i to word j-1,
		values are the corresponding subtree treeposition.

		Here we only keep subtree spans, but not leaf spans, i.e. one layer subtrees like (NNP China) are ignored.
		[experiment] include one layer subtrees like (NNP China) as subtrees

		:type tree: nltk.ParentedTree
		:param tree: a constituent phrase-based tree structure

		"""
		spanDict = {}
		snt = tree.leaves()
		#pdb.set_trace()
		for subtree in tree.subtrees():
			if not wordRulesFlag and subtree.height() <= 2:
				continue
			span = Frame.treeposition2offsetPosition([subtree.treeposition()], tree)[0] 
			spanDict[(span[0], span[1])] = subtree.treeposition()
		return spanDict

	def _consistentWithWA_(self, span, lan):
		"""
		Return True if "span" is consistent with the word alignment on language "lan",
		else return False.

		:type span: 2-tuple
		:param span: a span in language "lan"

		:type lan: str
		:param lan: "src" or "tgt" indicating the language

		"""
		if lan == 'src':
			wordAlign = self.waMatrix
		else:
			wordAlign = [[self.waMatrix[i][j] for i in xrange(len(self.waMatrix))] for j in xrange(len(self.waMatrix[0]))] 

		pos1 = [j for i in xrange(span[0], span[1]) for j in xrange(len(wordAlign[i])) if wordAlign[i][j] == 1]
		if pos1 == []: return True

		for i in xrange(span[0], span[1]):
			for j in xrange(min(pos1), max(pos1) + 1):
				if sum([wordAlign[row][j] for row in xrange(len(wordAlign[:span[0]]))]) == 0 and \
						sum([wordAlign[row][j] for row in xrange(span[1], len(wordAlign))]) == 0:
					continue
				else:
					return False
		#print >> debug_log, 'consistent:', span
		return True

	def _scanSpan_(self, span, lan):
		"""
		Return a 2-tuple, which is a span of the other language, representing the corresponding span of the "span" in "lan".

		:type span: 2-tuple
		:param span: a span in language "lan"

		:type lan: str
		:param lan: "src" or "tgt" indicating the language

		"""
		#pdb.set_trace()
		if lan == 'src':
			wordAlign = self.waMatrix
		else:
			wordAlign = [[self.waMatrix[i][j] for i in xrange(len(self.waMatrix))] for j in xrange(len(self.waMatrix[0]))] 
			
		otherSpan = [MAX, MIN]
		for i in xrange(span[0], span[1]):
			for j in xrange(len(wordAlign[i])):
				if wordAlign[i][j] == 1:
					if j < otherSpan[0]:
						otherSpan[0] = j
					if j+1 > otherSpan[1]:
						otherSpan[1] = j+1

		if otherSpan[0] == MAX or otherSpan[1] == MIN:
			return []

		# relax span to include not-aligned words
		otherSpanList = []
		for j in xrange(otherSpan[0]-1, -1, -1):
			if sum([wordAlign[i][j] for i in xrange(len(wordAlign))]) == 0:
				otherSpanList.append((j, otherSpan[1]))
			else:
				break
		for j in xrange(otherSpan[1], len(wordAlign[0])):
			if sum([wordAlign[i][j] for i in xrange(len(wordAlign))]) == 0:
				otherSpanList.append((otherSpan[0], j+1))
			else:
				break

		otherSpanList.append(tuple(otherSpan))
		return otherSpanList 

	def _mergeFrames_(self, frameSet):
		"""
		Return a list of Frame instances, merging set(Frame(f1, e1), Frame(f2, e1), ...) into [Frame([f1, f2], e1), ...] frames.

		:type frameSet: set
		:param frameSet: a set of frames

		"""
		mergedList = [] 
		frameList = list(frameSet)
		frameList.sort()
		for currentFrame in frameList:
			#print [currentFrame.srcTree[pos].leaves() for pos in currentFrame.srcList]
			#print [currentFrame.tgtTree[pos].leaves() for pos in currentFrame.tgtList]
			for frame in mergedList:
				if frame.mergable(currentFrame):
					#print "merge"
					mergedList.remove(frame)
					mergedList.append(Frame.merge(frame, currentFrame))
					break
			else:
				#print "append"
				mergedList.append(currentFrame)
			#print 

		return mergedList

	def __str__(self):
		# src and tgt tree
		tmp = 'srcTree:\n' + self.srcTree.pprint().encode('utf-8') + '\n\ntgtTree:\n' + self.tgtTree.pprint().encode('utf-8') 
		# wa matrix
		tmp += '\n\nwa matrix:\n'
		for i in xrange(len(self.waMatrix)):
			for j in xrange(len(self.waMatrix[i])):
				tmp += str(self.waMatrix[i][j])+' '
			tmp += '\n'
		tmp += '\n'
		# each frame
		for i, frame in enumerate(self.frameList):
			tmp += '='*30 + 'frame # ' + str(i) + '='*30 + '\n\n'
			tmp += frame.__str__() + '\n\n'
			#tmp += 'src subtrees:\n'
			#for srcPos in frame.srcList:
			#	tmp += self.srcTree[srcPos].pprint().encode('utf-8') + '\n'
			#tmp += '\ntgt subtrees:\n'
			#for tgtPos in frame.tgtList:
			#	tmp += self.tgtTree[tgtPos].pprint().encode('utf-8') + '\n'
			#tmp += '\n'
		if self.ruleList:
			tmp += '\nruleList:\n'
			for rule in self.ruleList:
				tmp += rule.__str__()
		tmp += '\n'
		return tmp

	def subtreeAlign(self, subtreeAlignFunc):
		"""
		For each frame in this sentence, pick one subtree alignment from it.

		"""
		for frame in self.frameList:
			frame.subtreeAlign(subtreeAlignFunc, self.srcTree, self.tgtTree)

	def consolidateRules(self, ruleList, fractionalCountFlag):
		spanCount = {}
		# compute number of rules per span
		for rule in ruleList:
			spanCount[rule.square[:4]] = spanCount.get(rule.square[:4], 0) + 1

		# compute fractional counts
		for rule in ruleList:
			if fractionalCountFlag:
				rule.count = 1.0 / spanCount[rule.square[:4]]
			else:
				rule.count = 1.0

		# consolidate counts:
		consolidatedCount = {}
		for rule in ruleList:
			key = (' '.join(rule.rhsSrc), ' '.join(rule.rhsTgt), tuple(rule.alignment))
			consolidatedCount[key] = consolidatedCount.get(key, 0) + rule.count

		for rule in ruleList:
			key = (' '.join(rule.rhsSrc), ' '.join(rule.rhsTgt), tuple(rule.alignment))
			rule.count = consolidatedCount[key]
			consolidatedCount[key] = 0

		return ruleList

def loadData(srcTrList, tgtTrList, waList, alignFunc, ruleExFlag, wordRulesFlag, minMemFlag, procID, verbose, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t): 
	if minMemFlag:
		if 'hacept' not in os.listdir('/dev/shm'):
			os.mkdir('/dev/shm/hacept')
		f1 = codecs.open('/dev/shm/hacept/rule.' + str(procID), 'w', 'utf-8')
		f2 = codecs.open('/dev/shm/hacept/ruleInv.' + str(procID), 'w', 'utf-8')
		gf1 = codecs.open('/dev/shm/hacept/glueRule.' + str(procID), 'w', 'utf-8')
	else:
		result = []
	
	basicGlueRuleTopLabels, basicGlueRuleLabels = set([]), set([])

	for i in xrange(len(waList)):
		srcTr = nltk.ParentedTree(srcTrList[i])
		tgtTr = nltk.ParentedTree(tgtTrList[i])
		wa = [item.split('-') for item in waList[i].split()]
		wa = [([int(i) for i in item[0].split(',')], [int(j) for j in item[1].split(',')]) for item in wa]

		if minMemFlag:
			if len(srcTr.leaves()) == 0 or len(tgtTr.leaves()) == 0:
				continue
			else:
				tmpSntFrame = SntFrame(srcTr, tgtTr, wa, alignFunc, ruleExFlag, wordRulesFlag, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t, verbose)
				for rule in tmpSntFrame.ruleList:
					r, rinv = rule[0], rule[1]
					#r, rinv = rule.mosesFormatRule()
					f1.write(r)
					f2.write(rinv)
				if s2t:
					for rule in tmpSntFrame.glueRuleList:
						r, rinv = rule[0], rule[1]
						gf1.write(r)
		else:
			if len(srcTr.leaves()) == 0 or len(tgtTr.leaves()) == 0:
				result.append(None)
			else:
				tmpSntFrame = SntFrame(srcTr, tgtTr, wa, alignFunc, ruleExFlag, wordRulesFlag, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t, verbose)
				result.append(tmpSntFrame)

		if s2t: 
			basicGlueRuleTopLabels.update(tmpSntFrame.basicGlueRuleTopLabels)
			basicGlueRuleLabels.update(tmpSntFrame.basicGlueRuleLabels)

	if minMemFlag: return [None], basicGlueRuleTopLabels, basicGlueRuleLabels
	else: return result, basicGlueRuleTopLabels, basicGlueRuleLabels

def loadDataParallelWrapper(srctrFilename, tgttrFilename, waFilename, numProc, alignFunc, ruleExFlag, wordRulesFlag, minMemFlag, verbose, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t):
	s = time.clock()
	#srcTreeList = [nltk.ParentedTree(re.sub(' \(\)', ' -lbr-)', re.sub(' \)\)', ' -rbr-)', line))) for line in codecs.open(srctrFilename, 'r', 'utf-8')]
	srcTreeList = codecs.open(srctrFilename, 'r', 'utf-8').readlines()
	print 'srcTreeList:', len(srcTreeList)
	tgtTreeList = codecs.open(tgttrFilename, 'r', 'utf-8').read().split('\n')[:-1]
	print 'tgtTreeList:', len(tgtTreeList)
	waList = open(waFilename, 'r').readlines()

	#waList = [[(tuple([int(i) for i in item.split('-')[0].split(',')]), tuple([int(j) for j in item.split('-')[1].split(',')])) \
	#		for item in line.split()] for line in open(waFilename, 'r').readlines()]
	print 'waList:', len(waList)
	print 'reading in all data time: ', time.clock() - s

	assert(len(srcTreeList) == len(tgtTreeList))
	assert(len(srcTreeList) == len(waList))

	basicGlueRuleTopLabels, basicGlueRuleLabels = [], [] 

	if numProc > 1:
		pool = mp.Pool(processes = numProc)
		sntList = []
		tmp = []
		base = len(waList) / (numProc - 1)
		for i in xrange(1, numProc + 1):
			start = base * (i - 1)
			end = base * i if i < numProc else len(waList)
			tmp.append(pool.apply_async(loadData, args=(srcTreeList[start:end], tgtTreeList[start:end], waList[start:end], alignFunc, ruleExFlag, wordRulesFlag, minMemFlag, i, verbose, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t)))

		for t in tmp:
			ans, tmp1, tmp2 = t.get()
			sntList.extend(ans)
			basicGlueRuleTopLabels.append(tmp1)
			basicGlueRuleLabels.append(tmp2)
		
		basicGlueRuleTopLabels = list(set([rule for proc in basicGlueRuleTopLabels for rule in list(proc)]))
		basicGlueRuleLabels = list(set([rule for proc in basicGlueRuleLabels for rule in list(proc)]))

	else:
		sntList, tmp1, tmp2 = loadData(srcTreeList, tgtTreeList, waList, alignFunc, ruleExFlag, wordRulesFlag, minMemFlag, 1, verbose, extensiveRulesFlag, fractionalCountFlag, phraseRulesFlag, s2t)
		basicGlueRuleTopLabels, basicGlueRuleLabels = list(tmp1), list(tmp2)

	if minMemFlag:
		if 'rule.all' in os.listdir('/dev/shm/hacept/'):
			os.remove('/dev/shm/hacept/rule.all')
		if 'ruleInv.all' in os.listdir('/dev/shm/hacept/'):
			os.remove('/dev/shm/hacept/ruleInv.all')

		if s2t:
			if 'glueRule.all' in os.listdir('/dev/shm/hacept/'):
				os.remove('/dev/shm/hacept/glueRule.all')

		import subprocess
		for i in xrange(1, numProc + 1):
			subprocess.call("cat %s >> %s" % ('/dev/shm/hacept/rule.' + str(i), '/dev/shm/hacept/rule.all'), shell = True)
			subprocess.call("cat %s >> %s" % ('/dev/shm/hacept/ruleInv.' + str(i), '/dev/shm/hacept/ruleInv.all'), shell = True)
			if s2t:
				subprocess.call("cat %s >> %s" % ('/dev/shm/hacept/glueRule.' + str(i), '/dev/shm/hacept/glueRule.all'), shell = True)
	
	return sntList, basicGlueRuleTopLabels, basicGlueRuleLabels 

if __name__ == "__main__":
	"""
	python2.7 Frame.py chtb_0008.srctr chtb_0008.tgttr chtb_0008.wa
	
	"""
	sntList = SntFrame.loadData(sys.argv[1], sys.argv[2], sys.argv[3])

	for i, sntFrame in enumerate(sntList):
		print
		print '='*30, i, '='*30
		#if i == 2171:
		#	pdb.set_trace()
		print sntFrame


