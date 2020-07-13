#!/usr/bin/env python
import os

import common


# 1. fetch variables
q2_vars = common.get_q2_environment_variables()

# 2. Dereference reference.link inputs into artifact FPs and metadata FPs
loaded_inputs = {}
for name, input_temps in q2_vars['inputs'].items():
    loaded_inputs[name] = []
    for temp_path in input_temps.split(' '):
        with open(temp_path) as fh:
            loaded_inputs[name].append(fh.readline())

loaded_metadata = {}
for name, md_temps in q2_vars['metadata'].items():
    md = md.split(':')
    with open(md[0]) as fh:
        loaded_metadata[name] = md
        md[0] = fh.readline()

q2_vars['inputs'] = loaded_inputs
q2_vars['metadata'] = loaded_metadata

# 3. Template inputs and action into a Python script. Dereferencing the
#    monsoon paths and primitives (which are strings) will occur inside of
#    this templated script. The script should also generate an output manifest
#    for consumption on bacon

# 4. Use paramiko to transfer the templated script

# 5. Use paramiko to `srun` (or maybe `sbatch` and `tail`) the script,
#    blocking until the queue finishes the job

# 6. If successful, transfer the output manifest and write out reference.link
#    files
