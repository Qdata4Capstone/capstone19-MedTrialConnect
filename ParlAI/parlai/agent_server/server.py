from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from parlai.scripts.interactive import setup_args
from parlai.core.worlds import create_task
from parlai.core.agents import create_agent
from parlai.agents.tfidf_retriever.tfidf_retriever import TfidfRetrieverAgent
from query_agent import QueryAgent

CLINICAL_TRIALS_URL = "/clinicaltrials"

class ClinicalTrialsTFIDFRetrieverHandler(RequestHandler):
    def initialize(self, opt):
        self.opt = opt
        self.retriever_agent = create_agent(self.opt, requireModelExists=True)

    def get(self):
        self.opt['query'] = self.get_argument('query', default='')
        # setup agents
        query_agent = QueryAgent(self.opt)
        # get retriever output
        world = create_task(self.opt, [query_agent, self.retriever_agent])
        world.parley()
        retriever_output = world.acts[-1]
        # retrieve trial data as dict
        candidates = retriever_output['candidates']
        candidate_scores = retriever_output['candidate_scores']
        for i in range(len(candidates)):
            candidates[i]['tfidf_score'] = candidate_scores[i]
        self.write({'candidates':candidates})

if __name__ == '__main__':
    # setup arguments
    parser = setup_args()
    parser.add_argument("--port", help="server port number", type=int)
    opt = parser.parse_args()
    urls = [(CLINICAL_TRIALS_URL, ClinicalTrialsTFIDFRetrieverHandler, dict(opt=opt))]
    app = Application(urls)
    app.listen(opt['port'])
    print(f'server listening on port {opt["port"]}')
    IOLoop.instance().start()