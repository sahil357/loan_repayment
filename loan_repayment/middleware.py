from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from user.models import CustomerUser


class MyAuthenticationClass(TokenAuthentication):
    model = CustomerUser
    is_system_user = False

    def authenticate(self, request):
        if "login" in request.build_absolute_uri() or "create" in request.build_absolute_uri():
            return super(MyAuthenticationClass, self).authenticate(request)

        if 'Token' not in request.headers:
            raise exceptions.AuthenticationFailed('Token not provided')

        response = self.authenticate_credentials(request.headers.get('Token'))
        if response is not None:
            request.user = response[0]
        return response

    def authenticate_credentials(self, token):
        try:
            user = self.get_model().objects.get(token=token)
        except self.get_model().DoesNotExist:
            raise exceptions.AuthenticationFailed('User doesnot exist with this token')
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid token. - {}'.format(e))

        return user, token
