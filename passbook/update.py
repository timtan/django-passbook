from .utils import write_tempfile
from apns import APNs, PassbookPayload
import logging
logger = logging.getLogger('passbook.signal')
class ChannelBase(object):
    def __init__(self, private_key, certficate):
        pass
    def notify(self, token):
        pass
class PassbookApnChannel(ChannelBase):

    __payload  = PassbookPayload()

    def __init__(self, private_key, certificate):
        self.__keyfile  = write_tempfile(private_key)
        self.__certfile = write_tempfile(certificate)
        self.__apn      = APNs(use_sandbox=False, cert_file=self.__certfile, key_file=self.__keyfile)

    def __del__(self):
        for file in (self.__keyfile, self.__certfile):
            pass #os.remove(file) # Cannot all it in destructor...

    def notify(self, token):
        self.__apn.gateway_server.send_notification(token, PassbookApnChannel.__payload)


class ChannelsBase(object):
    def notify(self, identifier,  signer):
        pass

class PassbookChannels(ChannelsBase):
    def __init__(self, ChannelCls=PassbookApnChannel):

        self.channels = {}
        self.ChannelCls = ChannelCls

    def notify(self,  signer, token):

        if signer.label not in self.channels:
            logger.info('the channel for the signer %s is created', signer)
            self.channels[signer.label] = self.ChannelCls(signer.private_key, signer.certificate)

        try:
            self.channels[signer.label].notify(token)
            logger.debug('notifier fire notification to token(%s)', token)
        except KeyError as e:
            logger.error('identifier is not available in signer table. it is because pass label and identifier not the same')

