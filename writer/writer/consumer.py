import datetime
import logging
import logging.config
from base64 import b64decode

from kombu.mixins import ConsumerMixin
from umsgpack import unpackb, packb
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
            callbacks=[self.process_task]
        )]

    def save_persona(self, envelope):
        """
        Saves a Persona from a Registration message.
        """

        unpacked_envelope = unpackb(envelope)
        unpacked_message = unpackb(b64decode(unpacked_envelope.get('message')))
        unpacked_body = unpackb(b64decode(unpacked_message.get('messageBody')))

        address = unpacked_envelope.get('sender')
        pubkey = unpacked_body.get('publicKey')
        nickname = unpacked_body.get('publicNickname')

        # Workaround since INVITE and REGISTRATION are actually
        # sharing the same type on the Python client
        if address and pubkey and nickname:
            persona = Persona(
                address=address,
                pubkey=pubkey,
                nickname=nickname,
            )
            persona.save()

    def save_message(self, envelope):
        """
        Saves a Message from an envelope.
        """

        unpacked_envelope = unpackb(envelope)

        address = unpacked_envelope.get('sender')
        persona = Persona.get(address)

        # There's no ACL or Objects on Invite and Registration
        # Default to an empty string
        acl = packb(unpacked_envelope.get('ACL')) or ''
        objects = packb(unpacked_envelope.get('objects')) or ''

        message_type = str(unpacked_envelope.get('messageType'))
        message_hash = unpacked_envelope.get('messageHash')
        message_signature = unpackb(b64decode(unpacked_envelope.get('messageSign')))
        signature = message_signature.get('signature')
        timestamp = message_signature.get('timestamp')
        dossier_hash = unpacked_envelope.get('dossierHash')
        body_hash = unpacked_envelope.get('bodyHash')
        message = unpacked_envelope.get('message')

        message = Message(
            persona_sender=persona.address,
            persona_pubkey=persona.pubkey,
            persona_nickname=persona.nickname,
            type=message_type,
            hash=message_hash,
            signature=signature,
            timestamp=timestamp,
            dossier_hash=dossier_hash,
            body_hash=body_hash,
            acl=acl,
            objects=objects,
            message=message,
            created_at=datetime.datetime.now().isoformat(),
        ) 
        message.save()

    def process_task(self, body, message):
        """
        Parse the envelope to find its type and call the correct saved methods.
        """

        logger.info(f'Received message with body={body}')

        unpacked_envelope = unpackb(body)
        type = unpacked_envelope.get('messageType')

        if type in [MessageTypes.SERVICE, MessageTypes.DELEGATION]:
            logger.error(f'Message Type {type} not implemented')

        if type in [MessageTypes.INVITE]:
            self.save_message(body)

        if type == MessageTypes.REGISTRATION:
            self.save_persona(body)
            self.save_message(body)

        if type in [MessageTypes.ASSERTION, MessageTypes.ATTESTATION]:
            self.save_message(body)

        message.ack()

        logger.info(f'Message processed')


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    with Connection(BROKER_URL) as conn:
        worker = Worker(conn)
        logger.info('Starting worker')
        worker.run()
