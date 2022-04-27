from mcstatus import JavaServer
from mcstatus.pinger import PingResponse

def ping_address_with_return(address, port) -> PingResponse | None:
    if isinstance(port, str):
        port = int(port)
    try:
        server = JavaServer(address, port)
        status = server.status()
        return status
    except TimeoutError:
        return
    except ConnectionAbortedError:
        return
    except ConnectionResetError:
        return
    except IOError:
        return
    except KeyError as keyerr:
        if "text" in keyerr.args or "#" in keyerr.args:
            print("Retrying...")
            return ping_address_with_return(address)
    except IndexError as indexerr:
        if "bytearray" in indexerr.args:
            print("Retrying...")
            return ping_address_with_return(address)
