from .utils import write_tempfile
from apns import APNs, PassbookPayload
import os

class PassbookApnChannel(object):

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


class Channels:
    def __init__(self, signers):

        self.channels = {}

        for signer in signers:
            self.channels[signer.label] = PassbookApnChannel(signer.private_key, signer.certificate)

    def notify(self, identifier, token):
        self.channels[identifier].notify(token)