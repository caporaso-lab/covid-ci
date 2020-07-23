#!/usr/bin/env python
import io
import os
import sys
import uuid
import time
import json

import common


# 1. fetch variables
if 'SCRIPT' in os.environ:
    template = common.get_template(os.environ['SCRIPT'])
    deref, vars_ = common.get_script_variables()
    deref = common.deref_block(deref)
    script = io.StringIO(template.render(**vars_, **deref))
    job_name = os.environ['SCRIPT']
else:
    q2_vars = common.get_q2_environment_variables()

    if 'plugin' in q2_vars:
        # 2. Dereference reference.link inputs into artifact FPs and metadata
        #    FPs
        dereferenced = {}
        dereferenced['inputs'] = common.deref_block(q2_vars['inputs'])
        dereferenced['metadata'] = common.deref_block(q2_vars['metadata'])
        dereferenced['columns'] = {
            k: [common.deref(md), c]
            for k, (md, c) in q2_vars['columns'].items()}
        dereferenced['params'] = q2_vars['params']
        dereferenced['outputs'] = q2_vars['outputs']

        # 3. Template inputs and action into a Python script. Loading the
        #    monsoon paths and primitives (which are strings) will occur inside
        #    of this templated script. The script should also generate an
        #    output manifest for consumption on bacon

        template = common.get_template('q2_action.py')
        script = io.StringIO(template.render(concourse_args=dereferenced,
                                            plugin=q2_vars['plugin'],
                                            action=q2_vars['action']))
        job_name = '%s::%s' % (q2_vars['plugin'], q2_vars['action'])
    elif q2_vars['action'] == 'import':
        input_ = common.deref(q2_vars['input'])
        type_ = q2_vars['type']

        if 'format' in q2_vars:
            format_ = repr(q2_vars['format'])
        else:
            format_ = None

        output = q2_vars['output']

        template = common.get_template('q2_import.py')
        script = io.StringIO(template.render(input_=input_, type_=type_,
                                            format_=format_, output=output))
        job_name = 'import'
    elif q2_vars['action'] == 'export':
        input_ = common.deref(q2_vars['input'])

        if 'format' in q2_vars:
            format_ = repr(q2_vars['format'])
        else:
            format_ = None

        ext = q2_vars['ext']
        output = q2_vars['output']

        template = common.get_template('q2_export.py')
        script = io.StringIO(template.render(input_=input_, format_=format_,
                                            ext=ext, output=output))
        job_name = 'export'
    elif q2_vars:
        raise Exception(f"unrecognized action {q2_vars['action']}")
    else:
        raise Exception("Nothing to do.")

# 4. Use paramiko to transfer the templated script

slurm_vars = common.get_slurm_environment_variables()
job_id = str(uuid.uuid4())
job_dir = os.path.join(common.get_working_dir(), job_id)
submission_template = common.get_template('job.sh')
submission = io.StringIO(
    submission_template.render(job_name=job_name, workdir=job_dir,
                               slurm_vars=slurm_vars))

with common.make_client_from_env() as client:
    sftp = client.open_sftp()
    sftp.mkdir(job_dir)
    sftp.putfo(script, os.path.join(job_dir, 'job.py'))
    job_path = os.path.join(job_dir, 'job.sh')
    sftp.putfo(submission, job_path)

# 5. Use paramiko to `srun` (or maybe `sbatch` and `tail`) the script,
#    blocking until the queue finishes the job

    print(f"Preparing job: {job_id}")
    transport = client.get_transport()
    channel = transport.open_session()
    channel.set_combine_stderr(True)
    channel.exec_command(f'sbatch --wait {job_path}')
    output_path = os.path.join(job_dir, 'stdio.out')
    stdout_fh = None
    while not channel.exit_status_ready():
        time.sleep(0.5)
        if channel.recv_ready():
            print(channel.recv(1024).decode('utf-8'), end='')

        if stdout_fh is None:
            try:
                stdout_fh = iter(sftp.open(output_path, 'r'))
                for line in stdout_fh:
                    print(line, end='')
            except IOError:
                pass
        else:
            for line in stdout_fh:
                print(line, end='')

    for line in stdout_fh:
        print(line, end='')
    stdout_fh.close()

    error_code = channel.recv_exit_status()
    if error_code:
        print('There was an error completing the job.')
        sys.exit(error_code)

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

    for file_ in sftp.listdir(job_dir):
        sftp.remove(os.path.join(job_dir, file_))
    sftp.rmdir(job_dir)
