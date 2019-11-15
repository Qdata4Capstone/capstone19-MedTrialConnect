# MedTrialConnect
## Build ParlAI Project
```bash
$ cd ParlAI/
$ python3 setup.py develop
```
## Download & Display Data
```bash
$ python3 examples/display_data.py -t clinical_trials
```
## Construct Sparse Matrix(validation takes a very long time, can be skipped by entering Ctrl+C when terminal shows validating...)
```bash
$ python3 examples/train_model.py -m tfidf_retriever -t $ clinical_trials -mf MODEL_PATH -dt train:ordered -eps 1
```
## Setup Flask Server
```bash
$ cd parlai/medtrial_connect/
```
## Config URL, PORT, MODEL_PATH
```bash
#modify parlai/medtrial_connect/config.py
```
## Run Flask Server
```bash
$ export FLASK_APP=server.py
$ flask run --host=0.0.0.0
```
## Setup React-Native Dev Environment
```bash
#visit https://facebook.github.io/react-native/docs/getting-started
```
## Build React Native App With IOS Simulator On MacOS
```bash
$ cd ../../../App
$ npm install
$ cd ios/
$ pod install
$ cd ..
$ react-native run-ios
```