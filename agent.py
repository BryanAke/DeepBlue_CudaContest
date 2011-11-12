import random

class agent(object):
    
    def __init__(self, knowledgeBase):
        self.knowledge = knowledgeBase
        
    def should_draw(self):
        return true
    
    def place_card(self, card):
        return random.randint(0, 19)