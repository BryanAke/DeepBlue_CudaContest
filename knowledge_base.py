from __future__ import division
import random

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