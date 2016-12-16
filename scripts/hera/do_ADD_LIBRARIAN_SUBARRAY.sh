#! /bin/bash
set -e

conn_name=$1
librarian_path=$3
f=$(basename $2 uvc)

for ext in HH ; do
    FILE="$f$ext.uvc"
    echo upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
    upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
done
