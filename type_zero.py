from __future__ import division

from SimpleXMLRPCServer import SimpleXMLRPCServer

import logging
from logging import debug, info, warning, error, exception, critical

import functools
import socket
import sys

import agent
import knowledge_base

LISTEN = ('0.0.0.0', 1337)

# This is a hack to patch slow socket.getfqdn calls that
# BaseHTTPServer (and its subclasses) make.
# See: http://bugs.python.org/issue6085
# See: http://www.answermysearches.com/xmlrpc-server-slow-in-python-how-to-fix/2140/

import BaseHTTPServer

def _bare_address_string(self):
    host, port = self.client_address[:2]
    return '%s' % host

BaseHTTPServer.BaseHTTPRequestHandler.address_string = _bare_address_string

# End hack.

logging.basicConfig(level=logging.DEBUG)

def trycatch(f):
    @functools.wraps(f)
    def fw(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            exception("Exception in %s", f.__name__)
            raise
    return fw

class RackO(object):
    @trycatch
    def ping(self, p):
        debug("ping(%s)", repr(p))
        return "pong"

    @trycatch
    def start_game(self, args):
        debug("start_game(%s)", repr(args))

        self.game_id = args['game_id']

        self.k = knowledge_base.Knowledge(args)
        self.a = agent.orderingAgent(self.k)
        ##self.a = agent.Agent(self.k)

        info("Starting game %d going %s against team %d.", args['game_id'], ("first", "second")[args['player_id']], args['other_player_id'])

        return ""

    @trycatch
    def get_move(self, args):
        debug("get_move(%s)", repr(args))

        if args['game_id'] != self.game_id:
            error("Got a request for a move in non-active game.")

        if not self.k.rack:
            self.k.set_initial_rack(args['rack'])

        self.k.ttg(args['remaining_microseconds'])
        #sys.stderr.write("\r{:8d}".format(args['remaining_microseconds']))

        if args['other_player_moves']:
            move = args['other_player_moves'][0][1]

            if move['move'] == 'take_discard':
                debug("The other player took %d and put it in slot %d.", self.k.peek_discard(), move['idx'])
            elif move['move'] == 'take_deck':
                debug("The other player drew and put it in slot %d.", move['idx'])
            elif move['move'] == 'no_move':
                debug("The other player made no move.")
            elif move['move'] == 'illegal':
                debug("The other player made an illegal move: %s.", move['reason'])
            elif move['move'] == 'timed_out':
                debug("The other player timed out.")
            else:
                error("The other player did something unknown!")

            self.k.their_move(move, args['discard'])


        our_move = { }

        self.should_draw = self.a.should_draw()
        if self.should_draw:
            our_move['move'] = 'request_deck'
        else:
            self.card = self.k.peek_discard()
            self.idx = self.a.place_card(self.card)
            if(0 > self.idx or 20 <= self.idx):
                info("idx(%s), card(%s)", repr(self.idx), repr(self.card) )
            if self.idx < 0:
                self.idx = 0
            if self.idx >= 20:
                self.idx = 19
            our_move['move'] = 'request_discard'
            our_move['idx'] = self.idx

        return our_move

    @trycatch
    def get_deck_exchange(self, args):
        debug("get_deck_exchange(%s)", repr(args))
        if args['game_id'] != self.game_id:
            error("Got a request for a move in non-active game.")

        self.k.ttg(args['remaining_microseconds'])

        self.card = args['card']
        self.idx = self.a.place_card(self.card)
        if(0 > self.idx or 20 <= self.idx):
            info("idx(%s), card(%s)", repr(self.idx), repr(self.card) )
        if self.idx < 0:
            self.idx = 0
        if self.idx >= 20:
            self.idx = 19

        return self.idx

    @trycatch
    def move_result(self, args):
        debug("move_result(%s)", repr(args))
        if args['game_id'] != self.game_id:
            error("Got a request for a move in non-active game.")

        move = args['move']
        if args['move'] == 'move_ended_game' or args['move'] == 'next_player_turn':
            self.k.our_move(move, self.should_draw, self.idx, self.card)

        if move == 'next_player_turn':
            debug("We moved successfully")
        elif args['move'] == 'move_ended_game':
            debug("The game is over: %s", args['reason'])
        elif move == 'illegal':
            error("We made an illegal move: %s", args['reason'])
        elif move == 'timed_out':
            error("We timed out.")
        else:
            error("We did something unexpected.")

        return ""

    @trycatch
    def game_result(self, args):
        debug("game_result(%s)", repr(args))
        if args['game_id'] != self.game_id:
            error("Got a request for a move in non-active game.")

        self.k.final(args['your_score'], args['other_score'], args['reason'])

        self.k.pickle()

        info("The game is over after %d moves: %d - %d because %s", len(self.k.moves)/2, args['your_score'], args['other_score'], args['reason'])

        self.game_id = None

        return ""

server = SimpleXMLRPCServer(LISTEN, logRequests=False)
server.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
server.register_instance(RackO())
server.serve_forever()
