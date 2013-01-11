from .models import Field, Pass, Location, Barcode, Signer
from .update import Channels
from django.db.models.signals import post_save
import logging

logger = logging.getLogger('passbook')

channels = Channels(Signer.objects.all())

def updatePassDate(_pass):
    logger.debug('updated related pass')
    _pass.description = _pass.description  # For Update Time, I change to auto update the field updated_at
    _pass.save()

def notifyDevices(_pass):
    devices = _pass.device_set.all()
    identifier = _pass.identifier
    logger.debug('enter notification, identifier: %s', identifier)

    for device in devices:
        logger.debug('enter notification, push token: %s', device.push_token)
        channels.notify(identifier, device.push_token)

def fieldChangeHandler(sender, instance, created, **kwargs):


    if sender == Field:
        _pass = instance._pass
        updatePassDate(_pass)
    elif sender in (Location, Barcode):
        for _pass in instance.passes.all():
            updatePassDate(_pass)
    elif sender == Pass:
        notifyDevices(instance)


post_save.connect(fieldChangeHandler)


