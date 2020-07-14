import os
import io
import contextlib

import paramiko
import jinja2

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
    key = make_key_from(pk, kt)
    with make_client(host, user, key) as client:
        yield client

def get_template(name):
    path = os.path.join(os.path.dirname(__file__), '..', 'templates')   
    loader = jinja2.FileSystemLoader(searchpath=path)
    env = jinja2.Environment(loader=loader)
    return env.get_template(name)


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


def get_slurm_environment_variables():
    return {
        'cpus_per_task': os.environ['SLURM_cpus_per_task'],
        'time': os.environ['SLURM_time'],
        'mem': os.environ['SLURM_mem']
    }


def get_q2_environment_variables():
    result = {}

    result['action'], result['plugin'] = os.environ['Q2_ACTION'].split('::')

    result['inputs'] = _split_values(_environ_search_strip('Q2_I_'), ' ')

    result['params'] = _split_values(_environ_search_strip('Q2_P_'), ' ')
    result['metadata'] = _split_values(_environ_search_strip('Q2_M_'), ' ')
    result['columns'] = _split_values(_environ_search_strip('Q2_C_'), '::')

    result['outputs'] = _environ_search_strip('Q2_O_')

    return result

def get_working_dir():
    return os.environ['WORKDIR']


def _environ_search_strip(search):
    return {k.lstrip(search):v
            for k,v in os.environ.items() if k.startswith(search)}


def _split_values(dict_, delimiter):
    return {k:(v.split(delimiter) if delimiter in v else v)
            for k,v in dict_.items()}


def deref_block(block):
    dereferenced_block = {}

    for name, input_temps in block.items():
        elements, is_list = _listify(input_temps)
        dereferenced = []
        for temp_path in elements:
            dereferenced.append(deref(temp_path))

        if not is_list:
            dereferenced = dereferenced[0]

        dereferenced_block[name] = dereferenced

    return dereferenced_block


def deref(fp):
    with open(os.path.join(fp, 'reference.link')) as fh:
        return fh.readline()

def _listify(obj):
    is_list = True

    if type(obj) is not list:
        is_list = False
        obj = [obj]

    return obj, is_list
