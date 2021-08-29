class NotLazyError(TypeError):
    """ Raised when an operation is attempted on a non-lazy user """


class GenerateUsernameError(TypeError):
    """ Raised when is not possible to create a unique username """
