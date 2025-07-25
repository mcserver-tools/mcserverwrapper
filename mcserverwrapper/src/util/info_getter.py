"""A module containing the ping_address_with_return function"""

from __future__ import annotations

import sys

from mcstatus import JavaServer

# version-specific code doesn't work well with pylnt
# https://github.com/pylint-dev/pylint/issues/7240
# pylint: disable=import-error, no-name-in-module

# python versions above 3.9
if sys.version_info.minor > 9:
    from mcstatus.responses import JavaStatusResponse
else:
    from mcstatus.status_response import JavaStatusResponse

# pylint: enable=import-error, no-name-in-module

def ping_address_with_return(address, port, timeout=3) -> JavaStatusResponse | None:
    """Pings a given address/port combination and returns the result or None"""

    if isinstance(port, str):
        port = int(port)

    try:
        server = JavaServer(address, port, timeout=timeout)
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
