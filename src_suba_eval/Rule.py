#!/usr/bin/python2.7

import pdb

class Rule:
	def __init__(self, lhsSrc, lhsTgt, rhsSrc, rhsTgt, alignment, wordAlignment, srcSnt, tgtSnt, square):
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
		if lhsSrc == None:
			self.lhsSrc, self.lhsTgt, self.rhsSrc, self.rhsTgt, self.alignment, self.square = None, None, None, None, None, None
		else:
			self.lhsSrc, self.lhsTgt = lhsSrc, lhsTgt
			self.rhsSrc = [srcSnt[i] if (not isinstance(i, str)) else '['+i+']' for i in rhsSrc] 
			self.rhsTgt = [tgtSnt[i] if (not isinstance(i, str)) else '['+i+']' for i in rhsTgt] 
			#print self.rhsSrc, self.rhsTgt, alignment
			self.alignment = self.setupAlignment(alignment, wordAlignment, rhsSrc, rhsTgt)
			self.square = square

		self.count = 1

	def setupAlignment(self, alignment, wordAlignment, rhsSrc, rhsTgt):
		#pdb.set_trace()
		ans = []
		srcXDic, tgtXDic = {}, {}
		k = 0
		for i in xrange(len(rhsSrc)):
			if not isinstance(rhsSrc[i], str):
				for j in xrange(len(wordAlignment[rhsSrc[i]])):
					if wordAlignment[rhsSrc[i]][j] == 1 and j in rhsTgt:
						ans.append((i, rhsTgt.index(j)))
			else:
				srcXDic[k] = i
				k += 1

		k = 0
		for i in xrange(len(rhsTgt)):
			if isinstance(rhsTgt[i], str):
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
		tmp = self.lhsSrc + ' ' + self.lhsTgt + ' -> ' + ' '.join([item.encode('utf-8') for item in self.rhsSrc]) + ' | ' + \
				' '.join([item.encode('utf-8') for item in self.rhsTgt]) + ' | ' + \
				' '.join([str(item) for item in self.alignment]) + \
				' ||| covering ' +  str(self.square)
		return tmp

	def mosesFormatRule(self):
		rhsS = list(self.rhsSrc)
		rhsT = list(self.rhsTgt)

		for item in self.alignment:
			if rhsS[item[0]][0] == '[' and rhsS[item[0]][-1] == ']' and \
					rhsT[item[1]][0] == '[' and rhsT[item[1]][-1] == ']':
						tmp = rhsS[item[0]] + rhsT[item[1]]
						rhsS[item[0]] = tmp
						rhsT[item[1]] = tmp

		rule = rhsS + ['[' + self.lhsSrc + ']'] + ['|||'] + rhsT + ['[' + self.lhsTgt + ']'] + ['|||']
		ruleInv = rhsT + ['[' + self.lhsTgt + ']'] + ['|||'] + rhsS + ['[' + self.lhsSrc + ']'] + ['|||']

		for item in self.alignment:
			rule.append(str(item[0])+'-'+str(item[1]))
			ruleInv.append(str(item[1])+'-'+str(item[0]))

		rule.append('||| ' + str(self.count) + ' \n')		
		ruleInv.append('||| ' + str(self.count) + ' \n')
		return ' '.join(rule), ' '.join(ruleInv)
