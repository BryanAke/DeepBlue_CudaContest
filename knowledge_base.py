from __future__ import division

from logging import debug, info, warning, error, exception, critical

import random
import pickle
import os
import math

import algorithms

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

        self.runs = []

        self.game_id = args['game_id']
        self.player_id = args['player_id']
        self.other_player_id = args['other_player_id']
        self.other_rack = [None] * kRackSize
        self.other_other_cards = []

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
        self.update_runs()

    def their_move(self, move, discard):
        if move['move'] == 'take_discard':
            card = self.pop_discard()
            self.other_rack[move['idx']] = card
            self.moves.append([False, False, move['idx'], card])
        elif move['move'] == 'take_deck':
            self.other_rack[move['idx']] = 0
            self.draw()
            self.moves.append([False, True, move['idx'], 0])

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
            if drew:
                self.draw()
                self.deck.discard(card)
            else:
                self.pop_discard()
            self.push_discard(self.rack[idx])
            self.rack[idx] = card

        self.update_impossibilites_and_happiness_at_idx(idx)
        self.update_runs()

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

    def getIdealSlot(self, card):
        return int(math.ceil((card/80.0) * 20) -1)

    def update_impossibilites_and_happiness_at_idx(self, idx):
        if (kCardCount - self.rack[idx] < kRackSize - idx or idx + 1 > self.rack[idx]):
            self.impossibilities[idx] = True
        else:
            self.impossibilities[idx] = False
        self.happiness[idx] = 1.0 - abs(((self.rack[idx]/kCardCount) - ((idx+1)/kRackSize)))

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
            if not run or i == run[-1] + 1:
                run.append(i)
            else:
                ret.append(tuple(run))
                run = [i]
        return [i for i in ret if len(i) > 1]

    def checkDiscard(self, num):
        for elem in self.discard_pile:
            if num is elem:
                return True
        for elem in self.other_rack:
            if num is elem:
                return True
        return False

    #find out whether 5 card run is possible to create
    def getRunCompletion(self, run):
        ascend = range(run[1]+1,run[0]+5)[:len(self.rack)-run[3]]
        decend = range(run[0]-1,run[1]-5,-1)[:run[2]]
        a = run[3]-run[2]
        d = run[3]-run[2]
        if (run[0]+5) <= 80:
            for num in ascend:
                if self.checkDiscard(num):
                    break
                else:
                    a += 1
        if (run[1]-5) >=1:
            for num in decend:
                if self.checkDiscard(num):
                    break
                else:
                    d += 1
        if a < 5 and d < 5:
            a,d = 0,0
        res = (a,d)
        return res

    def update_runs(self):
        self.runs = []
        start = 0
        stop = 1
        for i in xrange(1,len(self.rack)):
            if self.rack[i] == self.rack[i-1]+1:
                stop = i+1
            else:
                if start != stop:
                    self.runs.append((self.rack[start], self.rack[stop-1], start, stop))
                start = i
                stop = i + 1
        if start != stop:
            self.runs.append((self.rack[start], self.rack[stop-1], start, stop))

        def run_weight(r):
            w = (r[3]-r[2]) * algorithms.getHappiness((r[0]+r[1])/2, (r[2]+r[3]-1)/2)
            w *= sum(getRunCompletion(r))
            return w

        self.runs.sort(key=run_weight, reverse=True)

        # When runs are out-of-order

        while self.runs and run_weight(self.runs[-1]) == 0:
            self.runs.pop()

    def getNumsAdjacentToRuns(self):
        importantCards = set()
        for run in self.runs:
            importantCards.add(run[0]-1)
            importantCards.add(run[1]+1)

        #possible edge cases
        importantCards.discard(0)
        importantCards.discard(81)

        return importantCards


    def getIndicesInSortedArr(self, card):
        for i in range(len(self.rack)):
            if card < self.rack[i]:
                return (i-1, i)

        return (19, 19)

    def pickLocationInSortedArr(self, card):
        idxs = self.getIndicesInSortedArr(card)
        if idxs[0] == -1:
            return 0

        if self.countTheoreticalRunSize(card, idxs[0]) > self.countTheoreticalRunSize(card, idxs[1]):
            return idxs[0]
        else:
            return idxs[1]


    def countTheoreticalRunSize(self, card, idx):

        rack = self.rack
        count = 1
        lastVal = card

        for i in range(idx + 1, len(self.rack)):
            if rack[i] is lastVal + 1:
                count += 1
                lastVal = rack[i]
            else:
                break
        lastVal = card
        for i in range(idx -1, -1, -1):
            if rack[i] is lastVal - 1:
                count += 1
                lastVal = rack[i]
            else:
                break

        return count

    ## returns the probabilty of drawing a card from the deck
    def probabilityToDraw(self, card):
        if (card in self.discard_pile and card != peak_discard()):
            return 0.0
        removedCards = kCardCount - kRackSize - len(self.discard_pile)
        return 1/removedCards

    def pickle(self):
        fileName = os.path.join("pickledKnowledge", str(self.game_id) + "_" + str(self.other_player_id) + ".pickle")
        with open(fileName, 'w') as file:
            pickle.dump(self, file)

def test_main():
    rack = [0]*kRackSize
    for i in range(0, kRackSize):
        rack[i] = random.randint(1, kCardCount)
    args = dict()
    args['game_id'] = 1243
    args['player_id'] = 0
    args['other_player_id'] = 1
    args['initial_discard'] = 3
    kb = Knowledge(args)
    kb.find_impossibilities_and_happiness(rack)
    print "Rack: " + str(rack)
    print "Happiness: " + str(kb.happiness)
    print "Impossibilities: " + str(kb.impossibilities)
    print "Probability to pull a 5: " + str(kb.probabilityToDraw(5))

if __name__ == '__main__':
    test_main()
