"""
Script to download the sequences from NCBI.
"""

import json
import os
import re

from Bio import Entrez
from bs4 import BeautifulSoup

# Relative path to this module.
MODULE_LOCATION = os.path.realpath(__file__)
MODULE_DIR = os.path.split(MODULE_LOCATION)[0]
PROJECT_HOME_DIR = os.path.split(MODULE_DIR)[0]

# Destination for downloads.
DESTINATION_DIR = os.path.join(PROJECT_HOME_DIR, 'sequences')

# Source html with ids.
DEFAULT_SOURCE_HTML_TABLE = os.path.join(DESTINATION_DIR, 'sequence_ids.html')

# Email sent to NCBI with request to avoid getting throttled.
EMAIL = 'gleb@genetics.med.harvard.edu'

# NCBI recommends adding an email to your request, reducing the chances
# that they throttle you.
Entrez.email = EMAIL


def download(source_id_list, force_download=[]):
    """Attempts to download and save all the sequences defined in the source
    file.

    Args:
        source_id_list: List of source ids used to query NCBI.
    """
    if not os.path.exists(DESTINATION_DIR):
        os.mkdir(DESTINATION_DIR)

    failed_fetches = []

    for seq_id in source_id_list:
        print 'Fetching %s ...' % seq_id
        source_output = os.path.join(DESTINATION_DIR, seq_id + '.gbk')
        if not seq_id in force_download and os.path.exists(source_output):
            print '...already fetched.'
            continue

        try:
            data_handle = Entrez.efetch(db='nucleotide', id=seq_id, rettype='gb')
            with open(source_output, 'w') as fh:
                fh.write(data_handle.read())
        except:
            print '...failed.'
            failed_fetches.append(seq_id)

    # Write the failed files
    failed_output = os.path.join(DESTINATION_DIR, 'failed_seq_fetch.txt')
    with open(failed_output, 'w') as fh:
        for failed_id in failed_fetches:
            fh.write(failed_id + '\n')


def extract_source_ids_from_html(html_source=None):
    """Extracts the list of ids from the html source.

    Returns:
        List of strings ids.
    """
    use_html_source = html_source if html_source else DEFAULT_SOURCE_HTML_TABLE
    with open(use_html_source) as fh:
        soup = BeautifulSoup(fh.read())

    source_id_list = []

    id_attribute_els = soup.find_all('span', {'class': 'tag-json'})
    # assert 61 == len(id_attribute_els)
    for seq_id_el in id_attribute_els:
        json_obj = json.loads(seq_id_el.string)
        source_id_list.append(str(json_obj['attrs']['text']))

    return source_id_list


if __name__ == '__main__':
    source_id_list = extract_source_ids_from_html()
    download(source_id_list, force_download=['U00096'])
