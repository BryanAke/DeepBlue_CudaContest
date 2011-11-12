import random
import knowledge_base
import algorithms
import math

class Agent(object):

    def __init__(self, knowledgeBase):
        self.knowledge = knowledgeBase

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
        #if(algorithms.adjacent_inversions(rack) == 0):
            #group cards.
        good_cards = self.knowledge.getNumsAdjacentToRuns()
        top_card = self.knowledge.peek_discard()
        if top_card in good_cards:
            return False
        else:
            return True
        #else:
        #    return False

    def place_card(self, card):
        #info(card/80.0, int(card/80.0 * 20))
        rack = self.knowledge.rack

        # Finish a run.  The runs are sorted in order from "best" to "worst", so complete the first one.
        for run in self.knowledge.runs:
            if card == run[0]-1 and run[2] != 0:
                # We can insert this card at the beginning of the run
                return run[2]-1
            if card == run[1]+1 and run[3] != len(self.knowledge.rack):
                # We can insert this card at the end of the run
                return run[3]+1

        if(algorithms.adjacent_inversions(rack) == 0):
            # We're already in sorted order, so keep it that way.
            for loc in xrange(len(rack)):
                if rack[loc] > card:
                    break
            # We can replace either loc or loc-1, except
            if loc == 0:
                return loc
            for run in self.knowledge.runs:
                if run[2] <= loc < run[3]:
                    # loc conflicts with this run, so use loc-1
                    return loc-1
                if run[2] <= loc-1 < run[3]:
                    # loc-1 conflicts with this run, so use loc
                    return loc
        else:
            # Not yet sorted
            currentSpot = self.knowledge.getIdealSlot(card)

            for k, r in enumerate(self.knowledge.runs):
                if r[2] <= currentSpot < r[3]:
                    # This card collides with a run in the Ideal slot
                    if card < r[0]:
                        if r[0] != 0:
                            newSpot = r[2] - 1
                            delta = +1
                            break
                        else:
                            return 0
                    if car > r[3]:
                        if r[3] != len(rack):
                            newSpot = r[3]
                            delta = -1
                            break
                        else:
                            return r[3] - 1
            else:
                prev = -1
                while(0 <= currentSpot < 20 and self.knowledge.happiness[currentSpot] > (algorithms.getHappiness(card, currentSpot))):
                    if(currentSpot == prev):
                        break

                    prev = currentSpot
                    if (card > rack[currentSpot]):
                        currentSpot += 1
                    else:
                        currentSpot -= 1

                return currentSpot

            if newSpot == currentSpot:
                return currentSpot

            for n, r in enumerate(self.knowledge.runs):
                if r[2] <= newSpot < r[3]:
                    if k < n:
                        return newSpot
                    elif n < k:
                        return newSpot + delta
            return newSpot


        #highest_wgo = 0
        #highest_idx = 0
        #for i in range(0, len(rack)):
        #    if rack[i] > highest_wgo and rack[i] < card and self.knowledge.happiness[i] > .8:
        #        highest_wgo = rack[i]
        #        highest_idx = i
        #if (i is 0 and card > 15):
        #return i + 1
