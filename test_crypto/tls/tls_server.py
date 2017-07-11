import socket, ssl

bindsocket = socket.socket()
bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
bindsocket.bind(('', 11111))
bindsocket.listen(5)

def do_something(connstream, data):
	print("Get data:", data)
	connstream.write(data.upper())
	return False

def deal_with_client(connstream):
	data = connstream.read()
	while data:
		if not do_something(connstream, data):
			break
		data = connstream.read()

while True:
	newsocket, fromaddr = bindsocket.accept()
	connstream = ssl.wrap_socket(newsocket,
 								 ssl_version=ssl.PROTOCOL_TLSv1_2,
								 server_side=True,
								 certfile="server.crt",
								 keyfile="server.key")
	try:
		deal_with_client(connstream)
	finally:
		connstream.shutdown(socket.SHUT_RDWR)
		connstream.close()
