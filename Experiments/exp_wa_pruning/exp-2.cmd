
echo ========== removing all exp-2.gdfa*
mv exp-2.gdfa* ~/.recycle/

echo ========== getting gdfa-inter difference wa points from the training data set as the training examples
../../src_wa_pruning/diff_waF.py ../../Data/hacept_train.gdfaWA ../../Data/hacept_train.interWA exp-2.gdfa-inter.training.wa

echo ========== extracting features for the training examples 
../../src_wa_pruning/makeFeatFile2.py ../../Data/hacept_train.ch ../../Data/hacept_train.en ../../Data/hacept_train.gwa exp-2.gdfa-inter.training.wa exp-2.gdfa-inter.training.feat

echo ========== training a mallet maxent model using these training examples
~/tools/mallet/mallet-2.0.7/bin/mallet import-file --input exp-2.gdfa-inter.training.feat --output /dev/shm/train.mallet

~/tools/mallet/mallet-2.0.7/bin/mallet train-classifier --input /dev/shm/train.mallet --output-classifier exp-2.gdfa-inter.training.feat.model --trainer MaxEnt

echo ========== getting gdfa-inter difference wa points from the test data set as the test examples
../../src_wa_pruning/diff_waF.py ../../Data/hacept_test.gdfaWA ../../Data/hacept_test.interWA exp-2.gdfa-inter.testing.wa

echo ========== extracting features for the testing examples
../../src_wa_pruning/makeFeatFile2.py ../../Data/hacept_test.ch ../../Data/hacept_test.en ../../Data/hacept_test.gwa exp-2.gdfa-inter.testing.wa exp-2.gdfa-inter.testing.feat

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp-2.gdfa-inter.testing.feat --output exp-2.gdfa-inter.testing.feat.auto --classifier exp-2.gdfa-inter.training.feat.model

echo ========== converting the mallet output auto file into a wa file
../../src_wa_pruning/malletAuto2wa.py exp-2.gdfa-inter.testing.feat.auto exp-2.gdfa-inter.testing.feat.auto.wa

echo ========== merging the auto gdfa-inter wa file with inter wa file
../../src_wa_pruning/merge_waF.py exp-2.gdfa-inter.testing.feat.auto.wa ../../Data/hacept_test.interWA exp-2.gdfa_pruned.testing.wa

echo ========== evaluating the file gdfa_pruned wa file
../../src_wa_pruning/evalWA.py ../../Data/hacept_test.gwa exp-2.gdfa_pruned.testing.wa
