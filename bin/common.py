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
    return _pop_strip(os.environ.copy(), 'SLURM_')


def get_script_variables():
    vars_ = _pop_strip(os.environ.copy(), 'SCRIPT_')
    deref = _split_values(_pop_strip(vars_, 'I_'), ' ')
    return deref, vars_


def get_q2_environment_variables():
    result = {}

    q2_vars = _pop_strip(os.environ.copy(), 'Q2_')
    if '::' in q2_vars['ACTION']:
        result['plugin'], result['action'] = q2_vars['ACTION'].split('::')
        del q2_vars['ACTION']

    result['inputs'] = _split_values(_pop_strip(q2_vars, 'I_'), ' ')

    result['params'] = _split_values(_pop_strip(q2_vars, 'P_'), ' ')
    result['metadata'] = _split_values(_pop_strip(q2_vars, 'M_'), ' ')
    result['columns'] = _split_values(_pop_strip(q2_vars, 'C_'), '::')

    result['outputs'] = _pop_strip(q2_vars, 'O_')

    result.update({k.lower(): v for k, v  in q2_vars.items()})

    return result


def get_working_dir():
    return os.environ['WORKDIR']


def _pop_strip(mapping, search):
    popped = {}
    for key, value in list(mapping.items()):
        if key.startswith(search):
            stripped_key = key[len(search):]
            popped[stripped_key] = value
            del mapping[key]
    return popped


def _split_values(dict_, delimiter):
    result = {}
    for key, value in dict_.items():
        if value.startswith('++NOLIST++ '):
            result[key] = value[len('++NOLIST++ '):]
        elif delimiter in value:
            result[key] = value.split(delimiter)
        else:
            result[key] = value
    return result


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
    contents = os.listdir(fp)
    if len(contents) == 1 and contents[0] != 'reference.link':
        fp = os.path.join(fp, contents[0])

    with open(os.path.join(fp, 'reference.link')) as fh:
        return fh.readline()


def _listify(obj):
    is_list = True

    if type(obj) is not list:
        is_list = False
        obj = [obj]

    return obj, is_list
