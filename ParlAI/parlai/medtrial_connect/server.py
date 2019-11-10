from flask import Flask, request
from parlai.core.agents import Agent
from parlai.core.params import ParlaiParser
from parlai.core.message import Message
from parlai.core.agents import create_agent
from parlai.core.worlds import MultiAgentDialogWorld
from parlai.utils.misc import Opt

from config import PORT_NUM, URL, MODEL_FILE_PATH

# parlai agent for search input
class QueryAgent(Agent):
    def __init__(self, opt, shared=None, search_input=None):
        super().__init__(opt)
        self.id = 'query_agent'
        self.opt = opt
        self.searchInput = search_input
    
    def observe(self, observation):
        pass

    def act(self):
        reply = Message()
        reply['id'] = self.getID()
        reply['text'] = self.searchInput
        return reply

# setup parlai environment
# parlai_parser = ParlaiParser(True, True, 'Parser For MedTrialConnect Server')
parlai_opt = Opt()
parlai_opt['model_file'] = MODEL_FILE_PATH
parlai_opt['task'] = None
retriever_agent = create_agent(parlai_opt, requireModelExists=True)

# setup flask app
app = Flask(__name__)

@app.route(URL, methods=['GET'])
def search():
    query_agent = QueryAgent(parlai_opt, search_input=request.args.get('query'))
    world = MultiAgentDialogWorld(parlai_opt, [query_agent, retriever_agent])
    world.parley()
    retriever_output = world.acts[-1]
    candidates = retriever_output['candidates']
    candidate_scores = retriever_output['candidate_scores']
    for i in range(len(candidates)):
        candidates[i]['tfidf_score'] = candidate_scores[i]
    return {'search_results':candidates}