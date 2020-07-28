#!/usr/bin/env python

import os
import time

import common

if 'INPUT_FILE' in os.environ:
    input_file = os.path.join('input', os.environ['INPUT_FILE'])
    file_name = str(int(time.time())) + '_' + os.environ['INPUT_FILE']
else:
    input_file = os.path.join('input', os.listdir('input')[0])
    file_name = os.path.basename(input_file)

output_path = os.path.join(os.environ['EXTERNAL_DIR'], file_name)

with common.make_client_from_env() as client:
    sftp = client.open_sftp()
    sftp.put(input_file, output_path)

with open(os.path.join('output', 'reference.link'), 'w') as fh:
    fh.write(output_path)
