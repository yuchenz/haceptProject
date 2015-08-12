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
