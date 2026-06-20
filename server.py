import os
import asyncio
import logging
import websockets
from cloudlink import server
from cloudlink.server.protocols import clpv4

PORT = int(os.environ.get("PORT", 3000))

# Suppress the noisy HEAD request errors - they don't affect WS clients
logging.getLogger("websockets.server").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)

async def process_request(connection, request):
    """Respond to Render's health checks with HTTP 200."""
    try:
        method = request.method
    except AttributeError:
        return None
    
    if method in ("HEAD", "GET"):
        headers = {}
        try:
            headers = dict(request.headers)
        except Exception:
            pass
        
        if headers.get("upgrade", "").lower() != "websocket":
            # Plain HTTP health check — respond OK
            from websockets.http11 import Response
            from websockets.datastructures import Headers
            response = Response(
                200, "OK",
                Headers([("Content-Length", "2")]),
                b"OK"
            )
            await connection.send_response(response)
            return response
    
    return None  # Real WebSocket connection — let it through

async def run():
    cl_server = server()
    clpv4(cl_server)
    
    # Start CloudLink but intercept the underlying websockets.serve call
    # by monkey-patching the process_request into it
    original_run = cl_server.run.__func__ if hasattr(cl_server.run, '__func__') else None
    
    # Directly use websockets.serve with CloudLink's handler + our health check
    async with websockets.serve(
        cl_server.handle,           # CloudLink's internal handler
        "0.0.0.0",
        PORT,
        process_request=process_request,
    ):
        logging.info(f"✅ CloudLink + health check running on port {PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run())
