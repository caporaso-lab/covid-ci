#!/usr/bin/env python
import os
import uuid
import json

import pandas as pd

import qiime2

selection = qiime2.Artifact.load('{{ selection }}')
sel_ids = selection.view(qiime2.Metadata).to_dataframe().index

metadata_files = {{ md }}
context_df = pd.read_csv('{{ context_md }}', sep='\t')
context_df = context_df[context_df['id'].isin(sel_ids)]

dfs = [pd.read_csv(f, sep='\t') for f in metadata_files]

dfs.append(context_df)
merged_df = pd.concat(dfs)

path = os.path.join('{{ output }}', 'metadata-' + str(uuid.uuid4()) + '.tsv')
merged_df = merged_df[[
    'id', 'gisaid_epi_isl', 'region', 'country', 'division', 'location',
    'combined_location', 'date', 'submitting_lab']]
merged_df.to_csv(path, sep='\t', index=False)

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
