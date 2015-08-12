#!/usr/bin/python2.7

class Rule:
	def __init__(self, lhs, rhsSrc, rhsTgt, alignment):
		"""
		Initialize a SCFG rule.

		:type lhs: str
		:param lhs: a non-terminal 'X'

		:type rhsSrc: a list of strings
		:param rhsSrc: left hand side, i.e. rule on source language, strings can be terminal or non-terminal symbols

		:type rhsTgt: a list of strings
		:param rhsTgt: right hand side, i.e. rule on target language, strings can be terminal or non-terminal symbols

		:type alignment: a list of tuples
		:param alignment: alignments of non-terminal symbols between rhsSrc and rhsTgt 

		"""
		self.lhs = lhs
		self.rhsSrc = rhsSrc
		self.rhsTgt = rhsTgt
		self.alignment = alignment
