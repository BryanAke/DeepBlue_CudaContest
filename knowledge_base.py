from __future__ import division

from logging import debug, info, warning, error, exception, critical

import random
import pickle
import os

## constants
kCardCount = 80
kRackSize = 20

#thresholds
kVeryUnhappy = .4
kUnhappy = .6
kOk = .8
kHappy = .9
kVeryHappy = 1.0

## the knowledge base which contains all of the knowledge
## which the player know in the game
class Knowledge(object):
    ## initializes the knowledge base
    def __init__(self, args):
        self.happiness = [0]*kRackSize
        self.impossibilities = [False]*kRackSize
        self.discard_pile = []
        self.deck = set(xrange(1,kCardCount + 1))
        self.deck_size = kCardCount - 2 * kRackSize - 1

        self.game_id = args['game_id']
        self.player_id = args['player_id']
        self.other_player_id = args['other_player_id']
        self.other_rack = [None] * kRackSize

        self.orig_discard = args['initial_discard']
        self.rack = self.orig_rack = []
        self.moves = []

        self.push_discard(args['initial_discard'])

        self.time = int(1e6)

    def push_discard(self, card):
        debug("Added %d to the discard pile", card)
        self.discard_pile.append(card)
        self.deck.discard(card)

    def pop_discard(self):
        card = self.discard_pile.pop()
        debug("Took %d from the discard pile", card)
        return card

    def peek_discard(self):
        return self.discard_pile[-1]

    def ttg(self, time):
        self.time = time

    def set_initial_rack(self, rack):
        self.rack = self.orig_rack = rack
        self.deck.difference_update(rack)

    def their_move(self, move, discard):
        if move['move'] == 'take_discard':
            card = self.pop_discard()
            self.other_rack[move['idx']] = card
            debug("The other player took %d and put it in slot %d.", card, move['idx'])
            self.moves.append([False, False, move['idx'], card])
        elif move['move'] == 'take_deck':
            self.other_rack[move['idx']] = 0
            self.draw()
            self.moves.append([False, True, move['idx'], 0])
            debug("The other player drew and put it in slot %d.", move['idx'])
        elif move['move'] == 'no_move':
            debug("The other player made no move.")
        elif move['move'] == 'illegal':
            debug("The other player made an illegal move: %s.", move['reason'])
        elif move['move'] == 'timed_out':
            debug("The other player timed out.")
        else:
            error("The other player did something unknown!")

        self.push_discard(discard)

    def our_move(self, move, drew, idx, card):
        if move == 'next_player_turn':
            self.moves.append([True, drew, idx, card])
            debug("We moved successfully")
            if drew:
                self.draw()
                self.deck.discard(card)
            else:
                self.pop_discard()
            self.push_discard(self.rack[idx])
            self.rack[idx] = card
        elif move == 'move_ended_game':
            self.moves.append([True, drew, idx, card])
            debug("The game is over: %s", args['reason'])
            if drew:
                self.draw()
                self.deck.discard(card)
            else:
                self.pop_discard()
            self.push_discard(self.rack[idx])
            self.rack[idx] = card
        elif move == 'illegal':
            error("We made an illegal move: %s", args['reason'])
        elif move == 'timed_out':
            error("We timed out.")
        else:
            error("We did something unexpected.")

    def final(self, us, them, reason):
        self.our_score = us
        self.their_schore = them
        self.finish_criterion = reason

    def draw(self):
        self.deck_size -= 1
        if self.deck_size == 0:
            self.deck = set(self.discard_pile[:-1])
            self.deck_size = len(self.deck)
            self.discard = [self.discard_pile[-1]]

    ## populates the boolean list of impossibilities
    def find_impossibilities_and_happiness(self, rack):
        for i in range(0, len(rack)):
            if (kCardCount - rack[i] < kRackSize - i or i + 1 > rack[i]):
                self.impossibilities[i] = True
            else:
                self.impossibilities[i] = False
            self.happiness[i] = 1.0 - abs(((rack[i]/kCardCount) - ((i+1)/kRackSize)))

    def update_impossibilites_and_happiness_at_idx(self, idx):
        if (kCardCount - self.rack[idx] < kRackSize - idx or idx + 1 > self.rack[idx]):
            self.impossibilities[idx] = True
        else:
            self.impossibilities[idx] = False
        self.happiness[idx] = 1.0 - abs(((rack[idx]/kCardCount) - ((idx+1)/kRackSize)))
        
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

    def getNumsAdjacentToRuns(self):
        runs = self.rackContainsRuns(self.rack)
        importantCards = set()
        for run in runs:
            importantCards.add(run[0] - 1)
            importantCards.add(run[-1] + 1)
        
        #possible edge cases
        importantCards.discard(0)
        importantCards.discard(81)
            
        return importantCards

    def pickle(self):
        fileName = os.path.join("pickledKnowledge", str(self.game_id) + "_" + str(self.other_player_id) + ".pickle")
        with open(fileName, 'w') as file:
            pickle.dump(self, file)

# def test_main():
#     rack = [0]*kRackSize
#     for i in range(0, kRackSize):
#         rack[i] = random.randint(1, kCardCount)
#     kb = Knowledge()
#     kb.find_impossibilities_and_happiness(rack)
#     print "Rack: " + str(rack)
#     print "Happiness: " + str(kb.happiness)
#     print "Impossibilities: " + str(kb.impossibilities)
#
# if __name__ == '__main__':
#     test_main()