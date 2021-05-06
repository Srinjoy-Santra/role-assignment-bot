# define Base class for other exceptions

class Error(Exception):
    pass

# define Python user-defined exceptions
class InvalidRequest(Error):
    pass