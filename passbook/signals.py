__author__ = 'tim'
from .models import Field, Pass, Location, Barcode
from django.db.models.signals import post_save

import logging
logger = logging.getLogger('passbook')


def notifyDevices(_pass):
    devices = _pass.device_set.all()
    for device in devices:
        logger.debug('push token is %s', device.push_token)

def fieldChangeHandler(sender, instance, created, **kwargs):

    if sender == Field:
        _pass = instance._pass
        notifyDevices(_pass)
    elif sender in (Location, Barcode):
        for _pass in instance.passes.all():
            notifyDevices(_pass)
    elif sender == Pass:
        notifyDevices(instance)


post_save.connect(fieldChangeHandler)


