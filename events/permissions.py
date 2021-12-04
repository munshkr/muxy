from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import BaseHasAPIKey

from .models import CustomAPIKey


class HasCustomAPIKey(BaseHasAPIKey):
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


class HasStreamKey(BasePermission):
    REQUIRED_KEY_ACTIONS = (
        "destroy",
        "update",
        "partial_update",
    )

    def has_permission(self, request, view):
        # If user is staff, or is an action that does not require a key, allow access
        if (
            request.user.is_staff
            or not view.is_web_request
            or (view.action not in self.REQUIRED_KEY_ACTIONS)
        ):
            return True
        # Otherwise, only allow access if the user has a valid stream key.
        # This guarantees that only the user that originally created the Stream
        # can delete or modify it later.
        stream_key = request.headers.get(settings.STREAM_KEY_HEADER)
        stream = view.get_object()
        return stream_key == stream.key
