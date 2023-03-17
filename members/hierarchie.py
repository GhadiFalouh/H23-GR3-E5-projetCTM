from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def allowed_users(allowed_roles=[]):
    def hierarchie(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.users.groups.exists():
                group = request.users.groups.all[0].name

            if group in allowed_roles:
                return view_func(request, kargs, **kwargs)
            else:
                return HttpResponse
        return wrapper-func
    return hierarchie