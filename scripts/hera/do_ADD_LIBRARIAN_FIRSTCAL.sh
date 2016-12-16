#! /bin/bash
set -e

conn_name=$1
librarian_path=$3
f=$(basename $2 uvc)

# Only the hexes get firstcal'd:

for ext in HH ; do
    local_file="$f$ext.uvc.fc.npz"
    librarian_file="$f$ext.uvc.firstcal.npz"
    echo upload_to_librarian.py $conn_name $local_file $librarian_path/$librarian_file
    upload_to_librarian.py $conn_name $local_file $librarian_path/$librarian_file
done
