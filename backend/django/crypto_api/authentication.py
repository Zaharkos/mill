from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return None  # або можна повернути помилку, залежно від логіки

        try:
            user = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key')

        return user, None
