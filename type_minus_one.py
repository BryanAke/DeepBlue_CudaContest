from SimpleXMLRPCServer import SimpleXMLRPCServer

import random

LISTEN = ('0.0.0.0', 1337)

class RackO(object):
	def ping(self, p):
		return "pong"

	def start_game(self, args):
		return ""

	def get_move(self, args):
		print "{:7d}".format(args['remaining_microseconds'])
		return { 'move' : 'request_deck' }

	def get_deck_exchange(self, args):
		return random.randint(0, 19)

	def move_result(self, args):
		if args['move'] == 'illegal':
			print("We made an illegal move: %s", args['reason'])
		elif args['move'] == 'timed_out':
			print("We timed out.")

		return ""

	def game_result(self, args):

		print("The game is over after %d moves: %d - %d because %s" % (self.moves, args['your_score'], args['other_score'], args['reason']))

		return ""

server = SimpleXMLRPCServer(LISTEN, logRequests=False)
server.register_instance(RackO())
server.serve_forever()