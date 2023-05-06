from django.core.exceptions import PermissionDenied
from functools import wraps


def is_staff_user(view):

    @wraps(view)
    def _view(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return view(self.request, *args, **kwargs)

    return _view
