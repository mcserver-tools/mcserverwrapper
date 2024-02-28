"""A module containing the ping_address_with_return function"""

from mcstatus import JavaServer
from mcstatus.pinger import PingResponse

def ping_address_with_return(address, port) -> PingResponse | None:
    """Pings a given address/port combination and returns the result or None"""

    if isinstance(port, str):
        port = int(port)

    try:
        server = JavaServer(address, port)
        status = server.status()
        return status
    except (TimeoutError, ConnectionAbortedError, ConnectionResetError, IOError):
        return None
    # a bug with the library pinging the minecraft server
    except KeyError as keyerr:
        if "text" in keyerr.args or "#" in keyerr.args:
            print("Retrying...")
            return ping_address_with_return(address, port)
    # happens randomly with some addresses
    except IndexError as indexerr:
        if "bytearray" in indexerr.args:
            print("Retrying...")
            return ping_address_with_return(address, port)
    return None
