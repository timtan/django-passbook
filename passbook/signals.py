from django.db.models.signals import post_save
from django.db.utils import DatabaseError
import logging
from .update import PassbookChannels
from django.conf import settings
from django.dispatch.dispatcher import Signal

logger = logging.getLogger('passbook')

NOTIFICATION_CLASS = getattr(settings, 'NOTIFICATION_CLASS', 'PassbookChannels')

if  NOTIFICATION_CLASS == 'PassbookChannels':
    channel_instance = PassbookChannels()
    channel = channel_instance.notify
    logger.debug('Use Apple APN for pass')
else:
    channel = NOTIFICATION_CLASS()
    logger.debug('Use Custom channel')

pass_update = Signal(providing_args=['signer', 'token'])



def notify_device(sender, signer, token, **kwarg):
    logger.debug('receive notification')
    channel(signer,token)



pass_update.connect(notify_device)



