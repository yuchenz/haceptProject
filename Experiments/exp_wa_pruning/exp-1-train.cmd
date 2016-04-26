
echo ========== removing all exp-1.train.*
mv exp-1.train.* ~/.recycle/

echo ========== extracting features for the training examples 
../../src_wa_pruning/makeFeatFile.py ../../Data/hacept_train.ch ../../Data/hacept_train.en ../../Data/hacept_train.gwa exp-1.train.feat 24 

echo ========== copying 37 times more True training examples
grep "^ID[0-9\-]*	True" exp-1.train.feat >> tmp 
for i in {1..37}
do
cat tmp >> exp-1.train.feat
done
rm tmp

echo ========== training a mallet maxent model using these training examples
~/tools/mallet/mallet-2.0.7/bin/mallet import-file --input exp-1.train.feat --output /dev/shm/train.mallet

~/tools/mallet/mallet-2.0.7/bin/mallet train-classifier --input /dev/shm/train.mallet --output-classifier exp-1.train.feat.model --trainer MaxEnt
