
import codecs

def feat_word(word, ID):
	return 'f' + str(ID) + '=' + word

def feat_wordPair(chW, enW, ID):
	return 'f' + str(ID) + '=' + chW + '_' + enW

def feat_relativeIndexDiff(i, j, lenCh, lenEn, ID):
	diff = int(round(abs(i * 10.0 / lenCh - j * 10.0 / lenEn)))
	return 'f' + str(ID) + '=' + str(diff) 

def feat_isFuncWord(word, ID):
	funcWordL = [line.split()[0] for line in codecs.open("ch_funcWordL.txt", 'r', 'utf-8').readlines()]
	funcWordL += " of about the be at in into which - , . to that 'd did \" ' 's up 've and a an".split(' ')

	if word in funcWordL: return 'f' + str(ID) + '=true'
	else: return 'f' + str(ID) + '=false'

def extractFeat(i, j, chSent, enSent):
	featList = []
	featID = 0

	featList.append(feat_word(chSent[i], featID)); featID += 1
	featList.append(feat_word(enSent[j], featID)); featID += 1
	featList.append(feat_wordPair(chSent[i], enSent[j], featID)); featID += 1
	featList.append(feat_isFuncWord(chSent[i], featID)); featID += 1
	featList.append(feat_isFuncWord(enSent[j], featID)); featID += 1

	featList.append(feat_relativeIndexDiff(i, j, len(chSent), len(enSent), featID)); featID += 1

	return featList
