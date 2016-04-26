
#wa=union
wa=gdfa

echo ========== removing all exp-1a.$wa.test.*
mv exp-1a.$wa.test.* ~/.recycle/

echo ========== extracting features for the testing examples
../../src_wa_pruning/makeFeatFile.py ../../Data/hacept_test.ch ../../Data/hacept_test.en ../../Data/hacept_test.${wa}WA exp-1a.$wa.test.feat 24
grep "^ID[0-9\-]*	True" exp-1a.${wa}.test.feat > tmp
cat tmp > exp-1a.$wa.test.feat
rm tmp

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp-1a.$wa.test.feat --output exp-1a.$wa.test.feat.auto --classifier exp-1.train.feat.model

echo ========== converting the mallet output auto file into a wa file
../../src_wa_pruning/malletAuto2wa.py exp-1a.$wa.test.feat.auto exp-1a.$wa.test.feat.auto.wa

echo ========== computing the accuracy on the test data set
evalMalletMaxEnt.py exp-1a.$wa.test.feat exp-1a.$wa.test.feat.auto 

echo ========== evaluating the file $wa_pruned wa file
../../src_wa_pruning/evalWA.py ../../Data/hacept_test.gwa exp-1a.$wa.test.feat.auto.wa

