"""
Script for running Progressive Mauve.
"""

import logging
import pickle
import os
import subprocess

from Bio import SeqIO
from Bio import Seq


# Useful absolute paths.
MODULE_LOCATION = os.path.realpath(__file__)
MODULE_DIR = os.path.split(MODULE_LOCATION)[0]
PROJECT_HOME_DIR = os.path.split(MODULE_DIR)[0]

# Location of sequences.
SEQUENCE_DIR = os.path.join(PROJECT_HOME_DIR, 'sequences')

# Special to our project.
MDS42_FILE = os.path.join(SEQUENCE_DIR, 'mds42.gbk')

# Destination for output.
OUTPUT_DIR = os.path.join(PROJECT_HOME_DIR, 'mauve_output')


# Progressive Mauve-related
PROGRESSIVE_MAUVE_BIN = '/opt/mauve_2.3.1/linux-x64/progressiveMauve'
MAUVE_OUTPUT = os.path.join(OUTPUT_DIR, 'align.xmfa')
MAUVE_TMP = os.path.join(MODULE_DIR, 'mauve_tmp')
MAUVE_SCRATCH_PATH_1 = os.path.join(MODULE_DIR, 'mauve_tmp_1')
MAUVE_SCRATCH_PATH_2 = os.path.join(MODULE_DIR, 'mauve_tmp_2')

# Caching.
CACHE_DIR = os.path.join(PROJECT_HOME_DIR, 'cache')
VALID_SEQ_FILES_CACHE = os.path.join(CACHE_DIR, 'valid_seq_files.cache')

# Logging
LOG_FILE = os.path.join(MODULE_DIR, 'progressive_mauve_runner.log')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
        format='%(asctime)s %(message)s')


def run_progressive_mauve(sequence_file_paths):
    """Run progressive mauve."""
    cmd_as_list = ['env', 'TMPDIR=' + MAUVE_TMP, PROGRESSIVE_MAUVE_BIN]

    # Set the output destination.
    cmd_as_list.extend(['--output=' + MAUVE_OUTPUT])

    # # Set scratch paths manually.
    # cmd_as_list.extend(['--scratch-path-1=' + MAUVE_SCRATCH_PATH_1])
    # cmd_as_list.extend(['--scratch-path-2=' + MAUVE_SCRATCH_PATH_2])

    for seq_file in sequence_file_paths:
        cmd_as_list.extend([seq_file])

    # Log the command we used so we can recover the order, just in case.
    logging.info(' '.join(cmd_as_list))

    subprocess.call(cmd_as_list)


def determine_valid_sequence_file_paths(force_recalculate=False):
    """Returns the list of valid sequence file paths.

    A file must be of type genbank and must have a sequence. Some downloaded
    genbank files dont have sequences because, for example, they are the master
    record from a shotgun sequencing run.

    Args:
        force_recalculate: Whether to force recalculation. Otherwise we try to
            look for cached output from a previous run.
    """
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    # Try to find cached.
    if not force_recalculate:
        try:
            with open(VALID_SEQ_FILES_CACHE) as fh:
                return pickle.load(fh)
        except:
            pass

    valid_sequence_files = []
    for maybe_seq_filename in os.listdir(SEQUENCE_DIR):
        print 'Testing %s ...' % maybe_seq_filename

        if not '.gbk' == os.path.splitext(maybe_seq_filename)[1]:
            print '...Not a genbank file. Skipping.'
            continue

        # Check if the file contains a sequence.
        path_to_file = os.path.join(SEQUENCE_DIR, maybe_seq_filename)
        with open(path_to_file) as fh:
            record = SeqIO.read(fh, 'genbank')
            if isinstance(record.seq, Seq.UnknownSeq):
                print '...No sequence detected. Skipping.'
                continue
            else:
                valid_sequence_files.append(path_to_file)

    # Hack to put mds42 first. I think this will make inspecting the initial
    # progressiveMauve output by eye a bit easier, since in the .backbone file
    # the first column will correspond to mds42.
    valid_sequence_files.append(MDS42_FILE)
    assert MDS42_FILE in valid_sequence_files
    valid_sequence_files.remove(MDS42_FILE)
    valid_sequence_files = [MDS42_FILE] + valid_sequence_files
    assert 0 == valid_sequence_files.index(MDS42_FILE)

    # Cache the results for future iterations.
    with open(VALID_SEQ_FILES_CACHE, 'w') as fh:
        pickle.dump(valid_sequence_files, fh)

    return valid_sequence_files


if __name__ == '__main__':
    sequence_file_paths = determine_valid_sequence_file_paths()
    run_progressive_mauve(sequence_file_paths)
