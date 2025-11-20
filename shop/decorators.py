from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def admin_required(function=None):
    """
    Decorator to check if user is admin (staff)
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

