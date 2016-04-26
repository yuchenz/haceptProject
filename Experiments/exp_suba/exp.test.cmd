
ps=gps
#wa=exp2gdfa_wa
#wa=exp2union_wa
wa=exp1gdfa_wa
#waFile=../exp_wa_pruning/exp-2.gdfa_pruned.testing.wa 
#waFile=../exp_wa_pruning/exp-2.union_pruned.testing.wa 
waFile=../exp_wa_pruning/exp-1a.gdfa.test.feat.auto.wa

echo ========== removing all exp.$ps.$wa.test.*
mv exp.$ps.$wa.test.* ~/.recycle/

echo ========== extracting subtree pairs and features for the testing examples
../../src_suba_eval/makeFeatFile_fromCompiled.py ../../Data/hacept_test.ch ../../Data/hacept_test.en ../../Data/hacept_test.ch.gps ../../Data/hacept_test.en.gps $waFile ../../Data/hacept_test.gsuba exp.$ps.$wa.test.feat

mv koala.suba exp.$ps.$wa.test.suba

echo ========== classifying the testing examples
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input exp.$ps.$wa.test.feat --output exp.$ps.$wa.test.feat.auto --classifier exp.gps.gwa.train.feat.model

echo ========== evaluating subtree alignments on the testing examples 
../../src_suba_eval/eval.py ../../Data/hacept_test.gsuba exp.$ps.$wa.test.feat.auto

echo ========== gold subtree coverage by extracted suba: # gold suba, # false suba, # all suba
grep -c "^ID[0-9\-]*	True" exp.$ps.$wa.test.feat
grep -c "^ID[0-9\-]*	False" exp.$ps.$wa.test.feat
wc -l exp.$ps.$wa.test.feat
