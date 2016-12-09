#! /bin/bash
#
# This doesn't delete any particular data on the still, but it marks the
# raw data managed by the librarian as deletable.

set -e
CONNECTION_NAME=$1
FILE_NAME=$2

librarian_set_file_deletion_policy.py $CONNECTION_NAME $FILE_NAME allowed
