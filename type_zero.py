from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import logging
import random

logging.basicConfig()

class RackO(object):
	def ping(self, p):
		return "pong"

	def _push_discard(self, card):
		debug("Added %d to the discard pile", card)
		self.discard.append(card)
		self.deck.discard(card)

	def _pop_discard(self):
		card = self.discard.pop()
		debug("Took %d from the discard pile", card)
		return card

	def start_game(self, args):
		self.game_id = args['game_id']
		self.player_id = args['player_id']
		self.discard = []
		self.other_player_id = args['other_player_id']

		self.deck = set(range(1, 81))
		self.deck_size = 80 - 20 - 20 - 1
		self.rack = []

		self.other_rack = [None] * 20

		info("Starting game %d going %s against team %d.", self.game_id, ("first", "second")[self.player_id], self.other_player_id)

		self._push_discard(args['initial_discard'])

		return ""

	def get_move(self, args):
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		if self.rack:
			if self.rack != args['rack']:
				error("Our rack is out-of-sync!")
				self.rack = args['rack']
		else:
			self.rack = args['rack']
			self.deck -= self.rack

		self.timeleft = args['remaining_microseconds']

		if args['other_player_moves']:
			other_move = args['other_player_moves'][0][1]
			if other_move['move'] == 'take_discard':
				card = self._pop_discard()
				self.other_rack[other_move['idx']] = card
				info("The other player took %d and put it in slot %d.", card, other_move['idx'])
			elif other_move['move'] == 'take_deck':
				self.other_rack[other_move['idx']] = 0
				self.deck_size -= 1
				info("The other player drew and put it in slot %d.", other_move['idx'])
			elif other_move['move'] == 'no_move':
				info("The other player made no move.")
			elif other_move['move'] == 'illegal':
				info("The other player made an illegal move: %s.", other_move['reason'])
			elif other_move['move'] == 'timed_out':
				info("The other player timed out.")
			else:
				error("The other player did something unknown!")

		self._push_discard(args['discard'])

		our_move = { }

		# Type -1 Play: Always draw
		our_move['move'] = 'request_deck'

		return our_move

	def get_deck_exchange(self, args):
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		self.timeleft = args['remaining_microseconds']

		self.card = args['card']

		self.deck_size -= 1
		self.deck.discard(card)

		self.new_rack = self.rack[:]

		# Level -1 Play: Insert in random location
		self.idx = random.randint(0, 19)

		return self.idx

	def move_result(self, args):
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		move = args['move']
		if move == 'next_player_move':
			info("We moved successfully")
			self._push_discard(self.rack[self.idx])
			self.rack[self.idx] = self.card
		elif move == 'move_ended_game':
			info("The game is over: %s", args['reason'])
		elif move == 'illegal':
			info("We made an illegal move: %s", args['reason'])

		return ""

	def game_result(self, args):
		if args['game_id'] != self.game_id:
			error("Got a request for a move in non-active game.")

		info("The game is over: %d - %d because %s", args['your_score'], args['other_score'], args['reason']

		return ""