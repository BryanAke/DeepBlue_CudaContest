from SimpleXMLRPCServer import SimpleXMLRPCServer

import logging
from logging import debug, info, warning, error, exception, critical

import collections
import functools
import random
import socket
import sys

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

logging.basicConfig(level=logging.INFO)

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
		self.a = agent.Agent(self.k)

		info("Starting game %d going %s against team %d.", args['game_id'], ("first", "second")[args['player_id']], args['other_player_id'])

		return ""

	@trycatch
	def get_move(self, args):
		debug("get_move(%s)", repr(args))

		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		if not self.rack:
			self.k.set_initial_rack(args['rack'])

		self.k.time(['remaining_microseconds'])
		#sys.stderr.write("\r{:8d}".format(args['remaining_microseconds']))

		if args['other_player_moves']:
			self.k.their_move(args['other_player_moves'][0][1], args['discard'])

		our_move = { }

		self.should_draw = self.a.should_draw()
		if self.should_draw:
			our_move['move'] = 'request_deck'
		else:
			self.card = self.k.peek_discard()
			self.idx = self.a.place_card(self.card)
			our_move['move'] = 'request_discard'
			our_move['idx'] = self.idx

		return our_move

	@trycatch
	def get_deck_exchange(self, args):
		debug("get_deck_exchange(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		self.k.time(args['remaining_microseconds'])

		self.card = args['card']
		self.idx = self.a.place_card(self.card)

		return self.idx

	@trycatch
	def move_result(self, args):
		debug("move_result(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		move = args['move']
		self.k.our_move(move, self.should_draw, self.idx, self.card)

		return ""

	@trycatch
	def game_result(self, args):
		debug("game_result(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		self.k.finish(args['your_score'], args['other_score'], args['reason'])

		self.k.pickle()

		info("The game is over after %d moves: %d - %d because %s", self.k.moves, args['your_score'], args['other_score'], args['reason'])

		return ""

server = SimpleXMLRPCServer(LISTEN, logRequests=False)
server.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
server.register_instance(RackO())
server.serve_forever()