#!/usr/bin/env python

import qiime2
import pandas as pd
import pandas.testing as pdt


seqs = qiime2.Artifact.load('{{ seqs }}')
md = qiime2.Metadata.load('{{ metadata }}')

seqs_index = seqs.view(pd.Series).index
md_index = md.to_dataframe().index

pdt.assert_index_equal(seqs_index, md_index)
