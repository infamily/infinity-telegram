# coding: utf-8


class IntentHandleException(Exception):
    """
    Exception subclass that will be handled in the intent-handle-flow:
    * Send a message reply on command/conversation
    * Make an empty results set on inline query
    etc.

    :see: inftybot.handlers
    """
    def __init__(self, message, *args):
        super(IntentHandleException, self).__init__(*args)
        self.message = message


class UnauthenticatedException(IntentHandleException):
    pass


class ValidationError(IntentHandleException):
    pass


class CaptchaValidationError(ValidationError):
    def __init__(self, *args, **kwargs):
        self.captcha = kwargs.pop('captcha', None)
        super(CaptchaValidationError, self).__init__(*args)


class AuthenticationError(IntentHandleException):
    pass


class APIResourceError(IntentHandleException):
    pass
