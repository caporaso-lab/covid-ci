#!/usr/bin/env python
import os
import json
import qiime2
import qiime2.util
import qiime2.sdk as sdk

artifact = qiime2.Artifact.load('{{ input_ }}')
view = artifact.view(sdk.parse_format({{ format_ }}))

path = os.path.join('{{ output }}', str(artifact.uuid) + '{{ ext }}')

qiime2.util.duplicate(str(view), path)

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
