
ps=binbps
wa=gdfa_pruned
waFile=../exp_wa_pruning/exp-stages.gdfa_pruned.testing.wa 

echo ========== removing all exp-stages.$ps.$wa.test.*
mv exp-stages.$ps.$wa.test.* ~/.recycle/

echo ========== extracting subtree pairs and features for the testing examples (slow ~ ?? min)
../../src_suba_eval/makeFeatFile_fromCompiled.py ../../../temp2/stages.ch ../../../temp2/stages.en ../../../temp2/stages.ch.bps ../../../temp2/stages.en.bps $waFile None /dev/shm/exp-stages.$ps.$wa.test.feat
mv /dev/shm/exp-stages.$ps.$wa.test.feat .

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp-stages.$ps.$wa.test.feat --output /dev/shm/exp-stages.$ps.$wa.test.feat.auto --classifier exp.gps.gwa.train.feat.model
mv /dev/shm/exp-stages.$ps.$wa.test.feat.auto .

../../src_wa_pruning/malletAuto2wa.py exp-stages.$ps.$wa.test.feat.auto exp-stages.$ps.$wa.test.feat.auto.suba

../../src_suba_eval/ruleExtract.py ../../../temp2/stages.ch ../../../temp2/stages.en exp-stages.$ps.$wa.test.feat.auto.suba $waFile > exp-stages.$ps.$wa.test.feat.auto.suba.rules 2> exp-stages.$ps.$wa.test.feat.auto.suba.invRules

