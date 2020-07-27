#!/usr/bin/env python
import uuid
import pandas as pd

metadata_files = {{ md }}
dfs = [pd.read_csv(f, sep='\t') for f in metadata_files]

merged_df = pd.concat(dfs)

path = os.path.join('{{ output }}', str(uuid.uuid4())
merged_df.to_csv(path, sep='\t', index=False)

with open(os.path.join(os.getcwd(), 'manifest.json'), 'w') as fh:
    fh.write(json.dumps({'result': path}))
