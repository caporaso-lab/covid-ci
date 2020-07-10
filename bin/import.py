#!/usr/bin/env python

import io
import os
import sys

print(sys.version)
print(os.__file__)

import common

cwd = os.getcwd()

input_ref = os.path.join(cwd, 'input_dir', 'reference.link')
with open(input_ref) as fh:
    print(fh.read())

created_file = os.path.join(os.getenv('EXTERNAL_RESOURCE_DIR'), 'example.txt')

host = os.getenv('HOSTNAME')
user = os.getenv('USERNAME')
pk = os.getenv('PRIVATE_KEY')
kt = os.getenv('KEY_TYPE')
key = common.make_key_from(pk, kt)
with common.make_sftp(host, user, key) as sftp:
    sftp.putfo(io.StringIO('Hello World'), created_file)

output = os.path.join(cwd, 'output_dir', 'reference.link')
with open(output, 'w') as fh:
    fh.write(created_file)
