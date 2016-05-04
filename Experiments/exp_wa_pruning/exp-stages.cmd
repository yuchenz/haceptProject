
wa=gdfa

echo ========== removing all exp-stages.$wa*
mv exp-stages.$wa* ~/.recycle/

echo ========== getting $wa-inter difference wa points from the test data set as the test examples
../../src_wa_pruning/diff_waF.py ../../../temp2/stages.${wa}WA ../../../temp2/stages.interWA exp-stages.$wa-inter.testing.wa

echo ========== extracting features for the testing examples
../../src_wa_pruning/makeFeatFile2.py ../../../temp2/stages.ch ../../../temp2/stages.en ../../../temp2/stages.interWA exp-stages.$wa-inter.testing.wa /dev/shm/exp-stages.$wa-inter.testing.feat
mv /dev/shm/exp-stages.gdfa-inter.testing.feat .

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp-stages.$wa-inter.testing.feat --output /dev/shm/exp-stages.$wa-inter.testing.feat.auto --classifier exp-2.$wa-inter.training.feat.model
mv /dev/shm/exp-stages.gdfa-inter.testing.feat.auto .

echo ========== converting the mallet output auto file into a wa file
../../src_wa_pruning/malletAuto2wa.py exp-stages.$wa-inter.testing.feat.auto /dev/shm/exp-stages.$wa-inter.testing.feat.auto.wa
mv /dev/shm/exp-stages.gdfa-inter.testing.feat.auto.wa .

echo ========== merging the auto $wa-inter wa file with inter wa file
../../src_wa_pruning/merge_waF.py exp-stages.$wa-inter.testing.feat.auto.wa ../../../temp2/stages.interWA /dev/shm/exp-stages.${wa}_pruned.testing.wa
mv /dev/shm/exp-stages.gdfa_pruned.testing.wa .
