from parlai.core.teachers import DialogTeacher
from .build import build, TASK_DIR, TXT_DIR, TXT_FILE

import os 

class ClinicalTrialTeacher(DialogTeacher):
    """
    Reads clinical trial data one at a time
    """
    def __init__(self, opt, shared=None):
        self.id = 'clinical_trials'
        build(opt)
        self.opt = opt
        opt['datafile'] = os.path.join(opt['datapath'])
        self.id = 'clinical_trials'
        super().__init__(opt, shared)

    def setup_data(self, path):
        all_trials_txt = os.path.join(path, TASK_DIR, TXT_DIR, TXT_FILE)
        with open(all_trials_txt) as f:
            for line in f.readlines():
                yield (line, ['']), True

class DefaultTeacher(ClinicalTrialTeacher):
    pass