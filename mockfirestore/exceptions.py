class ClientError(Exception):
    code = None

    def __init__(self, message, *args):
        self.message = message
        super().__init__(message, *args)

    def __str__(self):
        return "{} {}".format(self.code, self.message)


class Conflict(ClientError):
    code = 409


class NotFound(ClientError):
    code = 404


class AlreadyExists(Conflict):
    pass
