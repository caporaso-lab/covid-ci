#!/usr/bin/env python
import os
import qiime2

artifact = qiime2.Artifact.import_data('{{ type_ }}', '{{ input_ }}',
                                       view_type='{{ format_ }}')
path = artifact.save(os.path.join('{{ output }}', str(artifact.uuid)))

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
