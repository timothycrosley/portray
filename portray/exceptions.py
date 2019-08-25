class PortrayError(Exception):
    """Base class for all exceptions returned from Portray"""

    pass


class NoProjectFound(PortrayError):
    """Exception should be thrown when portray is ran in a directory with no Python project"""

    def __init__(self, directory):
        super().__init__(
            self, "No Python project found in the given directory: '{}'".format(directory)
        )
        self.directory = directory


class DocumentationAlreadyExists(PortrayError):
    """Throw when portray has been told to output documentation where it already exists"""

    def __init__(self, directory):
        super().__init__(
            self,
            "Documentation already exists in '{}'. Use --overwrite to ignore".format(directory),
        )
        self.directory = directory
