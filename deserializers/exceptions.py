class BaseDeserializerException(Exception):
    pass


class DeserializerKeyError(BaseDeserializerException):
    def __init__(self, key):
        message = f"Value {key} is required"
        super().__init__(message)


class DeserializerValueError(BaseDeserializerException):
    def __init__(self, key):
        message = f"{key}"
        super().__init__(message)


class ShittyError(BaseDeserializerException):
    def __init__(self, key):
        message = f"Some unknown error: {key}"
        super().__init__(message)
