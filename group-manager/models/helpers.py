from os import getenv
from werkzeug.exceptions import HTTPException

def env(envname, default=""):
    value = getenv(envname)
    return value or default

class Panic(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code