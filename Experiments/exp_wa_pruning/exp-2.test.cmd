
#wa=union
wa=gdfa

echo ========== removing all exp-2.$wa*
mv exp-2.$wa*.testing.* ~/.recycle/

echo ========== getting $wa-inter difference wa points from the test data set as the test examples
../../src_wa_pruning/diff_waF.py ../../Data/hacept_test.${wa}WA ../../Data/hacept_test.interWA exp-2.$wa-inter.testing.wa

echo ========== extracting features for the testing examples
../../src_wa_pruning/makeFeatFile2.py ../../Data/hacept_test.ch ../../Data/hacept_test.en ../../Data/hacept_test.gwa exp-2.$wa-inter.testing.wa exp-2.$wa-inter.testing.feat

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp-2.$wa-inter.testing.feat --output exp-2.$wa-inter.testing.feat.auto --classifier exp-2.$wa-inter.training.feat.model

echo ========== converting the mallet output auto file into a wa file
../../src_wa_pruning/malletAuto2wa.py exp-2.$wa-inter.testing.feat.auto exp-2.$wa-inter.testing.feat.auto.wa

echo ========== merging the auto $wa-inter wa file with inter wa file
../../src_wa_pruning/merge_waF.py exp-2.$wa-inter.testing.feat.auto.wa ../../Data/hacept_test.interWA exp-2.${wa}_pruned.testing.wa

echo ========== computing the accuracy on the test data set
evalMalletMaxEnt.py exp-2.$wa-inter.testing.feat exp-2.$wa-inter.testing.feat.auto 

echo ========== evaluating the file $wa_pruned wa file
../../src_wa_pruning/evalWA.py ../../Data/hacept_test.gwa exp-2.${wa}_pruned.testing.wa

