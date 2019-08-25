class PortrayException(Exception):
    """Base class for all exceptions returned from Portray"""

    pass


class NoProjectFound(PortrayException):
    """Exception should be thrown when portray is ran in a directory with no Python project"""

    def __init__(self, directory):
        super().__init__(
            self, "ERROR: No Python project found in the given directory {}".format(directory)
        )
        self.directory = directory
