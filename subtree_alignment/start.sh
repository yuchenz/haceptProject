
echo "./makeFeatFile.py ../../hacept_raw_data/train/ training.feat"
./makeFeatFile.py ../../hacept_raw_data/train/ training.feat 

echo "./makeFeatFile.py ../../hacept_raw_data/test/ testing.feat"
./makeFeatFile.py ../../hacept_raw_data/test/ testing.feat 

echo "~/tools/mallet/mallet-2.0.7/bin/mallet import-file --input training.feat --output train.mallet"
~/tools/mallet/mallet-2.0.7/bin/mallet import-file --input training.feat --output train.mallet
echo "~/tools/mallet/mallet-2.0.7/bin/mallet train-classifier --input train.mallet --output-classifier training.feat.model --trainer MaxEnt"
~/tools/mallet/mallet-2.0.7/bin/mallet train-classifier --input train.mallet --output-classifier training.feat.model --trainer MaxEnt

echo "~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input testing.feat --output testing.feat.auto --classifier training.feat.model"
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input testing.feat --output testing.feat.auto --classifier training.feat.model 
echo "~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input training.feat --output training.feat.auto --classifier training.feat.model"
~/tools/mallet/mallet-2.0.7/bin/mallet classify-file --input training.feat --output training.feat.auto --classifier training.feat.model

echo evalMalletMaxEnt.py training.feat training.feat.auto
evalMalletMaxEnt.py training.feat training.feat.auto
echo evalMalletMaxEnt.py testing.feat testing.feat.auto 
evalMalletMaxEnt.py testing.feat testing.feat.auto 
