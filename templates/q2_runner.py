#!/usr/bin/env python

import os
import json

import qiime2
import qiime2.sdk as sdk
from qiime2.sdk.util import parse_primitive

from qiime2.plugins.{{ plugin }}.actions import {{ action }}

concourse_args = {{ concourse_args }}

pm = sdk.PluginManager()
action = sdk.get_plugin(id={{ plugin }}).actions[{{ action }}]

# generate kwargs after dereferencing QZAs and MD
kwargs = {}

for param, spec in actions.signature.parameters.items():
    if param not in concourse_args['params']:
        continue
    arg = concourse_args['params'][param]
    deserialized = parse_primitive(spec.qiime_type, arg)
    kwargs[param] = deserialized

for param, spec in actions.signature.parameters.items():
    if param not in concourse_args['metadata']:
        continue
    arg = concourse_args['metadata'][param]
    if type(arg) is list:
        loaded = [qiime2.Metadata.load(f) for f in arg]
        loaded = loaded[0].merge(*loaded[1:])
    else:
        loaded = qiime2.Metadata.load(arg)
    kwargs[param] = loaded

for param, spec in actions.signature.parameters.items():
    if param not in concourse_args['columns']:
        continue
    file_, col = concourse_args['columns'][param]
    loaded = qiime2.Metadata.load(file_).get_column(col)
    kwargs[param] = loaded

for param, spec in actions.signature.parameters.items():
    if param not in concourse_args['inputs']:
        continue
    arg = concourse_args['inputs'][param]
    if type(arg) is list:
        loaded = [qiime2.Artifact.load(f) for f in arg]
    else:
        loaded = qiime2.Artifact.load(arg)
    kwargs[param] = loaded


results = {{ action }}(**kwargs)

manifest = {}

for key, value in zip(results._fields, results):
    uuid = value.uuid
    output_path = os.path.join(concourse_args['outputs'][key], uuid)
    output_path = value.save(output_path)
    manifest[key] = output_path

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps(manifest))
