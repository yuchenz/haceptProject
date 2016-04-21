
import codecs

DATA_DIR = "/home/b/yuchenz/Projects/haceptProject/src/Data/"

def feat_word(word, ID):
	return 'f' + str(ID) + '=' + word

def feat_wordPair(chW, enW, ID):
	return 'f' + str(ID) + '=' + chW + '_' + enW

def relativeIndex(i, length):
	index = int(round(i * 10.0 / length))
	return index

def feat_relativeIndex(i, length, ID):
	return 'f' + str(ID) + '=' + str(relativeIndex(i, length))

def feat_relativeIndexDiff(i, j, lenCh, lenEn, ID):
	indexCh = relativeIndex(i, lenCh)
	indexEn = relativeIndex(j, lenEn)
	diff = abs(indexCh - indexEn)
	#diff = 'far' if diff >= 2 else 'close' 
	return 'f' + str(ID) + '=' + str(diff) 

def feat_relativeIndexPair(i, j, lenCh, lenEn, ID):
	return 'f' + str(ID) + '=' + str(relativeIndex(i, lenCh)) + '_' + str(relativeIndex(j, lenEn)) 

def feat_isFuncWord(word, fwD, ID):
	if word in fwD: return 'f' + str(ID) + '=true'
	else: return 'f' + str(ID) + '=false'

def feat_inDict(chWord, enWord, wpD, ID):
	if (chWord, enWord) in wpD: 
	#if (chWord, enWord) in wpD and wpD[(chWord, enWord)] > 0:
		return 'f' + str(ID) + '=true'
	else:
		return 'f' + str(ID) + '=false'

def feat_alwaysOn(ID):
	return 'f' + str(ID) + '=On'

def extractFeat(i, j, chSent, enSent, wpD, fwD):
	featList = []
	featID = 0

	#featList.append(feat_word(chSent[i], featID)); featID += 1
	featList.append(feat_word(enSent[j], featID)); featID += 1
	#featList.append(feat_wordPair(chSent[i], enSent[j], featID)); featID += 1
	#featList.append(feat_isFuncWord(chSent[i], fwD, featID)); featID += 1
	#featList.append(feat_isFuncWord(enSent[j], fwD, featID)); featID += 1

	#featList.append(feat_relativeIndexDiff(i, j, len(chSent), len(enSent), featID)); featID += 1
	#featList.append(feat_relativeIndexPair(i, j, len(chSent), len(enSent), featID)); featID += 1
	#featList.append(feat_relativeIndex(i, len(chSent), featID)); featID += 1
	#featList.append(feat_relativeIndex(j, len(enSent), featID)); featID += 1

	featList.append(feat_inDict(chSent[i], enSent[j], wpD, featID)); featID += 1
	#featList.append(feat_alwaysOn(featID)); featID += 1

	return featList
