#!/usr/bin/env python

import tarfile
import collections
import pandas as pd
from sys import argv
import skbio.io

def _file_handle_from_tar_fp(archive_fp, target_file_extension):
    archive_f = tarfile.open(archive_fp, mode='r')
    if not target_file_extension.startswith('.'):
        target_file_extension = '.%s' % target_file_extension
    target_fn = None
    for n in archive_f.getnames():
        if n.endswith(target_file_extension):
            if target_fn is None:
                target_fn = n
            else:
                raise ValueError(
                       'More than one %s file are present in the archive (%s and %s).' 
                       % (target_file_extension, n, target_fn))

    if target_fn is None:            
        raise ValueError(
           'No %s file found in the archive. Contents are:\n %s' 
           % (target_file_extension, '\n '.join(sequences_f.getnames())))
    
    return archive_f.extractfile(target_fn)

def _process_gisaid(sequences_f, md_f, dl_f, output_sequences_fp, 
                    output_metadata_fp, verbose=True, test_run=False):

    genome_metadata_fields = ['id', 
                             'metadata_id',
                             'fasta_id',
                             'collection_date',
                             'submission_date',
                             'full_location',
                             'location1',
                             'location2',
                             'location3',
                             'location4',
                             'location5',
                             'location6',
                             'location7',
                             'host']
    GenomeMetadata = collections.namedtuple('GenomeMetadata', genome_metadata_fields)

    # skip the header line (though ultimately we should use this to id columns of interest)
    _ = md_f.readline()
    _ = dl_f.readline()

    genome_metadata = collections.OrderedDict()

    processed_records = 0
    with open(output_sequences_fp, 'w') as output_seqs_f:
        for md_line, dl_line, seq in zip(md_f, dl_f, skbio.io.read(sequences_f, format='fasta')):
            
            if test_run and processed_records == 100:
                break
            
            md_line = md_line.decode(encoding='UTF-8')
            dl_line = dl_line.decode(encoding='UTF-8')

            fasta_id = ' '.join([seq.metadata['id'], seq.metadata['description']])

            md_fields = md_line.split('\t')
            md_id = md_fields[0]
            accession_id = md_fields[2]

            dl_fields = dl_line.split('\t')
            collection_date = dl_fields[1]
            location = dl_fields[2]
            split_location = [None] * 7
            for i, loc in enumerate(location.split('/')):
                split_location[i] = loc.strip()
            submission_date = dl_fields[4]

            date_label = '|'.join([collection_date, submission_date])

            if accession_id in genome_metadata:
                print('💩 : Duplicate accession id detected (%s)' % accession_id)
            elif md_id not in fasta_id:
                print('💩 : metadata id (%s) and fasta id (%s) are inconsistent for accession id %s' %
                        (md_id, fasta_id, accession_id))
            elif md_id not in fasta_id:
                print('💩 : metadata id (%s) and fasta id (%s) are inconsistent for accession id %s' %
                        (md_id, fasta_id, accession_id))
            elif date_label not in fasta_id:
                print('💩 : date label (%s) is inconsistent with fasta id %s' %
                        (date_label, fasta_id))
            else:
                seq.metadata['id'] = accession_id
                seq.metadata['description'] = ''
                genome_metadata[accession_id] = \
                    GenomeMetadata(id=accession_id, collection_date=collection_date,
                                full_location=location, submission_date=submission_date, 
                                metadata_id=md_id, fasta_id=fasta_id, 
                                location1=split_location[0], location2=split_location[1], 
                                location3=split_location[2], location4=split_location[3],
                                location5=split_location[4], location6=split_location[5],
                                location7=split_location[6], host=None)
                seq.write(output_seqs_f)
            processed_records += 1
    
    metadata = pd.DataFrame(genome_metadata.values(), columns=genome_metadata_fields).set_index('id')
    metadata.to_csv(output_metadata_fp, sep='\t')

    if verbose: print("🦠 Processed %d records." % processed_records)

if __name__ == "__main__":
    usage = ("process_gisaid.py input-sequences-path "
             "input-dates-and-locations-path input-metadata-path "
             "output-sequences-path output-metadata-path")
    
    test_run = False
    
    if len(argv) == 2 and argv[1] == '--help':
        print(usage)
        exit(0)
    elif len(argv) != 6:
        print("Must pass exactly five command line parameters:")
        print(usage)
        exit(-1)
    else:
        sequences_f = _file_handle_from_tar_fp(argv[1], '.fasta')
        dl_f = _file_handle_from_tar_fp(argv[2], '.tsv')
        md_f = _file_handle_from_tar_fp(argv[3], '.tsv')
        output_sequences_fp = argv[4]
        output_metadata_fp = argv[5]

        _process_gisaid(sequences_f, md_f, dl_f, output_sequences_fp, 
                        output_metadata_fp, verbose=True, test_run=test_run)
    
