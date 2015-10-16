#!/usr/bin/python2.7

def sampleData(split, stem, suffixList):
	"""
	e.g. ./sampleHaceptData 90 hacept100 ch en ch.gps en.gps ch.bps en.bps suba wa
	means to split the hacept100 files with suffix like '.ch', '.en.bps', 'wa', etc. 
	into 90%:10%, output to hacept90 and hacept10 with according suffix

	type split: int
	param split: percentage to be sampled out

	type stem: str
	param stem: stem filename

	type suffix: list
	param suffix: a list of suffix that will form full filenames with the stem

	"""





	

if __name__ == '__main__':
	sampleData(sys.argv[1], sys.argv[2], sys.argv[3:])
