#!/usr/bin/env python
import os

import pandas as pd

input_ = '{{ input }}'
df = pd.read_csv(input_, sep='\t')
df = df.rename(columns={'strain': 'id'})

path = os.path.join('{{ output }}', os.path.basename(input_))
df.to_csv(path, sep='\t')

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path))
