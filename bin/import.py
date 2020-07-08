#!/usr/bin/env python

import os

cwd = os.cwd()

input_dir = os.path.join(cwd, 'input_dir')
output = os.path.join(cwd, 'output_dir', 'file.txt')

print(os.path.listdir(input_dir))

with open(output, 'w') as fh:
    fh.write("hello world")
