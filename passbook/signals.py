from django.db.models.signals import post_save
from django.db.utils import DatabaseError
import logging
import update
from django.conf import settings
from django.dispatch.dispatcher import Signal

logger = logging.getLogger('passbook')


pass_update = Signal(providing_args=['identifier', 'token'])


def notify_device(sender, identifier, token, **kwarg):
    channel = update.getChannels()
    channel.notify(identifier,token)



if not getattr(settings, 'TESTING',False):
    pass_update.connect(notify_device)

