from __future__ import division
import random
import pickle
import os

## constants
kCardCount = 80
kRackSize = 20

## the knowledge base which contains all of the knowledge
## which the player know in the game
class Knowledge(object):
    ## initializes the knowledge base
    def __init__(self):
        self.happiness = [0]*kRackSize
        self.impossibilities = [False]*kRackSize
        self.discard_pile = []
        self.deck = set()
       
    ## populates the boolean list of impossibilities 
    def find_impossibilities_and_happiness(self, rack):
        for i in range(0, len(rack)):
            if (kCardCount - rack[i] < kRackSize - i or i + 1 > rack[i]):
                self.impossibilities[i] = True
            else:
                self.impossibilities[i] = False
            self.happiness[i] = 1.0 - abs(((rack[i]/kCardCount) - ((i+1)/kRackSize)))
            
    def rackContains(self, rack, val):
        idx = rack.index(val)
        return (idx != -1) and not self.impossibilities[idx]
    
    def rackContainsAdjacent(self, rack, val):
        return self.rackContains(rack, val + 1) or self.rackContains(rack, val - 1)

    def rackContainsRuns(self, rack):
        #return a list of tuples representing runs
        ret = []
        run = []
        for i in rack:
            if not run or i is run[-1] :
                run.append(i)
            else:
                ret.append(tuple(run))
                run = [i]
        return [i for i in ret if len(i) > 1]
    
    def getNumsAdjacentToRuns(self, rack):
        runs = self.rackContainsRuns(rack)
        importantCards = set()
        for run in runs:
            importantCards.add(run[0] - 1)
            importantCards.add(run[-1] + 1)
        return importantCards
    
    def pickle(self):
        fileName = os.path.join("pickledKnowledge", self.game_id + "__" + self.other_player_id + ".pickle")
        with open(fileName, 'w') as file:
            pickle(self, file)
        
            
def test_main():
    rack = [0]*kRackSize
    for i in range(0, kRackSize):
        rack[i] = random.randint(1, kCardCount)
    kb = Knowledge()
    kb.find_impossibilities_and_happiness(rack)
    print "Rack: " + str(rack)
    print "Happiness: " + str(kb.happiness)
    print "Impossibilities: " + str(kb.impossibilities)
    
test_main()