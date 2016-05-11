
#wa=union
wa=gdfa

echo ========== removing all exp-2.$wa*
mv exp-2.$wa*.training.* ~/.recycle/

echo ========== getting $wa-inter difference wa points from the training data set as the training examples
../../src_wa_pruning/diff_waF.py ../../Data/hacept_train.${wa}WA ../../Data/hacept_train.interWA exp-2.$wa-inter.training.wa

echo ========== extracting features for the training examples 
../../src_wa_pruning/makeFeatFile2.py ../../Data/hacept_train.ch ../../Data/hacept_train.en ../../Data/hacept_train.gwa exp-2.$wa-inter.training.wa exp-2.$wa-inter.training.feat

echo ========== training a mallet maxent model using these training examples
~/tools/mallet/mallet-2.0.7/bin/mallet import-file --input exp-2.$wa-inter.training.feat --output /dev/shm/train.mallet

~/tools/mallet/mallet-2.0.7/bin/mallet train-classifier --input /dev/shm/train.mallet --output-classifier exp-2.$wa-inter.training.feat.model --trainer MaxEnt

