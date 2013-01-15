from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from .models import Field, Pass, Location, Barcode
import logging
import update
from django.dispatch.dispatcher import Signal

logger = logging.getLogger('passbook')


pass_update = Signal(providing_args=['identifier', 'token'])


def notify_device(sender, identifier, token, **kwarg):
    channel = update.getChannels()
    channel.notify(identifier,token)

from django.conf import settings


if not getattr(settings, 'IN_UNIT_TEST',False):
    pass_update.connect(notify_device)

