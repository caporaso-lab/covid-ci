#!/usr/bin/env python
import sys

import qiime2
import pandas as pd
import pandas.testing as pdt


seqs = qiime2.Artifact.load('{{ seqs }}')
md = qiime2.Metadata.load('{{ metadata }}')

seqs_index = seqs.view(pd.Series).index
md_index = md.to_dataframe().index

missing_metadata = seqs_index.difference(md_index)

if not missing_metadata.empty:
    print("Missing metadata for the following ids:", flush=True)
    for id_ in missing_metadata:
        print('  ' + id, flush=True)

    sys.exit(1)