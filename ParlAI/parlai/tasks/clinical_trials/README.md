# Clinical Trials Retrival Task

Build the project:
python3 setup.py develop

Display clinical trials data:
python3 examples/display_data.py -t clinical_trials

Construct a TFIDF matrix for use in retrieval for the clinical trials task(eval step takes a long time, you might want to skip)
python3 examples/train_model.py -m tfidf_retriever -t clinical_trials -mf /tmp/clinical_trials_tfidf -dt train:ordered -eps 1

Run the TFIDF model interactively:
python3 examples/interactive.py -mf /tmp/clinical_trials_tfidf