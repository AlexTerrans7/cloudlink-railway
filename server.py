from cloudlink import server
from cloudlink.server.protocols import clpv4

server = server()
server.logging.basicConfig(level=server.logging.DEBUG)

clpv4 = clpv4(server)

server.run(ip="0.0.0.0", port=3000)
