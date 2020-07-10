#!/usr/bin/env python




# 1. fetch variables

# 2. Dereference reference.link inputs into artifact FPs and metadata FPs

# 3. Template inputs and action into a Python script. Dereferencing the
#    monsoon paths and primitives (which are strings) will occur inside of
#    this templated script. The script should also generate an output manifest
#    for consumption on bacon

# 4. Use paramiko to transfer the templated script

# 5. Use paramiko to `srun` (or maybe `sbatch` and `tail`) the script, 
#    blocking until the queue finishes the job

# 6. If successful, transfer the output manifest and write out reference.link
#    files