from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import logging

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

	def start_game(self, game_id, player_id, initial_discard, other_player_id):
		self.game_id = game_id
		self.player_id = player_id
		self.discard = []
		self.other_player_id = other_player_id

		self.deck = set(range(1, 81))
		self.rack = []

		info("Starting game %d going %s against team %d.", game_id, ("first", "second")[player_id], other_player_id)

		self._push_discard(initial_discard)

		return ""

	def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
		if game_id != self.game_id:
			error("Got a request for a move in non-active game.")

		if self.rack:
			if self.rack != rack:
				error("Our rack is out-of-sync!")
				self.rack = rack
		else:
			self.rack = rack

		if self.discard[-1] != discard:
			error("The discard pile is out-of-sync!")
			self.discard = [ discard ]



		pass

	def get_deck_exchange(self, game_id, remaining_microseconds, rack, card):
		pass

	def move_result(self, game_id, move):
		return ""

	def game_result(self, game_id, your_score, other_score, reason):
		return ""