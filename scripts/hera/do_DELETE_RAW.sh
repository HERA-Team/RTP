#! /bin/bash
set -e

#rm -rf $1
FILENAME=$2
CONNECTION_NAME=$1
librarian_set_file_deletion_policy.py $CONNECTION_NAME $FILE_NAME allowed
