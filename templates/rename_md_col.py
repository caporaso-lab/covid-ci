#!/usr/bin/env python
import os

import pandas as import pd


df = pd.read_csv('{{ input }}', sep='\t')
df = df.rename(columns={'strain':'id'})

df.to_csv('{{ output }}' ,sep='\t')

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': '{{ output }}'}))
