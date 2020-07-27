#!/usr/bin/env python
import os
import uuid
import json

import pandas as pd


metadata_files = {{ md }}
dfs = [pd.read_csv(f, sep='\t') for f in metadata_files]

merged_df = pd.concat(dfs)

path = os.path.join('{{ output }}', 'metadata-' + str(uuid.uuid4()) + '.tsv')
merged_df.to_csv(path, sep='\t', index=False)
merged_df = merged_df[[
    'id', 'gisaid_epi_isl', 'region', 'country', 'division', 'location',
    'combined_location', 'date', 'submitting_lab']]

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
