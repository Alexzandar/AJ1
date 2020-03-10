from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class ExpiringTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        # Adding this for testing purpose
        token.delete()
        if not settings.DEBUG:
            token.delete()

        return (token.user, token)


class SessionTokenAuthentication(TokenAuthentication):

    @staticmethod
    def _expires_in(token):
        time_elapsed = timezone.now() - token.created
        left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
        return left_time

    def _is_token_expired(self, token):
        return self._expires_in(token) < timedelta(seconds=0)

    def _token_expire_handler(self, token):
        is_expired = self._is_token_expired(token)
        if is_expired:
            token.delete()
        return is_expired

    def authenticate_credentials(self, key):
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        is_expired = self._token_expire_handler(token)
        if is_expired:
            raise exceptions.AuthenticationFailed('Token expired.')

        return (token.user, token)
