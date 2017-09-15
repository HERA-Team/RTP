#! /bin/bash
set -e
if [ -d "$1" ]; then
    # make directory rw to remove, since librarian defaults to ro
    chmod -R u+w "$1"
    rm -rf "$1"
fi
echo scp -r -c arcfour256 "$2" .
scp -r -c arcfour256 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "$2" .
