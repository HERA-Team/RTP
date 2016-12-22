#! /bin/bash
#
# We have to make the directories writeable to remove them since
# Librarian makes things read-only on ingest.
set -e
chmod -R u+w "$1"
rm -rf "$1"

