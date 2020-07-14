#!/usr/bin/env python
import io
import os
import uuid
import time
import json

import common


# 1. fetch variables
q2_vars = common.get_q2_environment_variables()

# 2. Dereference reference.link inputs into artifact FPs and metadata FPs
dereferenced = {}
dereferenced['inputs'] = common.deref_block(q2_vars['inputs'])
dereferenced['metadata'] = common.deref_block(q2_vars['metadata'])
dereferenced['columns'] = {
    k: [common.deref(md), c] for k, (md, c) in q2_vars['columns']}
dereferenced['params'] = q2_vars['params']
dereferenced['outputs'] = q2_vars['outputs']

# 3. Template inputs and action into a Python script. Loading the
#    monsoon paths and primitives (which are strings) will occur inside of
#    this templated script. The script should also generate an output manifest
#    for consumption on bacon

template = common.get_template('q2_runner.py')
script = io.StringIO(template.render(concourse_args=dereferenced,
                                     plugin=q2_vars['plugin'], 
                                     action=q2_vars['action']))

# 4. Use paramiko to transfer the templated script

slurm_conf = common.get_slurm_environment_variables()

job_dir = os.path.join(common.get_working_dir(), str(uuid.uuid4()))
submission_template = common.get_template('job.sh')
submission = io.StringIO(
    submission_template.render(job_name='', workdir=job_dir, **slurm_conf))

with common.make_client_from_env() as client:
    sftp = client.open_sftp()
    sftp.mkdir(job_dir)
    sftp.putfo(script, os.path.join(job_dir, 'job.py'))
    job_path = os.path.join(job_dir, 'job.sh')
    sftp.putfo(submission, job_path)

# 5. Use paramiko to `srun` (or maybe `sbatch` and `tail`) the script,
#    blocking until the queue finishes the job

    channel = client.invoke_shell()
    channel.set_combine_stderr(True)
    channel.exec_command(f'sbatch --wait {job_path}')
    output_path = os.path.join(job_dir, 'stdio.out')
    while not channel.exit_status_ready():
        time.sleep(0.5)
        if channel.recv_ready():
            print(channel.recv(1024), end='')

        try:
            with sftp.open(output_path, 'r') as fh:
                for line in fh:
                    print(line, end='')
            break
        except IOError:
            pass
        
# 6. If successful, transfer the output manifest and write out reference.link
#    files

    # script has finished
    with sftp.open(os.path.join(job_dir, 'manifest.json'), 'r') as fh:
        manifest = json.loads(fh.read())
        for key, path in manifest.items():
            outdir = os.path.join('outputs', key)
            os.mkdir(outdir)
            with open(os.path.join(outdir, 'reference.link'), 'w') as fh:
                fh.write(path)
