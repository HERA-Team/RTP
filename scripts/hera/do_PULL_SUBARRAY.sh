#! /bin/bash
set -e

echo "extract_hh.py --extension=HH --filetype=miriad ${1}"
extract_hh.py --extension=HH --filetype=miriad ${1}
