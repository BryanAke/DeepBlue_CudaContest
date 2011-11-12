from SimpleXMLRPCServer import SimpleXMLRPCServer

import logging
from logging import debug, info, warning, error, exception, critical

import collections
import functools
import random
import socket

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
	def _push_discard(self, card):
		debug("Added %d to the discard pile", card)
		self.discard.append(card)
		self.deck.discard(card)

	def _pop_discard(self):
		card = self.discard.pop()
		debug("Took %d from the discard pile", card)
		return card

	def _print_game_state(self):
		print "Turn", self.moves
		if self.player_id == 0:
			print "Us:", self.rack
			print "Them:", self.other_rack
		else:
			print "Them:", self.other_rack
			print "Us:", self.rack
		print "Deck contains", self.deck_size, "cards from", self.deck
		print "Discard pile contains", self.discard

	@trycatch
	def ping(self, p):
		debug("ping(%s)", repr(p))
		return "pong"

	@trycatch
	def start_game(self, args):
		debug("start_game(%s)", repr(args))
		self.game_id = args['game_id']
		self.player_id = args['player_id']
		self.discard = collections.deque()
		self.other_player_id = args['other_player_id']

		self.deck = set(range(1, 81))
		self.deck_size = 80 - 20 - 20 - 1
		self.rack = []

		self.moves = 0

		self.other_rack = [None] * 20

		info("Starting game %d going %s against team %d.", self.game_id, ("first", "second")[self.player_id], self.other_player_id)

		self._push_discard(args['initial_discard'])

		return ""

	@trycatch
	def get_move(self, args):
		debug("get_move(%s)", repr(args))
		self.moves += 1

		if args['game_id'] != self.game_id:
			#error("Got a request for a move in non-active game.")

		if self.rack:
			if self.rack != args['rack']:
				print("Our rack is out-of-sync!")
				self.rack = args['rack']
		else:
			self.rack = args['rack']
			self.deck.difference_update(self.rack)

		self.timeleft = args['remaining_microseconds']
		print "{:7d}".format(args['remaining_microseconds'])

		if args['other_player_moves']:
			other_move = args['other_player_moves'][0][1]
			if other_move['move'] == 'take_discard':
				card = self._pop_discard()
				self.other_rack[other_move['idx']] = card
				debug("The other player took %d and put it in slot %d.", card, other_move['idx'])
			elif other_move['move'] == 'take_deck':
				self.other_rack[other_move['idx']] = 0
				self.deck_size -= 1
				debug("The other player drew and put it in slot %d.", other_move['idx'])
			elif other_move['move'] == 'no_move':
				debug("The other player made no move.")
			elif other_move['move'] == 'illegal':
				debug("The other player made an illegal move: %s.", other_move['reason'])
			elif other_move['move'] == 'timed_out':
				debug("The other player timed out.")
			else:
				error("The other player did something unknown!")

			self._push_discard(args['discard'])

		our_move = { }

		# Type -1 Play: Always draw
		our_move['move'] = 'request_deck'

		return our_move

	@trycatch
	def get_deck_exchange(self, args):
		debug("get_deck_exchange(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		self.timeleft = args['remaining_microseconds']

		self.card = args['card']

		self.deck_size -= 1
		self.deck.discard(self.card)

		# Level -1 Play: Insert in random location
		self.idx = random.randint(0, 19)

		return self.idx

	@trycatch
	def move_result(self, args):
		debug("move_result(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		move = args['move']
		if move == 'next_player_turn':
			debug("We moved successfully")
			self._push_discard(self.rack[self.idx])
			self.rack[self.idx] = self.card
		elif move == 'move_ended_game':
			debug("The game is over: %s", args['reason'])
		elif move == 'illegal':
			print("We made an illegal move: %s", args['reason'])
		elif move == 'timed_out':
			print("We timed out.")
		else:
			error("We did something unexpected.")

		return ""

	@trycatch
	def game_result(self, args):
		debug("game_result(%s)", repr(args))
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		print("The game is over after %d moves: %d - %d because %s", self.moves, args['your_score'], args['other_score'], args['reason'])

		return ""

server = SimpleXMLRPCServer(LISTEN, logRequests=False)
server.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
server.register_instance(RackO())
server.serve_forever()