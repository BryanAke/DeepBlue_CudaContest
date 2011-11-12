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
            ## primary check if it is directly adjacent
            if(topCard in self.knowledge.getNumsAdjacentToRuns()):
                return True
            ## greedily find ordered index (least)
            orderedIndex = algorithms.closestValidFit(topCard, self.knowledge.rack)
            utility = -1
            if(algorithms.normal_or_relative(self.knowledge.rack) == 0):
                ## check happiness at that index
                utility = algorithms.getHappiness(topCard, orderedIndex)
                ## check if happy is greater than threshhold
                if(utility > knowledge_base.kHappy and utility > self.knowledge.happiness[orderedIndex]):
                    return False
                else:
                    return True
            else:
                utility = algorithms.getScore(self.knowledge.rack) - algorithms.getOrderedScore(self.knowledge.rack, topCard)
                if(utility > 0):
                    return False
                else:
                    return True
        else:
            return True

    def place_card(self, card):
        if(card in self.knowledge.getNumsAdjacentToRuns()):
            for i in range(0, len(self.knowledge.rack)-1):
                if(self.knowledge.rack[i] - card == 1):
                    return i - 1
                elif(card - self.knowledge.rack[i] == 1):
                    return i + 1
        return algorithms.closestValidFit(card, self.knowledge.rack)
    
class orderingAgent(Agent):
    def shouldDraw(self):
        return False
    
    def place_card(self, card):
        #info(card/80.0, int(card/80.0 * 20))
        return int((card/80.0) * 20)
        #highest_wgo = 0
        #highest_idx = 0
        #rack = self.knowledge.rack
        #for i in range(0, len(rack)):
        #    if rack[i] > highest_wgo and rack[i] < card and self.knowledge.happiness[i] > .8:
        #        highest_wgo = rack[i]
        #        highest_idx = i
        #if (i is 0 and card > 15):
        #return i + 1
    
