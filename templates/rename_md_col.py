#!/usr/bin/env python
import os
import json
import skbio

import pandas as pd

input_ = '{{ input }}'

with skbio.io.open(input_) as fh:
    df = pd.read_csv(fh, sep='\t')

new_df = pd.DataFrame()

new_df['id'] = df['strain']

if 'gisaid_epi_isl' in df.columns:
    new_df['gisaid_epi_isl'] = df['gisaid_epi_isl']
    non_epi_ids = ~new_df['gisaid_epi_isl'].str.startswith('EPI_')
    new_df['gisaid_epi_isl'].loc[non_epi_ids] = None

new_df['submitting_lab'] = df['submitting_lab']
new_df['region'] = df['region'].str.replace(' ', '')
new_df['country'] = df['country'].str.replace(' ', '')
new_df['division'] = df['division'].str.replace(' ', '')
new_df['location'] = df['location'].str.replace(' ', '')

new_df['combined_location'] = \
    new_df[['country', 'division', 'location']].agg(
        lambda x: '.'.join([s if type(s) == str else 'MISSING' for s in x]),
        axis=1)

new_df['date'] = df['date']

new_df = new_df.loc[new_df['date'].str.count('-') == 2]

path = os.path.join('{{ output }}', os.path.basename(input_))
new_df.to_csv(path, sep='\t', index=False)

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
