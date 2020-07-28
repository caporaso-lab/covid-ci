import os
import json

from scipy.sparse import diags
from biom.table import Table

from qiime2 import Artifact, Metadata


input_ = '{{ input }}'
seqs = Artifact.load(input_)
md = seqs.view(Metadata)
ids = list(md.get_ids())

matrix = Table(diags([1], 0, shape=(len(ids), len(ids))), observation_ids=ids,
               sample_ids=ids)
art = Artifact.import_data('FeatureTable[Frequency]', matrix)

path = os.path.join('{{ output }}', os.path.basename(input_))
art.save(path)

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
