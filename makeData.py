#!/usr/bin/python2.7

import codecs
import sys

def extract(partEnFile, wholeEnFile, wholeChFile, wholeEnGpsFile, wholeEnBpsFile, wholeChGpsFile, wholeChBpsFile, wholeSubaFile, wholeWaFile):
	pEn = [line.lower() for line in codecs.open(partEnFile, 'r', 'utf-8').readlines()]
	wEn = [line.lower() for line in codecs.open(wholeEnFile, 'r', 'utf-8').readlines()]
	wCh = codecs.open(wholeChFile, 'r', 'utf-8').readlines()
	wEnG = codecs.open(wholeEnGpsFile, 'r', 'utf-8').readlines()
	wEnB = codecs.open(wholeEnBpsFile, 'r', 'utf-8').readlines()
	wChG = codecs.open(wholeChGpsFile, 'r', 'utf-8').readlines()
	wChB = codecs.open(wholeChBpsFile, 'r', 'utf-8').readlines()
	wSuba = codecs.open(wholeSubaFile, 'r', 'utf-8').readlines()
	wWa = codecs.open(wholeWaFile, 'r', 'utf-8').readlines()

	pCh, pEnG, pEnB, pChG, pChB, pSuba, pWa = [], [], [], [], [], [], []
	k = 0
	for i, en in enumerate(wEn):
		if k >= len(pEn):
			break
		if en == pEn[k]:
			pCh.append(wCh[i])
			pEnG.append(wEnG[i])
			pEnB.append(wEnB[i])
			pChG.append(wChG[i])
			pChB.append(wChB[i])
			pSuba.append(wSuba[i])
			pWa.append(wWa[i])
			k += 1
		else:
			continue

	stem = partEnFile.split('.')[0]
	pChF = codecs.open(stem+'.ch', 'w', 'utf-8')
	pEnGF = codecs.open(stem+'.en.gps', 'w', 'utf-8')
	pEnBF = codecs.open(stem+'.en.bps', 'w', 'utf-8')
	pChGF = codecs.open(stem+'.ch.gps', 'w', 'utf-8')
	pChBF = codecs.open(stem+'.ch.bps', 'w', 'utf-8')
	pSubaF = codecs.open(stem+'.suba', 'w', 'utf-8')
	pWaF = codecs.open(stem+'.wa', 'w', 'utf-8')
	for i in xrange(len(pEnG)):
		pChF.write(pCh[i])
		pEnGF.write(pEnG[i])
		pEnBF.write(pEnB[i])
		pChGF.write(pChG[i])
		pChBF.write(pChB[i])
		pSubaF.write(pSuba[i])
		pWaF.write(pWa[i])

if __name__ == '__main__':
	extract(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
