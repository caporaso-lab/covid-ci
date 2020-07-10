#!/usr/bin/env python
import qiime2
import qiime2.sdk as sdk

from qiime2.plugins.{{ plugin }}.actions import {{ action }}

concourse_args = {{ concourse_args }}


# generate kwargs after derefencing QZAs and MD


results = {{ action }}(**kwargs)

manifest = {}

for key, value in zip(results._fields, results):
    uuid = value.uuid
    output_path = os.join(concourse_args['outputs'][key], uuid)
    output_path = value.save(output_path)
    manifest[key] = output_path

