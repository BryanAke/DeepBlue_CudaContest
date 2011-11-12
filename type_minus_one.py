from SimpleXMLRPCServer import SimpleXMLRPCServer

import random
import socket

# This is a hack to patch slow socket.getfqdn calls that
# BaseHTTPServer (and its subclasses) make.
# See: http://bugs.python.org/issue6085
# See: http://www.answermysearches.com/xmlrpc-server-slow-in-python-how-to-fix/2140/

import BaseHTTPServer

def _bare_address_string(self):
    host, port = self.client_address[:2]
    return '%s' % host

BaseHTTPServer.BaseHTTPRequestHandler.address_string = \
        _bare_address_string

# End hack.



LISTEN = ('0.0.0.0', 1337)

class RackO(object):
	def ping(self, p):
		return "pong"

	def start_game(self, args):
		return ""

	def get_move(self, args):
		#print "{:7d}".format(args['remaining_microseconds'])
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
server.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
server.register_instance(RackO())
server.serve_forever()