import random
import knowledge_base

class agent(object):
    
    def __init__(self, knowledgeBase):
        self.knowledge = knowledgeBase
        
    def should_draw(self):
        ## get the top of the discard pile
        topCard = -1
        if(len(self.knowledge.discard_pile) > 0):
            topCard = self.knowledge.discard_pile[0]
        if(topCard >= 0):
            ## greedily find ordered index (least)
            orderedIndex = random.randint(0, 20)
            ## check happiness at that index
            happy = 1.0 - abs(((topCard/kCardCount) - ((orderedIndex+1)/kRackSize)))
            ## check if happy is greater than threshhold
            if(happy > kOk):
                return true
            else:
                return false
    
    def place_card(self, card):
        return random.randint(0, 19)