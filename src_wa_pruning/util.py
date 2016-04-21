#!/usr/bin/python2.7

import codecs 

DATA_DIR = "/home/b/yuchenz/Projects/haceptProject/src/Data/"

class Example:
	def __init__(self, ID, label):
		self.ID = ID
		self.featList = []
		self.label = label
	
	def __str__(self):
		return self.ID + '\t' + self.label + '\t' + '\t'.join(self.featList) + '\n'

def loadWordPairDict(filename):
	lines = [line.split() for line in codecs.open(DATA_DIR+filename, 'r', 'utf-8').readlines()] 
	D = {}
	for line in lines:
		D[(line[0], line[1])] = int(line[2]) 
	
	return D

def loadFuncWordDict(filename):
	funcWordL = [line.split()[0] for line in codecs.open(DATA_DIR+filename, 'r', 'utf-8').readlines()]
	funcWordL += " of about the be at in into which - , . to that 'd did \" ' 's up 've and a an".split(' ')
	return funcWordL

