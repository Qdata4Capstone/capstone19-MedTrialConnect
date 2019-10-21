# Clinical Trials Retrival Task

Build the project:
```bash
python3 setup.py develop
```
Display clinical trials data:
```bash
python3 examples/display_data.py -t clinical_trials
```
Construct a TFIDF matrix for use in retrieval for the clinical trials task(eval step takes a long time, you might want to skip)
```bash
python3 examples/train_model.py -m tfidf_retriever -t clinical_trials -mf CLINICAL_TRIALS_MODEL_FILE_PATH -dt train:ordered -eps 1
```
Run the TFIDF model interactively:
```bash
python3 examples/interactive.py -mf CLINICAL_TRIALS_MODEL_FILE_PATH
```
