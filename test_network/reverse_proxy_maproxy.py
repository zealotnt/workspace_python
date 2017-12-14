#!/usr/bin/env python3
import tornado.ioloop
import maproxy.proxyserver
import socket

# [Ref](https://pypi.python.org/pypi/maproxy)

add_from = socket.gethostbyname(socket.gethostname())
port_from_to = 42000
add_to = "192.168.1.250"

# HTTP->HTTP: On your computer, browse to "add_from" and you'll get "add_to"
server = maproxy.proxyserver.ProxyServer(add_to, port_from_to)
server.listen(port_from_to)
print("%s:%d -> %s" % (add_from, port_from_to, add_to))
tornado.ioloop.IOLoop.instance().start()
