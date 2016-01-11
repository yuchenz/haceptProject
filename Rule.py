#!/usr/bin/python2.7

import pdb

class Rule:
	def __init__(self, lhs, rhsSrc, rhsTgt, alignment, wordAlignment, srcSnt, tgtSnt):
		"""
		Initialize a SCFG rule.

		:type lhs: str
		:param lhs: a non-terminal 'X'

		:type rhsSrc: a list of integer/'X'
		:param rhsSrc: left hand side, i.e. rule on source language, integers are the indexes of words, i.e. terminal symbols,
						'X's are non-terminal symbols

		:type rhsTgt: a list of integer/'X'
		:param rhsTgt: right hand side, i.e. rule on target language, integers are the indexes of words, i.e. terminal symbols, 
						'X's are non-terminal symbols

		:type alignment: a list of tuples
		:param alignment: alignments of non-terminal symbols between rhsSrc and rhsTgt 

		:type wordAlignment: a list of list of '0's and '1's
		:param wordAlignment: word alignment matrix

		:type srcSnt: list
		:param srcSnt: the list of words of source snt

		:type tgtSnt: list
		:param tgtSnt: the list of words of target snt 

		"""
		if lhs == None:
			self.lhs, self.rhsSrc, self.rhsTgt, self.alignment = None, None, None, None
		else:
			self.lhs = lhs
			self.rhsSrc = [srcSnt[i] if i != 'X' else 'X' for i in rhsSrc] 
			self.rhsTgt = [tgtSnt[i] if i != 'X' else 'X' for i in rhsTgt] 
			#print self.rhsSrc, self.rhsTgt, alignment
			self.alignment = self.setupAlignment(alignment, wordAlignment, rhsSrc, rhsTgt)

	def setupAlignment(self, alignment, wordAlignment, rhsSrc, rhsTgt):
		#pdb.set_trace()
		ans = []
		srcXDic, tgtXDic = {}, {}
		k = 0
		for i in xrange(len(rhsSrc)):
			if rhsSrc[i] != 'X':
				for j in xrange(len(wordAlignment[rhsSrc[i]])):
					if wordAlignment[rhsSrc[i]][j] == 1 and j in rhsTgt:
						ans.append((i, rhsTgt.index(j)))
			else:
				srcXDic[k] = i
				k += 1

		k = 0
		for i in xrange(len(rhsTgt)):
			if rhsTgt[i] == 'X':
				tgtXDic[k] = i
				k += 1

		for align in alignment:
			ans.append((srcXDic[align[0]], tgtXDic[align[1]]))

		return sorted(ans)

	def __eq__(self, other):
		if self.lhs == other.lhs and self.rhsSrc == other.rhsSrc and \
				self.rhsTgt == other.rhsTgt and self.alignment == other.alignment:
					return True
		else:
			return False
	
	def __str__(self):
		tmp = self.lhs + ' -> ' + ' '.join([item.encode('utf-8') for item in self.rhsSrc]) + ' | ' + \
				' '.join([item.encode('utf-8') for item in self.rhsTgt]) + ' | ' + \
				' '.join([str(item) for item in self.alignment]) 
		return tmp

	def mosesFormatRule(self):
		rhsS = []
		for item in self.rhsSrc:
			if item == 'X':
				rhsS.append('[X][X]')
			else:
				rhsS.append(item)

		rhsT = []
		for item in self.rhsTgt:
			if item == 'X':
				rhsT.append('[X][X]')
			else:
				rhsT.append(item)

		rule = rhsS + ['[X]', '|||'] + rhsT + ['[X]', '|||']
		ruleInv = rhsT + ['[X]', '|||'] + rhsS + ['[X]', '|||']

		for item in self.alignment:
			rule.append(str(item[0])+'-'+str(item[1]))
			ruleInv.append(str(item[1])+'-'+str(item[0]))

		rule.append('||| 1 \n')		# set the count as 1 by default
		ruleInv.append('||| 1 \n')		# set the count as 1 by default
		return ' '.join(rule), ' '.join(ruleInv)
