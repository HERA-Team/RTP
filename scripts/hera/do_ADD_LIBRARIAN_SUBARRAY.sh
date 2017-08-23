#! /bin/bash
set -e

conn_name=$1
librarian_path=$2
f=$(basename $3 uv)

for ext in HH ; do
    FILE="$f$ext.uv"
    echo upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
    upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
done
