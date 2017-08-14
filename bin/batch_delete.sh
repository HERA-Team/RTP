#! /bin/bash
#delete lots of files. Use sparingly

CONNECTION_NAME='local-rtp'
for FILENAME in $*
do
echo 'librarian_set_file_deletion_policy.py' $CONNECTION_NAME $FILENAME allowed
librarian_set_file_deletion_policy.py $CONNECTION_NAME $FILENAME allowed
done
