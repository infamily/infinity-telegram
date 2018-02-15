# coding: utf-8
import gettext

_ = gettext.gettext


class IntentHandleException(Exception):
    """
    Exception subclass that will be handled in the intent-handle-flow:
    * Send a message reply on command/conversation
    * Make an empty results set on inline query
    etc.

    :see: inftybot.handlers
    """
    default_message = None

    def __init__(self, message=None, *args):
        self.message = message or self.default_message
        super(IntentHandleException, self).__init__(message, *args)


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


class ChatNotFoundError(IntentHandleException):
    default_message = _('CHAT_NOT_FOUND')


class CommunityRequiredError(IntentHandleException):
    """Raised when the intent was called in the direct chat instead of group or channel"""
    default_message = _('COMMUNITY_REQUIRED')


class AdminRequiredError(IntentHandleException):
    """Raised when the user is not administrator of the group or channel"""
    default_message = _('ADMIN_REQUIRED')


class APIResourceError(IntentHandleException):
    pass
