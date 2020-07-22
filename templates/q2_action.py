#!/usr/bin/env python
import os
import json
import itertools

import qiime2
import qiime2.sdk as sdk
from qiime2.sdk.util import parse_primitive

import qiime2.plugins.{{ plugin }}.actions as q2_{{ plugin }}

concourse_args = {{ concourse_args }}
used = set()

def _load_as_metadata(fp):
    if fp.endswith('.qza'):
        return qiime2.Artifact.load(fp).view(qiime2.Metadata)
    else:
        return qiime2.Metadata.load(fp)

def _dereference_kwargs(kwargs, kwarg_type, ref):
    for param, spec in ref.items():
        if param not in concourse_args[kwarg_type]:
            continue

        if kwarg_type == 'columns':
            file_, col = concourse_args['columns'][param]
            loaded = _load_as_metadata(file_).get_column(col)
            used.add(param)
        else:
            arg = concourse_args[kwarg_type][param]
            used.add(param)

            if kwarg_type == 'params':
                loaded = parse_primitive(spec.qiime_type, arg)
            elif kwarg_type == 'metadata':
                if type(arg) is list:
                    loaded = [_load_as_metadata(f) for f in arg]
                    loaded = loaded[0].merge(*loaded[1:])
                else:
                    loaded = _load_as_metadata(arg)
            elif kwarg_type == 'inputs':
                if type(arg) is list:
                    loaded = [qiime2.Artifact.load(f) for f in arg]
                else:
                    loaded = qiime2.Artifact.load(arg)

        kwargs[param] = loaded


pm = sdk.PluginManager()
action = pm.get_plugin(id='{{ plugin }}').actions['{{ action }}']

# generate kwargs after dereferencing QZAs and MD
kwargs = {}

_dereference_kwargs(kwargs, 'inputs', action.signature.inputs)
_dereference_kwargs(kwargs, 'metadata', action.signature.parameters)
_dereference_kwargs(kwargs, 'columns', action.signature.parameters)
_dereference_kwargs(kwargs, 'params', action.signature.parameters)

for param in itertools.chain(concourse_args,
                             concourse_args['inputs'],
                             concourse_args['metadata'],
                             concourse_args['columns'],
                             concourse_args['params']):
    if param not in used:
        raise ValueError(f"Unused parameter: {param} is it misspelled?")

print()
print('Now executing {{ plugin }} {{ action }} with these arguments:',
      flush=True)
for param, arg in kwargs.items():
    print(f'  {param}: {arg}', flush=True)

results = q2_{{ plugin }}.{{ action }}(**kwargs)

print("Execution successful.", flush=True)
print()

manifest = {}

for key, value in zip(results._fields, results):
    uuid = str(value.uuid)
    output_path = os.path.join(concourse_args['outputs'][key], uuid)
    print(f'Saving {key} ({value})', flush=True)
    output_path = value.save(output_path)
    manifest[key] = output_path

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps(manifest))

print()
print("Done.", flush=True)
