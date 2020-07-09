import io
import contextlib

import paramiko


@contextlib.contextmanager
def make_client(host, user, private_key):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, pkey=private_key)
        yield client


@contextlib.contextmanager
def make_sftp(host, user, private_key):
    with make_client(host, user, private_key) as client:
        t = client.get_transport()
        sftp = paramiko.sftp_client.SFTPClient.from_transport(t)
        yield sftp


def make_key_from(key_string, key_type):
    key_file = io.StringIO(key_string)

    if key_type == 'dsa' or key_type == 'dss':
        return paramiko.dsskey.DSSKey.from_private_key(key_file)
    elif key_type == 'rsa':
        return paramiko.rsakey.RSAKey.from_private_key(key_file)
    elif key_type == 'ecdsa':
        return paramiko.ecdsakey.ECDSAKey.from_private_key(key_file)
    elif key_type == 'ed25519':
        return paramiko.ed25519key.Ed25519Key.from_private_key(key_file)

    raise ValueError(f'Invalid key_type {key_type}')
