from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from parlai.scripts.interactive import setup_args
from parlai.core.worlds import create_task
from parlai.core.agents import create_agent
from parlai.agents.tfidf_retriever.tfidf_retriever import TfidfRetrieverAgent
from query_agent import QueryAgent

PORT = 8888
CLINICAL_TRIALS_URL = "/clinicaltrials"
TFIDF_RETRIEVER_MF = '/tmp/clinical_trials_tfidf'

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
        self.write({'candidates':candidates, 'candidate_scores':candidate_scores})

def make_app():
    # setup arguments
    parser = setup_args()
    opt = parser.parse_args()
    opt['model_file'] = TFIDF_RETRIEVER_MF
    urls = [(CLINICAL_TRIALS_URL, ClinicalTrialsTFIDFRetrieverHandler, dict(opt=opt))]
    return Application(urls)

if __name__ == '__main__':
    app = make_app()
    app.listen(PORT)
    print(f'server listening on port {PORT}')
    IOLoop.instance().start()