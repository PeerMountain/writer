from kombu import Connection, Exchange, Queue
from msgpack import packb

from config import BROKER_URL
from queues import writer_queue, writer_exchange


invite_envelope = packb({
    'messageType': 0,
})

registration_envelope = packb({
    'sender': 'sender_address',
    'messageType': 1,
    'messageHash': b'message_hash',
    'messageSign': {
        b'signature': b'message_signature',
        b'timestamp': b'message_timestamp',
    },
    'dossierHash': b'dossier_hash',
    'bodyHash': b'body_hash',
    'message': {
        'messageBody': {
            'publicKey': 'registration_public_key',
            'publicNickname': 'public_nick_name',
        }
    },
})

assertion_envelope = packb({
    'sender': 'sender_address',
    'messageType': 3,
    'messageHash': b'assertion_envelope_message_hash',
    'messageSign': {
        b'signature': b'message_signature',
        b'timestamp': b'message_timestamp',
    },
    'dossierHash': b'dossier_hash',
    'bodyHash': b'body_hash',
    'ACL': [{
        'reader': 'reader_address',
        'key': 'reader_key',
    }],
    'objects': [{
        'objectHash': b'object_hash',
        'metaHashes': [
            'one_meta_hash',
        ],
        'container': {
            'containerHash': b'container_hash',
            'containerSign': {
                b'signature': b'message_signature',
                b'timestamp': b'message_timestamp',
            },
            'objectContainer': 'object_container',
        }
    }],
    'message': 'message',
})

attestation_envelope = packb({
    'sender': 'sender_address',
    'messageType': 3,
    'messageHash': b'attestation_envelope_message_hash',
    'messageSign': {
        b'signature': b'message_signature',
        b'timestamp': b'message_timestamp',
    },
    'dossierHash': b'dossier_hash',
    'bodyHash': b'body_hash',
    'ACL': [{
        'reader': 'reader_address',
        'key': 'reader_key',
    }],
    'objects': [{
        'objectHash': b'object_hash',
        'metaHashes': [
            'one_meta_hash',
        ],
        'container': {
            'containerHash': b'container_hash',
            'containerSign': {
                b'signature': b'message_signature',
                b'timestamp': b'message_timestamp',
            },
            'objectContainer': 'object_container',
        }
    }],
    'message': 'message',
})

service_envelope = packb({
    'messageType': 4,
})

delegation_envelope = packb({
    'messageType': 5,
})


with Connection(BROKER_URL) as conn:
    producer = conn.Producer(serializer='msgpack')

    print('#' * 80)
    print('# Message INVITE')
    producer.publish(
        invite_envelope,
        exchange=writer_exchange,
        routing_key='writer',
        declare=[writer_queue]
    )
    print('#' * 80)

    print('#' * 80)
    print('# Message REGISTRATION')
    producer.publish(
        registration_envelope,
        exchange=writer_exchange,
        routing_key='writer',
        declare=[writer_queue]
    )
    print('#' * 80)

    print('#' * 80)
    print('# Message ASSERTION')
    producer.publish(
        assertion_envelope,
        exchange=writer_exchange,
        routing_key='writer',
        declare=[writer_queue]
    )
    print('#' * 80)

    print('#' * 80)
    print('# Message ATTESTATION')
    producer.publish(
        attestation_envelope,
        exchange=writer_exchange,
        routing_key='writer',
        declare=[writer_queue]
    )
    print('#' * 80)

    # print('#' * 80)
    # print('# Message SERVICE')
    # producer.publish(
    #     service_envelope,
    #     exchange=writer_exchange,
    #     routing_key='writer',
    #     declare=[writer_queue]
    # )
    # print('#' * 80)

    # print('#' * 80)
    # print('# Message DELEGATION')
    # producer.publish(
    #     delegation_envelope,
    #     exchange=writer_exchange,
    #     routing_key='writer',
    #     declare=[writer_queue]
    # )
    # print('#' * 80)
