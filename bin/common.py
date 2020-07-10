import os
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

@contextlib.contextmanager
def make_client_from_env():
    host = os.getenv('HOSTNAME')
    user = os.getenv('USERNAME')
    pk = os.getenv('PRIVATE_KEY')
    kt = os.getenv('KEY_TYPE')
    key = common.make_key_from(pk, kt)
    with make_client(host, user, key) as client:
        yield client


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


def get_q2_environment_variables():
    result = {}

    result['action'], result['plugin'] = os.environ['Q2_ACTION'].split(':')
    result['metadata'] = _split_values(_environ_search_strip('Q2_M_'), ':')

    result['inputs'] = _split_values(_environ_search_strip('Q2_I_'), ' ')
    result['params'] = _split_values(_environ_search_strip('Q2_P_'), ' ')
    result['outputs'] = _environ_search_strip('Q2_O_')

    return result

def _environ_search_strip(search):
    return {k.lstrip(search):v
            for k,v in os.environ.items() if k.startswith(search)}

def _split_values(dict_, delimiter):
    return {k:(v.split(delimiter) if delimiter in v else v)
            for k,v in dict_.items()}
