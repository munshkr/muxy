from rest_framework_api_key.permissions import BaseHasAPIKey

from .models import CustomAPIKey


class HasUserAPIKey(BaseHasAPIKey):
    model = CustomAPIKey

    def has_permission(self, request, view):
        key = self.get_key(request)
        if not key:
            return False
        is_valid = self.model.objects.is_valid(key)
        if is_valid:
            prefix, _, _ = key.partition(".")
            instance = self.model.objects.get(prefix=prefix)
            request.is_web = instance.is_web
        return is_valid
