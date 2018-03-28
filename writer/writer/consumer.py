import datetime
import logging
import logging.config

from kombu.mixins import ConsumerMixin
from msgpack import unpackb, packb
from himalaya_models import Message, Persona

from config import BROKER_URL, LOGGING
from queues import writer_queue


logger = logging.getLogger('writer')
logging.config.dictConfig(LOGGING)


class MessageTypes(object):
    INVITE = 0
    REGISTRATION = 1
    ASSERTION = 2
    ATTESTATION = 3
    SERVICE = 4
    DELEGATION = 5


class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=writer_queue,
            accept=['msgpack'],
            callbacks=[self.process_task]
        )]

    def process_envelope(self, envelope):
        """
        Parse the envelope to find its type and call the correct saved methods.
        """

        unpacked_envelope = unpackb(envelope)
        type = unpacked_envelope.get(b'messageType')

        if type in [MessageTypes.SERVICE, MessageTypes.DELEGATION]:
            logger.error(f'Message Type {type} not implemented')

        if type in [MessageTypes.INVITE]:
            self.save_message(envelope)

        if type == MessageTypes.REGISTRATION:
            self.save_persona(envelope)
            self.save_message(envelope)

        if type in [MessageTypes.ASSERTION, MessageTypes.ATTESTATION]:
            self.save_message(envelope)

    def save_persona(self, envelope):
        """
        Saves a Persona from a Registration message.
        """

        unpacked_envelope = unpackb(envelope)

        address = unpacked_envelope.get(b'sender').decode()
        pubkey = unpacked_envelope.get(b'message').get(b'messageBody').get(b'publicKey').decode()
        nickname = unpacked_envelope.get(b'message').get(b'messageBody').get(b'publicNickname').decode()

        persona = Persona(address=address, pubkey=pubkey, nickname=nickname)
        persona.save()

    def save_message(self, envelope):
        """
        Saves a Message from an envelope.
        """

        unpacked_envelope = unpackb(envelope)

        address = unpacked_envelope.get(b'sender').decode()
        persona = Persona.get(address)

        # There's no ACL or Objects on Invite and Registration
        # Default to an empty string
        acl = packb(unpacked_envelope.get(b'ACL')) or ''
        objects = packb(unpacked_envelope.get(b'objects')) or ''

        message = Message(
            persona_sender=persona.address,
            persona_pubkey=persona.pubkey,
            persona_nickname=persona.nickname,
            type=str(unpacked_envelope.get(b'messageType')),
            hash=unpacked_envelope.get(b'messageHash').decode(),
            signature=unpacked_envelope.get(b'messageSign').get(b'signature').decode(),
            timestamp=unpacked_envelope.get(b'messageSign').get(b'timestamp').decode(),
            dossier_hash=unpacked_envelope.get(b'dossierHash').decode(),
            body_hash=unpacked_envelope.get(b'bodyHash').decode(),
            acl=acl,
            objects=objects,
            message=unpacked_envelope.get(b'message').decode(),
            created_at=datetime.datetime.now().isoformat(),
        ) 
        message.save()

    def process_task(self, body, message):
        logger.info(f'Received message with body={body}')
        self.process_envelope(body)
        logger.info(f'Message processed')


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    with Connection(BROKER_URL) as conn:
        worker = Worker(conn)
        logger.info('Starting worker')
        worker.run()
