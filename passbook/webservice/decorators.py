from django.http import HttpResponse
from passbook.models import Pass


def is_authorized(func):
    def wrapper(request, *args, **kwargs):
        serial_number = kwargs.get('serial_number')
        authorization = request.META.get('HTTP_AUTHORIZATION')
        if serial_number is not None and authorization is not None:
            authorization = authorization.replace('ApplePass', '').strip()
            if Pass.objects.filter(serial_number=serial_number,
                                   auth_token=authorization).exists():

                return func(request, *args, **kwargs)
        return HttpResponse(status_code=401)
    return wrapper
