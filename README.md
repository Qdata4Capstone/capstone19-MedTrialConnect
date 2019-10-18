# MedTrialConnect
## Building the ParlAI backend
1. build the parlai project:  
```bash 
python3 setup.py develop
```
2. download, build and display the clinical trials data:  
```bash
python3 examples/display_data.py -t clinical_trials
```
3. build tf-idf sparse matrix
```bash
python3 examples/train_model.py -m tfidf_retriever -t clinical_trials -mf CLINICAL_TRIALS_MODEL_FILE_PATH -dt train:ordered -eps 1
```
4. start tf-idf retriever agent as a server, config url and port and model file path in server.py
```bash
python3 parlai/agent_server/server.py --port PORT_NUMBER --model_file CLINICAL_TRIALS_MODEL_FILE_PATH
```