from rest_framework_api_key.permissions import BaseHasAPIKey

from .models import UserAPIKey


class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey

    def has_permission(self, request, view):
        key = self.get_key(request)
        if not key:
            return False
        is_valid = self.model.objects.is_valid(key)
        if is_valid:
            prefix, _, _ = key.partition(".")
            instance = self.model.objects.get(prefix=prefix)
            request.user = instance.user
        return is_valid
