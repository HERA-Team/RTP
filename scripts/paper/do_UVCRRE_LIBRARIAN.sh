#! /bin/bash
#
# example configuration: args = ['onsite', '%s/%s' % (path,basename)]
#
# first argument is the "connection" -- used to decide how to connect to librarian
# second argument is the local file name with path prefix
#
# Note that the actual file of interest is present in PWD *without* the
# path prefix.
#
# XXX redundant with the other do_*_LIBRARIAN.sh scripts

conn="$1"
fullpath="$2"

exec upload_to_librarian.py $conn $(basename $fullpath) $fullpath
