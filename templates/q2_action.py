#!/usr/bin/env python
import os
import json

import qiime2
import qiime2.sdk as sdk
from qiime2.sdk.util import parse_primitive

import qiime2.plugins.{{ plugin }}.actions as q2_{{ plugin }}


def _dereference_kwargs(kwargs, kwarg_type, ref):
    for param, spec in ref.items():
        if param not in concourse_args[kwarg_type]:
            continue

        if kwarg_type == 'columns':
            file_, col = concourse_args['columns'][param]
            loaded = qiime2.Metadata.load(file_).get_column(col)
        else:
            arg = concourse_args[kwarg_type][param]

            if kwarg_type == 'param':
                loaded = parse_primitive(spec.qiime_type, arg)
            elif kwarg_type == 'metadata':
                if type(arg) is list:
                    loaded = [qiime2.Metadata.load(f) for f in arg]
                    loaded = loaded[0].merge(*loaded[1:])
                else:
                    loaded = qiime2.Metadata.load(arg)
            elif kwarg_type == 'inputs':
                if type(arg) is list:
                    loaded = [qiime2.Artifact.load(f) for f in arg]
                else:
                    loaded = qiime2.Artifact.load(arg)

        kwargs[param] = loaded


concourse_args = {{ concourse_args }}

pm = sdk.PluginManager()
action = pm.get_plugin(id='{{ plugin }}').actions['{{ action }}']

# generate kwargs after dereferencing QZAs and MD
kwargs = {}

_dereference_kwargs(kwargs, 'params', action.signature.parameters)
_dereference_kwargs(kwargs, 'metadata', action.signature.parameters)
_dereference_kwargs(kwargs, 'columns', action.signature.parameters)
_dereference_kwargs(kwargs, 'inputs', action.signature.inputs)

results = q2_{{ plugin }}.{{ action }}(**kwargs)

manifest = {}

for key, value in zip(results._fields, results):
    uuid = str(value.uuid)
    output_path = os.path.join(concourse_args['outputs'][key], uuid)
    output_path = value.save(output_path)
    manifest[key] = output_path

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps(manifest))
