import random
import knowledge_base
import algorithms
import math

import logging
from logging import debug, info, warning, error, exception, critical

class Agent(object):

    def __init__(self, knowledgeBase):
        self.knowledge = knowledgeBase
        
        self.cachedSlot = None

    def should_draw(self):
        ## get the top of the discard pile
        topCard = -1
        if(len(self.knowledge.discard_pile) > 0):
            topCard = self.knowledge.peek_discard()
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
        
        top_card = self.knowledge.discard_pile[-1]
        
        runIdx = self.knowledge.findRunIdx(top_card)
        if(runIdx is not None):
            self.cachedSlot = runIdx
            return False
        
        if algorithms.adjacent_inversions(self.knowledge.rack) > 0:
            sorted_idx = self.knowledge.speculateSorted(card)
            if sorted_idx != -1:
                self.cachedSlot = sorted_idx
                return False
        
        if algorithms.adjacent_inversions(self.knowledge.rack) >= 5:
            
            idealSlot = self.knowledge.getIdealSlot(top_card)        
            if(algorithms.getHappiness(top_card, idealSlot) >= knowledge_base.kOK > self.knowledge.happiness[idealSlot]):
                self.cachedSlot = idealSlot
                return False
            
        return True
    
    def place_card(self, card):
        if self.cachedSlot is not None:
            i = self.cachedSlot
            self.cachedSlot = None
            return i
        
        #info(card/80.0, int(card/80.0 * 20))
        rack = self.knowledge.rack         
        info("Adjacent Inversions: (%s)", repr(algorithms.adjacent_inversions(rack)))
        
        runIdx = self.knowledge.findRunIdx(card)
        if(runIdx is not None):
            return runIdx
        
        else:
            currentSpot = self.knowledge.getIdealSlot(card)
            prev = -1
            while( (0 <= currentSpot < 20) and self.knowledge.happiness[currentSpot] > 
                   (algorithms.getHappiness(card, currentSpot))):
                
                if self.knowledge.isInRun(rack[currentSpot]):
                    run = self.knowledge.getRun(rack[currentSpot])
                    if card < run[0]:
                        return run[2] - 1
                    else:
                        return run[3]
                else:
                    if(currentSpot == prev):
                        break
                    
                    prev = currentSpot
                    if (card > rack[currentSpot]):
                        currentSpot += 1
                    else:
                        currentSpot -= 1
            return currentSpot
