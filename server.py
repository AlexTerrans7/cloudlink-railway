from cloudlink import server
from cloudlink.server.protocols import clpv4
import os

server = server()
server.logging.basicConfig(level=server.logging.DEBUG)

clpv4 = clpv4(server)

port = int(os.environ.get("PORT", 3000))
server.run(ip="0.0.0.0", port=port)
