#!/usr/bin/env python

import os

cwd = os.getcwd()

input_ref = os.path.join(cwd, 'input_dir', 'reference.link')
with open(input_ref) as fh:
    print(fh.read())

created_file = os.path.join(os.getenv('EXTERNAL_RESOURCE_DIR'), 'example.txt')

output = os.path.join(cwd, 'output_dir', 'reference.link')
with open(output, 'w') as fh:
    fh.write(created_file)
