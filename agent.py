import random
import knowledge_base
import algorithms

class Agent(object):

    def __init__(self, knowledgeBase):
        self.knowledge = knowledgeBase

    def should_draw(self):
        ## get the top of the discard pile
        topCard = -1
        if(len(self.knowledge.discard_pile) > 0):
            topCard = self.knowledge.discard_pile[0]
        if(topCard >= 0):
            ## greedily find ordered index (least)
            orderedIndex = algorithms.closestValidFit(topCard, self.knowledge.rack)
            ## check happiness at that index
            happy = algorithms.getHappiness(topCard, orderedIndex)
            ## check if happy is greater than threshhold
            if(happy > knowledge_base.kOk and happy > knowledge_base.happiness[orderedIndex]):
                return False
            else:
                return True
        else:
            return True

    def place_card(self, card):
        return algorithms.closestValidFit(card, self.knowledge.rack)