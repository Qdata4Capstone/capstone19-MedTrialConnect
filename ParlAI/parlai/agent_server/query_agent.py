from parlai.core.agents import Agent
from parlai.core.message import Message


class QueryAgent(Agent):
    def __init__(self, opt, shared=None):
        super().__init__(opt)
        self.id = 'queryAgent'
        self.opt = opt
    
    def observe(self, observation):
        pass

    def act(self):
        reply = Message()
        reply['id'] = self.getID()
        reply['text'] = self.opt['query']
        return reply



    
