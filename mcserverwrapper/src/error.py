"""Module containing all McServerWrapper-related errors"""

class McServerWrapperError(Exception):
    """The base exception, can be used to catch all other McServerWrapper-related errors"""

class ServerExitedError(McServerWrapperError):
    """An error occuring if the minecraft server unexpectedly crashed"""
